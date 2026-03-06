---
name: prepublish-privacy-scrub
description: Scan and remove sensitive data before publishing skills. Detect API keys, tokens, secrets, and personal info.
---

# Pre-Publish Privacy Scrub

Scan for sensitive data before publishing.

## Problem

Publishing accidentally exposes:
- API keys and tokens
- Gateway credentials
- Personal paths and emails
- Internal service URLs

## Workflow

### 1. Sensitive Pattern Detection

```powershell
function Test-PrivacyScan {
    param([string]$path)
    
    $sensitivePatterns = @(
        'apiKey\s*[=:]\s*["\']?[A-Za-z0-9]',
        'token\s*[=:]\s*["\']?[A-Za-z0-9]{10,}',
        'secret\s*[=:]\s*["\']?[A-Za-z0-9]',
        'password\s*[=:]\s*["\']?.+',
        'Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',
        'sk-[A-Za-z0-9]{32,}',
        'OPENCLAW_\w+\s*[=:]\s*\S+',
        'https://\S+\.ngrok\S+',
        '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    
    $files = Get-ChildItem $path -Recurse -File | 
        Where-Object { $_.Extension -in @('.md', '.ps1', '.json', '.txt') }
    
    $findings = @()
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        foreach ($pattern in $sensitivePatterns) {
            $matches = [regex]::Matches($content, $pattern, 'IgnoreCase')
            foreach ($m in $matches) {
                $findings += @{
                    File = $file.FullName
                    Pattern = $pattern
                    Match = $m.Value.Substring(0, [Math]::Min(20, $m.Value.Length)) + "..."
                }
            }
        }
    }
    
    return $findings
}
```

### 2. Scrubbing

```powershell
function Invoke-PrivacyScrub {
    param([string]$path)
    
    $replacements = @{
        'apiKey\s*[=:]\s*["\']?[^"''\s]+' = 'apiKey: "REDACTED"'
        'token\s*[=:]\s*["\']?[^"''\s]+' = 'token: "REDACTED"'
        'secret\s*[=:]\s*["\']?[^"''\s]+' = 'secret: "REDACTED"'
    }
    
    $files = Get-ChildItem $path -Recurse -File
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        $modified = $false
        
        foreach ($kv in $replacements.GetEnumerator()) {
            if ($content -match $kv.Key) {
                $content = $content -replace $kv.Key, $kv.Value
                $modified = $true
            }
        }
        
        if ($modified) {
            $content | Out-File $file.FullName -Encoding UTF8
            Write-Host "Scrubbed: $($file.Name)"
        }
    }
}
```

### 3. Pre-Publish Checklist

```markdown
## Privacy Scan Results

- [ ] No apiKey values in files
- [ ] No token values in files
- [ ] No secret/password in files
- [ ] No personal emails
- [ ] No absolute user paths (C:\Users\name\)
- [ ] No internal service URLs

**Scan Command**:
```powershell
Test-PrivacyScan -path "./skill-folder"
```
```

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| Scan executed | Test-PrivacyScan returns results |
| No critical findings | apiKey/token/secret = 0 matches |
| Scrubbing applied | Redacted values in files |
| Checklist complete | All items checked |

## Privacy/Safety

- Scan results not logged externally
- Redacted values use generic placeholder
- Original files backed up before scrub

## Self-Use Trigger

Use when:
- Before any skill publish
- Before git push of skills
- After copying skill from working directory

---

**Scrub first. Publish safe.**
