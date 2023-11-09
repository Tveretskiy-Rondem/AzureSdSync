import Functions
import Vars
import requests

azureUrl = Vars.azureUrl
azureHeaders = Vars.azureHeaders
id = 8

response = requests.request("GET", (azureUrl + "?ids=" + str(id)), headers=azureHeaders, verify=False)
print(response)