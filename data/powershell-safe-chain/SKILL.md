---
name: powershell-safe-chain
description: Chain PowerShell commands safely without &&. Use try/catch, ErrorAction, and proper sequencing for reliable Windows execution.
---

# PowerShell Safe Chain

Chain commands reliably on Windows PowerShell. No `&&` anti-patterns.

## Problem

PowerShell differs from bash:
- `&&` does NOT work for command chaining
- Parameter parsing is case-insensitive but strict
- Errors continue by default (no fail-fast)
- Path separators vary (`\` vs `/`)

## Workflow

### 1. Safe Chaining Pattern

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
    Write-Error "Failed at step: $_"
    exit 1
}
```

### 2. Conditional Chaining

```powershell
# If-then pattern
if (Test-Path $file) {
    Remove-Item $file
    Write-Host "Deleted"
} else {
    Write-Warning "File not found"
}

# Pipeline with error handling
Get-Process | Where-Object CPU -GT 100 | Stop-Process -WhatIf
```

### 3. Splatting for Complex Commands

```powershell
$params = @{
    Path = $filePath
    Encoding = 'UTF8'
    Force = $true
}
Set-Content @params
```

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| No `&&` in scripts | `Select-String '&&' *.ps1` returns nothing |
| ErrorAction set | `Select-String 'ErrorAction' *.ps1` matches |
| try/catch present | `Select-String 'try|catch' *.ps1` matches |
| Paths use Join-Path | `Select-String 'Join-Path' *.ps1` matches |

## Privacy/Safety

- No hardcoded credentials
- Use `[SecureString]` for passwords
- Environment variables via `$env:VAR`

## Self-Use Trigger

Use when:
- Writing any PowerShell script
- Chaining 2+ commands
- Executing file operations

---

**Chain safely. Fail explicitly.**
