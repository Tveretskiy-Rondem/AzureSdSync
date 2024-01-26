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

# Проверка на наличие связанной задачи в SD, проверка на статус в sd:
workItemsBySd = []
for workItemId in workItemsBacklog:
    print("For1", workItemId)
    linkedIssueId = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id = " + str(workItemId))
    if linkedIssueId != []:
        linkedIssueId = linkedIssueId[0][0]
        print("Linked issue id flat:", linkedIssueId)
        isLinkedIssueBacklog = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT * FROM sd_statuses WHERE id = " + str(linkedIssueId) + " AND status = 'Бэклог' AND is_last = true)")
        if isLinkedIssueBacklog:
            workItemsBySd.append(workItemId)

# Проверка на запись last_action = InitialReview
workItemsIR = []
for workItemId in workItemsBySd:
    print("For2", workItemId)
    isInitialReview = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT * FROM azure_work_items WHERE id = " + str(workItemId) + " AND last_action = 'Initial review')")
    print("SELECT EXISTS (SELECT * FROM azure_work_items WHERE id = " + str(workItemId) + " AND last_action = 'Initial review')")
    print(workItemId, isInitialReview)
    if isInitialReview:
        workItemsIR.append(workItemId)
print(workItemsIR)

# # Todo проверка статуса в SD != backlog (вынесено в первый блок проверки)
# workItemsBySdBacklog = []
# for workItem in workItemsIR:

# Todo изменение статуса в SD:


# Todo изменение last_action azure_work_items на InitialReviewBacklog

# Todo комментарий в SD