import Functions
import Vars
import random

service = "azure"
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
workItemsRange = []
lastIdInDb = []

# fullRange = True
# workItemsRange = Vars.azureWorkItemsRange

# Debug:
notInDb = []

while lastIdInDb == []:
    # Получение последнего id в БД:
    lastIdInDb = Functions.dbQuerySender(dbCreds, "SELECT",
                                         "SELECT id FROM azure_work_items WHERE url IS NOT NULL ORDER BY id DESC LIMIT 1")

lastIdInDb = lastIdInDb[0][0]

# Выбор между обычным и расширенным сканированием диапазона:
if random.randint(1, 26) == 9:
    # Расширенный диапазон:
    workItemsRange.append(lastIdInDb - 10000)
    workItemsRange.append(lastIdInDb + 300)
else:
    # Обычный диапазон:
    workItemsRange.append(lastIdInDb - 300)
    workItemsRange.append(lastIdInDb + 300)

print("Azure ids to DB range:", workItemsRange)

# Создание диапазона azure work items id для обработки (старая версия):
# if lastIdInDb != []:
#     workItemsRangeShort.append(lastIdInDb)
#     workItemsRangeShort.append(workItemsRange[1])
# else:
#     workItemsRangeShort.append(1)
#     workItemsRangeShort.append(25000)

for workItemId in range(workItemsRange[0], workItemsRange[1]):
    response = Functions.requestSender(service, "exists", workItemId)
    if "value" in response:
        if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "azure_work_items", workItemId, "", "")):
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