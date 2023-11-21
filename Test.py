import re
import requests
import json

issueId = 2701
workItemId = 8698

responseWorkItemProject = "tveretskiy_test"
# postCommentHeaders = {'Content-Type': 'application/json-patch+json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}
postCommentHeaders = {'Content-Type': 'application/json', 'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOnV0bXRtbzQybjdjbHJlNGlwcTRmZ29rcHhiM3lieWV1ejV2d2RydXp2bHZtb3ZueGxtbXE='}

payloadComment = json.dumps({"text": "Заявка в SD #" + str(issueId) + ", сопоставленная с данной таской, была закрыта. Вот."})
responseAddComment = requests.request("POST", "https://10.0.2.14/PrimoCollection/" + responseWorkItemProject + "/_apis/wit/workItems/" + str(workItemId) + "/comments?api-version=7.0-preview.3", headers=postCommentHeaders,data=payloadComment, verify=False)
print(responseAddComment.text)

