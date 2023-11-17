import requests
import json
import psycopg2
import Vars
import Functions
import Debug

dbCreds = Vars.dbCreds
service = Vars.azureService
currentFileName = "AzureSdMatch"

Debug.message(currentFileName, "start", "")

# sdIssuesList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id, azure_work_item FROM sd_issues WHERE azure_work_item IS NOT NULL")
azureWorkItemsList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id, sd_issue FROM azure_work_items WHERE is_deleted = false AND sd_issue IS NOT NULL")

for issuesByWorkItem in azureWorkItemsList:
    workItemId = issuesByWorkItem[0]
    issuesByWorkItemPrepared = issuesByWorkItem[1].strip()
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace(", ", "---")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("https://sd.primo-rpa.ru/issues/", "")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("#!", "")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace("/", "")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.replace(" ", "---")
    issuesByWorkItemPrepared = issuesByWorkItemPrepared.split("---")
    for issueByWorkItem in issuesByWorkItemPrepared:
        issuesByWorkItemFromTable = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT sd_issue_id FROM azure_sd_match WHERE azure_work_item_id =" + str(workItemId))
        issuesByWorkItemFromTable = Functions.responseToOneLevelArray(issuesByWorkItemFromTable)
        # print(issueByWorkItem, type(issueByWorkItem))
        # print(issuesByWorkItemFromTable, type(issuesByWorkItemFromTable[0]))
        if int(issueByWorkItem) in issuesByWorkItemFromTable:
            pass
        else:
            Debug.message(currentFileName, "10", ("work item: " + str(workItemId) + " & sd issue: " + str(issueByWorkItem)))
            Functions.dbQuerySender(dbCreds, "INSERT", "INSERT INTO azure_sd_match (azure_work_item_id, sd_issue_id) VALUES(" + str(workItemId) + ", " + str(issueByWorkItem) + ")")