import time
import Vars
import datetime
import threading

# Todo добавить отправку сообщений о статусе.
# Todo завести все токены в переменную (а лучше в БД).

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
        print("Start SD to DB (SD - 1S)", flush=True)
        with open(path + "SdToDb.py") as sdtodb:
            exec(sdtodb.read())
        print("End SD to DB (SD - 1E)", flush=True)

        print("Start SD status checker (SD - 2S)", flush=True)
        with open(path + "SdStatusChecker.py") as statuschecker:
            exec(statuschecker.read())
        print("End SD status checker (SD - 2E)", flush=True)

        if (iteration % 3) == 0:
            print("Start SD info updater (SD - 3S)", flush=True)
            with open(path + "SdUpdateInfo.py") as sdupdate:
                exec(sdupdate.read())
            print("End SD info updater (SD - 3E)", flush=True)

        print("SD block end", flush=True)

    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on SD block!")
        print("An exception occurred:", error, flush=True)

def azureBlock():
    try:
        print("Start Azure work items list to DB (AZ - 1S)", flush=True)
        with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
            exec(azurelistdb.read())
        print("End Azure work items list to DB (AZ - 1E)", flush=True)

        print("Start Azure work items content to DB (AZ - 2S)", flush=True)
        with open(path + "AzureToDb.py") as azuretodb:
            exec(azuretodb.read())
        print("End Azure work items content to DB (AZ - 2E)", flush=True)

        if (iteration % 3) == 0:
            print("Start Azure info updater (AZ - 3S)", flush=True)
            with open(path + "AzureUpdateInfo.py") as azureupdate:
                exec(azureupdate.read())
            print("End Azure info updater (AZ - 3E)", flush=True)

        print("Start Azure status checker (Logic - 1S)", flush=True)
        with open(path + "AzureStatusChecker.py") as azurestatuschecker:
            exec(azurestatuschecker.read())
        print("End Azure status checker (Logic - 1E)", flush=True)

        print("Azure block end", flush=True)

    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on Azure block!")
        print("An exception occurred:", error, flush=True)

while True:
    print("Iteration:", iteration)
    iterationStartTime = datetime.datetime.now()

    threadAzure = threading.Thread(target=azureBlock)
    threadSd = threading.Thread(target=sdBlock)
    threadAzure.start()
    threadSd.start()

    threadSd.join()
    threadAzure.join()
    try:
        print("Start Matcher", flush=True)
        with open(path + "AzureSdMatch.py") as match:
            exec(match.read())
        print("End Matcher", flush=True)
    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on Matcher block!")
        print("An exception occurred:", error, flush=True)

    try:
        print("Initial review", flush=True)
        with open(path + "InitialReview.py") as initial:
            exec(initial.read())
        print("Initial review backlog", flush=True)
        with open(path + "InitialReviewBacklog.py") as initialBacklog:
            exec(initialBacklog.read())
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
    print("------------------------------------------------------")