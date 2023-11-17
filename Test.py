import re
import requests
import json
issueId = 2701
workItemId = 8572

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='
}

responseSdIssueComments = requests.request("GET", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/comments?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e")
responseSdIssueComments = json.loads(responseSdIssueComments.text)
for comment in responseSdIssueComments:
    author = comment["author"]
    author = author["name"]
    text = comment["content"]
    payload = json.dumps({"text": (text + "\nАвтор в SD:" + author) })
    requests.request("POST", "https://10.0.2.14/PrimoCollection/tveretskiy_test/_apis/wit/workItems/" + str(workItemId) + "/comments?api-version=7.0-preview.3", headers=headers, data=payload, verify=False)