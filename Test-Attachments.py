import datetime
import time
import requests
import json
import Functions

service = "sd"
issueId = "2940"
newAzureWorkItemId = "11439"
# azurePostUri = "https://azure-dos.s1.primo1.orch/PrimoCollection/Discovery/_apis/wit/attachments?fileName=TestFile.png"

responseIssue = Functions.requestSender(service, "getItem", issueId)
responseAttach = responseIssue["attachments"]


for attachment in responseAttach:
    urlGetAttach = "https://sd.primo-rpa.ru/api/v1/issues/" + str(issueId) + "/attachments/" + str(
        attachment["id"]) + "?api_token=ae095dff50035a3dd6fd64405de7bf57c1d08e6e"

    sdAttachmentResponse = requests.request("GET", urlGetAttach)
    sdAttachmentResponse = json.loads(sdAttachmentResponse.text)
    print(sdAttachmentResponse)

    # Получение и сохранение прикрепленного файла
    attachedFile = requests.request("GET", sdAttachmentResponse["attachment_url"])
    open("/tmp/" + sdAttachmentResponse["attachment_file_name"], 'wb').write(attachedFile.content)
    # print(attachFile.content)

    # Загрузка файла на сервер Azure
    # ToDo добавить удаление временных файлов!
    AzurePostAttachUrl = "https://azure-dos.s1.primo1.orch/PrimoCollection/Discovery/_apis/wit/attachments?fileName=" + sdAttachmentResponse["attachment_file_name"] + "&api-version=5.1"
    payload = {}
    files = [('', ('attach', open(('/tmp/' + sdAttachmentResponse["attachment_file_name"]), 'rb')))]
    headers = {'Content-Type': 'application/octet-stream', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}

    responseAzurePostAttachment = requests.request("POST", AzurePostAttachUrl, headers=headers, data=payload, files=files, verify=False)
    azureNewAttachmentJson = json.loads(responseAzurePostAttachment.text)
    print(azureNewAttachmentJson)
    print(azureNewAttachmentJson["url"])
    azureNewAttachmentUrl = azureNewAttachmentJson["url"]
    print(responseAzurePostAttachment.text)

    # Сопоставление файла с work item
    urlAttachToWI = "https://azure-dos.s1.primo1.orch/PrimoCollection/Discovery/_apis/wit/workitems/" + str(newAzureWorkItemId) + "?api-version=7.0"

    payload = json.dumps([
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "AttachedFile",
                "url": azureNewAttachmentUrl,
                "attributes": {
                    "comment": sdAttachmentResponse["description"]
                }
            }
        }
    ])
    headers = {
        'Content-Type': 'application/json-patch+json',
        'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='
    }

    responseAttachToWI = requests.request("PATCH", urlAttachToWI, headers=headers, data=payload, verify=False)