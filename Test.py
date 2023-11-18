import re
import requests
import json
issueId = 2701
workItemId = 8594

url = "https://sd.primo-rpa.ru/api/v1/issues/2701/statuses?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b"

payloadToBacklog = json.dumps({
  "code": "primo_rpa_backlog",
  "comment": "Тест перехода статуса в бэклог",
  "comment_public": False
})
headersToBacklog = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/statuses?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b", headers=headers, data=payload)

print(response.text)

