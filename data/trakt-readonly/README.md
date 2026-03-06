# Trakt Read-only Skill

A secure OpenClaw skill for querying Trakt.tv user data (read-only): current watching, recent episode history, watched shows, stats, and profile.

## Features

- **Watching**: Current movie or episode
- **Recent Episodes**: Recent episode history
- **Watched Shows**: Recently watched shows list
- **Stats**: User stats
- **Profile**: User profile info

## Prerequisites

- `jq` (for JSON parsing)
- `curl`

Install on Ubuntu/Debian:

```
sudo apt-get update && sudo apt-get install -y jq curl
```

## Setup

### Get a Trakt Client ID

1. Go to https://trakt.tv/oauth/applications
2. Click **New Application**
3. Fill in the form (any name). For redirect URI, you can use `urn:ietf:wg:oauth:2.0:oob`.
4. Save and copy the **Client ID**

### Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "trakt-readonly": {
        enabled: true,
        apiKey: "YOUR_TRAKT_CLIENT_ID", // convenience for TRAKT_CLIENT_ID
        env: {
          TRAKT_CLIENT_ID: "YOUR_TRAKT_CLIENT_ID",
          TRAKT_USERNAME: "YOUR_TRAKT_USERNAME",
          TRAKT_ACCESS_TOKEN: "YOUR_TRAKT_OAUTH_TOKEN", // required for playback
          TRAKT_CLIENT_SECRET: "YOUR_TRAKT_CLIENT_SECRET" // required for device token exchange
        }
      }
    }
  }
}
```

**Note:** OpenClaw injects these env vars at runtime (not globally). Never commit secrets to git. If you run the agent in a sandboxed session, set env vars under `agents.defaults.sandbox.docker.env`.

## Usage

### Read-only Commands (No OAuth Required)

**Read-only endpoints require only `TRAKT_CLIENT_ID` + `TRAKT_USERNAME`.**

| Command | Description | Example |
|---------|-------------|---------|
| `watching` | Current watching | `/trakt-readonly watching` |
| `recent [limit]` | Recent episodes | `/trakt-readonly recent 5` |
| `watched-shows` | Watched shows list | `/trakt-readonly watched-shows` |
| `stats` | User stats | `/trakt-readonly stats` |
| `profile` | User profile | `/trakt-readonly profile` |

## Playback progress (OAuth required)

Trakt playback progress requires OAuth. Configure `TRAKT_ACCESS_TOKEN` and use:

```
/trakt-readonly playback movies 2016-06-01T00:00:00.000Z 2016-07-01T23:59:59.000Z
```

## Device OAuth (activate)

1) Start device flow:
```
/trakt-readonly device-code
```
2) Visit https://trakt.tv/activate and enter the `user_code`.
3) Exchange the `device_code` for a token:
```
/trakt-readonly device-token <device_code>
```

## Security

- No hardcoded credentials
- Only connects to `https://api.trakt.tv`
- Read-only endpoints only; playback uses OAuth token read access
- Public Trakt profile required for read-only access

## References

- `references/trakt-api.md`
