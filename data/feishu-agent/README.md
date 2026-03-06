# Feishu Agent

Feishu Agent is a TypeScript/Node.js middleware layer for Feishu (Lark) API integration, designed for AI assistants.

## Features

- 📅 Calendar management (list calendars, events, create/delete events)
- ⚠️ **Automatic conflict detection** when creating events (uses FreeBusy API)
- ✅ Todo management via Bitable
- 👥 Contact management (list users, search by name/email)
- 🔐 OAuth 2.0 authentication with auto token refresh
- 🚀 CLI interface with commander

## Installation

### Global Install (Recommended)

```bash
bun add -g @teamclaw/feishu-agent
```

After installation, you can use the `feishu_agent` command directly:

```bash
feishu_agent calendar list
```

### Run with bunx (No Install)

```bash
bunx @teamclaw/feishu-agent calendar list
```

### Local Development

```bash
bun install
```

## Quick Start

### 1. Setup

Run the setup command to configure your Feishu app credentials:

```bash
feishu_agent setup
```

Or export environment variables:
```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
```

### 2. Authenticate

```bash
feishu_agent auth
```

This will open a browser window for OAuth 2.0 authorization.

## Usage

### Calendar

```bash
# List calendars
feishu_agent calendar list

# List events
feishu_agent calendar events

# Create event (automatically checks for time conflicts)
feishu_agent calendar create --summary "Meeting" --start "2026-03-01 14:00" --end "2026-03-01 15:00"

# Create event with attendees
feishu_agent calendar create --summary "Meeting" --start "2026-03-01 14:00" --end "2026-03-01 15:00" --attendee-name "张三"

# Delete event
feishu_agent calendar delete --event-id "xxx"
```

### Todo

```bash
# List todos (requires FEISHU_BASE_TOKEN env)
feishu_agent todo list

# Create todo
feishu_agent todo create --title "Task" --priority "High"

# Mark todo as done
feishu_agent todo done --record-id "xxx"
```

### Contact

```bash
# List users
feishu_agent contact list --dept "0"

# Search users
feishu_agent contact search "张三"
```

### Configuration

```bash
# Set config
feishu_agent config set appId cli_xxx

# Get config
feishu_agent config get appId

# List all config
feishu_agent config list
```

## Commands

```
feishu_agent <command> [options]

Commands:
  setup                 Initialize configuration
  auth                  Authenticate with Feishu OAuth
  whoami                Show current user info
  config                Manage configuration
  calendar              Manage calendar events
  todo                  Manage todos
  contact               Manage contacts
```

## Build

```bash
# Build binary
bun run build
```

## Test

```bash
bun test
```

## Architecture

```
src/
├── core/           # Business logic - Feishu API wrappers
│   ├── client.ts       # HTTP client with auth
│   ├── auth-manager.ts # Token lifecycle management
│   ├── config.ts       # Global config management
│   ├── calendar.ts     # Calendar API
│   ├── contact.ts      # Contact API
│   └── todo.ts         # Bitable Todo API
├── index.ts        # Main entry point with CLI router
└── types/          # TypeScript interfaces
```

## Configuration

Global config is stored at `~/.feishu-agent/config.json`:

```json
{
  "appId": "cli_xxx",
  "appSecret": "xxx",
  "userAccessToken": "xxx",
  "refreshToken": "xxx"
}
```

**Note:** User access tokens are automatically refreshed when expired. Just run `feishu_agent auth` again if the refresh token expires.

## License

MIT
