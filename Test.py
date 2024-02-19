import requests
import json
import Functions
import Vars

workItemId = 1151
wiGetHeaders = {
  'Content-Type': 'application/json-patch+json',
  'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='
}

workItemApi = requests.request("GET", ("https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids=" + str(workItemId)), headers=wiGetHeaders, verify=False)
workItemApi = json.loads(workItemApi.text)
workItemApi = workItemApi["value"]
workItemApi = workItemApi[0]

print(workItemApi["fields"]["System.IterationPath"])