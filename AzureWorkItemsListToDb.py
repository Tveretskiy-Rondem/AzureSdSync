import Functions
import Vars
import random

service = "azure"
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
workItemsRangeShort = []

# fullRange = True
# workItemsRange = Vars.azureWorkItemsRange

# Debug:
notInDb = []

# Выбор между полным неполным сканированием диапазона:
if random.randint(1, 9) == 9:
    lastIdInDb = [[1]]
else:
    # Получение последнего id в БД:
    lastIdInDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items WHERE url IS NOT NULL ORDER BY id DESC LIMIT 1")
    # Начальное значение = 1, если получен пустой ответ:
    if lastIdInDb == []:
        lastIdInDb = [[15000]]

lastIdInDb = lastIdInDb[0][0]

# Создание диапазона azure work items id для обработки:
if lastIdInDb > 15000:
    workItemsRangeShort.append(lastIdInDb - 300)
    workItemsRangeShort.append(lastIdInDb + 300)
else:
    workItemsRangeShort.append(0)
    workItemsRangeShort.append(lastIdInDb + 20000)

print("Azure ids to DB range:", workItemsRangeShort)

# Создание диапазона azure work items id для обработки (старая версия):
# if lastIdInDb != []:
#     workItemsRangeShort.append(lastIdInDb)
#     workItemsRangeShort.append(workItemsRange[1])
# else:
#     workItemsRangeShort.append(1)
#     workItemsRangeShort.append(25000)

for workItemId in range(workItemsRangeShort[0], workItemsRangeShort[1]):
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