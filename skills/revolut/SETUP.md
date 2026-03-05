# Setup

## Prerequisites

- Python 3
- Playwright with Chromium

```bash
pip install playwright
playwright install chromium
```

For Docker/sandbox deployments, use `mcr.microsoft.com/playwright/python` as base image.

## Configuration

Create `{workspace}/revolut/config.json`:

```json
{
  "users": {
    "oliver": {},
    "sylvia": { "pin": "123456" }
  }
}
```

- **Single user**: auto-selected, no `--user` needed.
- **Multiple users**: `--user` is required.
- **pin**: optional 6-digit app pin for auto-entry.

## Authentication

Requires **2FA via the Revolut app**. When the script initiates login, a QR code and approval link are generated. Either open the link on your phone or scan the QR code.

The QR code image is saved to `/tmp/openclaw/revolut/revolut_qr.png` and output as `QR_IMAGE:<path>` for the agent to send.
