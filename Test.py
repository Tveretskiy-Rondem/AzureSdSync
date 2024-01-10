import datetime
import time
import requests
import json
import Functions

service = "sd"
issueId = "2701"
newAzureWorkItemId = "9302"
azurePostUri = "https://azure-dos.s1.primo1.orch/PrimoCollection/Discovery/_apis/wit/attachments?fileName=TestFile.png"

responseIssue = Functions.requestSender(service, "getItem", issueId)
responseAttach = responseIssue["attachments"]

print(responseAttach)

for attachment in responseAttach:
    urlGetAttach = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/attachments/" + str(
        attachment["id"]) + "?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e"

    attachmentResponse = requests.request("GET", urlGetAttach)
    attachmentResponse = json.loads(attachmentResponse.text)
    print(attachmentResponse)

    # Получение и сохранение прикрепленного файла
    attachFile = requests.request("GET", attachmentResponse["attachment_url"])
    # open("/tmp/" + attachmentResponse["attachment_file_name"], 'wb').write(attachFile.content)
    print(attachFile.content)


    payload = json.dumps({"text": "Вложение: " + attachmentUrl})

    payload = json.dumps({"text": "<a href=\"" + attachmentUrl + "\">Вложение</a>"})
    headersComment = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='
    }
    respComment = requests.request("POST", "https://10.0.2.14/PrimoCollection/Discovery/_apis/wit/workItems/" + str(newAzureWorkItemId) + "/comments?api-version=7.0-preview.3", headers=headersComment, data=payload, verify=False)
