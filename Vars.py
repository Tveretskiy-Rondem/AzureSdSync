# Переключатели:
isTest = False
# 0 - no logs; 1 - minimum logs; 2 - full logs
logsLevel = 2

# DB:
# dbCreds = ["postgres", "LqzzPG626!", "192.168.26.26", "5432", "primo"]
dbCreds = ["postgres", "Qwe123!@#", "10.0.0.19", "5432", "primo"]

# SD:
sdService = "sd"
# sdToken = "ae095dff50035a3dd6fd64405de7bf57c1d08e6e"
sdToken = "8f4c0a6edc44f6ac72a016a1182d0e03a260eb0b"
sdUrl = "https://sd.primo-rpa.ru/api/v1/issues/"
sdTableFields = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "assigned_to"]
sdJsonKeys = ["id", "title", "created_at", "completed_at", ["type", "name"], ["priority", "name"], "company_id", ["author", "name"], ["assignee", "name"]]
sdStatusTableFields = ["status", "old_status"]
sdStatusJsonKeys = [["status", "name"], ["old_status", "name"]]
sdCheckUpdateFields = ["completed_at", "type", "priority", "assigned_to"]
sdCheckUpdateJsonKeys = ["completed_at", ["type", "name"], ["priority", "name"], ["assignee", "name"]]

# Azure:
azureService = "azure"
# azureUrl = "https://azure-dos.s1.primo1.orch/PrimoCollection/_apis/wit/workitems"
azureUrl = "https://10.0.2.14/PrimoCollection/_apis/wit/workitems"
azureHeaders = {'Authorization': 'Basic czFcZGV2LWF6dXJlLXNkOmNqcmQ2bjV5YWttY3BmbGt3Y3ljamVrc2hjY2tzeXY1ejZrbmttbG8zMjZqc3JrZnEyb3E='}
# azureTableFields = ["id", "project", "type", "status", "assigned_to", "created_at", "created_by", "title", "sd_issue", "client", "url"]
azureTableFields = ["id", "project", "type", "assigned_to", "created_at", "created_by", "title", "sd_issue", "client", "url"]
azureJsonKeys = ["id", ["fields", "System.AreaPath"], ["fields", "System.WorkItemType"], ["fields", ["System.AssignedTo", "displayName"]], ["fields", "System.CreatedDate"], ["fields", ["System.CreatedBy", "DisplayName"]], ["fields", "System.Title"], ["fields", "Custom.ServiceDesk"], ["fields", "Custom.Client"], "url"]
azureStatusTableFields = ["status"]
azureStatusJsonKeys = [["fields", "System.State"]]
azureCheckUpdateFields = ["project", "type", "assigned_to", "sd_issue"]
azureCheckUpdateJsonKeys = [["fields", "System.AreaPath"], ["fields", "System.WorkItemType"], ["fields", ["System.AssignedTo", "displayName"]], ["fields", "Custom.ServiceDesk"]]
azureWorkItemsRange = [1, 25000]
