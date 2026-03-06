# Google Script Email Bypass (SMTP Fix) ✉️🚀

A secure and reliable tool for bypassing **SMTP port restrictions** (Ports 25, 465, 587) by routing emails through your private Google Apps Script web relay. This is essential for agents hosted on providers like **DigitalOcean, AWS, GCP, or Linode** that block outgoing mail ports.

## 🧱 The Problem: Cloud SMTP Blocks
Many cloud providers block outgoing SMTP traffic for new accounts to prevent spam. This effectively "silences" your OpenClaw agent, preventing it from sending alerts, job applications, or critical notifications. 

This repository provides a **transparent, free, and self-hosted** bridge using Google Apps Script's `MailApp` service to restore your agent's communication capabilities.

---

## 🛡️ Security & Privacy
This tool is designed with a "Security-First" approach:
1.  **User-Owned Infrastructure:** You deploy the relay on your own Google account. No third-party servers see your data.
2.  **Encrypted Transport:** All communication between your agent and the relay happens over HTTPS (Port 443).
3.  **Token Authentication:** The relay is protected by a mandatory `AUTH_TOKEN`. Only your agent can trigger an email send.
4.  **Audit-Ready:** The entire relay code is less than 20 lines of clear JavaScript.

---

## 📂 Repository Structure
- `assets/Code.gs`: The Google Apps Script source code.
- `scripts/send_email.py`: The Python client for your agent.
- `references/setup.md`: Detailed deployment guide.

---

## 🚀 Quick Setup

### 1. Deploy the Google Script
1.  Go to [script.google.com](https://script.google.com) and create a **New Project**.
2.  Copy the contents of `assets/Code.gs` and paste it into the script editor.
3.  Go to **Project Settings** (gear icon) -> **Script Properties**.
4.  Add a property named `AUTH_TOKEN` and set it to a secure, random string (e.g., a long UUID).
5.  Click **Deploy** -> **New Deployment**.
6.  Select type: **Web App**.
7.  Set **Execute as:** `Me`.
8.  Set **Who has access:** `Anyone`.
9.  Copy the **Web App URL** provided after deployment.

### 2. Configure Your Agent
Set these environment variables in your OpenClaw environment or `.env` file:
```bash
GOOGLE_SCRIPT_URL="https://script.google.com/macros/s/..."
GOOGLE_SCRIPT_TOKEN="your-secure-token"
```

---

## 🛠️ Usage

### Python API
You can use the provided script to send emails from any sub-agent or task:

```bash
# Plain Text Email
python3 scripts/send_email.py "recipient@example.com" "Agent Alert" "This is a plain text alert."

# HTML Email
python3 scripts/send_email.py "recipient@example.com" "Daily Report" "Fallback text" "<h1>Your Daily Report</h1><p>Success!</p>"
```

### Integration
The `send_email.py` script can be imported directly into other Python-based agent tasks:

```python
from scripts.send_email import send_email

send_email(
    to="hr@company.com",
    subject="Application for Data Engineer",
    body="See attached profile...",
    html_body="<h2>Job Application</h2><p>Attached is the portfolio.</p>"
)
```

---

## ⚠️ Important Notes
- **Daily Limits:** Google Apps Script has daily quotas (usually 100-1500 emails/day depending on your account type).
- **Execution:** Ensure you have the `requests` library installed (`pip install requests`).

---
*Created by RISHIKREDDYL* 🐉
*We ride together.*
