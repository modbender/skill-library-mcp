# Plutio PowerShell 7 Workflows

Complete examples using PowerShell 7 for common Plutio task management workflows.

## Setup & Environment Variables

Store credentials securely. PowerShell 7 will cache the access token locally (~1 hour).

```powershell
# Set environment variables (for your session)
$env:PLUTIO_SUBDOMAIN = "grewing"
$env:PLUTIO_APP_KEY = "your_app_key_here"
$env:PLUTIO_SECRET = "your_secret_here"

# Or use inline in each command - See examples below
```

## Workflow 1: Check Today's Tasks

List all open tasks due today:

```powershell
$projectId = "your_project_id"
$today = Get-Date -Format "yyyy-MM-dd"

# Get all open tasks in a project
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-tasks `
  --project-id $projectId `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET `
  --status open `
  --json | ConvertFrom-Json | Where-Object { $_.dueDate -like "$today*" }
```

## Workflow 2: Create a Task from Variables

Programmatically create a task with dynamic values:

```powershell
$projectId = "your_project_id"
$taskTitle = "New Task: $(Get-Date -Format 'ddd, MMM d')"
$dueDate = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")

python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py create-task `
  --project-id $projectId `
  --title $taskTitle `
  --description "Automatically created task" `
  --due-date $dueDate `
  --priority "medium" `
  --status "open" `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET
```

## Workflow 3: Batch Close Tasks

Close all high-priority tasks in a project:

```powershell
$projectId = "your_project_id"

# Get all high-priority open tasks
$tasks = python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-tasks `
  --project-id $projectId `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET `
  --json | ConvertFrom-Json | Where-Object { $_.priority -eq "high" }

# Close each task
foreach ($task in $tasks) {
  Write-Host "Closing: $($task.title)"
  python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py update-task `
    --task-id $task._id `
    --status "closed" `
    --subdomain grewing `
    --app-key $env:PLUTIO_APP_KEY `
    --secret $env:PLUTIO_SECRET
}
```

## Workflow 4: Find and Assign Task to Person

Search for a person by name, then assign a task:

```powershell
$projectId = "your_project_id"
$taskId = "your_task_id"
$searchName = "John"

# List all people and find by name
$person = python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-people `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET `
  --json | ConvertFrom-Json | Where-Object { $_.name.first -eq $searchName } | Select-Object -First 1

if ($person) {
  Write-Host "Found: $($person.name.first) $($person.name.last) ($($person._id))"
  
  # Assign task
  python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py update-task `
    --task-id $taskId `
    --assignee-id $person._id `
    --subdomain grewing `
    --app-key $env:PLUTIO_APP_KEY `
    --secret $env:PLUTIO_SECRET
} else {
  Write-Host "Person not found: $searchName"
}
```

## Workflow 5: Daily Task Summary to Console

Get a daily briefing of all tasks (overdue, due today, due this week):

```powershell
$projectId = "your_project_id"
$today = Get-Date
$nextWeek = $today.AddDays(7)

# Get all tasks
$tasks = python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-tasks `
  --project-id $projectId `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET `
  --json | ConvertFrom-Json

# Categorize
$overdue = $tasks | Where-Object { [datetime]$_.dueDate -lt $today }
$dueToday = $tasks | Where-Object { [datetime]$_.dueDate -like "$($today.ToString('yyyy-MM-dd'))*" }
$dueThisWeek = $tasks | Where-Object { 
  $d = [datetime]$_.dueDate
  $d -ge $today -and $d -le $nextWeek 
}

Write-Host "━━━ PLUTIO DAILY BRIEFING ━━━`n"

if ($overdue) {
  Write-Host "🔴 OVERDUE:" -ForegroundColor Red
  $overdue | ForEach-Object { Write-Host "  • $($_.title) (was due $($_.dueDate.Split('T')[0]))" }
}

if ($dueToday) {
  Write-Host "`n🟡 DUE TODAY:" -ForegroundColor Yellow
  $dueToday | ForEach-Object { Write-Host "  • $($_.title)" }
}

if ($dueThisWeek) {
  Write-Host "`n🟢 DUE THIS WEEK:" -ForegroundColor Green
  $dueThisWeek | ForEach-Object { Write-Host "  • $($_.title) (due $($_.dueDate.Split('T')[0]))" }
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Workflow 6: List All Projects with Task Count

Get a summary of projects and how many tasks each has:

```powershell
# Get all projects
$projects = python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-projects `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET `
  --json | ConvertFrom-Json

Write-Host "📋 PROJECTS SUMMARY`n"

foreach ($project in $projects) {
  # Get task count for this project
  $tasks = python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-tasks `
    --project-id $project._id `
    --subdomain grewing `
    --app-key $env:PLUTIO_APP_KEY `
    --secret $env:PLUTIO_SECRET `
    --json | ConvertFrom-Json
  
  $taskCount = if ($tasks -is [array]) { $tasks.Count } else { 1 }
  Write-Host "$($project.name): $taskCount tasks"
}
```

## Workflow 7: Update Multiple Task Fields at Once

Update a task with multiple fields in one call:

```powershell
$taskId = "your_task_id"

python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py update-task `
  --task-id $taskId `
  --status "in_progress" `
  --priority "high" `
  --due-date "2026-03-20" `
  --description "Updated description with more details" `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET
```

## Workflow 8: Create Task with Custom Fields

Add a task with custom field values:

```powershell
$projectId = "your_project_id"

# Custom fields as JSON (replace with your field IDs)
$customFields = ConvertTo-Json @{
  "field_id_1" = "value1"
  "field_id_2" = "value2"
}

python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py create-task `
  --project-id $projectId `
  --title "Task with Custom Data" `
  --description "Task containing custom field data" `
  --priority "medium" `
  --custom-fields $customFields `
  --subdomain grewing `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET
```

## Workflow 9: Scheduled Daily Check (Windows Task Scheduler)

Create a PowerShell script and schedule it with Windows Task Scheduler:

**File: `C:\Scripts\plutio-daily-check.ps1`**
```powershell
# Plutio Daily Check Script
$env:PLUTIO_SUBDOMAIN = "grewing"
$env:PLUTIO_APP_KEY = "your_app_key"
$env:PLUTIO_SECRET = "your_secret"

# Run the daily briefing workflow
& "C:\Scripts\plutio-daily-briefing.ps1"

# Optional: Log to file
Add-Content -Path "C:\Logs\plutio.log" -Value "$(Get-Date): Daily check completed"
```

**To schedule (PowerShell as Admin):**
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\Scripts\plutio-daily-check.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Plutio-Daily-Check" -Description "Check Plutio tasks daily"
```

## Error Handling in PowerShell

### Check Command Success
```powershell
$result = python3 ... 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "Error occurred!" -ForegroundColor Red
  Write-Host $result
} else {
  Write-Host "Success!" -ForegroundColor Green
}
```

### Parse and Handle JSON Errors
```powershell
try {
  $tasks = python3 ... `
    --json | ConvertFrom-Json
} catch {
  Write-Host "Failed to parse response: $_" -ForegroundColor Red
}
```

### Retry Logic
```powershell
$maxRetries = 3
$retry = 0

while ($retry -lt $maxRetries) {
  try {
    $result = python3 ... --json | ConvertFrom-Json
    break
  } catch {
    $retry++
    if ($retry -lt $maxRetries) {
      Write-Host "Retry $retry/$maxRetries..."
      Start-Sleep -Seconds 5
    }
  }
}
```

## Performance Tips

- **Batch operations**: Use loops to process multiple items instead of individual calls
- **Cache results**: Store `list-projects` results in variables to avoid repeated calls
- **JSON parsing**: Use `ConvertFrom-Json` only when needed
- **Error suppression**: Add `2>$null` to suppress error output if expected

---

*Last updated: 2026-03-01*
