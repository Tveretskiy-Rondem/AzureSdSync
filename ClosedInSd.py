import requests
import json
import Vars
import Functions

toCloseWorkItemsList = []
onlyCommentClosedWorkItemsList = []
dbCreds = Vars.dbCreds
getWorkItemUrl = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids="
getWorkItemHeaders = {'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}
changeStatusHeaders = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}
postCommentHeaders = {'Content-Type': 'application/json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}
payloadToClose = json.dumps([{"op": "add", "path": "/fields/System.State", "value": "Closed"}])

# Debug:
azureClosed = []
azureCommented = []

# Получение списка заявок SD с последним статусом "Закрыта":
closedIssuesList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_statuses WHERE status = 'Закрыта' AND is_last = true")
closedIssuesList = Functions.responseToOneLevelArray(closedIssuesList)

# Получение списка заявок SD с последней активностью "Closed in SD":
alreadyClosedIssuesList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_issues WHERE last_action = 'Closed in SD' OR last_action = 'Closed in azure'")
alreadyClosedIssuesList = Functions.responseToOneLevelArray(alreadyClosedIssuesList)

# Для каждой закрытой заявки в SD:
for issueId in closedIssuesList:
    # Получение work item id для каждой заявки SD из списка:
    matchedWorkItems = Functions.dbQuerySender(dbCreds, "SELECT", ("SELECT azure_work_item_id FROM azure_sd_match WHERE sd_issue_id = " + str(issueId)))
    matchedWorkItems = Functions.responseToOneLevelArray(matchedWorkItems)

    # Проверка на последнюю активность и соответствие каким-либо work items в азуре:
    if issueId not in alreadyClosedIssuesList and matchedWorkItems !=[]:
        print(issueId)

        for workItemId in matchedWorkItems:
            # Запрос в API azure (получение проекта и статуса work item) СТАРЫЙ:
            # responseWorkItem = requests.request("GET", (getWorkItemUrl + str(workItemId)), headers=getWorkItemHeaders, verify=False)
            # responseWorkItem = json.loads(responseWorkItem.text)
            # responseWorkItem = responseWorkItem["value"]
            # responseWorkItem = responseWorkItem[0]
            # responseWorkItemStatus = responseWorkItem["fields"]
            # responseWorkItemStatus = responseWorkItemStatus["System.State"]
            # responseWorkItemProject = responseWorkItem["fields"]
            # responseWorkItemProject = responseWorkItemProject["System.TeamProject"]

            # Запрос в БД (получение проекта и статуса work item):
            workItemStatus = Functions.dbQuerySender(dbCreds, "SELECT",
                                                             "SELECT status FROM azure_statuses WHERE is_last = true AND id = " + str(workItemId))
            workItemStatus = workItemStatus[0][0]
            workItemProject = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT project FROM azure_work_items WHERE id = " + str(workItemId))
            workItemProject = workItemProject[0][0]

            # Проверка статуса work item в азуре:
            if workItemStatus == "Closed":
                # Запись о последнем действии:
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in SD' WHERE id = " + str(workItemId)))
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in SD' WHERE id = " + str(issueId)))

            # Если статус в azure "Design" или "Backlog":
            elif workItemStatus == "Design" or workItemStatus == "Backlog":
                # Закрытие wi:
                responseChangeStatus = requests.request("PATCH", ("https://10.0.2.14/PrimoCollection/" + workItemProject + "/_apis/wit/workItems/" + str(workItemId) + "?api-version=7.0-preview.3"), headers=changeStatusHeaders, data=payloadToClose, verify=False)
                # Комментарий wi:
                payloadComment = json.dumps({"text": ("Заявка в SD # " + str(issueId) + ", привязанная к этой задаче, была закрыта.")})
                responseAddComment = requests.request("POST", ("https://10.0.2.14/PrimoCollection/" + workItemProject + "/_apis/wit/workItems/" + str(workItemId) + "/comments?api-version=7.0-preview.3"), headers=postCommentHeaders, data=payloadComment, verify=False)
                # Запись о последнем действии:
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in SD' WHERE id = " + str(workItemId)))
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in SD' WHERE id = " + str(issueId)))

                toCloseWorkItemsList.append(workItemId)

            # Если статус в azure "Test", "Review", "Ready":
            elif workItemStatus == "Test" or workItemStatus == "Review" or workItemStatus == "Ready":
                # Оставляем комментарий о закрытии заявки в SD:
                payloadComment = json.dumps({"text": "Заявка в SD #" + str(issueId) + ", привязанная к этой задаче, была закрыта."})
                responseAddComment = requests.request("POST", "https://10.0.2.14/PrimoCollection/" + workItemProject + "/_apis/wit/workItems/" + str(
                workItemId) + "/comments?api-version=7.0-preview.3", headers=postCommentHeaders, data=payloadComment, verify=False)
                # Запись о последнем действии:
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in SD' WHERE id = " + str(workItemId)))
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in SD' WHERE id = " + str(issueId)))

                onlyCommentClosedWorkItemsList.append(workItemId)
                print("Test / Review / Ready", "Azure:", workItemId, "SD:", issueId)
                print("Response comment", responseAddComment.text)

print("Now closed in azure:", toCloseWorkItemsList)
print("Comment only:", onlyCommentClosedWorkItemsList)
