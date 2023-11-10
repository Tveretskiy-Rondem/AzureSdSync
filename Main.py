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
    with open(path + "SdDiffChecker.py") as sddiffchecker:
        exec(sddiffchecker.read())
    with open(path + "SdUpdateInfo.py") as sdupdate:
        exec(sdupdate.read())
    with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
        exec(azurelistdb.read())
    with open(path + "AzureToDb.py") as azuretodb:
        exec(azuretodb.read())
    with open(path + "AzureUpdateInfo.py") as azureupdate:
        exec(azureupdate.read())
    with open(path + "AzureDiffChecker.py") as azurediffchecker:
        exec(azurediffchecker.read())
    with open(path + "AzureSdMatch.py") as match:
        exec(match.read())
    print("Sleep 120 seconds...")
    if isTest:
        break
    time.sleep(120)