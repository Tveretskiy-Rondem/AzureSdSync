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

# Получение и преобразование в одномерный массив незаполненных строк в таблице azure_work_items:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items")
idsList = Functions.responseToOneLevelArray(idsListRaw)

for id in idsList:
    Debug.message(currentFileName, "10", str(id))
    workItemDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT " + checkUpdateFieldsStr + " FROM azure_work_items WHERE id = " + str(id))
    workItemDbPrepared = workItemDb[0]
    workItemApi = Functions.requestSender(service, "getItem", id)
    workItemApi = workItemApi["value"]
    workItemApi = workItemApi[0]
    workItemApiPrepared = Functions.jsonValuesToList(checkUpdateJsonKeys, workItemApi, 0)
    print(workItemDbPrepared)
    print(workItemApiPrepared)
    for i in range(len(workItemApiPrepared)):
        if workItemDbPrepared[i] == workItemDbPrepared[i]:
            print(workItemApiPrepared[i], "=", workItemDbPrepared[i])
        else:
            Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "azure_work_items", id, workItemApiPrepared, checkUpdateFields))