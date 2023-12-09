# Процесс для наполнения таблицы sd_issues
import time
import datetime
import Functions
import Vars

# Функция искусственной задержки запросов в SD:
def queryDelay(lastQueryTime):
    queryDelayMs = 270
    if (datetime.datetime.now() - lastQueryTime).microseconds < queryDelayMs:
        time.sleep((queryDelayMs - (datetime.datetime.now() - lastQueryTime).microseconds) / 1000)
#


service = Vars.sdService
sdToken = Vars.sdToken
dbCreds = Vars.dbCreds
tableFields = Vars.sdTableFields
jsonKeys = Vars.sdJsonKeys
lastQueryTime = datetime.datetime.now()

# Debug:
notInDb = []

# Получение списка ids из sd:
issuesList = []
while issuesList == []:
    queryDelay(lastQueryTime)
    issuesList = Functions.requestSender(service, "getList", "")
    lastQueryTime = datetime.datetime.now()

# Получение последнего id в БД и изменение списка из sd (удаляются все номера до последнего id в БД):
lastIdInDb = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "sd_issues", "last", "", ""))
if lastIdInDb != []:
    lastIdInDb = lastIdInDb[0][0]
    for id in issuesList.copy():
        if id < lastIdInDb + 1:
            issuesList.remove(id)

# Для каждого элемента списка проверяется условие существования в БД (для варианта без проверки последнего id),
# в случае отсутствия, веб-запросом получается json sd issue и помещается в БД:
for issueId in issuesList:
    # print("Processing issue #", issueNumber)
    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "sd_issues", issueId, "", "")):
        # print("Issue #", issueNumber, "exists in DB")
        pass
    else:
        # print("Issue #", issueNumber, "not exists in DB and will be added")
        queryDelay(lastQueryTime)
        responseIssue = Functions.requestSender(service, "getItem", issueId)
        responseIssue = Functions.jsonValuesToList(jsonKeys, responseIssue, 0)
        lastQueryTime = datetime.datetime.now()
        query = Functions.dbQueryGenerator("INSERT", "sd_issues" , responseIssue[0], responseIssue, tableFields)
        Functions.dbQuerySender(dbCreds, "INSERT", query)
        # Debug:
        notInDb.append(issueId)

print("Added to db:", notInDb)