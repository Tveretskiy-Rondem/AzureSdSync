import requests
import json
import Vars
import Functions

dbCreds = Vars.dbCreds
getWorkItemUrl = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids="
getWorkItemHeaders = {'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='}
workItemsList = []

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

print("Closed azure: ", closedWorkItemsList)
print("Already closed: ", alreadyClosedWorkItemsList)
print("Final list: ", workItemsList)

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
        # Todo проверка на наличие релиза в wi azure:
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
        requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headersUrlToIssue, data=payloadUrlToIssue, verify=False)
        # Todo Добавление информации о назначении на релиз в заявке SD:

        # Добавление отметки о последней активности:
        Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE azure_work_items SET last_action = 'Closed in azure' WHERE id = " + str(workItemId)))
        Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET last_action = 'Closed in azure' WHERE id = " + str(issueId)))