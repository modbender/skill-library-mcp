# Configuration Examples

## Single Repo (Discord Forum)

```json
{
  "repos": [
    {
      "owner": "openclaw",
      "repo": "openclaw",
      "displayName": "OpenClaw",
      "priorities": ["discord", "voice", "cron", "agent", "telegram"],
      "outputChannel": "<your-discord-forum-channel-id>",
      "outputFormat": "discord-forum",
      "language": "en",
      "includePrerelease": false
    }
  ],
  "versionStore": "release-tracker-state.json",
  "schedule": "0 10 * * *",
  "timezone": "UTC"
}
```

## Multi-Repo (Mixed)

```json
{
  "repos": [
    {
      "owner": "openclaw",
      "repo": "openclaw",
      "displayName": "OpenClaw",
      "priorities": ["discord", "voice", "telegram"],
      "outputChannel": "<your-discord-forum-channel-id>",
      "outputFormat": "discord-forum",
      "language": "zh"
    },
    {
      "owner": "anthropics",
      "repo": "claude-code",
      "displayName": "Claude Code",
      "priorities": ["terminal", "agent", "mcp"],
      "outputChannel": "1234567890",
      "outputFormat": "discord-channel",
      "language": "en"
    },
    {
      "owner": "tailscale",
      "repo": "tailscale",
      "displayName": "Tailscale",
      "priorities": ["macos", "dns", "serve"],
      "outputChannel": "1234567890",
      "outputFormat": "discord-channel",
      "language": "en"
    }
  ],
  "versionStore": "release-tracker-state.json",
  "schedule": "0 9 * * *",
  "timezone": "UTC"
}
```

## Telegram Delivery

```json
{
  "repos": [
    {
      "owner": "openclaw",
      "repo": "openclaw",
      "displayName": "OpenClaw",
      "priorities": ["telegram", "voice", "cron"],
      "outputChannel": "<telegram-chat-id>",
      "outputFormat": "telegram",
      "language": "en"
    }
  ],
  "versionStore": "release-tracker-state.json",
  "schedule": "0 9 * * *",
  "timezone": "UTC"
}
```

## Slack Delivery

```json
{
  "repos": [
    {
      "owner": "vercel",
      "repo": "next.js",
      "displayName": "Next.js",
      "priorities": ["app router", "turbopack", "middleware"],
      "outputChannel": "<slack-channel-id>",
      "outputFormat": "slack",
      "language": "en"
    }
  ],
  "versionStore": "release-tracker-state.json",
  "schedule": "0 9 * * 1-5",
  "timezone": "America/New_York"
}
```

## Priority Keywords Guide

Choose keywords that match what YOU care about. The tracker searches changelog text for these words and bubbles matching items to the top.

Examples by use case:
- **Discord bot developer**: `["discord", "voice", "components", "buttons", "slash"]`
- **Telegram bot developer**: `["telegram", "streaming", "polling", "webhook"]`
- **DevOps/infra**: `["docker", "security", "gateway", "config", "node"]`
- **Mobile developer**: `["ios", "android", "watch", "apns", "push"]`
- **Content creator**: `["tts", "voice", "media", "image", "audio"]`
