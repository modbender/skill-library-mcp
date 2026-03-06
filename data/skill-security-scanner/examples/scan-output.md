# Example Scan Outputs

## Example 1: Safe Skill (High Score)

```bash
$ ./scripts/skill-security-scanner.sh ~/.openclaw/skills/github

🔍 Scanning: github
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: 95/100 (🟢 Low)

📋 Permissions:
   • bins: gh

✅ Positive Signs:
   • Official OpenClaw skill
   • Has proper metadata
   • Well documented
   • Standard permissions

💡 Recommendation:
   Safe to use - well documented, standard permissions
```

## Example 2: Medium Risk Skill

```bash
$ ./scripts/skill-security-scanner.sh ~/.openclaw/skills/todoist-rs

🔍 Scanning: todoist-rs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: 68/100 (🟡 Medium)

📋 Permissions:
   • bins: td
   • env: TODOIST_API_KEY

⚠️ Issues Found:
   • [LOW] Requests API keys/tokens - verify needed
   • [LOW] Unknown third-party CLI

✅ Positive Signs:
   • Has proper metadata
   • Well documented

💡 Recommendation:
   Review before use, monitor usage
```

## Example 3: Suspicious Skill

```bash
$ ./scripts/skill-security-scanner.sh ~/.openclaw/skills/suspicious-skill

🔍 Scanning: suspicious-skill
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: 32/100 (🔴 Critical)

📋 Permissions:
   • bins: curl, base64
   • env: API_KEY, SECRET_TOKEN

🚨 CRITICAL ISSUES FOUND:
   1. [HIGH] Network exfiltration pattern detected
   2. [HIGH] Credential access attempt
   3. [HIGH] Obfuscated commands (base64)

✅ Positive Signs:
   • None

💡 Recommendation:
   DO NOT USE - Potential security risk
```

## Example 4: Full Audit Report

```markdown
# Security Analysis: cool-new-skill

## Score: 72/100 (🟡 Medium)

### Permissions Analysis

| Type | Requested | Risk |
|------|-----------|------|
| bins | none | Low |
| env | WEATHER_API_KEY | Low |

### Code Pattern Analysis
- ✅ No suspicious execution patterns
- ✅ No credential access attempts
- ⚠️ 1 network call to external domains (weather API - expected)

### Positive Indicators
- Clear documentation
- Minimal permissions
- Standard API integration

### Issues
- No recent updates (4 months ago)

### Recommendation
Safe to try in sandbox, monitor initial usage.
```
