import Functions
import Vars

service = Vars.azureService
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys
workItemsRange = Vars.azureWorkItemsRange

for id in range(workItemsRange[0], workItemsRange[1]):
    response = Functions.requestSender(service, "exists", id)
    print("Processing work item #", id)
    if "value" in response:
        if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "azure_work_items", id, "", "")):
            print("Already in DB")
        else:
            print("Adding work item to DB")
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "azure_work_items", id, [id], ["id"]))
    elif "errorCode" in response:
        print("Not exists in azure")