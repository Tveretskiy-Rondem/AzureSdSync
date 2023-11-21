import requests
import json
import re
import Functions
import Vars

dbCreds = Vars.dbCreds
service = "sd"
# ToDo заменить пре переходе из тестового проекта в Discovery
azureUrl = "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workitems/$Task?api-version=7.0"
# azureUrl = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workitems/$Task?api-version=7.0"
sdCompanyUrl = "https://sd.primo-rpa.ru/api/v1/companies/?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e&id="
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
        responseWorkItem = requests.request("GET", ("https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids=" + str(workItemId)), headers=headers, verify=False)
        responseWorkItem = json.loads(responseWorkItem.text)
        try:
            responseWorkItem = responseWorkItem["value"]
        except KeyError:
            continue
        responseWorkItem = responseWorkItem[0]
        responseWorkItem = responseWorkItem["fields"]
        responseWorkItemStatus = responseWorkItem["System.State"]
        responseWorkItemProject = responseWorkItem["System.AreaPath"]
        # ToDo изменить проект при перехоже на Discovery:
        if responseWorkItemStatus == "Бэклог" and responseWorkItemProject == "tveretskiy_test":
            payloadToBacklog = json.dumps({"code": "primo_rpa_backlog", "comment": "Заявка переведена в бэклог соответственно таске из azure.", "comment_public": False})
            headersToBacklog = {'Content-Type': 'application/json'}
            response = requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/statuses?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headersToBacklog, data=payloadToBacklog)
    else:
        # Связанной задачи нет:
        print("Issue #", issueId, "not assigned to any work item")
        # Получение информации из SD:
        responseIssue = Functions.requestSender(service, "getItem", issueId)
        responseIssueValues = Functions.jsonValuesToList(sdJsonKeys, responseIssue, 0)
        responseStatus = Functions.jsonValuesToList([["status", "name"]], responseIssue, 0)
        # Проверка актуальности статуса:
        if responseStatus == ['На рассмотрении']:
            payloadResult = []
            # Наполнение тела запроса данными:
            for i in range(len(sdJsonKeys)):
                payloadTemplate["path"] = azurePaths[i]
                # Проверка на заполнение типа и поля клиента:
                if azurePaths[i] == "/fields/System.WorkItemType":
                    # Определение статуса work item по статусу заявки SD:
                    if responseIssueValues[i] == "Инцидент" or "Ошибка" or "Прочее":
                      payloadTemplate["value"] = "Bug"
                    else:
                      payloadTemplate["value"] = "User Story"
                elif azurePaths[i] == "/fields/Custom.Client":
                    # Получение названия клиента по id:
                    sdCompanyUrlWithId = sdCompanyUrl + str(responseIssueValues[i])
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

            # Запрос на создание work item:
            payload = json.dumps(payloadResult)

            responseNewAzureWorkItem = requests.request("POST", azureUrl, headers=headers, data=payload, verify=False)
            responseNewAzureWorkItem = json.loads(responseNewAzureWorkItem.text)
            newAzureWorkItemId = responseNewAzureWorkItem["id"]
            newAzureWorkItemUrl = responseNewAzureWorkItem["url"]

            # Запись в таблицу соответствия
            Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_sd_match (azure_work_item_id, sd_issue_id) VALUES(" + str(newAzureWorkItemId) + ", " + str(issueId) + ")")

            # Запись о последнем действии:
            Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Initial review' WHERE id = " + str(newAzureWorkItemId)))
            Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Initial review' WHERE id = " + str(issueId)))

            # Перенос комментариев:
            # ToDo убрать токен:
            responseSdIssueComments = requests.request("GET", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e")
            responseSdIssueComments = json.loads(responseSdIssueComments.text)
            for comment in responseSdIssueComments:
                author = comment["author"]
                author = author["name"]
                text = comment["content"]
                payload = json.dumps({"text": (str(text) + "\Автор в SD:" + str(author))})
                # Todo изменить при переходе на Discovery
                requests.request("POST", "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workItems/" + str(workItemId) + "/comments?api-version=7.0-preview.3", headers=headers, data=payload, verify=False)

            # ToDo Пока не разобрался с добавлением в параметр azure, запись в виде комментария:
            payloadUrlToIssue = json.dumps({
                "comment": {
                    "content": ("Тестовый комментарий. Подлежит удалению. URL сопоставленной задачи в azure:" + str(newAzureWorkItemUrl)),
                    "public": False,
                    "author_id": 22,
                    "author_type": "employee"
                }
            })
            headersUrlToIssue = {'Content-Type': 'application/json'}
            requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headersUrlToIssue, data=payloadUrlToIssue, verify=False)
        else:
            # Статус не подтвержден:
            # ToDo: отправить оповещение?
            continue
