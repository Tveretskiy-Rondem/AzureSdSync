import re
import requests
import json
import Functions

service = "sd"
issueId = 2760
sdJsonKeys = ["id", "title", "created_at", "completed_at", ["type", "name"], ["priority", "name"], "company_id", ["author", "name"], ["assignee", "name"]]

# Получение ссылок на вложения:
responseIssue = Functions.requestSender(service, "getItem", issueId)
responseAttach = responseIssue["attachments"]

for attachment in responseAttach:
    urlGetAttach = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/attachments/" + str(attachment["id"]) + "?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e"

    attachmentResponse = requests.request("GET", urlGetAttach)
    attachmentResponse = json.loads(attachmentResponse.text)

    attachmentUrl = attachmentResponse["attachment_url"]