# Installation & Setup Guide

## Prerequisites

- A computer — Mac (recommended), Linux, or Windows with WSL
- Node.js 20+ — nodejs.org (LTS version)
- An Anthropic API key — console.anthropic.com
- A Telegram account
- ~30 minutes

**Budget note**: Anthropic charges per token. A typical day of active agent use runs $2–10 depending on how much you're working. Claude Sonnet 4.6 is the recommended model — good balance of capability and cost.

## Install OpenClaw

### macOS

```bash
# Install Node.js if you don't have it
brew install node

# Install OpenClaw globally
npm install -g openclaw

# Verify it's installed
openclaw --version
```

### Linux / WSL

```bash
# Install Node.js (via nvm recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 22
nvm use 22

# Install OpenClaw
npm install -g openclaw

# Verify
openclaw --version
```

## Run the Onboarding Wizard

```bash
openclaw onboard
```

### Step 1: API Key

When asked about authentication, choose Anthropic API key and paste the key from console.anthropic.com (starts with `sk-ant-...`).

To use 1Password for secure key storage: the wizard stores your key locally in `~/.openclaw/`. You can use 1Password CLI to inject the key at runtime instead of storing it in plaintext. Either approach works — 1Password is better practice for teams.

### Step 2: Workspace

The wizard creates a workspace directory for your agent — configuration files, soul file, memory, tools, etc. Default location works fine, or pick somewhere you prefer.

### Step 3: Gateway

The gateway is the background service that keeps your agent running. The wizard sets it up and offers to install as a system service for automatic start. Say yes.

### Step 4: Channels

Set up Telegram — this is how you'll talk to your agent day to day. See the Telegram section below.

### After the Wizard

Your agent is live. Start chatting:

```bash
# Web interface — easiest way to start
openclaw dashboard

# Terminal interface
openclaw tui
```

## Connect Telegram

### Create a Bot

1. Open Telegram and message @BotFather
2. Send `/newbot`
3. Choose a display name (e.g., "My IM Agent") and a username (e.g., `MyIM_Bot`)
4. BotFather gives you a bot token — copy it

### Connect It

If you didn't set up Telegram during onboarding:

```bash
openclaw channels login telegram
```

Paste your bot token. The wizard handles binding the bot to your agent and restarting the gateway.

Once connected, open Telegram and send your bot a message. It should reply as your agent.

## Connect iMessage (via BlueBubbles)

For macOS users who want iMessage integration:

1. Install the BlueBubbles app from bluebubbles.app
2. Install the OpenClaw BlueBubbles plugin:
   ```bash
   openclaw plugins install @openclaw/bluebubbles
   ```
3. Connect:
   ```bash
   openclaw channels add --channel bluebubbles --http-url http://localhost:1234 --password '<your-bluebubbles-password>'
   ```
4. Restart gateway: `openclaw gateway restart`

## Troubleshooting

- **Gateway won't start**: `openclaw doctor` runs health checks and quick fixes
- **Channel not connecting**: `openclaw channels status --probe` shows detailed status
- **Plugin errors**: Check `openclaw channels logs` for details
- **General help**: `openclaw --help` or docs.openclaw.ai
