import Functions
import Vars
import Debug

service = Vars.azureService
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
checkUpdateFields = Vars.azureCheckUpdateFields
checkUpdateJsonKeys = Vars.azureCheckUpdateJsonKeys
currentFileName = "AzureUpdateInfo"
checkUpdateFieldsStr = ""

# Сборка строки с перечислением полей таблицы для запроса в БД:
for i in range(len(checkUpdateFields)):
    checkUpdateFieldsStr = checkUpdateFieldsStr + checkUpdateFields[i]
    if (i + 1) < len(checkUpdateFields):
        checkUpdateFieldsStr = checkUpdateFieldsStr + ", "

# Получение и преобразование в одномерный массив id в таблице azure_work_items:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items ORDER BY id DESC")
idsList = Functions.responseToOneLevelArray(idsListRaw)
# idsList = [8605]

for id in idsList:
    workItemDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT " + checkUpdateFieldsStr + " FROM azure_work_items WHERE id = " + str(id))
    try:
        workItemDbPrepared = workItemDb[0]
        workItemApi = Functions.requestSender(service, "getItem", id)
    except IndexError:
        pass
    # Перехват исключения на несуществующий таск:
    try:
        workItemApi = workItemApi["value"]
    except:
    # except KeyError:
        # Удаление соответствия заявке SD, добавление пометки об удалении в таблицы azure_work_items, azure_statuses:
        Functions.dbQuerySender(dbCreds, "DELETE", "DELETE FROM azure_sd_match WHERE azure_work_item_id = " + str(id))
        # Functions.dbQuerySender(dbCreds, "DELETE", "DELETE FROM azure_work_items WHERE id = " + str(id))
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_work_items SET is_deleted = true WHERE id = " + str(id))
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_statuses SET is_last = false WHERE id = " + str(id))
        Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_statuses (status, id) VALUES('DELETED', " + str(id) + ")")
        print("Work item no more available! Status marked as DELETED")
        continue
    # Проверка на пометку об удалении. В случае наличия - снятие пометки, добавление записи об изменении статуса:
    if Functions.dbQuerySender(dbCreds, "SELECT", "SELECT is_deleted FROM azure_work_items WHERE id = " + str(id)) == "true":
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_work_items SET is_deleted = false WHERE id = " + str(id))
        Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_statuses SET is_last = false WHERE id = " + str(id))
        Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_statuses (status, id) VALUES('UNDELETED', " + str(id) + ")")
    workItemApi = workItemApi[0]
    workItemApiPrepared = Functions.jsonValuesToList(checkUpdateJsonKeys, workItemApi, 0)
    # print(workItemDbPrepared)
    # print(workItemApiPrepared)
    for i in range(len(workItemApiPrepared)):
        if workItemDbPrepared[i] == workItemDbPrepared[i]:
            pass
            # print(workItemApiPrepared[i], "=", workItemDbPrepared[i])
        else:
            Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "azure_work_items", id, workItemApiPrepared, checkUpdateFields))