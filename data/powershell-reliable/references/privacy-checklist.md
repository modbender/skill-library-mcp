# Privacy Security Checklist

Before using or publishing PowerShell scripts, complete these checks:

## File Scan

```powershell
# Scan for sensitive patterns
Get-ChildItem . -Recurse -Include *.ps1,*.psm1 | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match 'password|token|secret|apikey|credential') {
        Write-Warning "Sensitive pattern: $($_.FullName)"
    }
}
```

## Checklist

- [ ] No hardcoded passwords in scripts
- [ ] No API keys or tokens in plain text
- [ ] No personal paths (C:\Users\{name}\...)
- [ ] No email addresses or phone numbers
- [ ] Credentials use [SecureString] or environment variables
- [ ] Checkpoint files don't contain sensitive data
- [ ] Logs exclude sensitive variables

## Allowed Content

- Generic command examples
- Public API endpoints (official docs)
- Environment variable references ($env:VAR)
- Relative paths

## Forbidden Content

- Actual credentials or secrets
- User-specific absolute paths
- Personal identifiable information
- Internal service URLs

## Pre-Publish Verification

```powershell
# Run check
$files = Get-ChildItem . -Recurse -Include *.ps1,*.psm1,*.md
foreach ($f in $files) {
    $c = Get-Content $f.FullName -Raw
    if ($c -match '(?i)password\s*=|token\s*=|secret\s*=') {
        throw "Hardcoded secret detected: $($f.FullName)"
    }
}
Write-Host "Privacy check passed"
```

## Secure Credential Pattern

```powershell
# Use SecureString for passwords
$securePwd = Read-Host "Enter password" -AsSecureString
$cred = New-Object System.Management.Automation.PSCredential($user, $securePwd)

# Or use environment variables
$apiKey = $env:MY_API_KEY  # Set externally, not in script
```

## Quick Scan Command

```powershell
# One-liner to check all scripts
Get-ChildItem . -Recurse -Include *.ps1,*.md | 
    Select-String -Pattern 'password\s*=|token\s*=|secret\s*=' -CaseSensitive:$false
```

If no output, privacy check passed.

## Checkpoint Safety

For checkpoint files:

```powershell
# Safe checkpoint structure
$checkpoint = @{
    step = 2
    timestamp = Get-Date -Format 'o'
    # NEVER include: password, token, apiKey, credential
}
$checkpoint | ConvertTo-Json | Out-File '.checkpoint.json' -Encoding UTF8
```

---

**Keep secrets secret. Execute safely.**
