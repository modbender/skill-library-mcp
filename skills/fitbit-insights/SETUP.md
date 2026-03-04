# Fitbit Skill - Setup Guide

## Quick Setup (5 minutes)

### 1. Register Fitbit App

1. Go to https://dev.fitbit.com/apps
2. Click **"Register an App"**
3. Fill in:
   - **App Name:** "Personal Fitness Assistant" (or whatever you like)
   - **Description:** "AI assistant for fitness data"
   - **Website:** `http://localhost`
   - **OAuth 2.0 Application Type:** **Personal**
   - **Callback URL:** `http://localhost`
   - **Default Access Type:** **Read-Only**
4. Agree to terms and submit
5. Note your **Client ID** and **Client Secret**

### 2. Get OAuth Tokens

**Option A: OAuth Tutorial (Easiest)**

1. On your app page, scroll to **"OAuth 2.0 tutorial page"**
2. Click the link to "access your own data"
3. Authorize the app
4. Copy the **Access Token** and **Refresh Token**

**Option B: Manual OAuth Flow**

1. Visit authorization URL (replace YOUR_CLIENT_ID):
   ```
   https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&scope=activity%20heartrate%20sleep%20profile
   ```

2. Authorize and copy the `code` from the redirect URL

3. Exchange code for tokens:
   ```bash
   curl -X POST https://api.fitbit.com/oauth2/token \
     -H "Authorization: Basic $(echo -n 'YOUR_CLIENT_ID:YOUR_CLIENT_SECRET' | base64)" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "client_id=YOUR_CLIENT_ID&grant_type=authorization_code&redirect_uri=http://localhost&code=YOUR_CODE"
   ```

4. Copy `access_token` and `refresh_token` from response

### 3. Configure Skill

Create `fitbit-config.json` in your Clawdbot workspace:

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "access_token": "YOUR_ACCESS_TOKEN",
  "refresh_token": "YOUR_REFRESH_TOKEN",
  "expires_at": 0,
  "last_refreshed": ""
}
```

**Location:** `/root/clawd/fitbit-config.json` (or wherever your Clawdbot workspace is)

### 4. Install Skill

```bash
clawdbot skills install fitbit.skill
```

### 5. Test It!

Ask your AI assistant:
- "How did I do this week?"
- "Did I exercise today?"
- "What was my sleep like last night?"

## Token Management

**Auto-Refresh:** Tokens automatically refresh every 8 hours - no manual intervention needed!

**Manual Refresh (if needed):**
```bash
cd /root/clawd/fitbit
python3 scripts/refresh_token.py force
```

**Check Token Status:**
```bash
python3 scripts/refresh_token.py
```

## Scopes Required

The skill needs these Fitbit API scopes:
- `activity` - Steps, distance, calories, active minutes
- `heartrate` - Heart rate data and zones
- `sleep` - Sleep duration and stages  
- `profile` - Basic profile info

All included in the authorization URL above.

## Security Notes

- ✅ **Never commit config to git** - Add `fitbit-config.json` to `.gitignore`
- ✅ **Refresh tokens don't expire** - Keep them secure
- ✅ **Access tokens expire in 8 hours** - Auto-refreshed by skill
- ✅ **Read-only access** - Skill never writes to Fitbit

## Troubleshooting

**"Config file not found"**
- Make sure `fitbit-config.json` is in `/root/clawd/` (or your workspace root)

**"401 Unauthorized"**
- Token expired - run `python3 scripts/refresh_token.py force`
- Or re-authorize and get new tokens

**"Too Many Requests"**
- Fitbit has rate limits (150 requests/hour per user)
- Skill is optimized to minimize API calls

**"Invalid client credentials"**
- Check Client ID and Client Secret are correct in config

## File Locations

- **Config:** `/root/clawd/fitbit-config.json`
- **Skill:** `/root/nodejs/lib/node_modules/clawdbot/skills/fitbit/`
- **Scripts:** Inside skill folder under `scripts/`

## Next Steps

Once configured, just start asking fitness questions! The AI will:
1. Fetch relevant data from Fitbit
2. Analyze trends and patterns
3. Provide conversational insights

No need to check the app - just ask! 🏋️✨

## Support

- Full OAuth guide: See `references/fitbit-oauth-setup.md` in skill package
- Fitbit API docs: https://dev.fitbit.com/build/reference/web-api/
- Clawdbot community: https://discord.com/invite/clawd
