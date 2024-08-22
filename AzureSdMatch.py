import requests
import json
import psycopg2
import Vars
import Functions
import Debug

dbCreds = Vars.dbCreds
service = "azure"

# Debug
newMatches = []

# Удаление из БД связей по несуществующим work_item_id:
Functions.dbQuerySender(dbCreds, "DELETE", "DELETE FROM azure_sd_match WHERE azure_work_item_id NOT IN (SELECT id FROM azure_work_items WHERE is_deleted = false)")
# Получение из БД списка неудаленный work items:
azureWorkItemsList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id, sd_issue FROM azure_work_items WHERE is_deleted = false AND sd_issue IS NOT NULL")

# Для каждой заявки в SD в списке work items. Преобразование в номер:
for issuesByWorkItem in azureWorkItemsList:
    workItemId = issuesByWorkItem[0]
    issuesByWorkItemPrepared = issuesByWorkItem[1].strip()
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace(", ", "---")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("https://sd.primo-rpa.ru/issues/", "")
    # issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("ГазпромИнформ", "")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("#!", "")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("/", "")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace(" ", "---")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace(",", "---")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.split("---")

    # Проверка на наличие заявки SD в таблице соответствия:
    for issueByWorkItem in issuesByWorkItemPrepared:
        if not str(issueByWorkItem).isdigit():
            if str(issueByWorkItem) == "None":
                continue
            else:
                print("Incorrect value!")
                print("Azure work item:", workItemId)
                print("Value:", issueByWorkItem)
                continue
        issuesByWorkItemFromTable = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id =" + str(workItemId))
        issuesByWorkItemFromTable = Functions.responseToOneLevelArray(issuesByWorkItemFromTable)
        if int(issueByWorkItem) in issuesByWorkItemFromTable:
            # ToDo добавить актуализацию ссылки на azure:
            # Todo Если заявка уже в списке, проверка на актуальность ссылки на azure work item:
            pass
        else:
            Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_sd_match (azure_work_item_id, sd_issue_id) VALUES(" + str(workItemId) + ", " + str(issueByWorkItem) + ")")
            # pass
            # Debug:
            newMatches.append("Azure: " + str(workItemId) + "; SD: " + str(issueByWorkItem))

# Debug:
print("New matches:", newMatches)