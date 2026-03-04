---
name: model-route-guard
description: Diagnose and fix model routing conflicts. Ensure primary model uses correct provider endpoint without duplicate overrides.
---

# Model Route Guard

Fix model routing and provider endpoint conflicts.

## Problem

Model routing issues cause:
- Wrong provider endpoint used
- Duplicate provider definitions
- Agent overrides conflicting with global config
- Silent fallback to wrong model

## Workflow

### 1. Route Audit

```powershell
# Check global config
$cfg = Get-Content "$HOME/.openclaw/openclaw.json" -Raw | ConvertFrom-Json
$globalBase = $cfg.models.providers.bailian.baseUrl
$globalModel = $cfg.agents.defaults.model.primary

# Check agent overrides
$agentCfgPath = "$HOME/.openclaw/agents/main/agent/models.json"
if (Test-Path $agentCfgPath) {
    $agentCfg = Get-Content $agentCfgPath -Raw | ConvertFrom-Json
    $agentBase = $agentCfg.providers.bailian.baseUrl
}

"Global baseUrl = $globalBase"
"Global model   = $globalModel"
"Agent baseUrl  = $agentBase"

# Detect conflicts
if ($globalBase -ne $agentBase) {
    Write-Warning "Provider URL mismatch between global and agent config"
}
```

### 2. Fix Conflicts

```powershell
# Correct endpoint (coding.dashscope, not coding-intl)
$correctUrl = "https://coding.dashscope.aliyuncs.com/v1"

# Update global config
$cfg.models.providers.bailian.baseUrl = $correctUrl
$cfg | ConvertTo-Json -Depth 10 | Out-File "$HOME/.openclaw/openclaw.json" -Encoding UTF8

# Remove conflicting agent override
if (Test-Path $agentCfgPath) {
    Remove-Item $agentCfgPath -Force
}

# Restart
openclaw gateway restart
```

### 3. Verification

```powershell
# Test model call
openclaw models list

# Check active route
openclaw status
```

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| Single provider URL | Only one bailian.baseUrl in config |
| Correct endpoint | URL is coding.dashscope.aliyuncs.com |
| No duplicate overrides | models.json removed or aligned |
| Model call succeeds | `openclaw models list` works |

## Privacy/Safety

- No API keys in audit output
- Redact key values (show first 4 chars)
- Config files only, no external logging

## Self-Use Trigger

Use when:
- Model calls fail with endpoint errors
- Config shows multiple provider definitions
- After gateway restart with model issues
- Silent fallback to wrong model detected

---

**One route. One source of truth.**
