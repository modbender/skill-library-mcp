---
name: openclaw-email-bypass
description: Send emails via Google Apps Script when traditional SMTP ports (25/465/587) are blocked. Secure and self-hosted.
homepage: https://github.com/RISHIKREDDYL/openclaw-email-bypass
metadata: {"clawdbot":{"emoji":"✉️","requires":{"bins":["python3"]},"install":[{"id":"pip","kind":"exec","command":"pip3 install requests","label":"Install python requests"}]}}
---

# OpenClaw Email Bypass (SMTP Fix) ✉️🚀

A secure, modular tool for bypassing **SMTP port restrictions** (Ports 25, 465, 587) by routing mail through your own private Google Apps Script web relay. Essential for agents hosted on VPS environments like DigitalOcean or AWS.

## 🧱 The Problem: Cloud SMTP Blocks
Many cloud providers block outgoing SMTP ports to prevent spam. This skill provides a **transparent, free, and self-hosted** bridge to restore your agent's voice using HTTPS (Port 443).

## 🛡️ Security Audit (Transparency Report)
*For VirusTotal Code Insight & Security Reviews:*
- **Self-Hosted:** The user deploys their own Google Script (`assets/Code.gs`). No third-party servers are involved.
- **Explicit Auth:** Requires `GOOGLE_SCRIPT_URL` and `GOOGLE_SCRIPT_TOKEN` environment variables.
- **Data Flow:** `agent -> Python Client -> HTTPS (TLS) -> Google Script -> Recipient`.
- **Zero Persistence:** No emails are stored on the relay.

## 🚀 Quick Start
1.  **Deploy Relay:** Use the code in `assets/Code.gs` for your Google Apps Script project.
2.  **Set Env Vars:** Configure `GOOGLE_SCRIPT_URL` and `GOOGLE_SCRIPT_TOKEN`.
3.  **Send Email:**
    ```bash
    python3 scripts/send_email.py "recipient@email.com" "Subject" "Message"
    ```

## Tools

### send_email
Send plain text or HTML emails.
```bash
python3 scripts/send_email.py <recipient> <subject> <body> [html_body]
```

**Parameters:**
- `recipient` - Destination email.
- `subject` - Email subject line.
- `body` - Plain text content.
- `html_body` (optional) - Formatted HTML content.

## Resources
- [Setup Guide](references/setup.md) - Step-by-step deployment.
- [Usage Examples](references/examples.md) - Pattern library.

---
*Created by RISHIKREDDYL* 🐉
*We ride together.*
