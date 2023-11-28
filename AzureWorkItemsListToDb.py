import Functions
import Vars

service = "azure"
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
workItemsRange = Vars.azureWorkItemsRange
workItemsRangeShort = []
fullRange = False

# Debug:
notInDb = []

# Todo: Вместо жестких рамок добавить остановку по достижении критического количества отсутствующих подряд work items.

# Получение последнего id в БД и изменение списка из sd или получение стартового значения :
if fullRange:
    lastIdInDb = [[8500]]
else:
    lastIdInDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items WHERE url IS NOT NULL ORDER BY id DESC LIMIT 1")

if lastIdInDb != []:
    workItemsRangeShort.append(lastIdInDb[0][0])
    workItemsRangeShort.append(workItemsRange[1])
else:
    workItemsRangeShort.append(1)
    workItemsRangeShort.append(10000)

for workItemId in range(workItemsRangeShort[0], workItemsRangeShort[1]):
    response = Functions.requestSender(service, "exists", workItemId)
    # print("Processing work item #", id)
    if "value" in response:
        if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "azure_work_items", workItemId, "", "")):
            # print("Already in DB")
            pass
        else:
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_work_items", workItemId, [workItemId], ["id"]))
            # Debug:
            notInDb.append(workItemId)
    elif "errorCode" in response:
        # print("Not exists in azure")
        pass

# Debug:
print("Added to DB:", notInDb)