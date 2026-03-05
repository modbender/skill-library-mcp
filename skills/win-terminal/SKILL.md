---
name: win-terminal
description: Controls the Windows Terminal to run commands, scripts, and manage processes on Windows. Enables AI agents to execute git, npm, pip, node, and any CLI commands. Use when you need to run terminal commands, manage dev servers, check git status, install dependencies, or automate Windows command-line workflows.
---

# Windows Terminal Control

A skill that enables AI agents to execute shell commands on Windows machines through PowerShell or Windows Terminal. Perfect for automating development workflows without context switching.

## Core Capabilities

- **Run Commands:** Execute any command-line tool or script (`git`, `npm`, `pip`, `node`, `python`, etc.)
- **Capture Output:** Read stdout and stderr from commands with proper encoding support
- **Timeout Protection:** Commands automatically timeout after 30 seconds (configurable) to prevent hangs
- **Working Directory Control:** Execute commands in specific project folders
- **Fallback Support:** Falls back to PowerShell if Windows Terminal is not installed

## Usage

### Basic Command Execution
```powershell
# Check git status
run-command.ps1 -Command "git status" -WorkingDirectory "C:\Users\kanja\projects\my-app"

# Install dependencies
run-command.ps1 -Command "npm install" -WorkingDirectory "C:\Users\kanja\projects\my-app" -TimeoutSeconds 60

# Run a dev server (non-blocking)
run-command.ps1 -Command "npm run dev" -WorkingDirectory "C:\Users\kanja\projects\my-app"
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `Command` | string | required | The command to execute |
| `WorkingDirectory` | string | current directory | Directory to execute command in |
| `TimeoutSeconds` | int | 30 | Maximum time to wait for command |
| `NoGui` | switch | false | Force PowerShell instead of Windows Terminal |

## Security & Limitations

### What This Skill CAN Do
✅ Run standard CLI tools (git, npm, pip, python, node, etc.)  
✅ Execute PowerShell commands  
✅ Read command output and errors  
✅ Operate in any directory you have access to  
✅ Start background processes  
✅ Handle output up to 100KB  

### What This Skill CANNOT Do
❌ Run interactive commands (vim, nano, ssh, etc.)  
❌ Run commands requiring Administrator privileges without approval  
❌ Access other users' files or system directories outside your workspace  
❌ Run indefinitely (30-second default timeout)  
❌ Execute commands with dangerous patterns (sanitization blocks known attack vectors)  

### Security Safeguards
- **Input Sanitization:** Blocks known dangerous patterns (command injection attempts)
- **Timeout Protection:** Prevents hanging commands
- **No Interactive Mode:** Interactive tools are blocked to prevent hangs
- **User Permissions Only:** Operates with your standard Windows user permissions
- **Output Limits:** Large outputs (>100KB) are truncated to prevent memory issues

### Important Notes
- **Not a Sandbox:** Commands run with your actual user permissions. The skill trusts command input.
- **GUI Commands:** Commands that spawn GUI windows may behave unexpectedly
- **Network Commands:** Commands requiring network access may timeout if the network is slow
- **Windows Terminal vs PowerShell:** Prefers Windows Terminal if installed, falls back to PowerShell

## Prerequisites
- Windows 10/11
- PowerShell 5.1 or later
- Windows Terminal (optional, but recommended)
- PowerShell Execution Policy set to `RemoteSigned` (for script execution)

## Troubleshooting

### "Command timed out"
Increase the timeout: `run-command.ps1 -Command "slow-command" -TimeoutSeconds 120`

### "Interactive command detected"
Use non-interactive alternatives:
- Instead of `vim file.txt`, use `Get-Content file.txt`
- Instead of `ssh user@host`, use `ssh user@host "command"`

### "Access denied"
The command may require elevated privileges. OpenClaw will ask for approval if needed.

### "Windows Terminal not found"
The skill automatically falls back to PowerShell. Install Windows Terminal for better experience.

## Examples

```powershell
# Git workflow
run-command.ps1 -Command "git add ." -WorkingDirectory "C:\projects\my-app"
run-command.ps1 -Command "git commit -m 'Update'" -WorkingDirectory "C:\projects\my-app"

# Python development
run-command.ps1 -Command "pip install -r requirements.txt" -WorkingDirectory "C:\projects\my-app" -TimeoutSeconds 120
run-command.ps1 -Command "python manage.py migrate" -WorkingDirectory "C:\projects\my-app"

# Node.js development
run-command.ps1 -Command "npm run build" -WorkingDirectory "C:\projects\my-app" -TimeoutSeconds 60
run-command.ps1 -Command "npm test" -WorkingDirectory "C:\projects\my-app"

# File operations
run-command.ps1 -Command "Get-ChildItem -Recurse -Filter '*.py' | Select-Object Name" -WorkingDirectory "C:\projects\my-app"
```
