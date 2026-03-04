# Channels Configuration

## Available Channels

| Channel | Config Key | Auth Method | Easiest Setup |
|---------|------------|-------------|---------------|
| Telegram | `channels.telegram` | Bot token | ⭐ Recommended first |
| WhatsApp | `channels.whatsapp` | QR pairing | Good for personal |
| Discord | `plugins.entries.discord` | Bot token | Good for communities |
| Slack | `plugins.entries.slack` | OAuth | Good for work |
| Signal | `plugins.entries.signal` | signal-cli | Privacy-focused |
| iMessage | `plugins.entries.bluebubbles` | BlueBubbles | macOS only |
| MS Teams | `plugins.entries.msteams` | Azure Bot | Enterprise |

---

## Telegram Setup

```json
{
  "channels": {
    "telegram": {
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing",
      "allowFrom": ["YOUR_USER_ID"],
      "groupPolicy": "allowlist",
      "groups": {
        "-100GROUPID": {
          "enabled": true,
          "requireMention": true
        }
      }
    }
  }
}
```

**Get bot token:** Message @BotFather on Telegram, `/newbot`
**Get your user ID:** Message @userinfobot

**dmPolicy options:**
- `pairing` — Unknown senders get a code, approve with CLI ⭐
- `allowlist` — Only allowFrom users can message
- `open` — Anyone can message (requires `"*"` in allowFrom)
- `disabled` — No DMs accepted

---

## WhatsApp Setup

```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "allowFrom": ["+15551234567"],
      "selfChatMode": true
    }
  }
}
```

**selfChatMode:** Enable if using your personal WhatsApp number.

**First run:** Shows QR code in terminal → scan with WhatsApp.

---

## Discord Setup

```json
{
  "plugins": {
    "entries": {
      "discord": {
        "enabled": true,
        "config": {}
      }
    }
  },
  "channels": {
    "discord": {
      "token": "YOUR_BOT_TOKEN",
      "dm": {
        "policy": "pairing",
        "allowFrom": ["YOUR_DISCORD_USER_ID"]
      },
      "guilds": {
        "GUILD_ID": {
          "enabled": true,
          "channelAllowFrom": ["CHANNEL_ID"]
        }
      }
    }
  }
}
```

**Create bot:** Discord Developer Portal → New Application → Bot

---

## Slack Setup

```json
{
  "plugins": {
    "entries": {
      "slack": {
        "enabled": true,
        "config": {}
      }
    }
  },
  "channels": {
    "slack": {
      "botToken": "xoxb-...",
      "appToken": "xapp-...",
      "dm": {
        "policy": "pairing"
      }
    }
  }
}
```

**Create app:** api.slack.com → Create New App → Socket Mode

---

## Multi-Channel Config

Multiple channels can run simultaneously:

```json
{
  "channels": {
    "telegram": { "botToken": "...", "allowFrom": ["123"] },
    "whatsapp": { "allowFrom": ["+1555..."] }
  },
  "plugins": {
    "entries": {
      "discord": { "enabled": true },
      "slack": { "enabled": true }
    }
  }
}
```

---

## Per-Channel Settings

Settings you can customize per channel:

| Setting | What it does |
|---------|--------------|
| `allowFrom` | User IDs allowed to message |
| `historyLimit` | Messages to include as context |
| `textChunkLimit` | Max characters per message |
| `blockStreaming` | Stream responses in chunks |
| `replyToMode` | Quote original messages (off/first/all) |
| `timeoutSeconds` | API timeout |
| `mediaMaxMb` | Max media size |

---

## Group Settings

```json
{
  "channels": {
    "telegram": {
      "groups": {
        "-100GROUPID": {
          "enabled": true,
          "requireMention": true,
          "allowFrom": ["123", "456"],
          "systemPrompt": "You are helping the Dev team...",
          "skills": ["coding", "github"]
        }
      }
    }
  }
}
```

**topics:** For Telegram supergroups with topics:
```json
{
  "groups": {
    "-100GROUPID": {
      "topics": {
        "1": { "enabled": true },
        "2": { "enabled": false }
      }
    }
  }
}
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not responding | Check `openclaw doctor`, verify token |
| "Not allowed" messages | Add user to `allowFrom` |
| Can't send to groups | Add group ID to `groups` config |
| Media not working | Check `mediaMaxMb` limit |
| Slow responses | Check `timeoutSeconds`, model latency |
