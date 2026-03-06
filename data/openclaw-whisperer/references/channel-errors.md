# Channel Errors

Channel-specific troubleshooting for WhatsApp, Telegram, Discord, Slack, and Signal.

## WhatsApp Errors

### WHATSAPP_NOT_LINKED

**Symptoms:**
- "WhatsApp not linked" error
- QR code doesn't appear
- Phone scan succeeds but connection fails
- "Session invalid" messages

**Common Causes:**
- WhatsApp session expired
- Phone not connected to internet
- Multi-device limit reached (4 devices)
- Account banned/restricted

**Diagnostic Commands:**
```bash
# Check WhatsApp status
openclaw channels status whatsapp

# View session info
openclaw whatsapp session-info

# Test connection
openclaw whatsapp test-connection

# Generate new QR code
openclaw whatsapp qr-code
```

**Fix:**
```bash
# Re-link WhatsApp
openclaw whatsapp link

# Clear old session
openclaw whatsapp logout
rm -rf .openclaw/whatsapp-session
openclaw whatsapp link

# Check multi-device slots
# Open WhatsApp on phone → Linked Devices → Remove old devices

# If banned, contact WhatsApp support or use different number
```

**Auto-Fix Available:** No (requires phone interaction)

**Prevention:**
- Keep phone connected to internet
- Don't logout from gateway frequently
- Monitor session health: `openclaw whatsapp session-health`

---

### WHATSAPP_RATE_LIMIT

**Symptoms:**
- Messages delayed or not sent
- "Rate limit exceeded" warning
- WhatsApp API throttling

**Fix:**
```bash
# Reduce message rate
openclaw config set channels.whatsapp.rateLimit.messagesPerMinute 20

# Enable message queuing
openclaw config set channels.whatsapp.queueing.enabled true
```

---

## Telegram Errors

### TELEGRAM_WEBHOOK_FAIL

**Symptoms:**
- Webhook setup fails
- "Invalid webhook URL" error
- Messages not received
- Telegram API returns 400/401

**Common Causes:**
- Invalid bot token
- Webhook URL not HTTPS (if remote)
- Port not accessible from internet
- Bot token revoked

**Diagnostic Commands:**
```bash
# Check bot status
openclaw channels status telegram

# Test bot token
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# View webhook info
openclaw telegram webhook-info

# Check current webhook
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

**Fix:**
```bash
# Re-set webhook (local mode)
openclaw telegram set-webhook --mode local

# For remote setup (needs HTTPS)
openclaw telegram set-webhook --url https://yourdomain.com/webhook/telegram

# Delete and recreate webhook
openclaw telegram delete-webhook
openclaw telegram set-webhook

# Use polling instead (fallback)
openclaw config set channels.telegram.mode polling
openclaw restart
```

**Auto-Fix Available:** Partial

---

### TELEGRAM_BOT_BLOCKED

**Symptoms:**
- "Bot was blocked by user" errors
- Cannot send messages to specific users

**Fix:**
- Users must /start the bot again
- Cannot be fixed from gateway side

---

## Discord Errors

### DISCORD_INVALID_PERMS

**Symptoms:**
- "Missing permissions" errors
- Cannot send messages in channels
- Cannot read message history
- Slash commands not working

**Required Permissions:**
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands
- Add Reactions

**Diagnostic Commands:**
```bash
# Check bot permissions
openclaw channels status discord

# List missing permissions
openclaw discord check-permissions

# View bot role
openclaw discord bot-info
```

**Fix:**
```bash
# Generate invite with correct permissions
openclaw discord generate-invite

# Or manually in Discord:
# 1. Server Settings → Roles → Bot Role
# 2. Enable required permissions
# 3. Ensure role is above other roles

# Re-invite bot with correct scopes
# https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=515396&scope=bot%20applications.commands
```

**Auto-Fix Available:** No (requires Discord admin)

---

### DISCORD_GATEWAY_ERROR

**Symptoms:**
- "Discord gateway connection failed"
- Bot appears offline
- Events not received

**Fix:**
```bash
# Check intents enabled in Discord Developer Portal
# Required: GUILD_MESSAGES, DIRECT_MESSAGES, MESSAGE_CONTENT

# Update config
openclaw config set channels.discord.intents '["GUILDS", "GUILD_MESSAGES", "DIRECT_MESSAGES", "MESSAGE_CONTENT"]'

# Restart connection
openclaw channels restart discord
```

---

## Slack Errors

### SLACK_BOLT_ERROR

**Symptoms:**
- Slack Bolt framework errors
- Events not received
- "Failed to verify request" errors

**Common Causes:**
- Incorrect signing secret
- Request timestamp too old
- Bolt app not initialized
- OAuth token expired

**Diagnostic Commands:**
```bash
# Check Slack connection
openclaw channels status slack

# Test signing secret
openclaw slack verify-signing-secret

# View app manifest
openclaw slack app-info
```

**Fix:**
```bash
# Update signing secret
openclaw config set channels.slack.signingSecret "your-secret"

# Refresh OAuth token
openclaw slack refresh-token

# Reinstall app
openclaw slack reinstall

# Check event subscriptions in Slack App dashboard
# Events API → Request URL should be: https://yourdomain.com/webhook/slack
```

**Auto-Fix Available:** Partial

---

### SLACK_SCOPE_MISSING

**Symptoms:**
- "Missing OAuth scope" errors
- Cannot call certain API methods

**Required Scopes:**
- chat:write
- channels:history
- groups:history
- im:history
- mpim:history
- users:read
- files:write

**Fix:**
```bash
# Regenerate OAuth token with correct scopes
# 1. Go to Slack App dashboard
# 2. OAuth & Permissions → Add scopes
# 3. Reinstall app to workspace
# 4. Update token in OpenClaw

openclaw config set channels.slack.botToken "xoxb-new-token"
openclaw channels restart slack
```

---

## Signal Errors

### SIGNAL_CLI_MISSING

**Symptoms:**
- "Signal CLI not found" error
- Command not in PATH
- Signal channel won't start

**Diagnostic Commands:**
```bash
# Check if signal-cli installed
which signal-cli
signal-cli --version

# Check PATH
echo $PATH
```

**Fix:**
```bash
# Install signal-cli (Linux)
wget https://github.com/AsamK/signal-cli/releases/download/v0.11.11/signal-cli-0.11.11-Linux.tar.gz
tar xf signal-cli-0.11.11-Linux.tar.gz -C /opt
sudo ln -sf /opt/signal-cli-0.11.11/bin/signal-cli /usr/local/bin/

# Install via package manager
# Debian/Ubuntu
sudo apt install signal-cli

# macOS
brew install signal-cli

# Verify installation
signal-cli --version

# Register with Signal
signal-cli -u +1234567890 register
signal-cli -u +1234567890 verify CODE

# Configure OpenClaw
openclaw config set channels.signal.phone "+1234567890"
openclaw channels start signal
```

**Auto-Fix Available:** Yes (can guide installation)

---

### SIGNAL_REGISTRATION_FAILED

**Symptoms:**
- Cannot register phone number
- "Rate limit exceeded" during registration
- Verification code not received

**Fix:**
```bash
# Wait 24h if rate limited

# Use voice verification
signal-cli -u +1234567890 register --voice

# Try different number

# Check phone number format (+country code)
```

---

## General Channel Debugging

### Channel Status Overview
```bash
# List all channels
openclaw channels list

# Check status
openclaw channels status --all

# Restart specific channel
openclaw channels restart whatsapp

# View channel logs
openclaw logs --channel telegram --last 30m
```

### Common Issues All Channels

**Channel Not Starting:**
```bash
# Check config
openclaw config validate

# Check token/credentials
openclaw config get channels.CHANNEL.token

# Review logs
openclaw logs --channel CHANNEL --level error

# Restart channel
openclaw channels restart CHANNEL
```

**Messages Not Received:**
```bash
# Check webhook/polling status
openclaw channels webhook-status CHANNEL

# Test connection
openclaw channels test CHANNEL

# Enable verbose logging
openclaw config set channels.CHANNEL.logging.level debug
openclaw channels restart CHANNEL
```

**Messages Not Sent:**
```bash
# Check rate limits
openclaw status --rate-limits

# Check message queue
openclaw queue status --channel CHANNEL

# Verify permissions
openclaw channels check-permissions CHANNEL
```

## Channel Configuration Template

```yaml
channels:
  whatsapp:
    enabled: true
    sessionPath: ".openclaw/whatsapp-session"
    rateLimit:
      messagesPerMinute: 20

  telegram:
    enabled: true
    botToken: "${TELEGRAM_BOT_TOKEN}"
    mode: "webhook"  # or "polling"
    webhookUrl: "https://yourdomain.com/webhook/telegram"

  discord:
    enabled: true
    botToken: "${DISCORD_BOT_TOKEN}"
    intents: ["GUILDS", "GUILD_MESSAGES", "MESSAGE_CONTENT"]

  slack:
    enabled: true
    botToken: "${SLACK_BOT_TOKEN}"
    signingSecret: "${SLACK_SIGNING_SECRET}"
    appToken: "${SLACK_APP_TOKEN}"

  signal:
    enabled: true
    phone: "${SIGNAL_PHONE}"
    cliPath: "/usr/local/bin/signal-cli"
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Configuration Errors](configuration-errors.md) - Config issues
- [Gateway Errors](gateway-errors.md) - Network issues
