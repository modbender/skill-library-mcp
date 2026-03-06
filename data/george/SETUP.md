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

Provide the George user ID (Verfügernummer or custom username) via:

- `--user-id` CLI flag, or
- `GEORGE_USER_ID` env var

No config file is strictly required — the user ID is the only credential. Authentication is handled interactively via 2FA in the George mobile app.

## Authentication

George uses **2FA via the George mobile app**. When the script initiates login:
1. A confirmation code is displayed in the terminal
2. Open the George app on your phone
3. Approve the login request if the code matches

Session tokens are cached in `{workspace}/george/token.json` to avoid repeated 2FA prompts.
