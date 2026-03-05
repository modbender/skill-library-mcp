# Channels Configuration Reference

Full schema for the `channels` block in `openclaw.json`. Channels are messenger integrations for interacting with agents.

---

## Table of Contents
1. [Universal Options](#universal-options)
2. [DM Policies](#dm-policies)
3. [Telegram](#telegram)
4. [WhatsApp](#whatsapp)
5. [Discord](#discord)
6. [Slack](#slack)
7. [Signal](#signal)
8. [iMessage / BlueBubbles](#imessage--bluebubbles)
9. [Google Chat](#google-chat)
10. [Microsoft Teams](#microsoft-teams)
11. [Matrix](#matrix)
12. [Zalo](#zalo)
13. [WebChat](#webchat)
14. [Channel CLI](#channel-cli)

---

## Universal Options

These options work across all channels:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable the channel |
| `dmPolicy` | string | `"pairing"` | DM access policy |
| `allowFrom` | array | `[]` | Allowlist of sender IDs |
| `groupPolicy` | string | - | Group access policy (where applicable) |
| `agentId` | string | `"main"` | Default agent for this channel |
| `streaming` | boolean | - | Enable response streaming (platform-dependent) |
| `retry` | object | - | Retry behavior for failed deliveries |
| `historyLimit` | number | - | Max messages to keep in context |
| `replyToMode` | string | - | How to handle reply-to messages |
| `reactionNotifications` | boolean | - | Notify on message reactions |
| `textChunkLimit` | number | - | Max characters per message chunk |
| `chunkMode` | string | - | How to split long messages |
| `mediaMaxMb` | number | - | Max media file size in MB |

---

## DM Policies

All channels support the same four DM policies:

| Policy | Behavior | Risk Level |
|--------|----------|-----------|
| `pairing` | Unknown senders get expiring pairing codes (1hr, max 3 pending) | Low |
| `allowlist` | Only `allowFrom` senders accepted, others blocked silently | Minimal |
| `open` | Anyone can DM (requires `allowFrom: ["*"]`) | High |
| `disabled` | All DMs ignored completely | None |

**Pairing flow:**
1. Unknown sender sends any message
2. Bot replies with a time-limited pairing code (expires in 1 hour)
3. Admin approves via `openclaw pairing approve`
4. Sender is now approved permanently

---

## Telegram

**Auth:** BotFather bot token

### Setup
1. Create bot at @BotFather on Telegram
2. Get the bot token
3. Add to config

### Full Schema

```json5
channels: {
  telegram: {
    botToken: "1234567890:ABCdef-GHIjkl...",
    enabled: true,

    // Access control
    dmPolicy: "pairing",
    allowFrom: ["*"],              // ["*"] = anyone, or specific IDs/usernames

    // Message streaming
    streamMode: "partial",         // off | partial | block
    //   off: Send complete message only
    //   partial: Stream as edits to existing message (best UX)
    //   block: Show "typing..." then send complete

    // Text limits
    textChunkLimit: 4000,          // Telegram's per-message character limit

    // Inline buttons
    inlineButtons: "dm",           // off | dm | group | all | allowlist

    // Transport
    webhookMode: false,            // false = polling (default), true = webhook

    // Group configuration
    groups: {
      "-1001234567890": {          // Group chat ID (negative for groups)
        requireMention: true,      // Must @mention bot to trigger
        agentId: "main",
        enabled: true
      },
      "*": {                       // Wildcard for all unspecified groups
        requireMention: true
      }
    }
  }
}
```

### Stream Modes

| Mode | Behavior | UX |
|------|----------|-----|
| `off` | Sends nothing until response is complete | User sees nothing for a while |
| `partial` | Sends message, then edits it as more content arrives | Best UX - feels responsive |
| `block` | Shows "typing..." indicator, sends complete when done | Middle ground |

### Inline Buttons

| Value | Shown In |
|-------|----------|
| `off` | Never |
| `dm` | Direct messages only |
| `group` | Group chats only |
| `all` | Everywhere |
| `allowlist` | Only for approved users |

---

## WhatsApp

**Auth:** QR code pairing via Baileys library

### Setup
```bash
openclaw channels login --channel whatsapp
# Scan QR code with WhatsApp mobile app
```

### Full Schema

```json5
channels: {
  whatsapp: {
    enabled: true,
    dmPolicy: "pairing",
    allowFrom: ["+15551234567"],      // E.164 format REQUIRED

    groupPolicy: "allowlist",         // allowlist | open | disabled
    groups: {
      "*": { requireMention: true },
      "120363xxxxxx@g.us": {          // Group JID format
        requireMention: false,
        agentId: "work",
        enabled: true
      }
    },

    readReceipts: true,
    maxInboundBytes: 52428800,        // 50MB inbound file cap

    historyInject: {
      enabled: true,
      maxMessages: 50
    }
  }
}
```

### CRITICAL: Phone Number Format

WhatsApp **requires E.164 format**: `+15551234567` (country code + number, no spaces, no dashes, no parentheses).

**Correct:** `"+15551234567"`, `"+4915012345678"`
**Wrong:** `"555-123-4567"`, `"(555) 123-4567"`, `"015012345678"`

### Group JID Format

WhatsApp groups use JID format: `120363xxxxxx@g.us`

### Multi-Account Support

WhatsApp supports multiple accounts (phone numbers). Each account gets a separate session.

---

## Discord

**Auth:** Bot token from Discord Developer Portal

### Setup
1. Create application at discord.com/developers
2. Create bot user
3. Enable required intents:
   - **Message Content Intent** (REQUIRED)
   - **Server Members Intent** (recommended)
4. Invite bot to server
5. Copy bot token

### Full Schema

```json5
channels: {
  discord: {
    token: "MTIzNDU2Nzg5...",
    enabled: true,
    dmPolicy: "pairing",
    groupPolicy: "allowlist",

    guilds: {
      "123456789012345678": {         // Guild (server) ID
        requireMention: true,
        agentId: "main",

        channels: {                    // Per-channel overrides
          "987654321098765432": {
            requireMention: false,
            agentId: "work"
          }
        },

        roles: {                       // Role-based routing
          "111111111111111111": {
            agentId: "special-agent"
          }
        }
      }
    },

    slashCommandsEnabled: true,
    pluralKitSupport: false
  }
}
```

### CRITICAL: Message Content Intent

You **must** enable "Message Content Intent" in Discord Developer Portal under Bot > Privileged Gateway Intents. Without it, the bot receives empty messages and cannot respond.

### Agent Routing Priority (Discord)

1. Exact peer match (user ID)
2. Role match (first matching role)
3. Channel ID match
4. Guild ID match
5. Global fallback

---

## Slack

**Auth:** Bot Token + App Token (Socket Mode) or Signing Secret (HTTP Mode)

### Setup
1. Create Slack app at api.slack.com/apps
2. Enable Socket Mode (recommended)
3. Add bot scopes: `chat:write`, `channels:read`, `channels:history`, `im:read`, `im:history`
4. Install to workspace
5. Copy tokens

### Full Schema

```json5
channels: {
  slack: {
    botToken: "xoxb-1234-5678-abcdef",
    appToken: "xapp-1-...",           // Socket Mode only
    signingSecret: "...",              // HTTP Mode only
    mode: "socket",                    // socket (recommended) | http
    enabled: true,
    dmPolicy: "pairing",

    threadMode: "first",               // off | first | all
    //   off: Always in main channel
    //   first: Thread if message is in a thread
    //   all: Always create/use threads

    streaming: false,

    channels: {
      "C1234567890": {
        agentId: "work",
        requireMention: false,
        enabled: true
      }
    }
  }
}
```

### Socket Mode vs HTTP Mode

| | Socket Mode | HTTP Mode |
|-|-------------|-----------|
| Requires | App Token (`xapp-...`) | Signing Secret + public URL |
| Network | Works behind firewalls/NAT | Needs public endpoint |
| Setup | Simpler | More infrastructure |
| Recommended | Yes | For serverless only |

---

## Signal

```json5
channels: {
  signal: {
    enabled: true,
    dmPolicy: "pairing",
    allowFrom: ["+15551234567"]
  }
}
```

Requires additional system configuration (signal-cli).

---

## iMessage / BlueBubbles

### iMessage (Legacy)
```json5
channels: {
  imessage: {
    enabled: true,
    dmPolicy: "pairing"
  }
}
```
Requires macOS with iMessage signed in. Legacy implementation.

### BlueBubbles (Recommended for iMessage)
```json5
channels: {
  bluebubbles: {
    enabled: true,
    serverUrl: "http://your-bluebubbles-server:1234",
    password: "your-bluebubbles-password",
    dmPolicy: "pairing"
  }
}
```
Requires BlueBubbles server running on a Mac.

---

## Google Chat

```json5
channels: {
  googlechat: {
    enabled: true,
    dmPolicy: "pairing"
  }
}
```

Requires Google Workspace app configuration in admin console.

---

## Microsoft Teams

```json5
channels: {
  teams: {
    enabled: true,
    appId: "...",
    appPassword: "...",
    dmPolicy: "pairing"
  }
}
```

Requires Teams app registration in Azure AD.

---

## Matrix

```json5
channels: {
  matrix: {
    enabled: true,
    homeserver: "https://matrix.example.com",
    accessToken: "syt_...",
    userId: "@openclaw:example.com",
    dmPolicy: "pairing"
  }
}
```

Available as an extension. Connects to a Matrix homeserver.

---

## Zalo

```json5
channels: {
  zalo: {
    enabled: true,
    oaId: "...",
    secretKey: "...",
    dmPolicy: "pairing"
  }
}
```

Available as an extension for the Vietnamese messaging platform.

---

## WebChat

The Gateway Control UI at `http://127.0.0.1:18789` includes a built-in WebChat. No additional configuration needed - enabled automatically.

---

## Channel CLI

```bash
openclaw channels login --channel whatsapp   # Authenticate channel
openclaw channels login --channel telegram
openclaw channels add                         # Interactive channel setup
openclaw channels status                      # All channel statuses
openclaw channels status --channel telegram   # Specific channel
openclaw channels list                        # List configured channels
```
