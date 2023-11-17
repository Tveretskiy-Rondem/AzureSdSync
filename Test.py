import re
import requests
import json
issueId = 2701
workItemId = 8572

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='
}

responseWorkItem = requests.request("GET", ("https://10.0.2.14/PrimoCollection/_apis/wit/workitems?ids=" + workItemId), headers=headers, verify=False)
responseWorkItem = json.loads(responseWorkItem.text)
#newAzureWorkItemStatus = responseWorkItem["id"]