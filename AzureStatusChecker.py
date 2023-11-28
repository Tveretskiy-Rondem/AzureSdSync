import Functions
import Vars
import Debug

service = "azure"
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
statusTableFields = Vars.azureStatusTableFields
jsonKeys = Vars.azureJsonKeys
statusJsonKeys = Vars.azureStatusJsonKeys

# Debug:
statusUpdated = []
statusNotExists = []

# Получение списка id work items из БД:
idsResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "azure_work_items", "", "", ""))
idsList = Functions.responseToOneLevelArray(idsResponse)

for workItemId in idsList:
    # print("Processing work item #", id)
    # Получение json work item:
    workItem = Functions.requestSender(service, "getItem", workItemId)
    # Переход на нужный уровень вложенности с проверкой на удаленный (?) work item:
    try:
        workItem = workItem["value"]
    except KeyError:
        # print("Item with id", id, "no more exists!")
        continue
    workItem = workItem[0]
    # Извлечение статуса:
    workItemStatus = Functions.jsonValuesToList(statusJsonKeys, workItem, 0)
    workItemStatusWithId = workItemStatus.copy()
    statusTableFieldsWithId = statusTableFields.copy()
    workItemStatusWithId.append(workItemId)
    statusTableFieldsWithId.append("id")

    # Проверка существования в таблице статусов записи с данным id:
    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "azure_statuses", workItemId, "", "")):
        # print("Status of work item already in DB. Compare statuses.")
        dbStatus = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECTlaststatus", "azure_statuses", workItemId, "", ""))
        if dbStatus[0][0] != workItemStatus[0]:
            workItemStatusWithIdOld = workItemStatusWithId.copy()
            statusTableFieldsWithIdOld = statusTableFieldsWithId.copy()
            workItemStatusWithIdOld.append(dbStatus[0][0])
            statusTableFieldsWithIdOld.append("old_status")
            Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_statuses SET is_last = false WHERE id = " + str(workItemId))
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_statuses", workItemId, workItemStatusWithIdOld, statusTableFieldsWithIdOld))

            # Debug:
            statusUpdated.append(workItemId)

        else:
            pass
            # print("Diffs NOT detected.")
    else:
        # print("Status with this id not exists in DB. Insert new status to DB.")
        Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_statuses", workItemId, workItemStatusWithId, statusTableFieldsWithId))

        # Debug:
        statusNotExists.append(workItemId)

# Debug:
print("Statuses updated:", statusUpdated)
print("New items:", statusNotExists)