---
name: powershell-reliable
description: Execute PowerShell commands reliably on Windows. Avoid &&, handle parameter parsing, recover from interruptions, and ensure cross-session continuity.
---

# PowerShell Reliable Execution

Execute commands reliably on Windows PowerShell. Avoid common pitfalls like `&&` chaining, parameter swallowing, and session interruptions.

## Problem Statement

Windows PowerShell differs from bash in critical ways:

| Issue | Bash | PowerShell | Solution |
|-------|------|------------|----------|
| Command chaining | `cmd1 && cmd2` | `cmd1 -ErrorAction Stop; if ($?) { cmd2 }` | Use semicolons + error handling |
| Parameter parsing | `-arg value` | `-Argument value` (case-insensitive) | Use full parameter names |
| Path separators | `/` | `\` (or `/` in some cmdlets) | Use `Join-Path` |
| Output redirection | `>` `>>` | `>` `>>` (encoding issues) | Use `Out-File -Encoding UTF8` |
| Environment vars | `$VAR` | `$env:VAR` | Use `$env:` prefix |

## Core Patterns

### 1. Safe Command Chaining

**Wrong**:
```powershell
mkdir test && cd test && echo done
```

**Right**:
```powershell
$ErrorActionPreference = 'Stop'
try {
    New-Item -ItemType Directory -Path test -Force
    Set-Location test
    Write-Host 'done'
} catch {
    Write-Error "Failed: $_"
    exit 1
}
```

### 2. Parameter Safety

**Wrong**:
```powershell
git commit -m "message"
```

**Right**:
```powershell
git commit -Message "message"
# Or use splatting:
$params = @{ Message = "message" }
git commit @params
```

### 3. Path Handling

**Wrong**:
```powershell
$path = "C:/Users/name/file.txt"
```

**Right**:
```powershell
$path = Join-Path $env:USERPROFILE "file.txt"
# Or use literal paths:
$path = 'C:\Users\name\file.txt'
```

### 4. Output Encoding

**Wrong**:
```powershell
echo "text" > file.txt
```

**Right**:
```powershell
"text" | Out-File -FilePath file.txt -Encoding UTF8
```

### 5. Session Continuity

For long-running commands:

```powershell
# Start background job
$job = Start-Job -ScriptBlock {
    param($arg)
    # Long operation
} -ArgumentList $arg

# Wait with timeout
Wait-Job $job -Timeout 300

# Get results
if ($job.State -eq 'Completed') {
    Receive-Job $job
} else {
    Stop-Job $job
    Write-Warning "Job timed out"
}
```

## Error Recovery

### Retry Pattern

```powershell
function Invoke-Retry {
    param(
        [scriptblock]$Command,
        [int]$MaxAttempts = 3,
        [int]$DelaySeconds = 2
    )
    
    $attempt = 0
    while ($attempt -lt $MaxAttempts) {
        try {
            $attempt++
            return & $Command
        } catch {
            if ($attempt -eq $MaxAttempts) { throw }
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

# Usage
Invoke-Retry -Command { Invoke-WebRequest -Uri $url } -MaxAttempts 3
```

### Interruption Recovery

```powershell
# Checkpoint pattern
$checkpointFile = ".checkpoint.json"

if (Test-Path $checkpointFile) {
    $state = Get-Content $checkpointFile | ConvertFrom-Json
    Write-Host "Resuming from step $($state.step)"
} else {
    $state = @{ step = 0 }
}

switch ($state.step) {
    0 { 
        # Step 1
        $state.step = 1
        $state | ConvertTo-Json | Out-File $checkpointFile
    }
    1 {
        # Step 2
        Remove-Item $checkpointFile
    }
}
```

## Privacy Security

**All execution is local**:
- NO command logging to external services
- NO credential capture in scripts
- NO automatic upload of execution results
- Sensitive data handled via `[SecureString]`
- Checkpoint files stored in working directory only

**Sensitive Data Filter**:
Before writing any checkpoint or log:
- Exclude `Password`, `Token`, `Secret`, `ApiKey`
- Use `[SecureString]` for credentials
- Never echo sensitive variables

## Executable Completion Criteria

A PowerShell command execution is reliable if and only if:

| Criteria | Verification |
|----------|-------------|
| No `&&` chaining | `Select-String '&&' script.ps1` returns nothing |
| Error handling present | `Select-String 'try|catch|ErrorAction' script.ps1` matches |
| Paths use Join-Path | `Select-String 'Join-Path|\\$env:' script.ps1` matches |
| Output encoding specified | `Select-String 'Out-File.*Encoding' script.ps1` matches |
| Checkpoint for long ops | Checkpoint file pattern present for ops > 60s |
| No hardcoded secrets | `Select-String 'password|token|secret' script.ps1` returns nothing |

## Quick Reference

### Common Cmdlet Mappings

| Task | Bash | PowerShell |
|------|------|------------|
| List files | `ls -la` | `Get-ChildItem -Force` |
| Change dir | `cd /path` | `Set-Location C:\path` |
| Create dir | `mkdir x` | `New-Item -ItemType Directory x` |
| Copy file | `cp a b` | `Copy-Item a b` |
| Move file | `mv a b` | `Move-Item a b` |
| Delete | `rm x` | `Remove-Item x` |
| View file | `cat x` | `Get-Content x` |
| Edit file | `vim x` | `notepad x` |
| Find text | `grep x` | `Select-String x` |
| Pipe | `\|` | `\|` (same) |
| Redirect | `>` | `>` (use Out-File) |

### Splatting Template

```powershell
$params = @{
    Path = $filePath
    Encoding = 'UTF8'
    Force = $true
}
Set-Content @params
```

## References

- `references/privacy-checklist.md` - Privacy security checklist
- Microsoft Docs: [PowerShell Best Practices](https://docs.microsoft.com/powershell)

---

**Execute reliably. Recover gracefully.**
