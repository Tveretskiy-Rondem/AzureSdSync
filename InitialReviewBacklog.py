import requests
import json
import re
import Functions
import Vars

# Todo выборки списками - словари?

dbCreds = Vars.dbCreds
sdToken = Vars.sdToken
headersComment = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='
}

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
        # Была реализована проверка на отсутствие статуса бэклог в заявке SD, изменено на проверку статуса на рассмотрение.
        # isLinkedIssueBacklog = Functions.dbQuerySender(dbCreds, "EXISTS", "SELECT EXISTS (SELECT * FROM sd_statuses WHERE id = " + str(linkedIssueId) + " AND status != 'Бэклог' AND is_last = true)")
        isLinkedIssueBacklog = Functions.dbQuerySender(dbCreds, "EXISTS",
                                                       "SELECT EXISTS (SELECT * FROM sd_statuses WHERE id = " + str(
                                                           linkedIssueId) + " AND status = 'На рассмотрении' AND is_last = true)")
        if isLinkedIssueBacklog:
            sdIssues.append(linkedIssueId)

print(sdIssues)

# Todo убрать после проверки:
# TEST:
for issueId in sdIssues:
    lastAction = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT last_action FROM sd_issues WHERE id = " + str(issueId))
    status = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT status FROM sd_statuses WHERE is_last = true AND id = " + str(issueId))
    status = status[0][0]
    print(issueId, status, lastAction)

for issueId in sdIssues:
    # Получение статуса заявки в SD:
    status = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT status FROM sd_statuses WHERE is_last = true AND id = " + str(issueId))
    status = status[0][0]
    # Получение id azure work item для каждой заявки SD:
    azureWorkItemId = Functions.dbQuerySender(dbCreds, "SELECT",
                                              "SELECT azure_work_item_id FROM azure_sd_match WHERE sd_issue_id = " + str(issueId))
    azureWorkItemId = azureWorkItemId[0][0]
    if status == "Закрыта":
        # Комментарий в azure:
        payload = json.dumps({"text": "Связанная задача в SD " + str(issueId) + " находится в статусе 'Закрыта'"})
        respComment = requests.request("POST", "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workItems/" + str(
            azureWorkItemId) + "/comments?api-version=7.0-preview.3", headers=headersComment, data=payload, verify=False)
    else:
        # Изменение статуса в SD:
        urlChangeSdStatus = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/statuses?api_token=" + sdToken
        payloadChangeSdStatus = json.dumps({
            "code": "primo_rpa_backlog",
            "name": "Бэклог",
            "comment": "Соответствующая задача в azure была переведена в бэклог.",
            "custom_parameters": {
                "planned_release": "Номер релиза будет определен позже"
            },
            "skip_options": [
                "skip_triggers",
                "skip_notifications",
                "skip_webhooks"
            ]
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", urlChangeSdStatus, headers=headers, data=payloadChangeSdStatus)

    # Изменение last_action в azure_work_items и в sd_issues на Initial review backlog:
    Functions.dbQuerySender(dbCreds, "UPDATE",
                            ("UPDATE sd_issues SET last_action = 'Initial review backlog' WHERE id = " + str(issueId)))
    Functions.dbQuerySender(dbCreds, "UPDATE",
                            ("UPDATE azure_work_items SET last_action = 'Initial review backlog' WHERE id = " + str(azureWorkItemId)))

# Debug:
print("SD issues transferred to backlog: ", sdIssues)