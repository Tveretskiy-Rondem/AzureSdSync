import requests
import json
import psycopg2
import Vars

def dbQueryGenerator(type, table, issueId, insertData, tableFields):
    # Проверка типа запроса
    if type == "SELECT":
        return "SELECT * FROM " + table + " WHERE id = " + str(issueId)
    elif type == "EXISTS":
        return "SELECT EXISTS (SELECT id FROM " + table + " WHERE id = " + str(issueId) + ")"
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
    azUrl = Vars.azUrl
    azHeaders = Vars.azHeaders

    if service == "sd":
        if type == "getList":
            response = requests.request("GET", (sdUrl + "/count?api_token=" + sdToken))
        elif type == "getItem":
            response = requests.request("GET", (sdUrl + str(id) + "?api_token=" + sdToken))
    if service == "az":
        if type == "exists":
            response = requests.request("GET", (azUrl + "?ids=" + str(id) + "&fields=id&api-version=7.0"), headers=azHeaders, verify=False)
        elif type == "getItem":
            response = requests.request("GET", (azUrl + str(id)), headers=azHeaders, verify=False)
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
                jsonValues.append("")
        elif type(keys[i]) == list:
            jsonValues.append(jsonValuesToList(keys[i], response[keys[i][0]], 1))
    for value in jsonValues:
        if type(value) == str or type(value) == int:
            jsonValuesNormalized.append(value)
        elif type(value) == list:
            jsonValuesNormalized.append(value[0])
    return jsonValuesNormalized
