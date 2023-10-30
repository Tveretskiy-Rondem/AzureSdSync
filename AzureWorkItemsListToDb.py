import Functions
import Vars

service = Vars.azureService
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
workItemsRange = Vars.azureWorkItemsRange
workItemsRangeShort = []

# Todo: Вместо жестких рамок добавить остановку по достижении критического количества отсутствующих подряд work items.

# Получение последнего id в БД и изменение списка из sd (удаляются все номера до последнего id в БД). Для полного перебора закомментировать, workItemsRangeShort заменить на workItemsRange:
lastIdInDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items WHERE url IS NOT NULL ORDER BY id DESC LIMIT 1")
if lastIdInDb != []:
    workItemsRangeShort.append(lastIdInDb[0][0])
    workItemsRangeShort.append(workItemsRange[1])
else:
    workItemsRangeShort.append(1)
    workItemsRangeShort.append(15000)

for id in range(workItemsRangeShort[0], workItemsRangeShort[1]):
    response = Functions.requestSender(service, "exists", id)
    print("Processing work item #", id)
    if "value" in response:
        if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "azure_work_items", id, "", "")):
            print("Already in DB")
        else:
            print("Adding work item to DB")
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_work_items", id, [id], ["id"]))
    elif "errorCode" in response:
        print("Not exists in azure")