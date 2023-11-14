import Functions
import Vars

dbCreds = Vars.dbCreds

def lastSdStatuses():
    idsResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "sd_issues", "", "", ""))
    idsList = Functions.responseToOneLevelArray(idsResponse)

    for id in idsList:
        numberOfRecords = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT COUNT(*) FROM sd_statuses WHERE is_last = true AND id = " + str(id))
        print("Id:", id)
        numberOfRecords = numberOfRecords[0][0]
        print(numberOfRecords)
        while numberOfRecords > 1:
            Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE sd_statuses SET is_last = false WHERE checked_at = (SELECT checked_at FROM sd_statuses WHERE id = " + str(id) + " AND is_last = true ORDER BY checked_at ASC LIMIT 1)")
            numberOfRecords = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT COUNT(*) FROM sd_statuses WHERE is_last = true AND id = " + str(id))
            numberOfRecords = numberOfRecords[0][0]
            print(numberOfRecords)

def lastAzureStatuses():
    idsResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "azure_work_items", "", "", ""))
    idsList = Functions.responseToOneLevelArray(idsResponse)

    for id in idsList:
        numberOfRecords = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT COUNT(*) FROM azure_statuses WHERE is_last = true AND id = " + str(id))
        print("Id:", id)
        numberOfRecords = numberOfRecords[0][0]
        print(numberOfRecords)
        while numberOfRecords > 1:
            Functions.dbQuerySender(dbCreds, "UPDATE", "UPDATE azure_statuses SET is_last = false WHERE checked_at = (SELECT checked_at FROM azure_statuses WHERE id = " + str(id) + " AND is_last = true ORDER BY checked_at ASC LIMIT 1)")
            numberOfRecords = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT COUNT(*) FROM azure_statuses WHERE is_last = true AND id = " + str(id))
            numberOfRecords = numberOfRecords[0][0]
            print(numberOfRecords)

lastSdStatuses()
lastAzureStatuses()