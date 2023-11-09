import requests
import json
import psycopg2
import Vars
import Functions

dbCreds = Vars.dbCreds
service = Vars.azureService

print("Start")
sdIssuesList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id, azure_work_item FROM sd_issues WHERE azure_work_item IS NOT NULL")
azureWorkItemsList = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id, sd_issue FROM azure_work_items WHERE sd_issue IS NOT NULL")

print(sdIssuesList)
print(azureWorkItemsList)
for issues in azureWorkItemsList:
    issue = issues[1].strip()
    issue = issue.replace(", ", "---")
    issue = issue.replace("https://sd.primo-rpa.ru/issues/", "")
    issue = issue.replace("#!", "")
    issue = issue.replace("/", "")
    issue = issue.replace(" ", "---")
    issue = issue.split("---")
    for issueElement in issue:
        workItemForIssue = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT azure_work_item FROM sd_issues WHERE id = " + issueElement)
        if workItemForIssue != []:
            print(workItemForIssue[0][0])
            if workItemForIssue[0][0] == str(issues[0]):
                print("Sd issue #", issueElement, "already mapped with azure work item #", issues[0])
            else:
                print("Update sd issue #", issueElement, "by value of azure WI:", issues[0])
                Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET azure_work_item = '" + str(issues[0]) + "' WHERE id = '" + str(issueElement) + "'"))
        else:
            print("Update sd issue #", issueElement, "by value of azure WI:", issues[0])
            Functions.dbQuerySender(dbCreds, "UPDATE", ("UPDATE sd_issues SET azure_work_item = '" + str(issues[0]) + "' WHERE id = '" + str(issueElement) + "'"))