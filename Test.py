import datetime
import time
import requests
import Functions

issueId = 2788

responseIssue = Functions.requestSender("sd", "getItem", issueId)
for sdParameter in responseIssue["parameters"]:
    print(sdParameter["code"])
    if str(sdParameter["code"]) == "steps_to_reproduce":
        print("It is!")
        print(sdParameter["value"])

print(responseIssue["parameters"])