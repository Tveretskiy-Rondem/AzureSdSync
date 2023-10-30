import Functions
import Vars

service = Vars.sdService
sdToken = Vars.sdToken
dbCreds = Vars.dbCreds
tableFields = Vars.sdTableFields
statusTableFields = Vars.sdStatusTableFields
jsonKeys = Vars.sdJsonKeys
statusJsonKeys = Vars.sdStatusJsonKeys

idsResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "sd_issues", "", "", ""))
idsList = Functions.responseToOneLevelArray(idsResponse)

# lastIdInDb = 2600
# for id in idsList.copy():
#     if id < lastIdInDb + 1:
#         idsList.remove(id)

for id in idsList:
    print("Processing issue #", id)
    # Получение sd issue запросом, преобразование в json:
    responseIssueItem = Functions.requestSender(service, "getItem", id)
    responseIssueItem = Functions.jsonValuesToList(statusJsonKeys, responseIssueItem, 0)
    # Добавление id в ключи и поля:
    responseIssueItemWithId = responseIssueItem.copy()
    statusTableFieldsWithId = statusTableFields.copy()
    responseIssueItemWithId.append(id)
    statusTableFieldsWithId.append("id")

    # Проверка на наличие в таблице sd_statuses записи с этим id:
    if Functions.dbQuerySender(dbCreds, "EXISTS", Functions.dbQueryGenerator("EXISTS", "sd_statuses", id, "", "")):
        print("Status of issue already in DB. Compare statuses.")
        statusDbResponse = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECTlaststatus", "sd_statuses", id, "", ""))
        if statusDbResponse[0][0] != responseIssueItem[0]:
            print("Detected difference. Insert new status to DB.")
            Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "sd_statuses", id, responseIssueItemWithId, statusTableFieldsWithId))
        else:
            print("Diffs NOT detected.")
    else:
        print("Status with this id not exists in DB. Insert new status to DB.")
        Functions.dbQuerySender(dbCreds, "INSERT", Functions.dbQueryGenerator("INSERT", "sd_statuses", id, responseIssueItemWithId, statusTableFieldsWithId))