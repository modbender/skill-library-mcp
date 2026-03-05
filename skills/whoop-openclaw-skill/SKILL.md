---
name: whoop
description: Fetch and analyze Whoop recovery, strain, sleep, and HRV data via the Whoop API. Use when the user asks about their Whoop metrics, recovery status, sleep quality, daily strain, HRV trends, workout data, or wants health/training insights based on Whoop data. Also use for daily morning briefings, weekly analysis, trend tracking, or real-time health alerts.
---

# Whoop Integration

Interact with the Whoop API to fetch and analyze recovery, strain, sleep, HRV, and workout data.

## Quick Start

### First-time Setup

**Prerequisites:**
- Python 3.7+
- `requests` library: `pip install requests`

**Step 1: Create Whoop Developer App**

1. Go to https://app.whoop.com/ → Settings → Developer
2. Click "Create Application"
3. Fill in the required fields:
   - **Application Name**: Your choice (e.g., "Personal Whoop Assistant")
   - **Privacy Policy URL**: You need a public URL (see options below)
   - **Redirect URI**: You need a callback URL (see options below)
   - **Webhook URL**: Leave blank (optional for basic usage)
4. Save your **Client ID** and **Client Secret** (keep these private!)

**Privacy Policy & Redirect URI Options:**

*Option A - Quick GitHub Pages Setup:*
1. Create a GitHub repo (e.g., `whoop-oauth`)
2. Add the privacy/redirect HTML files from `references/oauth-pages/`
3. Enable GitHub Pages in repo settings
4. Use URLs like:
   - Privacy: `https://yourusername.github.io/whoop-oauth/privacy.html`
   - Redirect: `https://yourusername.github.io/whoop-oauth/redirect.html`

*Option B - Use your own domain:*
- Host the HTML files on your existing website

*Option C - Local testing only:*
- Privacy: `http://localhost/privacy.html` (Whoop may not accept this)
- Redirect: `http://localhost:8080/callback`

**Step 2: Complete OAuth Flow**

1. Create `whoop-config.json` with your app credentials:
   ```json
   {
     "client_id": "your-client-id-here",
     "client_secret": "your-client-secret-here",
     "redirect_uri": "https://yourusername.github.io/whoop-oauth/redirect.html"
   }
   ```

2. Generate authorization URL and authorize:
   ```bash
   python3 scripts/whoop_oauth.py --config whoop-config.json
   ```

3. Click the authorization URL, log in to Whoop, and authorize

4. Copy the authorization code from the redirect page

5. Exchange code for access token:
   ```bash
   python3 scripts/whoop_oauth.py --config whoop-config.json exchange <CODE>
   ```

6. Token is automatically saved to `~/.whoop_token`

**Step 3: Test Connection**
```bash
python3 scripts/whoop_client.py --action profile
```

You should see your Whoop profile information!

### Common Commands

**Today's summary** (recovery + sleep + strain):
```bash
python3 scripts/whoop_client.py --action today
```

**Specific metrics:**
```bash
# Recovery data (last 7 days)
python3 scripts/whoop_client.py --action recovery --days 7

# Sleep data
python3 scripts/whoop_client.py --action sleep --days 7

# Cycle data (strain, HRV, calories)
python3 scripts/whoop_client.py --action cycle --days 7

# Workout history
python3 scripts/whoop_client.py --action workout --days 10
```

**Get raw JSON** (for parsing/analysis):
```bash
python3 scripts/whoop_client.py --action today --json
```

## Analysis Workflows

### Morning Briefing

1. Fetch today's data:
   ```bash
   python3 scripts/whoop_client.py --action today --json
   ```

2. Analyze and provide insights:
   - **Recovery score**: Green (67-100%), Yellow (34-66%), Red (0-33%)
   - **HRV**: Compare to user's baseline (track trends, not absolute values)
   - **Sleep**: Check duration, quality, debt/credit
   - **Recommendations**: Based on recovery, suggest high/moderate/low strain day

Example briefing:
> "🔋 Recovery: 85% (Green) - Your body is well-recovered!
> 
> 📊 HRV: 68ms (up 8% from baseline)
> ❤️ RHR: 52 bpm (stable)
> 
> 😴 Sleep: 8.2 hours, 92% performance
> 
> 💪 Ready for a high-strain day. Go crush that workout!"

### Weekly Analysis

1. Fetch week of data:
   ```bash
   python3 scripts/whoop_client.py --action recovery --days 7 --json
   python3 scripts/whoop_client.py --action sleep --days 7 --json
   python3 scripts/whoop_client.py --action cycle --days 7 --json
   ```

2. Identify trends:
   - HRV trend (increasing/decreasing)
   - Sleep consistency
   - Strain vs recovery balance
   - Patterns (e.g., low recovery after high strain days)

3. Provide recommendations:
   - Adjust training load
   - Improve sleep habits
   - Plan recovery days

### Real-time Alerts

Monitor for warning signs:
- **HRV drops >20% from baseline** → Consider rest day
- **Recovery <33% for 2+ consecutive days** → Prioritize recovery
- **Sleep performance <50% for 3+ days** → Focus on sleep
- **High strain (>17) with low recovery (<40%)** → Risk of overtraining

## Data Interpretation Guide

For detailed metric interpretation and optimal ranges, see `references/whoop-api.md`.

**Key principles:**
- **Track trends, not absolute values** - HRV/RHR baselines vary by individual
- **Match strain to recovery** - High recovery = can handle high strain
- **Consistency matters** - Regular sleep schedule improves recovery
- **Listen to your body** - Metrics are guides, not rules

## Troubleshooting

### Setup Issues

**"Privacy Policy URL must be HTTPS"**:
- Whoop requires HTTPS URLs (not HTTP)
- Use GitHub Pages, Netlify, or your own HTTPS domain
- Local URLs (`localhost`) won't work for production apps

**"Redirect URI mismatch"**:
- The redirect URI must match EXACTLY what you configured in Whoop
- Check for trailing slashes, http vs https, etc.
- Example: `https://example.com/redirect.html` ≠ `https://example.com/redirect.html/`

**OAuth code expired**:
- Authorization codes expire quickly (usually within 10 minutes)
- Generate a new auth URL and try again immediately

### API Issues

**401 Unauthorized**:
- Token expired → Re-run OAuth flow to get a new token
- Invalid token → Check `~/.whoop_token` file exists and contains valid token
- Wrong scopes → Make sure you authorized all required scopes

**404 Not Found** (for sleep/cycle endpoints):
- Some endpoints may not be available depending on API version
- Check Whoop developer docs for current endpoint structure
- Try fetching recovery data which includes sleep-related metrics

**No data returned**:
- Whoop needs to be synced recently (open Whoop app to sync)
- Check date range (data only available for dates when you wore Whoop)
- New users may have limited historical data

**Rate limit errors**:
- Default limits: 10,000/day, 100/minute
- Spread out requests if hitting limits
- Use pagination (`next_token`) for large data fetches

### Data Issues

**Missing metrics**:
- Some metrics require Whoop 4.0 (older devices have limited data)
- Sleep data delayed ~1-2 hours after waking (processing time)
- Recovery score requires previous night's sleep to be processed

**Unexpected values**:
- HRV and RHR vary by individual - track trends, not absolute values
- Recovery score can be affected by alcohol, illness, stress
- Strain accumulates throughout the day (starts low in morning)

### Getting Help

1. Check Whoop Developer Docs: https://developer.whoop.com/
2. Review your app settings: https://app.whoop.com/settings/developer
3. Test with Whoop's API explorer (if available)
4. Verify your token with `--action profile` (simplest endpoint)
