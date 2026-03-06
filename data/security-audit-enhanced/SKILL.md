---
name: security-audit-enhanced
description: Enhanced security audit framework with automated scanning, cross-platform support, security scoring, and baseline comparison. Audits AI agent configurations, credentials, network exposure, and system hardening.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - jq
    primaryEnv: SECURITY_AUDIT_CONFIG
    emoji: "\U0001F510"
    homepage: https://github.com/lobsterai/security-audit-enhanced
---

# Security Audit Enhanced

Advanced security audit framework for AI agents and system configurations. Combines knowledge-based guidance with automated scanning scripts.

## Key Improvements Over Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| Automation | Knowledge only | Scripts + Knowledge |
| JSON Parsing | grep (unreliable) | jq (proper) |
| Platform | Linux only | macOS + Linux |
| Scoring | None | 0-100 scale |
| Baseline | None | Track changes |
| Reports | Text only | JSON/HTML/Markdown |

## Quick Start

### Run Full Audit

```bash
python3 ~/.security-audit/scripts/audit.py --full
```

### Quick Check (Critical Only)

```bash
python3 ~/.security-audit/scripts/audit.py --critical
```

### Generate JSON Report

```bash
python3 ~/.security-audit/scripts/audit.py --json --output report.json
```

### Compare with Baseline

```bash
python3 ~/.security-audit/scripts/audit.py --baseline ~/.security-audit/baseline.json
```

## Security Scoring

The audit produces a 0-100 security score:

| Score | Rating | Status |
|-------|--------|--------|
| 90-100 | Excellent | Minimal risk |
| 70-89 | Good | Minor issues |
| 50-69 | Fair | Needs attention |
| 30-49 | Poor | Significant risk |
| 0-29 | Critical | Immediate action required |

## The 13 Security Domains

### 1. Gateway Exposure 🔴 Critical

**Risk:** Unauthenticated network access to agent gateway.

**Check:**
```bash
jq '.gateway.bind, .gateway.auth_token' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- `bind`: `127.0.0.1` or `lan` (not `0.0.0.0`)
- `auth_token`: Set via env or config

**Fix:**
```bash
export CLAWDBOT_GATEWAY_TOKEN="$(openssl rand -hex 32)"
# Or in config:
jq '.gateway.bind = "127.0.0.1"' ~/.clawdbot/clawdbot.json
```

---

### 2. DM Policy Configuration 🟠 High

**Risk:** Any user can DM the bot and execute commands.

**Check:**
```bash
jq '.channels | to_entries[] | select(.value.dmPolicy) | {channel: .key, policy: .value.dmPolicy}' ~/.clawdbot/clawdbot.json
```

**Secure baseline:**
- `dmPolicy`: `allowlist` or `pairing` (not `open`)

---

### 3. Group Access Control 🟠 High

**Risk:** Anyone in groups can trigger bot commands.

**Check:**
```bash
jq '.channels | to_entries[] | select(.value.groupPolicy) | {channel: .key, policy: .value.groupPolicy}' ~/.clawdbot/clawdbot.json
```

**Secure baseline:**
- `groupPolicy`: `allowlist` with explicit group IDs

---

### 4. Credentials Security 🔴 Critical

**Risk:** Plaintext credentials with loose permissions.

**Check:**
```bash
# Check credential files exist and permissions
ls -la ~/.clawdbot/credentials/ 2>/dev/null
# Check config permissions
stat -f "%Lp" ~/.clawdbot/clawdbot.json 2>/dev/null || stat -c "%a" ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- Directory permissions: `700`
- File permissions: `600`

**Fix:**
```bash
chmod 700 ~/.clawdbot
chmod 600 ~/.clawdbot/clawdbot.json
chmod 600 ~/.clawdbot/credentials/*.json 2>/dev/null
```

---

### 5. Browser Control Exposure 🟠 High

**Risk:** Remote browser control without authentication.

**Check:**
```bash
jq '.browser.remoteControlUrl, .browser.remoteControlToken' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- `remoteControlToken`: Must be set if remote control enabled
- Use HTTPS for remote control URL

---

### 6. Network Binding 🟠 High

**Risk:** Gateway exposed to public internet.

**Check:**
```bash
jq '.gateway.bind, .gateway.mode, .gateway.tailscale' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- `mode`: `local` for development
- `bind`: `127.0.0.1` (localhost only)
- `tailscale.mode`: `off` unless intentionally used

---

### 7. Tool Access & Sandboxing 🟡 Medium

**Risk:** Excessive tool permissions increase blast radius.

**Check:**
```bash
jq '.restrict_tools, .mcp_tools, .workspaceAccess, .sandbox' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- `restrict_tools`: `true`
- `workspaceAccess`: `ro` or `none`
- `sandbox`: `all` for untrusted content

---

### 8. File Permissions 🟡 Medium

**Risk:** Other users can read sensitive configs.

**Check:**
```bash
# Check directory permission
stat -f "%Lp" ~/.clawdbot 2>/dev/null || stat -c "%a" ~/.clawdbot 2>/dev/null
# Check all JSON files
find ~/.clawdbot -name "*.json" -exec stat -f "%Lp %N" {} \; 2>/dev/null || find ~/.clawdbot -name "*.json" -exec stat -c "%a %n" {} \; 2>/dev/null
```

**Secure baseline:**
- `~/.clawdbot/`: `700`
- All `.json` files: `600`

---

### 9. Plugin Trust 🟡 Medium

**Risk:** Untrusted plugins can execute arbitrary code.

**Check:**
```bash
jq '.plugins' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- Use explicit `allowlist` for plugins

---

### 10. Logging & Redaction 🟡 Medium

**Risk:** Sensitive data leaks in logs.

**Check:**
```bash
jq '.logging.redactSensitive' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- `redactSensitive`: `tools` or `all`

---

### 11. Prompt Injection Protection 🟡 Medium

**Risk:** Untrusted content injects malicious prompts.

**Check:**
```bash
jq '.wrap_untrusted_content, .untrusted_content_wrapper, .mentionGate' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
- `wrap_untrusted_content`: `true`
- `mentionGate`: `true`

---

### 12. Dangerous Command Blocking 🟡 Medium

**Risk:** Destructive commands can be executed.

**Check:**
```bash
jq '.blocked_commands' ~/.clawdbot/clawdbot.json 2>/dev/null
```

**Secure baseline:**
Include patterns:
```json
{
  "blocked_commands": [
    "rm -rf",
    "rm -rf /",
    "dd if=",
    "mkfs",
    ":(){ :|:& };:",
    "curl | bash",
    "wget | bash",
    "git push --force",
    "chmod 777",
    "> /dev/sda"
  ]
}
```

---

### 13. Secret Scanning 🟡 Medium

**Risk:** Committed secrets in codebase.

**Check:**
```bash
which detect-secrets 2>/dev/null && detect-secrets --version
ls -la .secrets.baseline 2>/dev/null
```

**Secure baseline:**
- `detect-secrets` installed
- `.secrets.baseline` exists and is current

---

## Automated Scripts

### audit.py

Main audit script with scoring and reporting.

```bash
# Full audit with all checks
python3 scripts/audit.py --full

# Quick critical checks only
python3 scripts/audit.py --critical

# JSON output for CI/CD
python3 scripts/audit.py --json

# Compare with previous baseline
python3 scripts/audit.py --baseline baseline.json --diff

# Apply auto-fixes (safe only)
python3 scripts/audit.py --fix
```

### check_permissions.py

Standalone permission checker.

```bash
python3 scripts/check_permissions.py --path ~/.clawdbot --fix
```

### generate_report.py

Generate formatted reports.

```bash
# HTML report
python3 scripts/generate_report.py --format html --output report.html

# Markdown report
python3 scripts/generate_report.py --format markdown --output SECURITY.md
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Security Audit
        run: |
          pip install jq
          python3 scripts/audit.py --json --output audit-report.json
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: security-audit
          path: audit-report.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
python3 scripts/audit.py --critical || {
  echo "Security audit failed. Fix issues before committing."
  exit 1
}
```

## Baseline Management

### Create Baseline

```bash
python3 scripts/audit.py --save-baseline baseline.json
```

### Compare with Baseline

```bash
python3 scripts/audit.py --baseline baseline.json
```

### Update Baseline After Fixes

```bash
python3 scripts/audit.py --save-baseline baseline.json --force
```

## Report Formats

### JSON Output

```json
{
  "timestamp": "2026-02-21T14:00:00Z",
  "score": 85,
  "rating": "Good",
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "passed": 10
  },
  "findings": [
    {
      "domain": "dm-policy",
      "severity": "high",
      "finding": "DM policy is 'open'",
      "recommendation": "Set dmPolicy to 'allowlist'"
    }
  ]
}
```

### HTML Report

Generates styled HTML with:
- Score gauge visualization
- Severity breakdown chart
- Detailed findings table
- Remediation steps

## Extending the Framework

Add new checks by:

1. Create a new domain in `audit.py`:
```python
def check_new_domain(config):
    issues = []
    # Your check logic
    if vulnerable:
        issues.append({
            'domain': 'new-domain',
            'severity': 'medium',
            'finding': 'Description',
            'recommendation': 'How to fix'
        })
    return issues
```

2. Add domain to checklist in `SKILL.md`

3. Run tests to validate

## References

- OWASP API Security: https://owasp.org/www-project-api-security/
- Clawdbot Security Docs: https://docs.clawd.bot/gateway/security
- Original Framework: https://github.com/TheSethRose/Clawdbot-Security-Check

---

**Remember:** Security is not a one-time check. Run audits regularly, track baselines, and respond to changes promptly.
