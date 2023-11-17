import time
import Vars

# Переключатель тест/прод:
isTest = Vars.isTest

if isTest:
    # Test path:
    path = ""
else:
    # Service path:
    path = "/home/ubuntu/AzureSdSync/"

while True:
    with open(path + "SdToDb.py") as sdtodb:
        exec(sdtodb.read())
    with open(path + "SdStatusChecker.py") as statuschecker:
        exec(statuschecker.read())
    with open(path + "SdUpdateInfo.py") as sdupdate:
        exec(sdupdate.read())
    with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
        exec(azurelistdb.read())
    with open(path + "AzureToDb.py") as azuretodb:
        exec(azuretodb.read())
    with open(path + "AzureUpdateInfo.py") as azureupdate:
        exec(azureupdate.read())
    with open(path + "AzureStatusChecker.py") as azurestatuschecker:
        exec(azurestatuschecker.read())
    with open(path + "AzureSdMatch.py") as match:
        exec(match.read())
    with open(path + "InitialReview.py") as initial:
        exec(initial.read())
    print("Sleep 120 seconds...")
    if isTest:
        break
    time.sleep(120)