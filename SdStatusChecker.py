import time
import datetime
import Functions
import Vars

# Функция искусственной задержки запросов в SD:
def queryDelay(lastQueryTime):
    queryDelayMs = 270
    if (datetime.datetime.now() - lastQueryTime).microseconds < queryDelayMs:
        time.sleep((queryDelayMs - (datetime.datetime.now() - lastQueryTime).microseconds) / 1000)

service = "sd"
sdToken = Vars.sdToken
dbCreds = Vars.dbCreds
tableFields = Vars.sdTableFields
statusTableFields = Vars.sdStatusTableFields
jsonKeys = Vars.sdJsonKeys
statusJsonKeys = Vars.sdStatusJsonKeys
lastQueryTime = datetime.datetime.now()

# Debug:
diffsDetected = []
notExistInStatuses = []

# Получение списка ВСЕХ заявок в SD из БД:
idsResponse = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_issues ORDER BY id DESC")
idsList = Functions.responseToOneLevelArray(idsResponse)

for issueId in idsList:
    # print("Processing issue #", id)
    # Получение sd issue запросом, преобразование в json:
    # Todo добавлен try. Проверить!:
    try:
        queryDelay(lastQueryTime)
        responseIssueItem = Functions.requestSender(service, "getItem", issueId)
        lastQueryTime = datetime.datetime.now()
        responseIssueItem = Functions.jsonValuesToList(statusJsonKeys, responseIssueItem, 0)
    except:
        continue
    # Добавление id в ключи и поля:
    responseIssueItemWithId = responseIssueItem.copy()
    statusTableFieldsWithId = statusTableFields.copy()
    responseIssueItemWithId.append(issueId)
    statusTableFieldsWithId.append("id")

    # Проверка на наличие в таблице sd_statuses записи с этим id:
    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "sd_statuses", issueId, "", "")):
        # print("Status of issue already in DB. Compare statuses.")
        statusDbResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECTlaststatus", "sd_statuses", issueId, "", ""))
        if statusDbResponse[0][0] != responseIssueItem[0] or (str(statusDbResponse[0][0]) != "None" and str(responseIssueItem[0]) != "None"):
            # print("Detected difference. Insert new status to DB.")
            Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE sd_statuses SET is_last = false WHERE id = " + str(issueId))
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "sd_statuses", issueId, responseIssueItemWithId, statusTableFieldsWithId))
            # Debug:
            diffsDetected.append(issueId)
        else:
            pass
    else:
        # print("Status with this id not exists in DB. Insert new status to DB.")
        Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "sd_statuses", issueId, responseIssueItemWithId, statusTableFieldsWithId))
        # Debug:
        notExistInStatuses.append(issueId)

# Debug:
print("Not exists in statuses:", notExistInStatuses)
print("Statuses diffs detected:", diffsDetected)