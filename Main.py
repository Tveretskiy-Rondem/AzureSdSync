import time

# while True:
#     with open("SdToDb.py") as sdtodb:
#         exec(sdtodb.read())
#     with open("SdDiffChecker.py") as sddiffchecker:
#         exec(sddiffchecker.read())
#     with open("AzureWorkItemsListToDb.py") as azurelistdb:
#         exec(azurelistdb.read())
#     with open("AzureToDb.py") as azuredb:
#         exec(azuredb.read())
#     print("Sleep 120 seconds...")
#     time.sleep(120)

while True:
    with open("/home/ubuntu/AzureSdSync/SdToDb.py") as sdtodb:
        exec(sdtodb.read())
    with open("/home/ubuntu/AzureSdSync/SdDiffChecker.py") as sddiffchecker:
        exec(sddiffchecker.read())
    with open("/home/ubuntu/AzureSdSync/AzureWorkItemsListToDb.py") as azurelistdb:
        exec(azurelistdb.read())
    with open("/home/ubuntu/AzureSdSync/AzureToDb.py") as azuredb:
        exec(azuredb.read())
    print("Sleep 120 seconds...")
    time.sleep(120)