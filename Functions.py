import requests
import json
import psycopg2
import Vars

requests.packages.urllib3.disable_warnings()

# Todo: Переосмыслить логику и переделать генератор запросов, потому что сейчас - это пи*здец. Возможно, убрать его в sender.
def dbQueryGenerator(type, table, id, insertData, tableFields):
    # Проверка типа запроса
    if type == "SELECT":
        if str(id) == "" and tableFields == "":
            return "SELECT id FROM " + table + " ORDER BY id ASC"
        elif str(id) == "last":
            return "SELECT id FROM " + table + " ORDER BY id DESC LIMIT 1"
        elif str(id) != "" and tableFields != "":
            return "SELECT " + tableFields + " FROM " + table + " WHERE id = " + str(id) + " ORDER BY id DESC LIMIT 1"
        else:
            return "SELECT * FROM " + table + " WHERE id = " + str(id)
    elif type == "SELECTurl":
        return "SELECT url FROM " + table + " WHERE id = " + str(id)
    elif type == "SELECTstatus":
        return "SELECT status FROM " + table + " WHERE id = " + str(id)
    elif type == "SELECTlaststatus":
        return "SELECT status FROM " + table + " WHERE id = " + str(id) + " ORDER BY checked_at DESC LIMIT 1"
    elif type == "SELECTemptyazure":
        return "SELECT id FROM " + table + " WHERE url IS NULL"
    elif type == "EXISTS":
        return "SELECT EXISTS (SELECT id FROM " + table + " WHERE id = " + str(id) + ")"
    elif type == "INSERT":
        query = "INSERT INTO " + table + " ("
        # Цикл по длине массива полей БД
        for i in range(len(tableFields)):
            # Проверка на последнее поле
            if i < (len(tableFields) - 1):
                query = query + tableFields[i] + ", "
            else:
                query = query + tableFields[i] + ") VALUES("
        # Добавление значений переменных
        for i in range(len(tableFields)):
            # !!! Вывел из под if:
            insertDataElement = str(insertData[i])
            insertDataElement = insertDataElement.replace("'", " ")
            if i < (len(tableFields) - 1):
                if insertDataElement == "None":
                    query = query + " null, "
                else:
                    query = query + "'" + insertDataElement + "', "
            else:
                query = query + "'" + insertDataElement + "')"
        return query
    elif type == "UPDATE":
        query = "UPDATE " + table + " SET "
        # Цикл по длине массива полей БД
        for i in range(len(tableFields)):
            insertDataElement = str(insertData[i])
            insertDataElement = insertDataElement.replace("'", " ")
            # Проверка на последнее поле
            if i < (len(tableFields) - 1):
                if str(insertData[i]) == "None":
                    pass
                else:
                    query = query + tableFields[i] + " = '" + insertDataElement + "', "
            else:
                query = query + tableFields[i] + " = '" + insertDataElement + "' WHERE id = " + str(id)
        return query

def dbQuerySender(creds, type, query):
    connection = psycopg2.connect(user=creds[0], password=creds[1], host=creds[2], port=creds[3], database=creds[4])
    cursor = connection.cursor()
    cursor.execute(query)
    if type == "SELECT":
        return cursor.fetchall()
    elif type == "EXISTS":
        result = cursor.fetchall()
        return result[0][0]
    connection.commit()
    if connection:
        cursor.close()
        connection.close()

def requestSender(service, type, id):
    sdToken = Vars.sdToken
    sdUrl = Vars.sdUrl
    azureUrl = Vars.azureUrl
    azureHeaders = Vars.azureHeaders

    # Todo убрана обработка исключения. Проверить!:
    if service == "sd":
        if type == "getList":
            response = requests.request("GET", (sdUrl + "/count?api_token=" + sdToken))
        elif type == "getItem":
            response = requests.request("GET", (sdUrl + str(id) + "?api_token=" + sdToken))
    if service == "azure":
        if type == "exists":
            response = requests.request("GET", (azureUrl + "?ids=" + str(id) + "&fields=id&api-version=7.0"), headers=azureHeaders, verify=False)
        elif type == "getItem":
            response = requests.request("GET", (azureUrl + "?ids=" + str(id)), headers=azureHeaders, verify=False)
    return response.json()

def jsonValuesToList(keys, response, startElement):
    jsonValues = []
    jsonValuesNormalized = []
    for i in range(startElement, len(keys)):
        if type(keys[i]) == str:
            try:
                if response[keys[i]] == None:
                    jsonValues.append("None")
                else:
                    jsonValues.append(response[keys[i]])
            except:
                jsonValues.append("None")
        elif type(keys[i]) == list:
            try:
                jsonValues.append(jsonValuesToList(keys[i], response[keys[i][0]], 1))
            except KeyError:
                jsonValues.append("None")
    for value in jsonValues:
        if type(value) == str or type(value) == int:
            jsonValuesNormalized.append(value)
        elif type(value) == list:
            jsonValuesNormalized.append(value[0])
    return jsonValuesNormalized

def compare(values1, values2):
    diffIndexes = []
    for i in range(len(values1)):
        if values1[i] != values2[i]:
            diffIndexes.append(i)
    return diffIndexes

def responseToOneLevelArray(response):
    oneLevelArray = []
    for element in response:
        oneLevelArray.append(element[0])
    return oneLevelArray
