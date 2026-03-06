---
name: soundcloud-watcher
description: Monitor your SoundCloud account, track artist releases, and get notified about new followers and likes.
metadata:
  display_name: SoundCloud Watcher
  homepage: https://github.com/wlinds/OpenClaw-SoundCloud-Watcher
  tags:
    - soundcloud
    - music
    - notifications
    - openclaw-plugin
---

# SoundCloud Watcher

This skill connects your OpenClaw agent to your SoundCloud account.

**It can:**
- Check setup status and account info
- Track specific artists for new releases
- Get notifications about followers and likes
- Run silently for cron jobs

| Command | Description |
|---------|-------------|
| `/soundcloud-setup` | Show setup instructions and config status |
| `/soundcloud-status` | Show tracking status and account info |
| `/soundcloud-check` | Run immediate check (verbose output) |
| `/soundcloud-cron` | Run check for automation (silent if no updates) |
| `/soundcloud-add <username>` | Track artist(s) - space-separated |
| `/soundcloud-remove <username>` | Stop tracking an artist |
| `/soundcloud-list` | List all tracked artists |

## Installation

```bash
openclaw plugins install @akilles/soundcloud-watcher
openclaw plugins enable soundcloud-watcher
openclaw gateway restart
```

## Configuration

Create `~/.openclaw/secrets/soundcloud.env`:

```
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret
MY_USERNAME=your_soundcloud_username
```

Then in chat:

```
/soundcloud-setup
/soundcloud-status
```

For automation, add a cron:

```bash
openclaw cron add --name "soundcloud-check" \
  --every 6h \
  --isolated \
  --message "Run /soundcloud-cron and forward any updates to me."
```
