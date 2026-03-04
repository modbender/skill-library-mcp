# Whoop Integration Skill for Clawdbot

Complete Whoop API integration for tracking recovery, sleep, strain, HRV, and getting personalized health insights.

## Features

✅ **Complete v2 API Coverage** - All working Whoop API v2 endpoints
✅ **Automatic Token Refresh** - No more hourly re-authorization!
✅ **Morning Briefings** - Personalized daily health summary
✅ **Sleep Analytics** - Duration, performance, quality, sleep stages
✅ **Recovery Tracking** - HRV, RHR, SpO2, skin temperature
✅ **Strain Monitoring** - Daily load, calories, heart rate zones
✅ **Workout History** - Sports, strain, distance, altitude

## Quick Start

### 1. Install

```bash
# Download the skill
curl -O https://github.com/vraj1512/whoop-clawdbot-skill/releases/latest/download/whoop.skill

# Or clone this repo
git clone https://github.com/vraj1512/whoop-clawdbot-skill.git
```

### 2. Create Whoop Developer App

1. Go to https://app.whoop.com/ → Settings → Developer
2. Create a new application
3. Use the OAuth pages from `references/oauth-pages/` (see instructions there)
4. Save your Client ID and Client Secret

### 3. Authorize

```bash
# Create config
cat > whoop-config.json <<EOF
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "redirect_uri": "https://yourdomain.com/redirect.html"
}
EOF

# Generate auth URL
python3 scripts/whoop_oauth.py --config whoop-config.json

# Click the URL, authorize, and exchange the code
python3 scripts/whoop_oauth.py --config whoop-config.json exchange <CODE>
```

### 4. Use It!

```bash
# Get today's summary
python3 scripts/whoop_client.py --action today

# Morning briefing
python3 scripts/morning_briefing.py

# Get specific data
python3 scripts/whoop_client.py --action recovery --days 7
python3 scripts/whoop_client.py --action sleep --days 7
python3 scripts/whoop_client.py --action workout --days 30
```

## Token Auto-Refresh

**No more hourly re-authorization!** The skill automatically refreshes your access token using the refresh token. Your token stays valid indefinitely.

If you ever need to manually refresh:
```bash
python3 scripts/whoop_oauth.py refresh
```

## API Endpoints Supported

- ✅ Profile - User information
- ✅ Recovery - HRV, RHR, recovery scores (collection & by cycle)
- ✅ Cycle - Daily strain data (collection & by ID)
- ✅ Sleep - Sleep analytics (collection, by ID, by cycle)
- ✅ Workout - Workout history (collection & by ID)

## Requirements

- Python 3.7+
- `requests` library: `pip install requests`
- Whoop account with data to track

## Rate Limits

- API Day Limit: 10,000 calls/day
- API Minute Limit: 100 calls/min
- This skill uses ~20 calls/day max (0.2% of limit)

## Documentation

- **SKILL.md** - Complete setup guide and workflows
- **references/whoop-api.md** - API reference and data interpretation
- **references/oauth-pages/README.md** - OAuth page deployment guide

## Publishing to ClawdHub

See [PUBLISHING_WHOOP_SKILL.md](../../PUBLISHING_WHOOP_SKILL.md) for instructions.

## License

MIT

## Credits

Created for the Clawdbot community by Henry (@emeraldhorizonllc)

## Support

- Whoop Developer Docs: https://developer.whoop.com/
- ClawdHub: https://clawdhub.com
- Issues: https://github.com/vraj1512/whoop-clawdbot-skill/issues
