import time
import Vars
import datetime
import threading

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

startTime = datetime.datetime.now()

def sdBlock():
    try:
        print("SD to DB", flush=True)
        with open(path + "SdToDb.py") as sdtodb:
            exec(sdtodb.read())

        print("SD status checker", flush=True)
        with open(path + "SdStatusChecker.py") as statuschecker:
            exec(statuschecker.read())

        if (iteration % 3) == 0:
            print("SD info updater", flush=True)
            with open(path + "SdUpdateInfo.py") as sdupdate:
                exec(sdupdate.read())

        print("Azure block end", flush=True)

    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on SD block!")
        print("An exception occurred:", error, flush=True)

def azureBlock():
    try:
        print("Azure work items list to DB", flush=True)
        with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
            exec(azurelistdb.read())

        print("Azure work items content to DB", flush=True)
        with open(path + "AzureToDb.py") as azuretodb:
            exec(azuretodb.read())

        if (iteration % 3) == 0:
            print("Azure info updater", flush=True)
            with open(path + "AzureUpdateInfo.py") as azureupdate:
                exec(azureupdate.read())

        print("Azure status checker", flush=True)
        with open(path + "AzureStatusChecker.py") as azurestatuschecker:
            exec(azurestatuschecker.read())

        print("Azure block end", flush=True)

    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on Azure block!")
        print("An exception occurred:", error, flush=True)

while True:
    print("Iteration:", iteration)
    iterationStartTime = datetime.datetime.now()

    threadAzure = threading.Thread(target=azureBlock())
    threadSd = threading.Thread(target=sdBlock())
    threadAzure.start()
    threadSd.start()

    threadSd.join()
    threadAzure.join()

    print("Matcher", flush=True)
    with open(path + "AzureSdMatch.py") as match:
        exec(match.read())

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

    wholeTime = datetime.datetime.now() - startTime
    iterationTime = datetime.datetime.now() - iterationStartTime

    print("Iteration time:", iterationTime)
    print("Time from start:", wholeTime, flush=True)