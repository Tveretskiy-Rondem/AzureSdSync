import Functions
import Vars

service = "azure"
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys

# Debug:
infoAdded = []

# Получение и преобразование в одномерный массив незаполненных строк в таблице azure_work_items:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items WHERE url IS NULL")
idsList = Functions.responseToOneLevelArray(idsListRaw)

for workItemId in idsList:
    workItemUrl = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECTurl", "azure_work_items", workItemId, "", ""))
    workItemUrl = workItemUrl[0][0]

    # !!! Условие необязательно при использовании списка id по незаполненным строкам (упростить на досуге):
    if workItemUrl == None:
        # print("No information about work item", workItemId)
        # print("Adding information to DB...")

        # Отправка веб-запроса, получение ответа:
        workItem = Functions.requestSender(service, "getItem", workItemId)

        # Разбор полученного JSON до нужного уровня вложенности:
        workItem = workItem["value"]
        workItem = workItem[0]
        workItem = Functions.jsonValuesToList(jsonKeys, workItem, 0)

        workItemWithoutId = workItem.copy()
        tableFieldsWithoutId = tableFields.copy()

        # Удаление id из ключей и данных:
        del workItemWithoutId[0]
        del tableFieldsWithoutId[0]

        # Генерация и отправка в БД запроса на апдейт:
        # print(Functions.dbQueryGenerator("UPDATE", "azure_work_items", id, workItemWithoutId, tableFieldsWithoutId))
        Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "azure_work_items", workItemId, workItemWithoutId, tableFieldsWithoutId))

        # Debug:
        infoAdded.append(workItemId)

    else:
        # print("Information about work item", workItemId, "already in DB")
        pass

print("Added info to DB:", infoAdded)