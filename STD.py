import pandas as pd
import requests
import json
import time
import datetime
import Functions
import Vars

pathToTable = "/home/otter/Downloads/0504.xlsx"
service = "sd"
dbCreds = Vars.dbCreds
list = []
closed = []

def queryDelay(lastQueryTime):
    queryDelayMs = 270
    if (datetime.datetime.now() - lastQueryTime).microseconds <= queryDelayMs:
        time.sleep(abs((queryDelayMs - (datetime.datetime.now() - lastQueryTime).microseconds) / 1000))

def getSdIssue(issueId):
    url = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.text)
    return response.text

def getAzureWorkItem(workItemId):
    url = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids=" + str(workItemId)
    payload = {}
    headers = {'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='}
    response = requests.request("GET", url, headers=headers, data=payload,  verify=False)
    return response.text

def azureRemove(itemId, workItemProject):
    payloadToClose = json.dumps([{"op": "add", "path": "/fields/System.State", "value": "Removed"}])
    changeStatusHeaders = {'Content-Type': 'application/json-patch+json',
                           'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='}
    responseChangeStatus = requests.request("PATCH", (
                "https://10.0.2.14/PrimoCollection/" + workItemProject + "/_apis/wit/workItems/" + str(
            itemId) + "?api-version=7.0-preview.3"), headers=changeStatusHeaders, data=payloadToClose, verify=False)
    return responseChangeStatus

# Чтение таблицы:
pandasDF = pd.read_excel(pathToTable)
pandasValues = pandasDF.values

for row in pandasValues:
    list.append(row[0])

lastQueryTime = datetime.datetime.now()

print("Start")

for issueId in list:
    queryDelay(lastQueryTime)
    responseIssueItem = getSdIssue(issueId)
    lastQueryTime = datetime.datetime.now()
    responseIssueItem = json.loads(responseIssueItem)
    sdStatus = responseIssueItem["status"]
    sdStatus = sdStatus["name"]

    if sdStatus == 'Решена' or sdStatus == 'Закрыта' or sdStatus == 'Закрыта в связи с отсутствием реакции пользователя дольше 30 дней':
        workItemIds = Functions.dbQuerySender(dbCreds, "SELECT", ("SELECT azure_work_item_id FROM azure_sd_match WHERE sd_issue_id = " + str(issueId)))
        workItemIds = Functions.responseToOneLevelArray(workItemIds)
        if workItemIds != []:
            for workItemId in workItemIds:
                # print(issueId)
                responseAzureWorkItem = json.loads(getAzureWorkItem(workItemId))
                # print(responseAzureWorkItem)
                try:
                    responseAzureWorkItem = responseAzureWorkItem["value"]
                    responseAzureWorkItem = responseAzureWorkItem[0]
                except:
                    continue
                azureWorkItem = responseAzureWorkItem["fields"]
                azureWorkItemProject = azureWorkItem["System.TeamProject"]
                azureWorkItemState = azureWorkItem["System.State"]
                if azureWorkItemState == "Discovery" or azureWorkItemState == "Design":
                    # print(issueId, sdStatus)
                    print(workItemId, azureWorkItemProject, azureWorkItemState)
                    # print()
                    closed.append(workItemId)
                    removeResponse = azureRemove(workItemId, azureWorkItemProject)
                    print(removeResponse)
                    print(removeResponse.text)

print(closed)


