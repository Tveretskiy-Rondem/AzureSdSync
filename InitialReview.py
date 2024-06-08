import requests
import json
import re
import Functions
import Vars

azureAuth = Vars.azureAuth
dbCreds = Vars.dbCreds
service = "sd"

azureUrl = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workitems/$Bug?api-version=7.0"
sdCompanyUrl = "https://sd.primo-rpa.ru/api/v1/companies/?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e&id="
# azureUrl = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workitems/$Task?api-version=7.0"
# With Repro steps
# sdJsonKeys = ["title", "description", "description", ["type", "name"], "id", "company_id"]
# azurePaths = ["/fields/System.Title", "/fields/System.Description", "/fields/Microsoft.VSTS.TCM.ReproSteps", "/fields/System.WorkItemType", "/fields/Custom.ServiceDesk", "/fields/Custom.Client"]
sdJsonKeys = ["title", "description", ["type", "name"], "id", "company_id"]
azurePaths = ["/fields/System.Title", "/fields/System.Description", "/fields/System.WorkItemType", "/fields/Custom.ServiceDesk", "/fields/Custom.Client", "/fields/Microsoft.VSTS.TCM.ReproSteps"]
payloadTemplate = {"op": "add", "path": "", "from": None, "value": ""}
headers = {
  'Content-Type': 'application/json-patch+json',
  'Authorization': azureAuth
}

# Debug:
newWorkItemsList = []

# Получение списка заявок SD, перешедших в статус "На рассмотрении":
issuesOpenToInJob = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_statuses WHERE status = 'На рассмотрении' AND old_status != '' AND is_last = true")
issuesOpenToInJob = Functions.responseToOneLevelArray(issuesOpenToInJob)
for issueId in issuesOpenToInJob:
    # Попытка получения связанной задачи в Azure:
    workItemId = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT azure_work_item_id FROM azure_sd_match WHERE sd_issue_id = " + str(issueId))

    # Проверка на наличие связанной задачи в azure:
    if workItemId == []:
        # Если связанная задача не найдена в БД, производится запрос в SD:
        url = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b"
        payload = {}
        headers = {}
        responseSdAzureLink = requests.request("GET", url, headers=headers, data=payload)
        responseSdAzureLink = json.loads(responseSdAzureLink.text)
        for parameter in responseSdAzureLink["parameters"]:
            if parameter["code"] == "1111" and parameter["value"] != "":
                pattern = r"/(?<=\/)\d+"
                azureWorkItemId = re.search(pattern, parameter["value"]).group()
                azureWorkItemId = azureWorkItemId.replace('/', '')
                workItemId.append(azureWorkItemId)
            continue

    if workItemId != []:
        # Связанная задача есть, проверка статуса в azure:
        workItemId = workItemId[0][0]
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
        if responseWorkItemStatus == "Бэклог" and responseWorkItemProject == "Discovery":
            payloadToBacklog = json.dumps({"code": "primo_rpa_backlog", "comment": "Заявка переведена в бэклог соответственно связанной задаче из azure.", "comment_public": False})
            headersToBacklog = {'Content-Type': 'application/json'}
            response = requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/statuses?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headersToBacklog, data=payloadToBacklog)
    else:
        # Связанной задачи нет:
        # Получение информации из SD:
        responseIssue = Functions.requestSender(service, "getItem", issueId)
        responseIssueValues = Functions.jsonValuesToList(sdJsonKeys, responseIssue, 0)
        responseStatus = Functions.jsonValuesToList([["status", "name"]], responseIssue, 0)
        # Проверка актуальности статуса:
        if responseStatus == ['На рассмотрении']:
            payloadResult = []
            # Наполнение тела запроса данными:
            for i in range(len(sdJsonKeys) + 1):
                payloadTemplate["path"] = azurePaths[i]
                # Проверка на заполнение типа и поля клиента:
                if azurePaths[i] == "/fields/System.WorkItemType":
                    # Определение статуса work item по статусу заявки SD:
                    if responseIssueValues[i] == "Инцидент" or responseIssueValues[i] == "Ошибка" or responseIssueValues[i] == "Прочее":
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
                elif azurePaths[i] == "/fields/System.Description":
                    pattern = re.compile('<.*?>')
                    responseIssueValueNoHtml = re.sub(pattern, '', responseIssueValues[i])
                    payloadTemplate["value"] = responseIssueValues[i]
                # Неудачная попытка забрать шаги воспроизведения:
                elif azurePaths[i] == "/fields/Microsoft.VSTS.TCM.ReproSteps":
                    for sdParameter in responseIssue["parameters"]:
                        if str(sdParameter["code"]) == "steps_to_reproduce":

                            pattern = re.compile('<.*?>')
                            try:
                                sdParameterNoHtml = re.sub(pattern, '', sdParameter["value"])
                            except:
                                sdParameterNoHtml = re.sub(pattern, '', "---")
                            payloadTemplate["value"] = sdParameterNoHtml
                else:
                    payloadTemplate["value"] = responseIssueValues[i]
                payloadResult.append(payloadTemplate.copy())

            # Проверка и добавление ReproSteps:

            # Запрос на создание work item:
            payload = json.dumps(payloadResult)
            responseNewAzureWorkItem = requests.request("POST", azureUrl, headers=headers, data=payload, verify=False)
            responseNewAzureWorkItem = json.loads(responseNewAzureWorkItem.text)
            newAzureWorkItemId = responseNewAzureWorkItem["id"]
            newAzureWorkItemUrl = responseNewAzureWorkItem["url"]
            newAzureWorkItemProject = responseNewAzureWorkItem["fields"]
            newAzureWorkItemProject = newAzureWorkItemProject["System.AreaPath"]

            # Запись в таблицу соответствия
            Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_sd_match (azure_work_item_id, sd_issue_id) VALUES(" + str(newAzureWorkItemId) + ", " + str(issueId) + ")")

            # Запись о последнем действии:
            Functions.dbQuerySender(dbCreds, "INSERT", ("INSERT INTO azure_work_items (id, last_action) VALUES('" + str(newAzureWorkItemId) + "', 'Initial review')"))
            Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Initial review' WHERE id = " + str(issueId)))


            # Перенос комментариев:
            responseSdIssueComments = requests.request("GET", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e")
            responseSdIssueComments = json.loads(responseSdIssueComments.text)

            i = len(responseSdIssueComments)
            while i > 0:
            # for comment in responseSdIssueComments:
                comment = responseSdIssueComments[i - 1]
                author = comment["author"]
                author = author["name"]
                text = comment["content"]
                payload = json.dumps({"text": (str(text) + "   Автор в SD: " + str(author))})
                headersComment = {
                    'Content-Type': 'application/json',
                    'Authorization': azureAuth
                }
                respComment = requests.request("POST", "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workItems/" + str(newAzureWorkItemId) + "/comments?api-version=7.0-preview.3", headers=headersComment, data=payload, verify=False)
                i = i - 1

            # Добавление в заявку SD комментария о создании work item:
            workItemUrl = "https://azure-dos.s1.primo1.orch/PrimoCollection/" + newAzureWorkItemProject + "/_workitems/edit/" + str(newAzureWorkItemId)
            payloadUrlToIssueComment = json.dumps({
                "comment": {
                    "content": ("По этой задаче создан work item в azure: " + str(workItemUrl)),
                    "public": False,
                    "author_id": 22,
                    "author_type": "employee"
                }
            })

            # Добавление в заявку SD ссылки на azure дополнительным атрибутом:
            headersUrlToIssue = {'Content-Type': 'application/json'}
            requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headersUrlToIssue, data=payloadUrlToIssueComment, verify=False)
            payloadUrlToIssue = json.dumps({
                "custom_parameters": {
                    "1111": workItemUrl
                }
            })
            response = requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/parameters?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headersUrlToIssue, data=payloadUrlToIssue)

            # Перенос вложений
            responseIssue = Functions.requestSender(service, "getItem", issueId)
            responseAttach = responseIssue["attachments"]

            for attachment in responseAttach:
                try:
                    urlGetAttach = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/attachments/" + str(
                        attachment["id"]) + "?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e"

                    sdAttachmentResponse = requests.request("GET", urlGetAttach)
                    sdAttachmentResponse = json.loads(sdAttachmentResponse.text)
                    print("Response from SD after extract:", sdAttachmentResponse)

                    # Получение и сохранение прикрепленного файла
                    attachedFile = requests.request("GET", sdAttachmentResponse["attachment_url"])
                    open("/tmp/" + sdAttachmentResponse["attachment_file_name"], 'wb').write(attachedFile.content)
                    print("File saved locally")

                    # Загрузка файла на сервер Azure
                    AzurePostAttachUrl = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/attachments?fileName=" + sdAttachmentResponse["attachment_file_name"] + "&api-version=7.0-preview.3"
                    payload = {}
                    files = [('', ('attach', open(('/tmp/' + sdAttachmentResponse["attachment_file_name"]), 'rb')))]
                    headers = {'Content-Type': 'application/octet-stream', 'Authorization': azureAuth}

                    responseAzurePostAttachment = requests.request("POST", AzurePostAttachUrl, headers=headers, data=payload, files=files, verify=False)
                    azureNewAttachmentJson = json.loads(responseAzurePostAttachment.text)
                    azureNewAttachmentUrl = azureNewAttachmentJson["url"]
                    # print("Azure post file response:", responseAzurePostAttachment.text)

                    # Сопоставление файла с work item
                    urlAttachToWI = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workitems/" + str(
                        newAzureWorkItemId) + "?api-version=7.0-preview.3"

                    payload = json.dumps([
                        {
                            "op": "add",
                            "path": "/relations/-",
                            "value": {
                                "rel": "AttachedFile",
                                "url": azureNewAttachmentUrl,
                                "attributes": {
                                    "comment": sdAttachmentResponse["description"]
                                }
                            }
                        }
                    ])
                    headers = {
                        'Content-Type': 'application/json-patch+json',
                        'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='
                    }

                    responseAttachToWI = requests.request("PATCH", urlAttachToWI, headers=headers, data=payload,
                                                          verify=False)
                    print("Azure response attach to WI:", responseAttachToWI)
                except Exception as exc:
                    # Добавление в заявку SD комментария о проблемах с переносом вложений:
                    workItemUrl = "https://azure-dos.s1.primo1.orch/PrimoCollection/" + newAzureWorkItemProject + "/_workitems/edit/" + str(
                        newAzureWorkItemId)
                    payloadUrlToIssueComment = json.dumps({
                        "comment": {
                            "content": ("При переносе вложений в задачу azure возникли проблемы."),
                            "public": False,
                            "author_id": 22,
                            "author_type": "employee"
                        }
                    })
                    print("Error on attachment:", exc)

            # Debug:
            newWorkItemsList.append(newAzureWorkItemId)

        else:
            # Статус не подтвержден:
            # ToDo: отправить оповещение?
            continue

# Debug:
print("New azure work items:", newWorkItemsList)

# Удалить заявку в ажур, удалить по номеру заявки из таблицы
