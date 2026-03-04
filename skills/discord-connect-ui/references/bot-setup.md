# Discord Bot Setup Guide

Complete guide to creating and configuring a Discord bot for Clawdbot.

## Creating a Discord Application

### Step 1: Access Developer Portal

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Sign in with your Discord account
3. Click **New Application** (top right)

### Step 2: Create Application

1. Enter a name for your bot (e.g., "Koda", "MyAssistant")
2. Accept the Terms of Service
3. Click **Create**

### Step 3: Configure Bot Settings

1. Go to **Bot** tab in the left sidebar
2. Click **Reset Token** → Copy the token immediately
3. Store this token securely - you won't see it again!

### Step 4: Enable Intents

Under **Privileged Gateway Intents**, enable:

| Intent | Required | Purpose |
|--------|----------|---------|
| **Message Content Intent** | ✅ Yes | Read message content |
| **Server Members Intent** | Optional | Get member information |
| **Presence Intent** | Optional | See user status |

⚠️ **Message Content Intent is required** for Clawdbot to read messages.

### Step 5: Configure Permissions

Go to **OAuth2** → **URL Generator**:

**Scopes (required):**
- ✅ `bot`
- ✅ `applications.commands`

**Bot Permissions (recommended):**
- ✅ Send Messages
- ✅ Read Message History
- ✅ Add Reactions
- ✅ Embed Links
- ✅ Attach Files
- ✅ Use Slash Commands

**Additional permissions (optional):**
- ✅ Manage Messages (for message deletion)
- ✅ Manage Webhooks (for webhook features)
- ✅ Create Public Threads (for thread support)

### Step 6: Generate Invite URL

1. Scroll down to see the generated URL
2. Copy the URL
3. Open in browser
4. Select the server to add the bot
5. Click **Authorize**

## Bot Token Security

### Token Format

Discord bot tokens have three parts separated by periods:
```
MTEyMzQ1Njc4OTAxMjM0NTY3OA.GH1234.AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
└─────── User ID ───────┘.──────.──────── Random Secret ────────────
```

### Security Best Practices

1. **Never commit tokens to git** - Use environment variables or secrets management
2. **Use OpenBao for production** - Reference: `bao:channels/discord#bot_token`
3. **Rotate tokens regularly** - Especially if exposure is suspected
4. **Limit permissions** - Only request what you need

### If Token is Compromised

1. Go to Developer Portal → Your App → Bot
2. Click **Reset Token**
3. Update token in Clawdbot config
4. Restart gateway

## Permission Calculations

### Minimum Required (basic messaging)
```
Permission bits: 1110000011000000
Decimal: 379968
```

### Recommended (full features)
```
Permission bits: 1111100011010000
Decimal: 826448
```

### Full Admin (not recommended)
```
Permission bits: 1000000000000000000000000000000
Decimal: 8 (Administrator - grants all)
```

## Multi-Server Configuration

### Global Settings (all servers)

```yaml
channels:
  discord:
    botToken: "your-token"
    requireMention: true      # Require @mention in servers
    dmPolicy: "pairing"       # How to handle DMs
```

### Per-Server Override

```yaml
channels:
  discord:
    guilds:
      "123456789012345678":   # Server ID
        enabled: true
        requireMention: false  # Don't require mention in this server
        channels:
          "987654321098765432": # Channel ID
            enabled: true      # Enable specific channel
```

### Finding IDs

1. Enable Developer Mode: User Settings → Advanced → Developer Mode
2. Right-click server/channel/user → **Copy ID**

## Bot Presence

### Status Options

```yaml
channels:
  discord:
    presence:
      status: "online"        # online, idle, dnd, invisible
      activity:
        type: "playing"       # playing, watching, listening, competing
        name: "with humans"   # Activity text
```

### Example Configurations

```yaml
# Gaming style
presence:
  status: "online"
  activity:
    type: "playing"
    name: "assistant simulator"

# Professional style
presence:
  status: "online"
  activity:
    type: "listening"
    name: "your commands"

# Stealth mode
presence:
  status: "invisible"
```

## Rate Limits

Discord enforces rate limits on API calls:

| Action | Limit |
|--------|-------|
| Messages per channel | 5/5s |
| Reactions | 1/0.25s |
| Guild member requests | 10/10s |
| Global requests | 50/s |

Clawdbot handles rate limits automatically, but be aware of them when debugging.

## Troubleshooting Connection Issues

### Bot appears offline

1. Check token is valid: `./scripts/health-check.py --token TOKEN`
2. Verify gateway connection in logs: `clawdbot logs | grep discord`
3. Ensure intents are enabled in Developer Portal

### "Missing Access" errors

1. Re-invite bot with correct permissions
2. Check channel-level permission overwrites
3. Verify bot role is high enough in role hierarchy

### "Missing Intent" errors

1. Go to Developer Portal → Bot
2. Enable required intents
3. Restart gateway

### Messages not being received

1. Confirm **Message Content Intent** is enabled
2. Check `requireMention` setting
3. Verify bot can see the channel
4. Check channel permission overwrites

## Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord.js Documentation](https://discord.js.org/)
- [Permission Calculator](https://discordapi.com/permissions.html)
- [Gateway Intents Guide](https://discord.com/developers/docs/topics/gateway#gateway-intents)
