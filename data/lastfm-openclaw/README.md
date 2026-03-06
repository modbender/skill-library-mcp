# Last.fm OpenClaw Skill

A secure, configurable OpenClaw skill for accessing Last.fm user profile data.

## Features

- **Now Playing**: Get current or most recently played track
- **Top Tracks**: View top tracks by time period (7day, 1month, 3month, 6month, 12month, overall)
- **Top Artists**: View top artists by time period
- **Top Albums**: View top albums by time period
- **Loved Tracks**: See your loved tracks collection
- **Recent Tracks**: View recent listening history
- **Profile Info**: Get user profile statistics
- **Love/Unlove**: Mark tracks as loved (requires auth)

## Installation

### Prerequisites

- `jq` (for JSON parsing)
- `curl`

Install on Ubuntu/Debian:

```
sudo apt-get update && sudo apt-get install -y jq curl
```

### 1. Get a Last.fm API Key

1. Visit https://www.last.fm/api/account/create
2. Fill in the application details:
   - **Name**: Your preferred name (e.g., "OpenClaw Integration")
   - **Description**: "Personal OpenClaw skill for Last.fm"
   - **Application URL**: Leave blank or use your site
3. Save the **API Key** shown after creation

### 2. Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      lastfm: {
        enabled: true,
        apiKey: "YOUR_API_KEY_HERE", // convenience for LASTFM_API_KEY
        env: {
          LASTFM_API_KEY: "YOUR_API_KEY_HERE",
          LASTFM_USERNAME: "YOUR_USERNAME"
        }
      }
    }
  }
}
```

**Note:** OpenClaw injects these env vars at runtime (not globally). Never commit secrets to git. If you run the agent in a sandboxed session, set the env vars under `agents.defaults.sandbox.docker.env` (or per-agent) because sandboxed skills do not inherit host env.

### 3. Install the Skill

**From ClawHub:**
```bash
clawhub install lastfm
```

**From local directory:**
```bash
# Copy skill to your workspace
cp -r lastfm ~/.openclaw/skills/

# Or place in workspace skills folder
cp -r lastfm ./skills/
```

### 4. Verify Installation

```
/lastfm profile
```

## Usage

### Read Commands (No Auth Required)

**Read-only endpoints require only `LASTFM_API_KEY` + `LASTFM_USERNAME`.**

| Command | Description | Example |
|---------|-------------|---------|
| `now-playing`, `np` | Current/last track | `/lastfm np` |
| `top-tracks [period]` | Top tracks by period | `/lastfm top-tracks 7day` |
| `top-artists [period]` | Top artists by period | `/lastfm top-artists 1month` |
| `top-albums [period]` | Top albums by period | `/lastfm top-albums overall` |
| `loved` | Loved tracks | `/lastfm loved` |
| `recent [limit]` | Recent tracks | `/lastfm recent 20` |
| `profile` | User profile | `/lastfm profile` |

### Time Periods

- `7day` - Last 7 days
- `1month` - Last 30 days  
- `3month` - Last 90 days
- `6month` - Last 180 days
- `12month` - Last year
- `overall` - All time

### Write Commands (Auth Required)

**Write endpoints require `LASTFM_SESSION_KEY` + `LASTFM_API_SECRET`.**
See [Authentication Guide](references/auth-guide.md) for setup.

| Command | Description | Example |
|---------|-------------|---------|
| `love` | Love a track | `/lastfm love "Artist" "Track"` |
| `unlove` | Unlove a track | `/lastfm unlove "Artist" "Track"` |

## Examples

### Check What's Playing

```
User: What am I listening to on Last.fm?

🎵 Now Playing:
"The Less I Know The Better" by Tame Impala
from Currents
```

### Weekly Top Tracks

```
User: Show me my top tracks this week

🎵 Top Tracks (7 days):

1. "Blinding Lights" by The Weeknd (23 plays)
2. "Levitating" by Dua Lipa (18 plays)
3. "Save Your Tears" by The Weeknd (15 plays)
...
```

### Profile Stats

```
User: Show my Last.fm profile

🎵 Last.fm Profile: musiclover

📊 42,156 total scrobbles
🌍 United States
📅 Member since: Mar 2015
🔗 last.fm/user/musiclover
```

## Security

This skill follows OpenClaw security best practices:

- **No hardcoded credentials** - All secrets via environment variables
- **No external endpoints** - Only connects to `ws.audioscrobbler.com`
- **No install hooks** - No lifecycle scripts or setup commands
- **No obfuscated code** - All files are human-readable
- **Minimal permissions** - Only requests what's needed

## Configuration Options

```json5
{
  skills: {
    entries: {
      lastfm: {
        enabled: true,
        env: {
          LASTFM_API_KEY: "required",
          LASTFM_USERNAME: "required",
          LASTFM_SESSION_KEY: "optional, for write ops",
          LASTFM_API_SECRET: "optional, for write ops"
        }
      }
    }
  }
}
```

## Troubleshooting

### "Missing LASTFM_API_KEY"

Ensure your API key is set in `~/.openclaw/openclaw.json` under `skills.entries.lastfm.env.LASTFM_API_KEY`.

### "Invalid API key"

1. Verify your API key at https://www.last.fm/api/accounts
2. Check for typos in your configuration
3. Ensure the API key wasn't revoked

### "Rate limit exceeded"

Last.fm allows 5 requests/second. Wait a moment and try again.

### "Authentication failed for write operations"

Write operations require a session key. See [Authentication Guide](references/auth-guide.md).

## API Reference

See [API Endpoints](references/api-endpoints.md) for detailed API documentation.

## License

MIT

## Contributing

Issues and pull requests welcome at the repository.
