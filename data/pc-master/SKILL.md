---
name: pc-master
description: Control the Windows PC from WSL2. Use when the user asks to open/close applications, manage processes, take screenshots, control windows, manage files on Windows (C:\), automate tasks, or do anything that requires interacting with the Windows host from WSL2 (e.g. "open Chrome", "kill Spotify", "take a screenshot", "list running apps", "move a file on Windows").
---

# PC Master — Windows Control from WSL2

All Windows binaries are accessible via `/mnt/c/Windows/System32/`. Call them directly from bash.

## Prerequisites

WSL2 interop must be working. If `.exe` calls fail with `UtilAcceptVsock` errors, ask the user to run `wsl --shutdown` in Windows and relaunch WSL.

## Core Commands

### Processes
```bash
# List all processes
/mnt/c/Windows/System32/tasklist.exe

# Filter by name
/mnt/c/Windows/System32/tasklist.exe /FI "IMAGENAME eq chrome.exe"

# Kill by name
/mnt/c/Windows/System32/taskkill.exe /F /IM chrome.exe

# Kill by PID
/mnt/c/Windows/System32/taskkill.exe /F /PID 1234
```

### Launch Applications
```bash
# Open a URL in default browser
/mnt/c/Windows/System32/cmd.exe /c "start https://google.com"

# Open an app by name
/mnt/c/Windows/System32/cmd.exe /c "start chrome"
/mnt/c/Windows/System32/cmd.exe /c "start spotify"
/mnt/c/Windows/System32/cmd.exe /c "start notepad"

# Open a file with its default app
/mnt/c/Windows/System32/cmd.exe /c "start C:\\Users\\User\\file.pdf"

# Launch full path
/mnt/c/Windows/System32/cmd.exe /c "start \"\" \"C:\\Program Files\\App\\app.exe\""
```

> ⚠️ `cmd.exe /c start` must be run from a Windows path. Use `/mnt/c/Windows/System32/cmd.exe /c "cd /d C:\ && start ..."` if cwd is a UNC path (WSL path).

### PowerShell (advanced)
```bash
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe

# Run a command
$PS -NonInteractive -Command "Get-Process | Select-Object -First 10"

# Get window titles
$PS -NonInteractive -Command "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object Name, MainWindowTitle"

# Set volume
$PS -NonInteractive -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
```

### Screenshot
```bash
# Take a screenshot and save to Windows desktop
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
$PS -NonInteractive -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen | ForEach-Object { \$bmp = New-Object System.Drawing.Bitmap(\$_.Bounds.Width, \$_.Bounds.Height); \$g = [System.Drawing.Graphics]::FromImage(\$bmp); \$g.CopyFromScreen(\$_.Bounds.Location, [System.Drawing.Point]::Empty, \$_.Bounds.Size); \$bmp.Save('C:\\screenshot.png') }"
```

### File System (Windows paths)
```bash
# Windows C:\ is at /mnt/c/ in WSL
ls /mnt/c/Users/
cat /mnt/c/Users/Username/Desktop/file.txt
cp /mnt/c/Users/Username/Downloads/file.zip /mnt/c/Users/Username/Desktop/

# Find Windows username
ls /mnt/c/Users/ | grep -v "Public\|Default\|All Users"
```

### System Info
```bash
# Windows version
/mnt/c/Windows/System32/cmd.exe /c "ver"

# Disk usage
/mnt/c/Windows/System32/cmd.exe /c "wmic logicaldisk get size,freespace,caption"

# Network info
/mnt/c/Windows/System32/ipconfig.exe
```

## Common Patterns

**Close and reopen an app:**
```bash
/mnt/c/Windows/System32/taskkill.exe /F /IM chrome.exe
sleep 2
/mnt/c/Windows/System32/cmd.exe /c "start chrome"
```

**Check if app is running:**
```bash
/mnt/c/Windows/System32/tasklist.exe /FI "IMAGENAME eq spotify.exe" | grep -i spotify && echo "Running" || echo "Not running"
```

**Open a specific website:**
```bash
/mnt/c/Windows/System32/cmd.exe /c "start https://www.google.com"
```

## Notes
- Output may contain garbled characters (Windows encoding vs UTF-8) — this is normal, content is still readable
- Some GUI apps launched via `start` won't produce output — that's expected
- For interactive PowerShell scripts, write to a temp file and read it back instead of capturing stdout directly
- See `references/windows-apps.md` for common app executable names
