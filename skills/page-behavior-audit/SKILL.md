---
name: page-behavior-audit
description: Deep behavioral audit with hashed policy (CSP-compliant, no plaintext badwords)
homepage: https://github.com/openclaw/page-behavior-audit
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "type": "skill",
        "version": "1.0.3",
        "modelInvocable": false,
        "requiredEnv":
          [
            {
              "name": "WECOM_WEBHOOK_URL",
              "description": "WeCom webhook URL for critical alerts",
              "sensitive": true,
            },
            {
              "name": "OPENCLAW_AUDIT_DIR",
              "description": "Directory for audit logs, screenshots, and HAR files",
              "default": "${HOME}/.openclaw/audit",
            },
          ],
        "trigger": { "type": "webhook", "path": "/api/audit/scan", "method": "POST" },
        "timeout": 15000,
      },
  }
---

# page-behavior-audit

Deep behavioral page auditing with content safety policy enforcement.

## Features

- 🔍 Browser automation with redirect tracking
- 🛡️ Content policy checking (hashed badwords)
- 🎯 Response monitoring (SSRF/XXE detection)
- 📸 Full-page screenshots
- 📊 HAR export
- 🚨 WeCom alerts for critical findings

## Prerequisites

Set required environment variables:

```bash
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
export OPENCLAW_AUDIT_DIR="${HOME}/.openclaw/audit"  # optional
```

## Usage

### Via Webhook

```bash
curl -X POST http://localhost:8080/api/audit/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "include_har": true}'
```

### Via CLI

```bash
openclaw skill run page-behavior-audit --url https://example.com
```

## Configuration

**Input schema:**
- `url` (string, required): Target URL to audit
- `include_har` (boolean, optional): Export HAR file (default: true)

**Output:**
- `redirects`: Captured redirects
- `text_alerts`: Content policy violations
- `ct_alerts`: Response monitoring alerts
- `screenshot_path`: Screenshot file path
- `har_path`: HAR file path

## Security

- SHA256-hashed badword policies
- Ed25519 signature verification
- CSP-compliant (no plaintext sensitive words)
- Sandbox-isolated browser execution

## Alert Rules

**CRITICAL severity:**
- XML served from non-.xml endpoints (SSRF/XXE risk)
- Image endpoints returning XML (XXE evasion)

Alerts are sent to WeCom webhook when critical issues are detected.
