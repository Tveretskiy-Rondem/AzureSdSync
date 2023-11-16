import requests
import json
import Functions
import Vars

# Генерация адреса:


# Генерация тела запроса:

azureUrl = "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workItems/8039?api-version=7.0-preview.3"
azureHeaders = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}

payload = json.dumps([
  {
    "op": "add",
    "path": "/fields/System.Description",
    "value": "From python"
  },
  {
    "op": "add",
    "path": "/fields/Custom.ServiceDesk",
    "value": "9999"
  }
])

# response = requests.patch(azureUrl, data=payload, headers=azureHeaders, verify=False)
# print(response)
# print(response.headers)