---
name: strava-cli
description: Interact with Strava via the strava-client-cli Python tool. Use for viewing activities, athlete profiles, stats, and exporting data. Covers setup (creating a Strava account, API app, and OAuth) and all CLI commands.
---

# Strava CLI

## Install

```bash
uvx --from strava-client-cli strava --help
# Or install persistently:
uv tool install strava-client-cli
```

## Setup

### 1. Create a Strava Account (if needed)

Sign up at https://www.strava.com/register. Only name, email, and password required.

### 2. Create a Strava API Application

1. Go to https://www.strava.com/settings/api
2. Fill in:
   - **Application Name**: any descriptive name
   - **Category**: pick closest match (e.g. "Other")
   - **Website**: any URL (e.g. your GitHub)
   - **Authorization Callback Domain**: `localhost`
   - **Description**: brief description
3. Check the API Agreement checkbox
4. Click **Create**
5. Note your **Client ID** and **Client Secret**

> **Important**: New Strava API apps allow only **1 connected athlete**. To connect a different athlete, revoke the current one at Settings → My Apps → Revoke Access.

### 3. Authenticate

```bash
strava auth
```

Enter Client ID and Client Secret when prompted. Open the displayed URL in a browser, authorize, then copy the `code` parameter from the redirect URL (`http://localhost/?code=XXXXX`) and paste it back.

Tokens auto-refresh (every 6 hours). Config: `~/.config/strava-cli/config.json`, tokens: `~/.config/strava-cli/tokens.json`.

#### Manual Token Exchange (headless/automated)

If no browser is available, do the OAuth flow manually:

1. Build the auth URL:
   ```
   https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all,profile:read_all
   ```
2. Open in any browser, authorize, grab the `code` from the redirect URL
3. Exchange:
   ```bash
   curl -s -X POST https://www.strava.com/oauth/token \
     -d client_id=CLIENT_ID \
     -d client_secret=CLIENT_SECRET \
     -d code=CODE \
     -d grant_type=authorization_code
   ```
4. Save the response tokens to `~/.config/strava-cli/tokens.json`:
   ```json
   {
     "access_token": "...",
     "refresh_token": "...",
     "expires_at": 1234567890,
     "token_type": "Bearer"
   }
   ```

## Commands

```bash
strava profile                              # Athlete profile
strava stats                                # Run/ride/swim stats summary
strava activities --limit 10                # Recent activities
strava activities --type Run --after 2024-01-01  # Filter by type/date
strava activity 12345678                    # Detailed activity view
strava export --output ./data --format json # Bulk export
```

## Source

https://github.com/geodeterra/strava-cli
