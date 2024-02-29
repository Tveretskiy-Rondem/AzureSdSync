# Процесс для наполнения таблицы sd_issues
import time
import datetime
import Functions
import Vars
import requests
import json

# Функция искусственной задержки запросов в SD:
def queryDelay(lastQueryTime):
    queryDelayMs = 270
    if (datetime.datetime.now() - lastQueryTime).microseconds < queryDelayMs:
        time.sleep((queryDelayMs - (datetime.datetime.now() - lastQueryTime).microseconds) / 1000)

# Todo не работает!
def getIssuesByPage(page, sdToken):
    url = "https://sd.primo-rpa.ru/api/v1/issues/list?api_token=" + sdToken + "&page[size]=50&page[number]=" + str(page)
    payload = {}
    headers = {}
    issuesListExtended = requests.request("GET", url, headers=headers, data=payload)
    issuesListExtended = issuesListExtended.text
    issuesListExtended = json.loads(issuesListExtended)
    return issuesListExtended


service = Vars.sdService
sdToken = Vars.sdToken
dbCreds = Vars.dbCreds
tableFields = Vars.sdTableFields
jsonKeys = Vars.sdJsonKeys
lastQueryTime = datetime.datetime.now()
issuesList = []
# Debug:
notInDb = []

# Получение списка ids из sd (старый метод):
# while issuesList == []:
#     queryDelay(lastQueryTime)
#     issuesList = Functions.requestSender(service, "getList", "")
#     lastQueryTime = datetime.datetime.now()

print(0)
# Получение последнего id в БД:
lastIdInDb = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "sd_issues", "last", "", ""))
lastIdInDb = lastIdInDb[0][0]
# Изменение списка из sd (удаляются все номера до последнего id в БД):
# if lastIdInDb != []:
#     lastIdInDb = lastIdInDb[0][0]
#     for id in issuesList.copy():
#         if id < lastIdInDb + 1:
#             issuesList.remove(id)

# Получение списка ids из sd (запрос с пагинацией):
issuesListExtended = ["start value"]
page = 1
continueFlag = True

# Первоначальный запрос:
queryDelay(lastQueryTime)

url = "https://sd.primo-rpa.ru/api/v1/issues/list?api_token=" + sdToken + "&page[size]=50&page[number]=" + str(page)
payload = {}
headers = {}
issuesListExtended = requests.request("GET", url, headers=headers, data=payload)
issuesListExtended = issuesListExtended.text
issuesListExtended = json.loads(issuesListExtended)

# issuesListExtended = getIssuesByPage(page, sdToken)
lastQueryTime = datetime.datetime.now()

# Выполнение цикла до возвращения пустого значения:
while issuesListExtended != [] and continueFlag:
    # Добавление id к массиву:
    for issue in issuesListExtended:
        if issue["id"] == lastIdInDb:
            continueFlag = False
            break
        issuesList.append(issue["id"])
    page += 1
    # Очередной запрос + функция ожидания минимального времени:
    queryDelay(lastQueryTime)

    url = "https://sd.primo-rpa.ru/api/v1/issues/list?api_token=" + sdToken + "&page[size]=50&page[number]=" + str(page)
    payload = {}
    headers = {}
    issuesListExtended = requests.request("GET", url, headers=headers, data=payload)
    issuesListExtended = issuesListExtended.text
    issuesListExtended = json.loads(issuesListExtended)

    #issuesListExtended = getIssuesByPage(page, sdToken)
    lastQueryTime = datetime.datetime.now()

# Для каждого элемента списка проверяется условие существования в БД (для варианта без проверки последнего id),
# в случае отсутствия, веб-запросом получается json sd issue и помещается в БД:
for issueId in issuesList:
    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "sd_issues", issueId, "", "")):
        pass
    else:
        queryDelay(lastQueryTime)
        responseIssue = Functions.requestSender(service, "getItem", issueId)
        responseIssue = Functions.jsonValuesToList(jsonKeys, responseIssue, 0)
        lastQueryTime = datetime.datetime.now()
        query = Functions.dbQueryGenerator("INSERT", "sd_issues" , responseIssue[0], responseIssue, tableFields)
        Functions.dbQuerySender(dbCreds, "INSERT", query)
        # Debug:
        notInDb.append(issueId)

print("Added to db:", notInDb)