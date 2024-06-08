import json
import re

import requests

url = "https://sd.primo-rpa.ru/api/v1/issues/2703?api_token=8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)
response = json.loads(response.text)

for parameter in response["parameters"]:
    if parameter["code"] == "1111":
        print(parameter)
        if parameter["value"] == None:
            print("None!")
        else:
            pattern = r"/(?<=\/)\d+"
            azureWorkItemId = re.search(pattern, parameter["value"]).group()
            azureWorkItemId = azureWorkItemId.replace('/', '')
            print(azureWorkItemId)