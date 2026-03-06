---
name: gateway-token-doctor
description: Diagnose and fix gateway token mismatches causing 401 errors. Align tokens across config, service, and CLI surfaces.
---

# Gateway Token Doctor

Diagnose and fix 401 errors from token mismatches.

## Problem

Gateway token inconsistencies cause:
- 401 Unauthorized errors
- CLI/UI authentication failures
- Service startup failures
- Silent auth degradation

## Workflow

### 1. Token Audit

```powershell
# Check all token surfaces
$cfg = Get-Content "$HOME/.openclaw/openclaw.json" -Raw | ConvertFrom-Json
$auth = $cfg.gateway.auth.token
$remote = $cfg.gateway.remote.token
$service = $env:OPENCLAW_GATEWAY_TOKEN

"auth.token   = $auth"
"remote.token = $remote"
"service.token = $service"

if ($auth -and $remote -and $auth -ne $remote) {
    Write-Warning "Token mismatch: auth != remote"
}
```

### 2. Alignment Fix

```powershell
# Generate or use existing token
$token = $auth

# Update config
$cfg.gateway.auth.token = $token
$cfg.gateway.remote.token = $token
$cfg | ConvertTo-Json -Depth 10 | Out-File "$HOME/.openclaw/openclaw.json" -Encoding UTF8

# Update service startup script
$servicePath = "$HOME/.openclaw/gateway.cmd"
$content = Get-Content $servicePath -Raw
$content = $content -replace 'OPENCLAW_GATEWAY_TOKEN=.*', "OPENCLAW_GATEWAY_TOKEN=$token"
$content | Out-File $servicePath -Encoding UTF8

# Restart
openclaw gateway restart
```

### 3. Verification

```powershell
# Test gateway access
openclaw gateway status

# Test CLI auth
openclaw whoami
```

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| All tokens aligned | auth == remote == service |
| Gateway responds | `openclaw gateway status` succeeds |
| CLI auth works | `openclaw whoami` returns user |
| No 401 in logs | `Select-String "401" logs` returns nothing |

## Privacy/Safety

- Never log actual token values
- Redact tokens in output (show first 4 chars only)
- Store tokens only in config files

## Self-Use Trigger

Use when:
- 401 errors appear
- Gateway restart after config change
- CLI shows auth mismatch
- Service fails to start

---

**Align tokens. Restore access.**
