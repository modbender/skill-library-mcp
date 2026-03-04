---
name: openqq
description: QQ bot integration for OpenClaw with session isolation, logging, and AI auto-reply. Supports private chat and group @messages.
---

# OpenQQ Bot

QQ bot integration for OpenClaw. Enables AI auto-reply for QQ private chats and group @mentions with session isolation and comprehensive logging.

## Quick Start

```bash
# Initialize config
npm run setup

# Install dependencies
npm install

# Edit config
vim ~/.openclaw/workspace/open-qq-config.json

# Start bot
npm start
```

## Configuration

Edit `~/.openclaw/workspace/open-qq-config.json`:

```json
{
  "qq": {
    "appId": "YOUR_APP_ID",
    "token": "YOUR_TOKEN",
    "appSecret": "YOUR_APP_SECRET"
  }
}
```

Get credentials from [QQ Open Platform](https://bot.q.qq.com/).

## Usage

```bash
npm start        # Start bot
npm run health   # Health check
npm run logs     # View today's logs
npm run status   # Check running status
```

## Features

- **Session Isolation**: Each user/group has independent conversation history
  - Private: `qq-private-{user_openid}`
  - Group: `qq-group-{group_openid}`
- **Comprehensive Logging**: China timezone, log rotation, sensitive data filtering
- **Auto Reconnect**: WebSocket auto-reconnect with heartbeat
- **Message Retry**: Auto-retry failed messages (up to 2 times)
- **Graceful Shutdown**: Clean shutdown on SIGTERM/SIGINT

## Files

| File | Description |
|------|-------------|
| `qq-bot.js` | Main program (WebSocket + OpenClaw integration) |
| `logger.js` | Logging system (China timezone + rotation) |
| `scripts/health-check.sh` | Health check script |
| `package.json` | Dependencies (axios, ws) |

## npm Commands

| Command | Description |
|---------|-------------|
| `npm start` | Start bot |
| `npm run health` | Health check |
| `npm run logs` | View logs |
| `npm run setup` | Initialize config |
| `npm run status` | Check status |
| `npm run clean` | Clean node_modules |

## Security

- Do not commit `open-qq-config.json` to version control
- Set permissions: `chmod 600 ~/.openclaw/workspace/open-qq-config.json`
- Uses `spawn` instead of `exec` to prevent command injection
- Session IDs are whitelisted (alphanumeric + hyphen only)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Config not found | Run `npm run setup` |
| Missing credentials | Edit config file with appId/token/appSecret |
| WebSocket failed | Check Token and network |
| No reply | Test with `openclaw agent --message "test"` |

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

### v0.0.3 (Latest)
- 7 new npm commands
- FAQ section
- Message retry mechanism
- Graceful shutdown

## License

MIT License

## Links

- [ClawHub](https://clawhub.com/skills/openqq)
- [QQ Open Platform](https://bot.q.qq.com/)
- [OpenClaw Docs](https://docs.openclaw.ai/)
