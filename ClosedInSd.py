import requests
import json
import Vars
import Functions

toCloseWorkItemsList = []
onlyCommentClosedWorkItemsList = []
dbCreds = Vars.dbCreds
getWorkItemUrl = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids="
getWorkItemHeaders = {'Authorization': 'Basic czFcYXR2ZXJldHNraXk6eGRudGw2M3lkYWE1YnYzenRlNGY0cnBicmE1ZnUydTJoeHptZXJiaXUzcHFxd2VvamdicQ=='}
changeStatusHeaders = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}
postCommentHeaders = {'Content-Type': 'application/json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}
payloadToClose = json.dumps([{"op": "add", "path": "/fields/System.State", "value": "Closed"}])

# Получение списка заявок SD с последним статусом "Закрыта":
closedIssuesList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_statuses WHERE status = 'Закрыта' AND is_last = true")
closedIssuesList = Functions.responseToOneLevelArray(closedIssuesList)

# Получение списка заявок SD с последней активностью "Closed in SD":
alreadyClosedIssuesList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_issues WHERE last_action = 'Closed in SD'")
alreadyClosedIssuesList = Functions.responseToOneLevelArray(alreadyClosedIssuesList)

for issueId in closedIssuesList:
    # Получение work item id для каждой заявки SD из списка:
    matchedWorkItems = Functions.dbQuerySender(dbCreds, "SELECT", ("SELECT azure_work_item_id FROM azure_sd_match WHERE sd_issue_id = " + str(issueId)))
    matchedWorkItems = Functions.responseToOneLevelArray(matchedWorkItems)

    # Проверка на последнюю активность и соответствие каким-либо work items в азуре:
    if issueId not in alreadyClosedIssuesList and matchedWorkItems !=[]:
        print(issueId)

        for workItemId in matchedWorkItems:
            responseWorkItem = requests.request("GET", (getWorkItemUrl + str(workItemId)), headers=getWorkItemHeaders, verify=False)
            responseWorkItem = json.loads(responseWorkItem.text)
            responseWorkItem = responseWorkItem["value"]
            responseWorkItem = responseWorkItem[0]
            responseWorkItemStatus = responseWorkItem["fields"]
            responseWorkItemStatus = responseWorkItemStatus["System.State"]
            responseWorkItemProject = responseWorkItem["fields"]
            responseWorkItemProject = responseWorkItemProject["System.TeamProject"]

            # Проверка статуса work item в азуре:
            if responseWorkItemStatus == "Closed":
                # Запись о последнем действии:
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in SD' WHERE id = " + str(workItemId)))
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in SD' WHERE id = " + str(issueId)))

            elif responseWorkItemStatus == "Design" or responseWorkItemStatus == "Backlog":
                # Если статус в azure "Design" или "Backlog"
                # Закрытие wi с комментарием:
                # Закрытие:

                responseChangeStatus = requests.request("PATCH", ("https://10.0.2.14/PrimoCollection/" + responseWorkItemProject + "/_apis/wit/workItems/" + str(workItemId) + "?api-version=7.0-preview.3"), headers=changeStatusHeaders, data=payloadToClose, verify=False)
                # Комментарий:
                payloadComment = json.dumps({"text": ("Заявка в SD #" + str(issueId) + ", сопоставленная с данной таской, была закрыта.")})
                responseAddComment = requests.request("POST", ("https://10.0.2.14/PrimoCollection/" + responseWorkItemProject + "/_apis/wit/workItems/" + str(workItemId) + "/comments?api-version=7.0-preview.3"), headers=postCommentHeaders, data=payloadComment, verify=False)
                # Запись о последнем действии:
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in SD' WHERE id = " + str(workItemId)))
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in SD' WHERE id = " + str(issueId)))

                toCloseWorkItemsList.append(workItemId)
                print("Design / Backlog", "Azure:", workItemId, "SD:", issueId)
                print("Response status:", responseChangeStatus)
                print("Response comment", responseAddComment.text)

            elif responseWorkItemStatus == "Test" or responseWorkItemStatus == "Review" or responseWorkItemStatus == "Ready":
                # Оставляем комментарий о закрытии заявки в SD:
                payloadComment = json.dumps({"text": "Заявка в SD #" + str(issueId) + ", сопоставленная с данной таской, была закрыта. Вот."})
                responseAddComment = requests.request("POST", "https://10.0.2.14/PrimoCollection/" + responseWorkItemProject + "/_apis/wit/workItems/" + str(
                workItemId) + "/comments?api-version=7.0-preview.3", headers=postCommentHeaders, data=payloadComment, verify=False)
                # Запись о последнем действии:
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in SD' WHERE id = " + str(workItemId)))
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in SD' WHERE id = " + str(issueId)))

                onlyCommentClosedWorkItemsList.append(workItemId)
                print("Test / Review / Ready", "Azure:", workItemId, "SD:", issueId)
                print("Response comment", responseAddComment.text)

print("Были бы закрыты:", toCloseWorkItemsList)
print("Только комментарий:", onlyCommentClosedWorkItemsList)
