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
    # try:
    #     print("SD to DB")
    #     with open(path + "SdToDb.py") as sdtodb:
    #         exec(sdtodb.read())
    #     print("SD status checker")
    #     with open(path + "SdStatusChecker.py") as statuschecker:
    #         exec(statuschecker.read())
    #     print("SD info updater")
    #     with open(path + "SdUpdateInfo.py") as sdupdate:
    #         exec(sdupdate.read())
    # except Exception as error:
    #     print("---------------", "WARNING!", end='\n')
    #     print("Exception on SD block!")
    #     print("An exception occurred:", error)
    #
    # try:
    #     print("Azure work items list to DB")
    #     with open(path + "AzureWorkItemsListToDb.py") as azurelistdb:
    #         exec(azurelistdb.read())
    #     print("Azure work items content to DB")
    #     with open(path + "AzureToDb.py") as azuretodb:
    #         exec(azuretodb.read())
    #     print("Azure info updater")
    #     with open(path + "AzureUpdateInfo.py") as azureupdate:
    #         exec(azureupdate.read())
    #     print("Azure status checker")
    #     with open(path + "AzureStatusChecker.py") as azurestatuschecker:
    #         exec(azurestatuschecker.read())
    #     print("Matcher")
    #     with open(path + "AzureSdMatch.py") as match:
    #         exec(match.read())
    # except Exception as error:
    #     print("---------------", "WARNING!", end='\n')
    #     print("Exception on Azure block!")
    #     print("An exception occurred:", error)


    print("Initial review")
    with open(path + "InitialReview.py") as initial:
        exec(initial.read())
    # print("Closed in SD")
    # with open(path + "ClosedInSd.py") as closedsd:
    #     exec(closedsd.read())
    # print("Closed in azure")
    # with open(path + "ClosedInAzure.py") as closedazure:
    #     exec(closedazure.read())

        print("---------------", "WARNING!", end='\n')
        print("Exception on Main logic block!")
        print("An exception occurred:", error)

    iteration = iteration + 1

    if isTest:
        break