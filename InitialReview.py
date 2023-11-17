import requests
import json
import re
import Functions
import Vars

dbCreds = Vars.dbCreds
service = "sd"
azureUrl = "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workitems/$Task?api-version=7.0"
sdCompanyUrl = "https://sd.primo-rpa.ru/api/v1/companies/?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e&id="

# url = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workitems/$Task?api-version=7.0"
sdJsonKeys = ["title", "description", ["type", "name"], "id", "company_id"]
azurePaths = ["/fields/System.Title", "/fields/System.Description", "/fields/System.WorkItemType", "/fields/Custom.ServiceDesk", "/fields/Custom.Client"]
payloadTemplate = {"op": "add", "path": "", "from": None, "value": ""}
headers = {
  'Content-Type': 'application/json-patch+json',
  'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='
}

# Получение списка заявок SD, перешедших в статус "На рассмотрении":
issuesOpenToInJob = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_statuses WHERE status = 'На рассмотрении' AND old_status != '' AND is_last = true")
issuesOpenToInJob = Functions.responseToOneLevelArray(issuesOpenToInJob)
for issueId in issuesOpenToInJob:
    workItemId = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT azure_work_item_id FROM azure_sd_match WHERE sd_issue_id = " + str(issueId))
    # Проверка на наличие связанной задачи в azure:
    if workItemId != []:
        # Связанная задача есть, проверка статуса в azure:
        workItemId = workItemId[0][0]
        print("Issue #", issueId, "assigned to work item #", workItemId)
        # requests.request("")
    else:
        # Связанной задачи нет:
        print("Issue #", issueId, "not assigned to any work item")
        # Получение информации из SD:
        responseIssue = Functions.requestSender(service, "getItem", issueId)
        responseIssueValues = Functions.jsonValuesToList(sdJsonKeys, responseIssue, 0)
        responseStatus = Functions.jsonValuesToList([["status", "name"]], responseIssue, 0)
        print("Response status:", responseStatus)
        # Проверка актуальности статуса:
        if responseStatus == ['На рассмотрении']:
            payloadResult = []
            for i in range(len(sdJsonKeys)):
                payloadTemplate["path"] = azurePaths[i]
                # Проверка на заполнение типа (пропускаем, пока тестовому проекту не дали нужные типы) и поля клиента:
                if azurePaths[i] == "/fields/System.WorkItemType":
                    # ToDo Вернуть, когда в азуре появятся статусы:
                    # if responseIssueValues[i] == "Инцидент" or "Ошибка" or "Прочее":
                    #   payloadTemplate["value"] = "Bug"
                    # else:
                    #   payloadTemplate["value"] = "User Story"
                    # ToDo А тут убрать:
                    payloadTemplate["value"] = "Task"
                elif azurePaths[i] == "/fields/Custom.Client":
                    # Получение названия клиента по id:
                    sdCompanyUrlWithId = sdCompanyUrl + str(responseIssueValues[i])
                    print(sdCompanyUrlWithId)
                    responseSdCompany = requests.request("GET", sdCompanyUrlWithId)
                    responseSdCompany = json.loads(responseSdCompany.text)
                    try:
                        payloadTemplate["value"] = responseSdCompany["name"]
                    except KeyError:
                        payloadTemplate["value"] = "None"
                # ToDo очистка текста описания от тегов
                elif azurePaths[i] == "/fields/System.Description":
                    pattern = re.compile('<.*?>')
                    responseIssueValueNoHtml = re.sub(pattern, '', responseIssueValues[i])
                    payloadTemplate["value"] = responseIssueValues[i]
                else:
                    payloadTemplate["value"] = responseIssueValues[i]
                payloadResult.append(payloadTemplate.copy())
                print(payloadResult)

            payload = json.dumps(payloadResult)

            responseNewAzureWorkItem = requests.request("POST", azureUrl, headers=headers, data=payload, verify=False)
            responseNewAzureWorkItem = json.loads(responseNewAzureWorkItem.text)
            newAzureWorkItemId = responseNewAzureWorkItem["id"]

            # Запись в таблицу соответствия
            Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_sd_match (azure_work_item_id, sd_issue_id) VALUES(" + str(newAzureWorkItemId) + ", " + str(issueId) + ")")

            # ToDo перенос комментариев:
            # ToDo убрать токен:
            responseSdIssueComments = requests.request("GET", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e")
            responseSdIssueComments = json.loads(responseSdIssueComments.text)
            for comment in responseSdIssueComments:
                author = comment["author"]
                author = author["name"]
                text = comment["content"]
                payload = json.dumps({"text": (text + "\nАвтор в SD:" + author)})
                requests.request("POST", "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workItems/" + str(
                    workItemId) + "/comments?api-version=7.0-preview.3", headers=headers, data=payload, verify=False)
            # ToDo Запись в заявку SD:

        else:
            # Статус не подтвержден:
            # ToDo: отправить оповещение?
            continue
