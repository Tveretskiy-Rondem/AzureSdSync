import Vars

def message(fileName, position, addMessage):
    if fileName == "AzureDiffChecker":
        if position == "start":
            print("Start process: AzureDiffChecker")
    elif fileName == "AzureSdMatch":
        if position == "start":
            print("Start process: AzureSdMatch")
        elif position == "10":
            print("Sd issue id not matched. Adding:", addMessage)
    elif fileName == "AzureUpdateInfo":
        if position == "start":
            print("Start process: AzureUpdateInfo")
        elif position == "10":
            print("Processing work item:", addMessage)
        elif position == "20":
            print("No information about work item", addMessage)
            print("Adding information to DB...")