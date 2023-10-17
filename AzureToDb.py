import Functions
import Vars

service = "az"
dbCreds = Vars.azDbCreds
tableFields = Vars.azTableFields
jsonKeys = Vars.azJsonKeys

workItemsList = Functions.requestSender(service, "getList", "")

# for issueNumber in issuesList:
#     print("Processing issue #", issueNumber)
#     if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "sd_issues", issueNumber, "", "")):
#         print("Issue #", issueNumber, "exists")
#     else:
#         print("Issue #", issueNumber, "not exists and will be added to the database")
#         responseIssue = Functions.requestSender(service, "getItem", issueNumber)
#         responseIssue = Functions.jsonValuesToList(jsonKeys, responseIssue, 0)
#         Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "sd_issues" , responseIssue[0], responseIssue, tableFields))