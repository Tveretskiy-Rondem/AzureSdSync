import requests
import json
import Vars
import Functions

# Todo: добавить замедление

dbCreds = Vars.dbCreds
azureAuth = Vars.azureAuth
getWorkItemUrl = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids="
getWorkItemHeaders = {'Authorization': azureAuth}
workItemsList = []
sdToken = Vars.sdToken

# Debug:
issuesComment = []
issuesRelease = []

# Получение списка work items azure с последним статусом "Closed":
closedWorkItemsList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_statuses WHERE status = 'Closed' AND is_last = true ")
closedWorkItemsList = Functions.responseToOneLevelArray(closedWorkItemsList)

# Получение списка work items azure с последней активностью "Closed in azure":
alreadyClosedWorkItemsList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items WHERE last_action = 'Closed in azure' OR last_action = 'Closed in SD'")
alreadyClosedWorkItemsList = Functions.responseToOneLevelArray(alreadyClosedWorkItemsList)

# Получение финального списка work items:
for closedWorkItem in closedWorkItemsList:
    if closedWorkItem not in alreadyClosedWorkItemsList:
        workItemsList.append(closedWorkItem)

# print("Closed azure: ", closedWorkItemsList)
# print("Already closed: ", alreadyClosedWorkItemsList)
# print("Final list: ", workItemsList)
#exit()
for workItemId in workItemsList:
    # Получение заявок в SD для каждой таски:
    matchedIssues = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id = " + str(workItemId))
    matchedIssues = Functions.responseToOneLevelArray(matchedIssues)
    # Получение данных о проекте и назначении на релиз из work item:
    responseWorkItem = requests.request("GET", (getWorkItemUrl + str(workItemId)), headers=getWorkItemHeaders, verify=False)
    responseWorkItem = json.loads(responseWorkItem.text)
    responseWorkItem = responseWorkItem["value"]
    responseWorkItem = responseWorkItem[0]
    responseWorkItemFields = responseWorkItem["fields"]
    responseWorkItemProject = responseWorkItemFields["System.TeamProject"]
    responseWorkItemIteration = responseWorkItemFields["System.IterationPath"]
    responseWorkItemIteration = responseWorkItemIteration.strip(responseWorkItemProject + "\\\\")
    for issueId in matchedIssues:
        # Проверка на статус заявки в SD:
        # Получение статуса (закрыта или нет):
        isIssueClosed = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT status FROM sd_statuses WHERE status = 'Закрыта' AND is_last = true AND id = " + str(issueId) + ")")

        if isIssueClosed:
            continue
        else:
            # Проверка на наличие релиза в wi azure:
            if responseWorkItemIteration == "":
                # В поле релиза пусто:
                # Комментарий в привязанную заявку SD:
                payloadUrlToIssue = json.dumps({
                    "comment": {
                        "content": ("Связанная задача в azure № " + str(workItemId) + " была закрыта."),
                        "public": False,
                        "author_id": 22,
                        "author_type": "employee"
                    }
                })
                headersUrlToIssue = {'Content-Type': 'application/json'}
                requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=" + sdToken, headers=headersUrlToIssue, data=payloadUrlToIssue, verify=False)

                # Debug:
                issuesComment.append(issueId)

            else:
                # Поле релиза заполнено:
                # Комментарий в привязанную заявку SD:
                payloadUrlToIssue = json.dumps({
                    "comment": {
                        "content": ("Связанная задача в azure № " + str(workItemId) + " была закрыта. Запланировано на релиз: " + responseWorkItemIteration),
                        "public": False,
                        "author_id": 22,
                        "author_type": "employee"
                    }
                })
                headersUrlToIssue = {'Content-Type': 'application/json'}
                requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=" + sdToken, headers=headersUrlToIssue, data=payloadUrlToIssue, verify=False)

                # Заполнение поля "Номер релиза в Azure" в SD:
                url = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/parameters?api_token=" + sdToken
                payload = json.dumps({
                    "custom_parameters": {
                        "release_azure": responseWorkItemIteration
                    },
                    "skip_options": [
                        "skip_triggers",
                        "skip_notifications",
                        "skip_webhooks"
                    ]
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)

                # Debug:
                issuesRelease.append(issueId)

        # Добавление отметки о последней активности:
        Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in azure' WHERE id = " + str(workItemId)))
        Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in azure' WHERE id = " + str(issueId)))

# Debug:
print("Closed in azure results:")
print("Only commented:", issuesComment)
print("Commented with release:", issuesRelease)