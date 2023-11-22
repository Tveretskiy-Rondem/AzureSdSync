import re
import requests
import json

issueId = 2701
workItemId = 8698

responseNewAzureWorkItem = requests.request("POST", azureUrl, headers=headers, data=payload, verify=False)
responseNewAzureWorkItem = json.loads(responseNewAzureWorkItem.text)
newAzureWorkItemId = responseNewAzureWorkItem["id"]
newAzureWorkItemUrl = responseNewAzureWorkItem["url"]
