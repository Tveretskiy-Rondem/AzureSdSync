import requests
import json
import re
import Functions
import Vars

dbCreds = Vars.dbCreds

# Todo получение из azure_statuses списка со статусом бэклог, отличным от предыдущего:
workItemsBacklog = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_statuses WHERE status = 'Backlog' AND old_status != '' AND is_last = true")
workItemsBacklog = Functions.responseToOneLevelArray(workItemsBacklog)

# Todo проверка на наличие связанной задачи в SD:
workItemsSdBacklog = []
for workItemId in workItemsBacklog:
    print("For1", workItemId)
    linkedIssueId = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id = " + str(workItemId))
    if linkedIssueId != []:
        workItemsSdBacklog.append(workItemId)

# Todo проверка на запись last_action = InitialReview
workItemsIR = []
for workItemId in workItemsSdBacklog:
    print("For2", workItemId)
    isInitialReview = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT * FROM azure_work_items WHERE id = " + str(workItemId) + " AND last_action = 'Initial review')")
    print("SELECT EXISTS (SELECT * FROM azure_work_items WHERE id = " + str(workItemId) + " AND last_action = 'Initial review')")
    print(workItemId, isInitialReview)
    if isInitialReview:
        workItemsIR.append(workItemId)

# Todo проверка статуса в SD != backlog
# Todo изменение last_action azure_work_items на InitialReviewBacklog
# Todo изменение статуса в SD
# Todo комментарий в SD