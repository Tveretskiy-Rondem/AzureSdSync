import Functions
import Vars

dbCreds = Vars.dbCreds
azureWorkItemId = "9340"

plannedRelease = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT planned_release FROM azure_work_items WHERE id = " + str(azureWorkItemId))
plannedRelease = plannedRelease[0][0]

print(plannedRelease)