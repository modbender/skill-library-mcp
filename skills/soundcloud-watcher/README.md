# SoundCloud Watcher - OpenClaw Plugin

Monitor your SoundCloud account and track artist releases. Get notified when someone follows you, likes your tracks, or when artists you care about drop new music.

## Features

- **Follower tracking** - See who followed you recently
- **Track engagement** - Monitor who liked your tracks
- **New releases** - Get notifications when tracked artists release new music
- **Smart API usage** - Only fetches what changed, automatically skips dormant artists
- **Rate limit handling** - Exponential backoff for API reliability
- **OAuth 2.1** - Uses SoundCloud's latest authentication endpoint

## Prerequisites

- OpenClaw gateway running
- Node.js 22+ installed
- SoundCloud API credentials

## Quick Start

### 1. Install

```bash
openclaw plugins install @akilles/soundcloud-watcher
openclaw plugins enable soundcloud-watcher
openclaw gateway restart
```

### 2. Get SoundCloud Credentials

1. Log into SoundCloud
2. Go to [soundcloud.com/you/apps](https://soundcloud.com/you/apps)
3. Click "Register a new application"
4. Fill in name and website (any URL works)
5. Copy your **Client ID** and **Client Secret**

### 3. Configure

Create the credentials file:

```bash
nano ~/.openclaw/secrets/soundcloud.env
```

Add your credentials:

```
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret
MY_USERNAME=your_soundcloud_username
```

### 4. Restart & Verify

```bash
openclaw gateway restart
```

Then in chat:
```
/soundcloud-setup    # Should show "Already configured!"
/soundcloud-status   # Should show your account info
```

## Commands

| Command | Description |
|---------|-------------|
| `/soundcloud-setup` | Show setup instructions and config status |
| `/soundcloud-status` | Show tracking status and account info |
| `/soundcloud-check` | Run immediate check (verbose output) |
| `/soundcloud-cron` | Run check for automation (silent if no updates) |
| `/soundcloud-add <username>` | Track artist(s) - space-separated |
| `/soundcloud-remove <username>` | Stop tracking an artist |
| `/soundcloud-list` | List all tracked artists |

## Automated Checking

The plugin responds to commands but doesn't auto-poll. Set up a cron job for automatic notifications:

```bash
openclaw cron add --name "soundcloud-check" \
  --every 6h \
  --isolated \
  --message "Run /soundcloud-cron and forward any updates to me."
```

Uses `/soundcloud-cron` which:
- Returns updates only (silent if nothing new)
- Logs errors but doesn't spam on config issues

**Alternative:** Add to your `HEARTBEAT.md`:
```markdown
- [ ] Run /soundcloud-cron if not checked in last 6 hours
```

## File Locations

| File | Purpose |
|------|---------|
| `~/.openclaw/secrets/soundcloud.env` | Your API credentials |
| `~/.openclaw/data/artists.json` | Tracked artists data |
| `~/.openclaw/data/soundcloud_tracking.json` | Your account tracking data |

## Troubleshooting

### "Not configured" error

Check your credentials file exists and has correct format:

```bash
cat ~/.openclaw/secrets/soundcloud.env
```

Should contain:
```
SOUNDCLOUD_CLIENT_ID=...
SOUNDCLOUD_CLIENT_SECRET=...
MY_USERNAME=...
```

### Plugin not loading

```bash
openclaw plugins list
```

Should show `soundcloud-watcher` as `loaded`. If `disabled`:

```bash
openclaw plugins enable soundcloud-watcher
openclaw gateway restart
```

### API rate limits

The plugin handles rate limits automatically with exponential backoff. If issues persist, wait a few minutes and try again.

## Uninstalling

```bash
openclaw plugins disable soundcloud-watcher
rm -rf ~/.openclaw/extensions/soundcloud-watcher
```

Optionally remove data:
```bash
rm ~/.openclaw/secrets/soundcloud.env
rm ~/.openclaw/data/artists.json
rm ~/.openclaw/data/soundcloud_tracking.json
```

## Links

- **GitHub:** https://github.com/wlinds/openclaw-soundcloud-watcher
- **npm:** https://www.npmjs.com/package/@akilles/soundcloud-watcher
- **OpenClaw Docs:** https://docs.openclaw.ai/plugin

## License

MIT
