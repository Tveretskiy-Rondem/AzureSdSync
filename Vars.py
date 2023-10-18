# DB:
dbCreds = ["postgres", "postgres", "192.168.26.26", "5432", "SD"]

# SD:
sdService = "sd"
sdToken = "ae095dff50035a3dd6fd64405de7bf57c1d08e6e"
sdUrl = "https://sd.primo-rpa.ru/api/v1/issues/"
sdTableFields = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "assigned_at"]
sdJsonKeys = ["id", "title", "created_at", "completed_at", ["type", "name"], ["priority", "name"], "company_id", ["author", "name"], ["assignee", "name"]]
sdStatusTableFields = ["status", "old_status"]
sdStatusJsonKeys = [["status", "name"], ["old_status", "name"]]

# Azure:
azureService = "azure"
azureUrl = "https://azure-dos.s1.primo1.orch/PrimoCollection/_apis/wit/workitems"
azureHeaders = {'Authorization': 'Basic czFcYXR2ZXJldHNraXk6aHppaGhwbXdxamNoNjQ2NnhqN280cGJkbzcycTN5NDVpNTIzdmV0dmtkdmR0ZXJuc25ocQ=='}
azureTableFields = ["id", "project", "type", "status", "assigned_to", "created_at", "created_by", "title", "sd_issue", "client", "url"]
azureJsonKeys = ["id", ["fields", "System.AreaPath"], ["fields", "System.WorkItemType"], ["fields", "System.State"], ["fields", ["System.AssignedTo", "displayName"]], ["fields", "System.CreatedDate"], ["fields", ["System.CreatedBy", "DisplayName"]], ["fields", "System.Title"], ["fields", "Custom.ServiceDesk"], ["fields", "Custom.Client"], "url"]
azureWorkItemsRange = [1, 15000]

# azureJsonKeys = ["id"]
# azureHeaders = {'Authorization': 'Basic czFcYXR2ZXJldHNraXk6aHppaGhwbXdxamNoNjQ2NnhqN280cGJkbzcycTN5NDVpNTIzdmV0dmtkdmR0ZXJuc25ocQ==', 'Cookie': '__RequestVerificationToken=XOAvv89CrU2ZLjTd6rS6hnVJrwGhm0vOjLYlCjrgAXf_P3gg7Gl_s_kWfdh8XHLNuUpjumN0wzoCyTfOPGGnoGrg0shVJDj1OgJONY3RQXo1; __RequestVerificationToken23cee1b27-a61e-46de-9f45-791afa9423e4=XOAvv89CrU2ZLjTd6rS6hnVJrwGhm0vOjLYlCjrgAXf_P3gg7Gl_s_kWfdh8XHLNuUpjumN0wzoCyTfOPGGnoGrg0shVJDj1OgJONY3RQXo1'}

# sdTableFields = ["id", "title", "created_at", "completed_at", "type", "priority", "company_id", "author", "responsible", "status"]
# sdJsonKeys = ["id", "title", "created_at", "completed_at", ["type", "name"], ["priority", "name"], "company_id", ["author", "name"], ["assignee", "name"], ["status", "name"]]