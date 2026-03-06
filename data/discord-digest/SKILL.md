---
name: discord-digest
description: Generate formatted digests from Discord servers using a user token. Reads messages from selected channels/threads and creates concise summaries with links. Use when generating Discord server digests, monitoring Discord channels, or creating Discord activity reports. Supports multi-server configuration, interactive channel selection, token validation with expiry notifications, and configurable time periods.
---

# Discord Digest

Generate formatted digests from Discord servers. Reads channels via user token (no bot required).

## Setup

### 1. Set Discord User Token

Get token from browser: Discord (web) → F12 → Network → any API request → Headers → `Authorization` value.

```bash
python3 scripts/config_manager.py set-token "YOUR_TOKEN"
```

### 2. Scan & Select Servers

List all servers the user belongs to:

```bash
python3 scripts/discord_api.py "TOKEN" guilds
```

### 3. Scan & Select Channels

List channels for a specific server:

```bash
python3 scripts/discord_api.py "TOKEN" channels SERVER_ID
```

### 4. Add Server to Config

```bash
python3 scripts/config_manager.py add-server '{"id":"SERVER_ID","name":"Server Name","channels":[{"id":"CH_ID","name":"channel-name","type":"text"}]}'
```

## Usage

### Generate Digest

```bash
python3 scripts/run_digest.py [--hours 24] [--server SERVER_ID]
```

### Validate Token

```bash
python3 scripts/discord_api.py "TOKEN" validate
```

### Token Expiry Handling

Before each digest run, the token is validated via `GET /users/@me`. If it returns 401:

1. Notify user: "⚠️ Discord token expired, send new token"
2. Wait for new token
3. Update config: `python3 scripts/config_manager.py set-token "NEW_TOKEN"`
4. Retry digest

## Output Format

```
**#SERVER_NAME DD.MM.YY**

[→post](message_url) | 📝 channel-name
**Post Title**
Details: Brief 1-sentence summary of the post content
Links: [source 1](url) | [source 2](url)
```

## Config File

Located at `~/.openclaw/workspace/config/discord-digest.json`:

```json
{
  "discord_token": "...",
  "servers": [
    {
      "id": "829331298878750771",
      "name": "DOUBLETOP SQUAD",
      "channels": [
        {"id": "1238663837515911198", "name": "drops-alerts", "type": "text"}
      ]
    }
  ],
  "digest_period_hours": 24
}
```

## Scripts

| Script | Purpose |
|--------|---------|
| `discord_api.py` | Discord HTTP API client (user token auth) |
| `digest_formatter.py` | Format messages into digest |
| `config_manager.py` | Manage token, servers, channels config |
| `run_digest.py` | Main entry: validate → read → format |

## Rate Limits

Discord API rate limits: ~1 req/sec with automatic retry on 429. The scripts include built-in rate limit handling with exponential backoff.

## Important Notes

- **User tokens** may violate Discord ToS — use at your own risk for personal use only
- Token can expire; the skill includes validation and notification flow
- No external dependencies — uses only Python 3 stdlib (`urllib`, `json`)
