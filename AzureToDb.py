import Functions
import Vars

service = Vars.azureService
dbCreds = Vars.dbCreds
tableFields = Vars.azureTableFields
jsonKeys = Vars.azureJsonKeys

# Todo: Старый запрос. Удалить после тестирования.
# # Получение и преобразование в одномерный массив списка work items id:
# idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECT", "azure_work_items", "", "", ""))
# idsList = Functions.responseToOneLevelArray(idsListRaw)

# Получение и преобразование в одномерный массив незаполненных строк в таблице azure_work_items:
idsListRaw = Functions.dbQuerySender(dbCreds, "SELECT", "SELECT id FROM azure_work_items WHERE url IS NULL")
idsList = Functions.responseToOneLevelArray(idsListRaw)

for id in idsList:
    print("Processing work item", id)
    workItemUrl = Functions.dbQuerySender(dbCreds, "SELECT", Functions.dbQueryGenerator("SELECTurl", "azure_work_items", id, "", ""))
    workItemUrl = workItemUrl[0][0]

    # !!! Условие необязательно при использовании списка id по незаполненным строкам (упростить на досуге):
    if workItemUrl == None:
        print("No information about work item", id)
        print("Adding information to DB...")

        # Отправка веб-запроса, получение ответа:
        workItem = Functions.requestSender(service, "getItem", id)

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
        Functions.dbQuerySender(dbCreds, "UPDATE", Functions.dbQueryGenerator("UPDATE", "azure_work_items", id, workItemWithoutId, tableFieldsWithoutId))

    else:
        print("Information about work item", id, "already in DB")
