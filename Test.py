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

def getIssuesByPage(page):
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

# Debug:
notInDb = []

# Получение списка ids из sd (старый метод):
queryDelay(lastQueryTime)
issuesList = Functions.requestSender(service, "getList", "")
lastQueryTime = datetime.datetime.now()

# Получение списка ids из sd (запрос с пагинацией):
issuesListNormalized = []
issuesListExtended = ["start value"]
page = 1

# Первоначальный запрос:
queryDelay(lastQueryTime)
issuesListExtended = getIssuesByPage(page)
lastQueryTime = datetime.datetime.now()

# Выполнение цикла до возвращения пустого значения:
while issuesListExtended != []:
    # Добавление id к массиву:
    for issue in issuesListExtended:
        issuesListNormalized.append(issue["id"])
    page += 1
    # Очередной запрос + функция ожидания минимального времени:
    queryDelay(lastQueryTime)
    issuesListExtended = getIssuesByPage(page)
    lastQueryTime = datetime.datetime.now()
