import time
import Vars
import datetime
import threading

# Todo добавить отправку сообщений о статусе.
# Todo завести все токены в БД.

# Переключатель тест/прод:
isTest = Vars.isTest
iteration = 0
azureEndFlag = False
sdEndFlag = False
sdStatusEndFlag = False
azureStatusEndFlag = False

if isTest:
    # Test path:
    path = ""
else:
    # Service path:
    path = "/home/ubuntu/AzureSdSync/"

startTime = datetime.datetime.now()

def sdStatusesBlock():
    global sdEndFlag
    global azureEndFlag
    global sdStatusEndFlag
    while not sdEndFlag and not azureEndFlag:
        try:
            print("Start SD status checker (SDST - S)", flush=True)
            timer_sdSt = datetime.datetime.now()
            with open(path + "SdStatusChecker.py") as statuschecker:
                exec(statuschecker.read())
            delta_time_sdSt = datetime.datetime.now() - timer_sdSt
            print("End SD status checker (SDST - E)", delta_time_sdSt, flush=True)

            sdStatusEndFlag = True

        except Exception as error:
            print("---------------", "WARNING!", end='\n')
            print("Exception on SD statuses block!")
            print("An exception occurred:", error, flush=True)

            sdStatusEndFlag = True

def azureStatusesBlock():
    global sdEndFlag
    global azureEndFlag
    global azureStatusEndFlag
    while not sdEndFlag and not azureEndFlag:
        try:
            print("Start Azure status checker (AZST - S)", flush=True)
            timer_azureSt = datetime.datetime.now()
            with open(path + "AzureStatusChecker.py") as azurestatuschecker:
                exec(azurestatuschecker.read())
            delta_time_azureSt = datetime.datetime.now() - timer_azureSt
            print("End Azure status checker (AZST - E)", delta_time_azureSt, flush=True)

            azureStatusEndFlag = True

        except Exception as error:
            print("---------------", "WARNING!", end='\n')
            print("Exception on AZ statuses block!")
            print("An exception occurred:", error, flush=True)

            azureStatusEndFlag = True

def sdBlock():
    global sdEndFlag
    timer_sd_block = datetime.datetime.now()
    try:
        print("Start SD to DB (SD - 1S)", flush=True)
        timer_sd = datetime.datetime.now()
        with open(path + "SdToDb.py") as sdtodb:
            exec(sdtodb.read())
        delta_time_sd = datetime.datetime.now() - timer_sd
        print("End SD to DB (SD - 1E)", delta_time_sd, flush=True)

        # print("Start SD status checker (SD - 2S)", flush=True)
        # timer_sd = datetime.datetime.now()
        # with open(path + "SdStatusChecker.py") as statuschecker:
        #     exec(statuschecker.read())
        # delta_time_sd = datetime.datetime.now() - timer_sd
        # print("End SD status checker (SD - 2E)", delta_time_sd, flush=True)

        if (iteration % 9) == 0 or iteration == 0:
            print("Start SD info updater (SD - 3S)", flush=True)
            timer_sd = datetime.datetime.now()
            with open(path + "SdUpdateInfo.py") as sdupdate:
                exec(sdupdate.read())
            delta_time_sd = datetime.datetime.now() - timer_sd
            print("End SD info updater (SD - 3E)", delta_time_sd, flush=True)

        delta_time_sd_block = datetime.datetime.now() - timer_sd_block
        print("SD block end", delta_time_sd_block, flush=True)

        sdEndFlag = True

    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on SD block!")
        print("An exception occurred:", error, flush=True)

        sdEndFlag = True

def azureBlock():
    global azureEndFlag
    timer_azure_block = datetime.datetime.now()
    try:
        print("Start Azure work items list to DB (AZ - 1S)", flush=True)
        timer_azure = datetime.datetime.now()
        with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
            exec(azurelistdb.read())
        delta_time_azure = datetime.datetime.now() - timer_azure
        print("End Azure work items list to DB (AZ - 1E)", delta_time_azure, flush=True)

        print("Start Azure work items content to DB (AZ - 2S)", flush=True)
        with open(path + "AzureToDb.py") as azuretodb:
            exec(azuretodb.read())
        print("End Azure work items content to DB (AZ - 2E)", delta_time_azure, flush=True)

        if (iteration % 13) == 0 or iteration == 0:
            print("Start Azure info updater (AZ - 3S)", flush=True)
            timer_azure = datetime.datetime.now()
            with open(path + "AzureUpdateInfo.py") as azureupdate:
                exec(azureupdate.read())
            delta_time_azure = datetime.datetime.now() - timer_azure
            print("End Azure info updater (AZ - 3E)", delta_time_azure, flush=True)

        # print("Start Azure status checker (Logic - 1S)", flush=True)
        # timer_azure = datetime.datetime.now()
        # with open(path + "AzureStatusChecker.py") as azurestatuschecker:
        #     exec(azurestatuschecker.read())
        # delta_time_azure = datetime.datetime.now() - timer_azure
        # print("End Azure status checker (Logic - 1E)", delta_time_azure, flush=True)

        delta_time_azure_block = datetime.datetime.now() - timer_azure_block
        print("Azure block end", delta_time_azure_block, flush=True)

        azureEndFlag = True

    except Exception as error:
        print("---------------", "WARNING!", end='\n')
        print("Exception on Azure block!")
        print("An exception occurred:", error, flush=True)

        azureEndFlag = True

def mainLogicBlock():
    global sdStatusEndFlag
    global azureStatusEndFlag
    global sdEndFlag
    global azureEndFlag
    while not sdEndFlag and not azureEndFlag and not sdStatusEndFlag and not azureStatusEndFlag:
        time.sleep(60)
        try:
            print("Start Matcher", flush=True)
            timer_logic = datetime.datetime.now()
            with open(path + "AzureSdMatch.py") as match:
                exec(match.read())
            delta_time_logic = datetime.datetime.now() - timer_logic
            print("End Matcher", delta_time_logic, flush=True)
        except Exception as error:
            print("---------------", "WARNING!", end='\n')
            print("Exception on Matcher block!")
            print("An exception occurred:", error, flush=True)

        try:
            print("Initial review", flush=True)
            timer_logic = datetime.datetime.now()
            with open(path + "InitialReview.py") as initial:
                exec(initial.read())
            delta_time_logic = datetime.datetime.now() - timer_logic
            print("End Initial review", delta_time_logic, flush=True)

            print("Initial review backlog", flush=True)
            timer_logic = datetime.datetime.now()
            with open(path + "InitialReviewBacklog.py") as initialBacklog:
                exec(initialBacklog.read())
            delta_time_logic = datetime.datetime.now() - timer_logic
            print("End Initial review backlog", delta_time_logic, flush=True)
            # print("Closed in SD")
            # with open(path + "ClosedInSd.py") as closedsd:
            #     exec(closedsd.read())
            print("Closed in azure")
            timer_logic = datetime.datetime.now()
            with open(path + "ClosedInAzure.py") as closedazure:
                exec(closedazure.read())
            delta_time_logic = datetime.datetime.now() - timer_logic
            print("End Closed in azure", delta_time_logic, flush=True)
        except Exception as error:
            print("---------------", "WARNING!", end='\n')
            print("Exception on Main logic block!")
            print("An exception occurred:", error, flush=True)

while True:
    azureEndFlag = False
    sdEndFlag = False
    sdStatusEndFlag = False
    azureStatusEndFlag = False

    print("Iteration:", iteration)
    iterationStartTime = datetime.datetime.now()

    threadAzure = threading.Thread(target=azureBlock)
    threadSd = threading.Thread(target=sdBlock)
    threadAzureSt = threading.Thread(target=azureStatusesBlock)
    threadSdSt = threading.Thread(target=sdStatusesBlock)
    threadLogic = threading.Thread(target=mainLogicBlock)

    threadAzure.start()
    threadSd.start()
    threadAzureSt.start()
    threadSdSt.start()
    threadLogic.start()

    threadSd.join()
    threadAzure.join()
    threadSdSt.join()
    threadAzureSt.join()
    threadLogic.join()

    iteration = iteration + 1

    wholeTime = datetime.datetime.now() - startTime
    iterationTime = datetime.datetime.now() - iterationStartTime

    print("Iteration time:", iterationTime)
    print("Time from start:", wholeTime, flush=True)
    print("------------------------------------------------------")