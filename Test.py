import requests
import json
import Vars
import Functions

# Todo: добавить индикацию

dbCreds = Vars.dbCreds
getWorkItemUrl = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids="
getWorkItemHeaders = {'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='}
workItemsList = []
sdToken = Vars.sdToken

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

print("Closed azure: ", closedWorkItemsList)
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
                issuesComment.append(issueId)
            else:
                # Поле релиза заполнено:
                # Комментарий в привязанную заявку SD:
                issuesRelease.append(issueId)

print("Only commented:", issuesComment)
print("Commented with release:", issuesRelease)