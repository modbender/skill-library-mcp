# Google Apps Script Email Bypass Setup Guide

This guide will help you set up your private email relay.

## 1. Deploy the Google Apps Script Relay

1.  **Open Google Apps Script:** Go to [script.google.com](https://script.google.com) and click **"New Project"**.
2.  **Add the Code:** Locate `assets/Code.gs` in this skill's folder. Copy its contents and paste them into the script editor.
3.  **Set an Auth Token:**
    - Click **Project Settings** (gear icon).
    - Under **Script Properties**, add a property named `AUTH_TOKEN`.
    - Set the value to a secure random string.
4.  **Deploy as Web App:**
    - Click **"Deploy"** -> **"New deployment"**.
    - Select **"Web App"**.
    - Execute as: **Me**.
    - Who has access: **Anyone** (The `AUTH_TOKEN` protects it).
    - Click **"Deploy"** and copy the **Web App URL**.

## 2. Configure Environment Variables

Set these in your agent's environment or `.env` file:

```bash
# The URL from the deployment step
export GOOGLE_SCRIPT_URL="https://script.google.com/macros/s/.../exec"

# The AUTH_TOKEN you created
export GOOGLE_SCRIPT_TOKEN="your-secret-token"
```

## 3. Verification

Test the relay using the local script:

```bash
python3 scripts/send_email.py "your-email@example.com" "Test Subject" "Success!"
```
