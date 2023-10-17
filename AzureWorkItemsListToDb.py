import Functions
import Vars

service = "az"
dbCreds = Vars.dbCreds
tableFields = Vars.azTableFields
jsonKeys = Vars.azJsonKeys
workItemsRange = Vars.azWorkItemsRange

for id in range(workItemsRange[0], workItemsRange[1]):
    response = Functions.requestSender(service, "exists", id)
    print("Processing work item #", id)
    if "value" in response:
        if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "az_work_items_exists", id, "", "")):
            print("Already in DB")
        else:
            print("Adding work item to DB")
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "az_work_items_exists", id, [id, "true"], ["id", "exists"]))
    elif "errorCode" in response:
        print("Not exists")
        # if Functions.dbQuerySender(dbCreds, "EXISTS",  Functions.dbQueryGenerator("EXISTS", "az_work_items_exists", id, "", "")):
        #     pass
        # else:
        #     pass