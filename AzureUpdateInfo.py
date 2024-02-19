import requests
import json
import Functions
import Vars

# Todo исключить Archive

service = "azure"
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
checkUpdateFields = Vars.azureCheckUpdateFields
checkUpdateJsonKeys = Vars.azureCheckUpdateJsonKeys
wiGetHeaders = {
  'Content-Type': 'application/json-patch+json',
  'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='
}


# Debug:
deleted = []
undeleted = []
diffs = []
currentFileName = "AzureUpdateInfo"
checkUpdateFieldsStr = ""

# Сборка строки с перечислением полей таблицы для запроса в БД:
for i in range(len(checkUpdateFields)):
    checkUpdateFieldsStr = checkUpdateFieldsStr + checkUpdateFields[i]
    if (i + 1) < len(checkUpdateFields):
        checkUpdateFieldsStr = checkUpdateFieldsStr + ", "

# Получение и преобразование в одномерный массив id из таблицы azure_work_items:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items ORDER BY id DESC")
idsList = Functions.responseToOneLevelArray(idsListRaw)
# idsList = [8605]

for workItemId in idsList:
    workItemDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT " + checkUpdateFieldsStr + " FROM azure_work_items WHERE id = " + str(workItemId))
    try:
        workItemDbPrepared = workItemDb[0]
        # workItemApi = Functions.requestSender(service, "getItem", workItemId)
        workItemApi = requests.request("GET", ("https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids=" + str(workItemId)), headers=wiGetHeaders, verify=False)
        workItemApi = json.loads(workItemApi.text)
        # print(workItemApi)
    except IndexError:
        pass
    # Перехват исключения на несуществующий таск:
    try:
        workItemApi = workItemApi["value"]
    except:
        # except KeyError:
        # Удаление соответствия заявке SD, добавление пометки об удалении в таблицы azure_work_items, azure_statuses:
        Functions.dbQuerySender(dbCreds, "DELETE", "DELETE FROM azure_sd_match WHERE azure_work_item_id = " + str(workItemId))
        # Functions.dbQuerySender(dbCreds, "DELETE", "DELETE FROM azure_work_items WHERE id = " + str(id))
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_work_items SET is_deleted = true WHERE id = " + str(workItemId))
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_statuses SET is_last = false WHERE id = " + str(workItemId))
        Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_statuses (status, id) VALUES('DELETED', " + str(workItemId) + ")")

        # Debug:
        deleted.append(workItemId)
        # print("Deleted!", workItemId)

        continue

    # Проверка на пометку об удалении. В случае наличия - снятие пометки, добавление записи об изменении статуса:
    if Functions.dbQuerySender(dbCreds, "SELECT", "SELECT is_deleted FROM azure_work_items WHERE id = " + str(workItemId)) == "true":
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_work_items SET is_deleted = false WHERE id = " + str(workItemId))
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_statuses SET is_last = false WHERE id = " + str(workItemId))
        Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_statuses (status, id) VALUES('UNDELETED', " + str(workItemId) + ")")

        # Debug:
        undeleted.append(workItemId)

    workItemApi = workItemApi[0]
    workItemApiPrepared = Functions.jsonValuesToList(checkUpdateJsonKeys, workItemApi, 0)
    # print(workItemDbPrepared)
    # print(workItemApiPrepared)
    for i in range(len(workItemApiPrepared)):
        if workItemDbPrepared[i] == workItemDbPrepared[i]:
            pass
            # print(workItemApiPrepared[i], "=", workItemDbPrepared[i])
        else:
            Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "azure_work_items", workItemId, workItemApiPrepared, checkUpdateFields))

            # Debug:
            if workItemId not in diffs:
                diffs.append(workItemId)

    # Заполнение поля "запланировано на релиз"
    workItemReleaseDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT planned_release FROM azure_work_items WHERE id = " + str(workItemId))
    plannedReleaseApi = workItemApi["fields"]["System.IterationPath"]
    substringsToDelete = ["Studio", "Orchestrator", "Discovery", "Linux", "Studio Linux", "\\"]
    for substring in substringsToDelete:
        plannedReleaseApi = plannedReleaseApi.replace(substring, "")
    if plannedReleaseApi != workItemReleaseDb:
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_work_items SET planned_release = '" + plannedReleaseApi + "' WHERE id = " + str(workItemId))

# Debug:
print("Work items deleted:", deleted)
print("Work items UNDELETED:", undeleted)
print("Work items updated:", diffs)