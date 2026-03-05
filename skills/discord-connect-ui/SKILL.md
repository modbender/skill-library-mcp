---
name: discord-connect-hub
description: Complete Discord integration for Clawdbot with automatic UI installation. Provides Discord bot connectivity, dashboard tab, setup wizard, credential management, server monitoring, and plugin architecture hooks. Use when setting up Discord channel integration or adding Discord tab to the Control dashboard. Includes automatic installation of UI components, RPC handlers, and navigation updates.
---

# Discord Connect Hub

Complete Discord integration for Clawdbot with automatic UI installation. This skill provides everything needed for Discord bot connectivity including:

- **Discord Channel Plugin** - Full Discord bot integration for messaging
- **Dashboard UI Tab** - Web interface for setup and monitoring  
- **Setup Wizard** - Step-by-step bot creation and configuration
- **Credential Management** - Secure token storage (OpenBao support)
- **Server Monitoring** - Health checks and guild management
- **Plugin Architecture Hooks** - Automatic installation of UI components

## Installation

This skill automatically installs all necessary components:

```bash
# Install via agent
Install the discord-connect-hub skill from ClawHub
```

The skill will automatically:
1. Install Discord channel plugin if not present
2. Add Discord tab to the Control dashboard
3. Register RPC handlers for Discord management
4. Set up navigation and routing
5. Install UI components and views

## Features

### Discord Bot Integration
- Full Discord.js bot implementation
- Message sending/receiving with formatting preservation
- Reaction handling and emoji support
- File attachment support
- Slash command integration
- Member and guild management

### Dashboard UI
- **Connection Status** - Real-time bot status and health
- **Setup Wizard** - Interactive bot creation guide
- **Server Management** - View guilds, channels, and permissions
- **Invite Generator** - Create bot invite URLs
- **Health Diagnostics** - Automatic troubleshooting
- **Token Management** - Secure credential storage

### Plugin Architecture Integration
- Automatic UI tab installation
- Dynamic navigation updates
- RPC method registration
- Configuration management
- Restart orchestration

## Quick Setup

### 1. Discord Application Setup
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create **New Application** → Enter name → **Create**
3. Go to **Bot** tab → **Reset Token** → **Copy** token
4. Enable **Message Content Intent** ✅

### 2. Bot Permissions
Go to **OAuth2** → **URL Generator**:
- Scopes: `bot` + `applications.commands` 
- Permissions: Send Messages, Read History, Reactions, Embeds, Files, Slash Commands
- Copy invite URL → Open in browser → Authorize

### 3. Configure in Clawdbot
**Option A: Dashboard (Recommended)**
1. Open Control Dashboard → **Channels** → **Discord**
2. Paste bot token → **Save & Connect**

**Option B: Config File**
```yaml
channels:
  discord:
    botToken: "YOUR_BOT_TOKEN"
    # Or with OpenBao:
    # botToken: "bao:channels/discord#bot_token"
```

## Plugin Architecture Hooks

This skill includes hooks for the Clawdbot plugin architecture:

### Installation Hooks
- `install/navigation.js` - Adds Discord tab to dashboard
- `install/rpc-handlers.js` - Registers Discord RPC methods  
- `install/ui-components.js` - Installs UI views and templates
- `install/config-defaults.js` - Sets up default configuration

### Runtime Hooks
- `hooks/post-install.js` - Post-installation setup and verification
- `hooks/pre-uninstall.js` - Cleanup before removal
- `hooks/config-updated.js` - Responds to configuration changes

### Capabilities Registration
The skill declares its capabilities for the plugin system:
- **UI Tabs**: `discord` tab with navigation and routing
- **RPC Methods**: Discord API interaction endpoints
- **Channel Type**: `discord` messaging channel
- **Config Schema**: Discord channel configuration

## RPC Methods

| Method | Description |
|--------|-------------|
| `discord.status` | Get bot connection status and user info |
| `discord.health` | Run comprehensive health checks |
| `discord.guilds` | List connected Discord servers |
| `discord.guild` | Get detailed server information |
| `discord.channels` | List channels in a server |
| `discord.invite` | Generate bot invite URLs |
| `discord.testToken` | Validate token without saving |
| `discord.setToken` | Store and activate bot token |
| `discord.permissions` | Check bot permissions |

## Configuration Options

```yaml
channels:
  discord:
    # Required
    botToken: "YOUR_BOT_TOKEN"
    
    # Guild restrictions (optional)
    guilds:
      "SERVER_ID":
        enabled: true
        channels:
          "CHANNEL_ID":
            enabled: true
            requireMention: false
    
    # Global behavior
    requireMention: true        # Require @mention in servers
    dmPolicy: "pairing"         # DM handling: pairing|open|closed
    groupPolicy: "open"         # Server handling: open|mention|closed
    
    # Advanced options
    retryAttempts: 3
    heartbeatInterval: 30000
    reconnectDelay: 5000
```

## Security Features

- **Token Protection** - Never exposes full tokens in API responses
- **OpenBao Integration** - Vault-based credential storage
- **Scoped Permissions** - Requests only necessary bot permissions
- **Input Validation** - Sanitizes all Discord API inputs
- **Rate Limiting** - Respects Discord API limits
- **HTTPS Enforcement** - Secure token transmission

## Health Checks

Automatic diagnostics include:
- ✅ **Token Validity** - Bot token authentication
- ✅ **Gateway Connection** - Discord WebSocket status  
- ✅ **Message Intent** - Required intent enablement
- ✅ **Bot Permissions** - Guild-level permission verification
- ✅ **Channel Access** - Read/write permission checks
- ✅ **API Rate Limits** - Current usage and limits

## Troubleshooting

### Common Issues

**"Invalid token" errors:**
- Ensure you're using a **bot token** (not user token)
- Verify the token was copied completely
- Try resetting the token in Developer Portal

**Bot not responding in channels:**
- Check **Message Content Intent** is enabled
- Verify bot has permissions in the channel
- Check `requireMention` setting (try @mentioning)

**Dashboard not loading:**
- Verify UI installation completed successfully
- Check browser console for errors
- Restart gateway: `clawdbot gateway restart`

### Log Analysis
```bash
# Check Discord connection logs
clawdbot logs | grep discord

# Test token independently
python scripts/test-token.py YOUR_TOKEN
```

## Files Structure

```
discord-connect-hub/
├── SKILL.md                 # This skill guide
├── scripts/
│   ├── test-token.py       # Token validation utility
│   ├── install-plugin.js   # Plugin installation script
│   └── health-check.py     # Diagnostic tool
├── references/
│   ├── discord-api.md      # Discord API documentation
│   ├── bot-setup.md        # Detailed setup guide
│   └── troubleshooting.md  # Extended troubleshooting
└── assets/
    ├── discord-backend.ts   # RPC handler implementation
    ├── discord-views.ts     # UI component templates
    ├── navigation-hooks.js  # Navigation registration
    ├── install-hooks.js     # Installation automation
    └── config-schema.json   # Configuration validation
```

## Plugin Integration Details

### Automatic Installation Process
1. **Detect Environment** - Check if Clawdbot source is available
2. **Install Backend** - Copy RPC handlers to gateway
3. **Register Handlers** - Add method registration to server
4. **Install UI Components** - Copy views and templates
5. **Update Navigation** - Add Discord tab to dashboard
6. **Configure Routes** - Set up URL routing for tab
7. **Build & Restart** - Compile changes and restart gateway

### Manual Installation Fallback
If automatic installation isn't possible, the skill provides detailed manual instructions similar to the original discord-connect skill.

### Compatibility
- **Clawdbot**: >=2026.1.0
- **Node.js**: >=18.0.0
- **Discord.js**: >=14.0.0
- **Plugin Architecture**: v2+

## Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Bot Permissions Calculator](https://discordapi.com/permissions.html)
- [Clawdbot Discord](https://discord.com/invite/clawd)
- [ClawHub Repository](https://clawdhub.com)