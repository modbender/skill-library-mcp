# Privacy Security Checklist

Before publishing or using the phoenix-loop skill, complete the following checks:

## File Scan

```powershell
# Scan for sensitive patterns
Get-ChildItem skills/local/ -Recurse -File | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match 'apiKey|token|secret|password|Bearer |sk-|OPENCLAW_') {
        Write-Warning "Sensitive content: $($_.FullName)"
    }
}
```

## Checklist

- [ ] Skill file contains no API keys
- [ ] Skill file contains no gateway tokens
- [ ] Skill file contains no personal emails/phones
- [ ] Skill file contains no absolute paths (e.g., C:\Users\{name}\...)
- [ ] Memory files are anonymized (patterns only, no specific content)
- [ ] All data stored locally (`skills/local/`, `memory/`)

## Allowed Content

- Pattern names (e.g., `missing-api-key`)
- Generic solution steps (e.g., `Run openclaw configure`)
- Verification commands (e.g., `Test-Path`)
- Tool names and commands

## Forbidden Content

- Actual key values
- User-specific paths
- Personal identifiable information
- External service URLs (unless official documentation)

## Pre-Publish Verification

```powershell
# Run check
$files = Get-ChildItem skills/local/phoenix-loop* -Recurse -File
foreach ($f in $files) {
    $c = Get-Content $f.FullName -Raw
    if ($c -match '(?i)apiKey|token|secret|password') {
        throw "Sensitive content detected: $($f.FullName)"
    }
}
Write-Host "Privacy check passed"
```

## Quick Scan Command

```powershell
# One-liner to check all local skills
Get-ChildItem skills/local/ -Recurse -File | 
    Select-String -Pattern 'apiKey|token|secret|password' -CaseSensitive:$false
```

If no output, privacy check passed.
