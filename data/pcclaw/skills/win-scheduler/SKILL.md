---
name: win-scheduler
description: Windows Task Scheduler — create, list, manage, and delete scheduled tasks for automated workflows, zero dependencies.
metadata:
  {
    "openclaw":
      {
        "emoji": "⏰",
        "os": ["win32"],
      },
  }
---

# win-scheduler

Create and manage Windows scheduled tasks. Schedule one-time reminders, recurring automations, or startup tasks. Uses built-in ScheduledTasks PowerShell module.

Works on Windows 10/11. No external dependencies.

## List All Tasks

Lists non-Microsoft scheduled tasks (user/app tasks):

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-ScheduledTask | Where-Object { $_.TaskPath -notmatch '\\Microsoft\\' } | ForEach-Object {
    $info = Get-ScheduledTaskInfo -InputObject $_ -ErrorAction SilentlyContinue
    $next = if ($info.NextRunTime -and $info.NextRunTime.Year -gt 2000) { $info.NextRunTime.ToString('yyyy-MM-dd HH:mm') } else { '-' }
    Write-Host ('{0,-40} {1,-10} Next: {2}' -f $_.TaskName, $_.State, $next)
}
"
```

### List All Tasks (Including Microsoft)

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$tasks = Get-ScheduledTask
$tasks | Group-Object State | ForEach-Object {
    Write-Host ('{0}: {1}' -f $_.Name, $_.Count)
}
Write-Host ('Total: {0}' -f $tasks.Count)
"
```

### List Tasks in a Folder

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-ScheduledTask -TaskPath '\FOLDER_PATH\' | Select-Object TaskName, State | Format-Table -AutoSize
"
```

Replace `FOLDER_PATH` with the task folder (e.g., `PCClaw`, `Lenovo`).

## Get Task Details

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$task = Get-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\'
$info = Get-ScheduledTaskInfo -InputObject $task

Write-Host ('Name:        ' + $task.TaskName)
Write-Host ('Path:        ' + $task.TaskPath)
Write-Host ('State:       ' + $task.State)
Write-Host ('Description: ' + $task.Description)
Write-Host ('Last Run:    ' + $info.LastRunTime)
Write-Host ('Next Run:    ' + $info.NextRunTime)
Write-Host ('Last Result: ' + $info.LastTaskResult)
Write-Host ''
Write-Host '--- Triggers ---'
$task.Triggers | ForEach-Object {
    $type = $_.CimClass.CimClassName -replace 'MSFT_Task', '' -replace 'Trigger', ''
    Write-Host ('  Type: {0}, Start: {1}, Enabled: {2}' -f $type, $_.StartBoundary, $_.Enabled)
}
Write-Host ''
Write-Host '--- Actions ---'
$task.Actions | ForEach-Object {
    Write-Host ('  Execute: {0}' -f $_.Execute)
    Write-Host ('  Args:    {0}' -f $_.Arguments)
}
"
```

Replace `TASK_NAME` and `TASK_PATH` (e.g., `\` for root, `\PCClaw\` for PCClaw folder).

## Create One-Time Task

Runs a command once at a specific date/time:

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'PROGRAM' -Argument 'ARGUMENTS'
$trigger = New-ScheduledTaskTrigger -Once -At 'DATETIME'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
Write-Host 'Task created: TASK_NAME at DATETIME'
"
```

- `PROGRAM`: executable to run (e.g., `powershell.exe`, `notepad.exe`)
- `ARGUMENTS`: command-line arguments (e.g., `-NoProfile -Command "..."`)
- `DATETIME`: when to run (e.g., `2026-02-15 09:00`, `2026-03-01T14:30`)
- `TASK_NAME`: name for the task
- `DESCRIPTION`: what the task does

### Example: Reminder in 30 Minutes

```powershell
powershell.exe -NoProfile -Command "
$time = (Get-Date).AddMinutes(30)
$msg = 'REMINDER_TEXT'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(''{0}'', ''PCClaw Reminder'', ''OK'', ''Information'')\"' -f $msg)
$trigger = New-ScheduledTaskTrigger -Once -At $time
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'PCClaw-Reminder' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description $msg
Write-Host ('Reminder set for ' + $time.ToString('HH:mm'))
"
```

Replace `REMINDER_TEXT` with the reminder message.

### Example: Run PowerShell Script at Specific Time

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -ExecutionPolicy Bypass -File \"SCRIPT_PATH\"'
$trigger = New-ScheduledTaskTrigger -Once -At 'DATETIME'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
"
```

## Create Daily Task

Runs every day at a specified time:

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'PROGRAM' -Argument 'ARGUMENTS'
$trigger = New-ScheduledTaskTrigger -Daily -At 'TIME'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
Write-Host 'Daily task created: TASK_NAME at TIME every day'
"
```

- `TIME`: time of day (e.g., `09:00`, `17:30`, `06:00AM`)

### Every N Days

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'PROGRAM' -Argument 'ARGUMENTS'
$trigger = New-ScheduledTaskTrigger -Daily -DaysInterval INTERVAL -At 'TIME'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
"
```

Replace `INTERVAL` with number of days (e.g., `2` for every other day, `7` for weekly).

## Create Weekly Task

Runs on specific days of the week:

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'PROGRAM' -Argument 'ARGUMENTS'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek DAY_LIST -At 'TIME'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
"
```

- `DAY_LIST`: comma-separated days (e.g., `Monday,Wednesday,Friday` or `Sunday`)

## Create Logon Task

Runs when the user logs in:

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'PROGRAM' -Argument 'ARGUMENTS'
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
Write-Host 'Logon task created: TASK_NAME'
"
```

## Create Startup Task

Runs when the computer starts (before logon):

```powershell
powershell.exe -NoProfile -Command "
$action = New-ScheduledTaskAction -Execute 'PROGRAM' -Argument 'ARGUMENTS'
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\PCClaw\' -Action $action -Trigger $trigger -Settings $settings -Description 'DESCRIPTION'
Write-Host 'Startup task created: TASK_NAME'
"
```

Note: Startup tasks may require admin privileges depending on what they execute.

## Run Task Now

Manually trigger an existing task immediately:

```powershell
powershell.exe -NoProfile -Command "
Start-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\'
Write-Host 'Task triggered: TASK_NAME'
"
```

## Stop Running Task

```powershell
powershell.exe -NoProfile -Command "
Stop-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\'
Write-Host 'Task stopped: TASK_NAME'
"
```

## Enable / Disable Task

```powershell
powershell.exe -NoProfile -Command "
Enable-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\' | Out-Null
Write-Host 'Task enabled: TASK_NAME'
"
```

```powershell
powershell.exe -NoProfile -Command "
Disable-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\' | Out-Null
Write-Host 'Task disabled: TASK_NAME'
"
```

## Delete Task

```powershell
powershell.exe -NoProfile -Command "
Unregister-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\' -Confirm:`$false
Write-Host 'Task deleted: TASK_NAME'
"
```

## List PCClaw Tasks

List only tasks created by PCClaw (stored in `\PCClaw\` folder):

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$tasks = Get-ScheduledTask -TaskPath '\PCClaw\' -ErrorAction SilentlyContinue
if (-not $tasks) {
    Write-Host 'No PCClaw scheduled tasks found.'
} else {
    foreach ($task in $tasks) {
        $info = Get-ScheduledTaskInfo -InputObject $task -ErrorAction SilentlyContinue
        $next = if ($info.NextRunTime -and $info.NextRunTime.Year -gt 2000) { $info.NextRunTime.ToString('yyyy-MM-dd HH:mm') } else { '-' }
        $last = if ($info.LastRunTime -and $info.LastRunTime.Year -gt 2000) { $info.LastRunTime.ToString('yyyy-MM-dd HH:mm') } else { 'never' }
        Write-Host ('{0}' -f $task.TaskName)
        Write-Host ('  State: {0} | Last: {1} | Next: {2}' -f $task.State, $last, $next)
        Write-Host ('  {0}' -f $task.Description)
    }
}
"
```

## Delete All PCClaw Tasks

Remove all tasks in the `\PCClaw\` folder:

```powershell
powershell.exe -NoProfile -Command "
$tasks = Get-ScheduledTask -TaskPath '\PCClaw\' -ErrorAction SilentlyContinue
if (-not $tasks) {
    Write-Host 'No PCClaw tasks to remove.'
} else {
    $count = 0
    foreach ($task in $tasks) {
        Unregister-ScheduledTask -InputObject $task -Confirm:`$false
        Write-Host ('  Removed: ' + $task.TaskName)
        $count++
    }
    Write-Host ('{0} task(s) removed.' -f $count)
}
"
```

## Export Task (XML)

Export a task definition to XML (for backup or transfer):

```powershell
powershell.exe -NoProfile -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$xml = Export-ScheduledTask -TaskName 'TASK_NAME' -TaskPath '\TASK_PATH\'
$xml
"
```

## Common Workflows

### Set a timed reminder

```
1. win-scheduler: create one-time task with MessageBox action
2. Task fires at the specified time → popup appears
3. Optionally combine with win-notify for toast notification instead
```

### Daily morning briefing

```
1. win-scheduler: create daily task at 09:00
2. Action runs a PowerShell script that:
   - Checks weather (via web request)
   - Lists today's calendar events
   - Shows unread notifications
3. Combine with win-tts to read it aloud
```

### Auto-backup files weekly

```
1. win-scheduler: create weekly task (e.g., every Sunday at 02:00)
2. Action runs a PowerShell script that:
   - Uses win-files to copy important folders
   - Compresses to a timestamped archive
   - Sends win-notify when done
```

### Launch app at login

```
1. win-scheduler: create logon task
2. Action: Start-Process for the desired application
3. Runs automatically every time the user logs in
```

### Periodic system health check

```
1. win-scheduler: create daily task
2. Action runs win-sysinfo to check CPU, RAM, battery
3. Logs results or sends win-notify if anomalies detected
```

## Notes

- **Task folder**: PCClaw tasks are organized under `\PCClaw\` in Task Scheduler for easy management. Use Task Scheduler GUI (`taskschd.msc`) to browse.
- **Permissions**: Creating tasks for the current user works without admin. System-wide tasks (AtStartup, running as SYSTEM) may require elevation.
- **Battery**: All examples include `-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries` so tasks run on laptops.
- **Trigger types**: Once, Daily, Weekly, AtLogOn, AtStartup. For more complex schedules (monthly, event-based), use `schtasks.exe` or the Task Scheduler GUI.
- **Multiple triggers**: A single task can have multiple triggers — pass an array to the `-Trigger` parameter.
- **Working directory**: Add `-WorkingDirectory 'PATH'` to `New-ScheduledTaskAction` if the script needs a specific directory.
- **Hidden window**: Add `-WindowStyle Hidden` to PowerShell arguments to run silently.
- **Task Scheduler GUI**: Open with `taskschd.msc` or `Start-Process taskschd.msc`.
