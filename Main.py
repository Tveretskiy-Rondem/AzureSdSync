import time
import Vars

# Todo добавить отправку сообщений о статусе.

# Переключатель тест/прод:
isTest = Vars.isTest
iteration = 0

if isTest:
    # Test path:
    path = ""
else:
    # Service path:
    path = "/home/ubuntu/AzureSdSync/"

while True:
    print("Iteration:", iteration)

    try:
        print("SD to DB", flush=True)
        with open(path + "SdToDb.py") as sdtodb:
            exec(sdtodb.read())
        print("SD status checker", flush=True)
        with open(path + "SdStatusChecker.py") as statuschecker:
            exec(statuschecker.read())
        print("SD info updater", flush=True)
        with open(path + "SdUpdateInfo.py") as sdupdate:
            exec(sdupdate.read())
    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on SD block!")
        print("An exception occurred:", error, flush=True)

    try:
        print("Azure work items list to DB", flush=True)
        with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
            exec(azurelistdb.read())
        print("Azure work items content to DB", flush=True)
        with open(path + "AzureToDb.py") as azuretodb:
            exec(azuretodb.read())
        print("Azure info updater", flush=True)
        with open(path + "AzureUpdateInfo.py") as azureupdate:
            exec(azureupdate.read())
        print("Azure status checker", flush=True)
        with open(path + "AzureStatusChecker.py") as azurestatuschecker:
            exec(azurestatuschecker.read())
        print("Matcher", flush=True)
        with open(path + "AzureSdMatch.py") as match:
            exec(match.read())
    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on Azure block!")
        print("An exception occurred:", error, flush=True)

    try:
        print("Initial review", flush=True)
        with open(path + "InitialReview.py") as initial:
            exec(initial.read())
        # print("Closed in SD")
        # with open(path + "ClosedInSd.py") as closedsd:
        #     exec(closedsd.read())
        # print("Closed in azure")
        # with open(path + "ClosedInAzure.py") as closedazure:
        #     exec(closedazure.read())
    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on Main logic block!")
        print("An exception occurred:", error, flush=True)

    iteration = iteration + 1