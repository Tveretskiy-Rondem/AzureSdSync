import Functions
import Vars
import Debug

service = Vars.azureService
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
statusTableFields = Vars.azureStatusTableFields
jsonKeys = Vars.azureJsonKeys
statusJsonKeys = Vars.azureStatusJsonKeys

Debug.message("AzureDiffChecker", "start", "")

idsResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "azure_work_items", "", "", ""))
idsList = Functions.responseToOneLevelArray(idsResponse)

for id in idsList:
    print("Processing work item #", id)
    # Получение json work item:
    workItem = Functions.requestSender(service, "getItem", id)
    # Переход на нужный уровень вложенности с проверкой на удаленный (?) work item:
    try:
        workItem = workItem["value"]
    except KeyError:
        print("Item with id", id, "no more exists!")
        continue
        # ToDo: добавить поле в таблице об удалении ранее существовавшей записи (если такие будут встречаться)
    workItem = workItem[0]
    # Извлечение статуса:
    workItemStatus = Functions.jsonValuesToList(statusJsonKeys, workItem, 0)
    workItemStatusWithId = workItemStatus.copy()
    statusTableFieldsWithId = statusTableFields.copy()
    workItemStatusWithId.append(id)
    statusTableFieldsWithId.append("id")

    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "azure_statuses", id, "", "")):
        print("Status of work item already in DB. Compare statuses.")
        dbStatus = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECTlaststatus", "azure_statuses", id, "",""))
        if dbStatus[0][0] != workItemStatus[0]:
            print("Detected difference. Insert new status to DB.")
            workItemStatusWithIdOld = workItemStatusWithId.copy()
            statusTableFieldsWithIdOld = statusTableFieldsWithId.copy()
            workItemStatusWithIdOld.append(dbStatus[0][0])
            statusTableFieldsWithIdOld.append("old_status")
            print(workItemStatusWithIdOld)
            print(statusTableFieldsWithIdOld)
            print(Functions.dbQueryGenerator("INSERT", "azure_statuses", id, workItemStatusWithId, statusTableFieldsWithId))
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_statuses", id, workItemStatusWithIdOld, statusTableFieldsWithIdOld))
        else:
            print("Diffs NOT detected.")
    else:
        print("Status with this id not exists in DB. Insert new status to DB.")
        Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_statuses", id, workItemStatusWithId, statusTableFieldsWithId))