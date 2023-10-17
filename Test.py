import Functions

service = "sd"
sdToken = "ae095dff50035a3dd6fd64405de7bf57c1d08e6e"
azToken = ""

dbCreds = ["postgres", "postgres", "192.168.26.26", "5432", "SD"]
tableFields = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "responsible", "status"]
jsonKeys = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "assignee", "status"]
nestedKeys = ["0", "0", "0", "0", "name", "name", "0", "name", "name", "name"]

# ToDo:
# azure id, to release

issue = Functions.requestSender(service, "getItem", "200")
print(issue)
issue = Functions.jsonValuesToList(jsonKeys, nestedKeys, issue)
print(issue)