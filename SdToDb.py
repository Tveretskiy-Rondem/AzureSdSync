import Functions

service = "sd"
sdToken = "ae095dff50035a3dd6fd64405de7bf57c1d08e6e"
dbCreds = ["postgres", "postgres", "192.168.26.26", "5432", "SD"]
tableFields = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "responsible", "status"]
jsonKeys = ["id", "title", "created_at", "completed_at", ["type", "name"], ["priority", "name"], "company_id", ["author", "name"], ["assignee", "name"], ["status", "name"]]
# jsonKeys = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "assignee", "status"]
# nestedKeys = ["0", "0", "0", "0", "name", "name", "0", "name", "name", "name"]

# ToDo:
# azure id, to release

issuesList = Functions.requestSender(service, "getList", "")

for issueNumber in issuesList:
    print("Processing issue #", issueNumber)
    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "sd_issues", issueNumber, "", "")):
        print("Issue #", issueNumber, "exists")
    else:
        print("Issue #", issueNumber, "not exists and will be added to the database")
        responseIssue = Functions.requestSender(service, "getItem", issueNumber)
        responseIssue = Functions.jsonValuesToList(jsonKeys, responseIssue, 0)
        Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "sd_issues" , responseIssue[0], responseIssue, tableFields))