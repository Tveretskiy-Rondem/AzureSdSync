import Functions
import Vars
import Debug

service = Vars.sdService
dbCreds = Vars.dbCreds
tableFields = Vars.sdTableFields
jsonKeys = Vars.sdJsonKeys
checkUpdateFields = Vars.sdCheckUpdateFields
checkUpdateJsonKeys = Vars.sdCheckUpdateJsonKeys
currentFileName = "SdUpdateInfo"
checkUpdateFieldsStr = ""

# Сборка строки с перечислением полей таблицы для запроса в БД:
for i in range(len(checkUpdateFields)):
    checkUpdateFieldsStr = checkUpdateFieldsStr + checkUpdateFields[i]
    if (i + 1) < len(checkUpdateFields):
        checkUpdateFieldsStr = checkUpdateFieldsStr + ", "

# Получение и преобразование в одномерный массив незаполненных строк в таблице sd_issues:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM sd_issues")
idsList = Functions.responseToOneLevelArray(idsListRaw)

for id in idsList:
    Debug.message(currentFileName, "10", str(id))
    issueDb = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT " + checkUpdateFieldsStr + " FROM sd_issues WHERE id = " + str(id))
    issueDbPrepared = issueDb[0]
    issueApi = Functions.requestSender(service, "getItem", id)
    issueApiPrepared = Functions.jsonValuesToList(checkUpdateJsonKeys, issueApi, 0)
    print(issueDbPrepared)
    print(issueApiPrepared)
    for i in range(len(issueApiPrepared)):
        if issueDbPrepared[i] == issueDbPrepared[i]:
            # print(issueApiPrepared[i], "=", issueDbPrepared[i])
            pass
        else:
            Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "sd_issues", id, issueApiPrepared, checkUpdateFields))
            print("Information updated:", issueApiPrepared[i], "=", issueDbPrepared[i])