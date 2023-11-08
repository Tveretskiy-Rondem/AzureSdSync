while True:
    with open("SdToDb.py") as sdtodb:
        exec(sdtodb.read())
    with open("SdDiffChecker.py") as sddiffchecker:
        exec(sddiffchecker.read())
    with open("AzureWorkItemsListToDb.py") as azurelistdb:
        exec(azurelistdb.read())
    with open("AzureToDb.py") as azuredb:
        exec(azuredb.read())