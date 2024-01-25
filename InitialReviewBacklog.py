import requests
import json
import re
import Functions
import Vars

dbCreds = Vars.dbCreds

# Todo получение из azure_statuses списка со статусом бэклог, отличным от предыдущего:
workItemsBacklog = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_statuses WHERE status = 'Backlog' AND old_status != '' AND is_last = true")
workItemsBacklog = Functions.responseToOneLevelArray(workItemsBacklog)
print(workItemsBacklog)

# Todo проверка на наличие связанной задачи в SD:
workItemsSdBacklog = []
for workItemId in workItemsBacklog:
    linkedIssueId = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id = " + str(workItemId))
    print(workItemId, linkedIssueId)
    if linkedIssueId != []:
        workItemsSdBacklog.append(workItemId)
print(workItemsSdBacklog)
# Todo проверка на запись last_action = InitialReview

# Todo проверка статуса в SD != backlog
# Todo изменение last_action azure_work_items на InitialReviewBacklog
# Todo изменение статуса в SD
# Todo комментарий в SD