---
name: clawbsky
version: 1.1.4
description: Advanced Bluesky CLI with support for media (images/video), thread creation, and automated growth tools like non-mutual following cleanup.
homepage: https://github.com/jyothish12345/Clawbsky
metadata:
  openclaw:
    requires:
      env:
        - BLUESKY_HANDLE
        - BLUESKY_APP_PASSWORD
      bins:
        - ffmpeg
        - ffprobe
    primaryEnv: BLUESKY_APP_PASSWORD
---

# 🦞 clawbsky

A full-featured, professional Bluesky CLI designed for power users and automation. 

## ✨ Key Features

- **Media Support**: Post images and videos with automatic metadata/aspect ratio detection.
- **Growth Tools**: Identify and unfollow accounts that don't follow you back (`unfollow-non-mutuals`).
- **Thread Management**: Create long threads automatically from multiple text strings.
- **Search & Explore**: Deep search for posts, users, and hashtags.
- **Moderation**: Quick block, mute, and notification management.

## 🚀 Setup

1. **Get an App Password**: Go to [Bluesky Settings](https://bsky.app/settings/app-passwords) and create a new App Password. **NEVER** use your main account password.
2. **Install**:
   ```bash
   npm install
   ```
3. **Configure**:
   ```bash
   clawbsky login
   ```

## 🛠 Commands

### Growth & Maintenance
```bash
clawbsky unfollow-non-mutuals -n 50 # Unfollow top 50 non-mutuals
clawbsky follow-all "Query" -n 20   # Auto-follow users matching a topic
```

### Posting & Threads
```bash
clawbsky post "Text" [media...]          # Create a post
clawbsky thread "Part 1" "Part 2" ...     # Create a multi-post thread
clawbsky quote <uri> "My thoughts"      # Quote a post
```

### Reading
```bash
clawbsky home -n 20              # View your timeline
clawbsky user <handle>           # Inspect a profile
clawbsky user-posts <handle>     # View user's recent activity
clawbsky thread <uri>            # Read a full conversation branch
```

### Engagement & Moderation
```bash
clawbsky like/repost <uri>       # Engage with content
clawbsky block/mute <handle>     # Manage your boundaries
clawbsky notifications           # Check recent interactions
```

## 💡 Advanced Usage

### Global Options
- `--json`: Get raw data for piping to other tools.
- `--plain`: Disable emojis and formatting for cleaner logs.
- `-n <count>`: Limit results (default: 10).
- `--dry-run`: Preview actions (like unfollowing) without executing.

## 🛡 Safety & Ethics

Clawbsky provides powerful automation tools. To protect your account and the Bluesky community:

1. **Be Human**: Do not use `follow-all` to search and follow thousands of users daily. This is considered spam and will lead to an **account ban**.
2. **Respect Limits**: Use `unfollow-non-mutuals` for periodic maintenance, not for "follow/unfollow" churning.
3. **App Passwords**: Only use App Passwords. If you suspect your credentials have been compromised, revoke the App Password immediately in your Bluesky settings.
4. **Rate Limiting**: The tool includes built-in delays (1s/follow) to prevent hitting API limits. Do not attempt to disable these.

*Responsibility for account actions lies solely with the user.*

### Automatic Logic
- **Handle Completion**: `@username` or `username` automatically resolves to `username.bsky.social`.
- **Rich Text**: Mentions and links are auto-detected and facet-encoded for the AT Protocol.
- **Video Processing**: Automatically polls the Bluesky video service until processing completes.

---
*Built for the AT Protocol community.*
