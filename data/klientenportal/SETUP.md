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

Create `{workspace}/klientenportal/config.json`:

```json
{
  "portal_id": "652",
  "user_id": "YOUR_USER_ID",
  "password": "YOUR_PASSWORD"
}
```

The `portal_id` identifies your accountant's portal instance (e.g. `652` for HFP). The portal URL `https://klientenportal.at/prod/{portal_id}` is derived automatically.

### Environment Variables

Env vars override config.json values:

| Variable | Description |
|---|---|
| `KLIENTENPORTAL_PORTAL_ID` | Portal instance ID |
| `KLIENTENPORTAL_USER_ID` | Login user ID |
| `KLIENTENPORTAL_PASSWORD` | Login password |
