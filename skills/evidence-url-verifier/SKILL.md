---
name: evidence-url-verifier
description: Verify evidence URLs are real and accessible. Check that artifact links resolve to actual content, not placeholders.
---

# Evidence URL Verifier

Verify evidence URLs are real and accessible.

## Problem

Evidence links often:
- Point to non-existent resources
- Are placeholders (example.com)
- Expire or get deleted
- Don't match claimed content

## Workflow

### 1. URL Validation

```powershell
function Test-EvidenceUrl {
    param([string]$url)
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10
        return @{
            Valid = $true
            Status = $response.StatusCode
            ContentType = $response.ContentType
        }
    } catch {
        return @{
            Valid = $false
            Error = $_.Exception.Message
        }
    }
}

# Usage
$result = Test-EvidenceUrl "https://example.com/artifact"
if ($result.Valid) {
    Write-Host "URL valid: $($result.Status)"
} else {
    Write-Error "URL invalid: $($result.Error)"
}
```

### 2. Content Verification

```powershell
# Check URL matches claimed content type
$response = Invoke-WebRequest -Uri $url
if ($response.ContentType -notlike "text/*" -and $expectedType -eq "text") {
    Write-Warning "Content type mismatch"
}

# Check for placeholder text
$content = $response.Content
if ($content -match "lorem ipsum|placeholder|example") {
    Write-Warning "Content appears to be placeholder"
}
```

### 3. Artifact Existence

```powershell
# For local paths
if (Test-Path $artifactPath) {
    $size = (Get-Item $artifactPath).Length
    if ($size -eq 0) {
        Write-Warning "Artifact file is empty"
    }
} else {
    Write-Error "Artifact not found: $artifactPath"
}
```

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| URL resolves | HTTP 200 response |
| Content matches | Type matches expected |
| No placeholders | Content is substantive |
| Local paths exist | Test-Path returns true |

## Privacy/Safety

- Don't log full URL contents
- Redact sensitive data in responses
- Respect rate limits (max 1 req/sec)

## Self-Use Trigger

Use when:
- Task claims evidence artifact
- URL provided as proof
- Before marking task complete
- Audit of past completions

---

**Verify evidence. Trust but confirm.**
