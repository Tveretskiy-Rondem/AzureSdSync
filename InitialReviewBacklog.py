import requests
import json
import re
import Functions
import Vars

# Todo выборки списками - словари?

dbCreds = Vars.dbCreds

# Получение из azure_statuses списка со статусом бэклог, отличным от предыдущего:
workItemsBacklog = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_statuses WHERE status = 'Backlog' AND old_status != '' AND is_last = true")
workItemsBacklog = Functions.responseToOneLevelArray(workItemsBacklog)

# Проверка на запись last_action = InitialReview
workItemsIR = []
for workItemId in workItemsBacklog:
    isInitialReview = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT * FROM azure_work_items WHERE id = " + str(workItemId) + " AND last_action = 'Initial review')")
    if isInitialReview:
        workItemsIR.append(workItemId)

# Проверка на наличие связанной задачи в SD, получение списка задач в SD, проверка на статус в sd:
sdIssues = []
for workItemId in workItemsIR:
    linkedIssueId = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id = " + str(workItemId))
    if linkedIssueId != []:
        linkedIssueId = linkedIssueId[0][0]
        isLinkedIssueBacklog = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT * FROM sd_statuses WHERE id = " + str(linkedIssueId) + " AND status != 'Бэклог' AND is_last = true)")
        if isLinkedIssueBacklog:
            sdIssues.append(linkedIssueId)

print(sdIssues)

# TEST:
for issueId in sdIssues:
    lastAction = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT last_action FROM sd_issues WHERE id = " + str(issueId))
    status = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT status FROM sd_statuses WHERE is_last = true AND id = " + str(issueId))
    print(issueId, status, lastAction)


# Todo изменение статуса в SD:
# Todo поменять токен на свой
# urlChangeSdStatus = "https://sd.primo-rpa.ru/api/v1/issues/" +  + "/statuses?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e"
#
# payloadChangeSdStatus = json.dumps({
#   "code": "primo_rpa_backlog",
#   "name": "Бэклог",
#   "comment": "Тестовый перевод в бэклог.",
#   "skip_options": [
#     "skip_triggers",
#     "skip_notifications",
#     "skip_webhooks"
#   ]
# })
# headers = {'Content-Type': 'application/json'}
# response = requests.request("POST", urlChangeSdStatus, headers=headers, data=payloadChangeSdStatus)

# Todo изменение last_action azure_work_items на InitialReviewBacklog

# Todo комментарий в SD