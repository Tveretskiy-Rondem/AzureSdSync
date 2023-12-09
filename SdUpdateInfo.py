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
dbCreds = Vars.dbCreds
tableFields = Vars.sdTableFields
jsonKeys = Vars.sdJsonKeys
checkUpdateFields = Vars.sdCheckUpdateFields
checkUpdateJsonKeys = Vars.sdCheckUpdateJsonKeys
lastQueryTime = datetime.datetime.now()

# Debug:
updated = []
currentFileName = "SdUpdateInfo"
checkUpdateFieldsStr = ""

# Сборка строки с перечислением полей таблицы для запроса в БД:
for i in range(len(checkUpdateFields)):
    checkUpdateFieldsStr = checkUpdateFieldsStr + checkUpdateFields[i]
    if (i + 1) < len(checkUpdateFields):
        checkUpdateFieldsStr = checkUpdateFieldsStr + ", "

# Получение и преобразование в одномерный массив незаполненных строк в таблице sd_issues:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_issues ORDER BY id DESC")
idsList = Functions.responseToOneLevelArray(idsListRaw)

for issueId in idsList:
    issueDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT " + checkUpdateFieldsStr + " FROM sd_issues WHERE id = " + str(issueId))
    issueDbPrepared = issueDb[0]
    queryDelay(lastQueryTime)
    issueApi = Functions.requestSender(service, "getItem", issueId)
    lastQueryTime = datetime.datetime.now()
    issueApiPrepared = Functions.jsonValuesToList(checkUpdateJsonKeys, issueApi, 0)
    for i in range(len(issueApiPrepared)):
        if issueDbPrepared[i] == issueDbPrepared[i]:
            pass
        else:
            Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "sd_issues", issueId, issueApiPrepared, checkUpdateFields))

            # Debug:
            # print("Information updated:", issueApiPrepared[i], "=", issueDbPrepared[i])
            if issueId not in updated:
                updated.append(issueId)

print("Updated issues:", updated)