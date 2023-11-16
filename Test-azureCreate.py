import requests
import json
import Functions
# ToDo Перенос компонента (студия, орк...)

service = "sd"
issueId = 2701
azureUrl = "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workitems/$Task?api-version=7.0"
sdCompanyUrl = "https://sd.primo-rpa.ru/api/v1/companies/?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e&id="
# url = "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workitems/$Task?api-version=7.0"
sdJsonKeys = ["title", "description", ["type", "name"], "id", "company_id"]
azurePaths = ["/fields/System.Title", "/fields/System.Description", "/fields/System.WorkItemType", "/fields/Custom.ServiceDesk", "/fields/Custom.Client"]
payloadTemplate = {"op": "add", "path": "", "from": None, "value": ""}
headers = {
  'Content-Type': 'application/json-patch+json',
  'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='
}

responseIssue = Functions.requestSender(service, "getItem", issueId)
responseIssueValues = Functions.jsonValuesToList(sdJsonKeys, responseIssue, 0)

payloadResult = []

for i in range(len(sdJsonKeys)):
  payloadTemplate["path"] = azurePaths[i]
  # Проверка на заполнение типа (пропускаем, пока тестовому проекту не дали нужные типы) и поля коиента:
  if azurePaths[i] == "/fields/System.WorkItemType":
    # if responseIssueValues[i] == "Инцидент" or "Ошибка" or "Прочее":
    #   payloadTemplate["value"] = "Bug"
    # else:
    #   payloadTemplate["value"] = "User Story"
    payloadTemplate["value"] = "Task"
  elif azurePaths[i] == "/fields/Custom.Client":
    # Получение названия клиента по id:
    sdCompanyUrlWithId = sdCompanyUrl + str(responseIssueValues[i])
    print(sdCompanyUrlWithId)
    responseSdCompany = requests.request("GET", sdCompanyUrlWithId)
    responseSdCompany = json.loads(responseSdCompany.text)
    payloadTemplate["value"] = responseSdCompany["name"]
  else:
    payloadTemplate["value"] = responseIssueValues[i]
  payloadResult.append(payloadTemplate.copy())
  print(payloadResult)

payload = json.dumps(payloadResult)

responseNewAzureWorkItem = requests.request("POST", azureUrl, headers=headers, data=payload, verify=False)
responseNewAzureWorkItem = json.loads(responseNewAzureWorkItem.text)
newAzureWorkItemId = responseNewAzureWorkItem["id"]