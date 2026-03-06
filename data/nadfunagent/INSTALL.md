# Installation Guide - Nad.fun Autonomous Trading Agent

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 9.0.0 or higher
- **OpenClaw CLI**: Latest version

### Required Accounts

- Monad blockchain access (mainnet or testnet)
- Telegram account (for notifications, optional)
- GitHub account (for cloning repository)

## Installation Steps

### Step 1: Install OpenClaw CLI

```bash
# Install OpenClaw globally
npm install -g openclaw

# Verify installation
openclaw --version
```

### Step 2: Install Required OpenClaw Skills

```bash
# Install Monad development tools
clawhub install monad-development

# Install Nad.fun trading skill
clawhub install nadfun-trading

# Install Nad.fun indexer skill
clawhub install nadfun-indexer

# Install Nad.fun agent API skill
clawhub install nadfun-agent-api
```

See **DEPENDENCIES.md** for how these skills are used and how to use this repo's `trading/` folder instead of a separate nadfun-trading skill.

### Step 3: Install This Agent

```bash
# Install from GitHub (recommended)
clawhub install nadfunagent

# Or manual installation
git clone https://github.com/encipher88/nadfunagent.git
cd nadfunagent
# Copy SKILL.md to OpenClaw workspace
cp SKILL.md ~/.openclaw/workspace/skills/nadfunagent/
```

### Step 4: Start OpenClaw Gateway

```bash
# Start gateway service
openclaw gateway start

# Verify gateway is running
openclaw gateway status
```

Expected output:
```
Runtime: running
RPC probe: ok
```

## Configuration

### Step 1: Create Configuration Directory

```bash
mkdir -p $HOME/nadfunagent
cd $HOME/nadfunagent
```

### Step 2: Create Environment File

Create `.env` file:

```bash
nano .env
```

Add the following (replace with your values):

```env
# MMIND Token Address (for profit distribution)
MMIND_TOKEN_ADDRESS=0xCe122fd90bBD10A3fb297647A3ad21eC1Ea27777

# Monad Private Key (trading wallet)
MONAD_PRIVATE_KEY=0xYourPrivateKeyHere

# Monad RPC URL
MONAD_RPC_URL=https://rpc.monad.xyz

# Network (mainnet or testnet)
MONAD_NETWORK=mainnet

# Optional: Telegram Bot Token (for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: Telegram User ID (for notifications)
TELEGRAM_USER_ID=your_telegram_user_id
```

**Security Note**: Never commit `.env` file to Git! It contains sensitive information.

**Custom paths:** If you want to use a different location for `.env` or `positions_report.json`, set environment variables:
- `NADFUN_ENV_PATH` — path to `.env` file (default: `$HOME/nadfunagent/.env`)
- `POSITIONS_REPORT_PATH` — path to `positions_report.json` (default: `$HOME/nadfunagent/positions_report.json`)

Example:
```bash
export NADFUN_ENV_PATH=/home/user/myconfig/.env
export POSITIONS_REPORT_PATH=/home/user/myconfig/positions.json
```

### Step 3: Install Trading Scripts (Optional but Recommended)

If you cloned the repository, install dependencies for trading scripts:

```bash
cd nadfunagent/trading
npm install
```

This installs `viem` and `ethers` required for buy/sell/P&L scripts.

### Step 4: Set Permissions

```bash
chmod 600 .env
```

### Step 4: Initialize Agent

```bash
# Start OpenClaw chat
openclaw chat

# In chat, type:
"Initialize nadfunagent"

# The agent will ask for configuration:
# - MMIND_TOKEN_ADDRESS
# - MONAD_PRIVATE_KEY  
# - MONAD_RPC_URL
# - MONAD_NETWORK
# - Telegram user ID (optional)

# Provide values or say "use .env file"
```

The agent will save configuration in OpenClaw memory for future use.

## Verification

### Step 1: Verify Skills Installed

```bash
openclaw skill list | grep nadfun
```

Should show:
- nadfunagent
- nadfun-trading
- nadfun-indexer
- nadfun-agent-api

### Step 2: Test Agent

```bash
# Run agent manually
openclaw cron run <cron-job-id>

# Or via chat
openclaw chat
"Run trading cycle"
```

### Step 3: Check Logs

```bash
# View recent logs
tail -50 /tmp/openclaw/openclaw-*.log

# Filter for agent activity
tail -100 /tmp/openclaw/openclaw-*.log | grep "Nad.fun"
```

### Step 4: Verify Token Scanning

```bash
# Check found tokens file
cat $HOME/nadfunagent/found_tokens.json | jq '.[-1]'
```

## Setting Up Cron Job

### Automatic Setup (Recommended)

Use the cron message from **SKILL.md** (section "Start autonomous trading") so paths are floating: `NADFUN_ENV_PATH`, `NADFUNAGENT_DATA_DIR`, and scripts run from the **nadfun-trading** skill directory (e.g. after `clawhub install nadfun-trading`). The message includes: load config from .env, run `execute-bonding-v2.js` from nadfun-trading, then distribute profits to MMIND holders if profit >= 0.1 MON.

```bash
openclaw cron add \
  --name "Nad.fun Trading Agent" \
  --cron "*/10 * * * *" \
  --session isolated \
  --message "Run autonomous trading cycle: 1) Load config from .env (NADFUN_ENV_PATH or NADFUNAGENT_DATA_DIR/.env). 2) From nadfun-trading skill directory run node execute-bonding-v2.js (P&L from POSITIONS_REPORT_PATH/NADFUNAGENT_DATA_DIR). 3) If profit >= 0.1 MON, distribute to MMIND holders (MMIND_TOKEN_ADDRESS from .env, 30% in MON). English."
```

### Manual Setup

Edit crontab:

```bash
crontab -e
```

Add line:

```
*/10 * * * * openclaw cron run <cron-job-id>
```

## Telegram Setup (Optional)

### Step 1: Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create bot
4. Save the bot token

### Step 2: Get Your Telegram User ID

1. Search for [@userinfobot](https://t.me/userinfobot) in Telegram
2. Start conversation
3. Bot will send your user ID
4. Save the user ID

### Step 3: Configure Agent

Add to `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_user_id
```

### Step 4: Start Conversation with Bot

1. Find your bot in Telegram
2. Send `/start` command
3. Agent will now be able to send notifications

## Troubleshooting

### Issue: Gateway timeout

**Solution**:
```bash
openclaw gateway restart
sleep 3
openclaw gateway status
```

### Issue: Skills not found

**Solution**:
```bash
# Reinstall skills
clawhub install nadfunagent --force
clawhub install nadfun-trading --force
clawhub install nadfun-indexer --force
clawhub install nadfun-agent-api --force
```

### Issue: Cannot read .env file

**Solution**:
```bash
# Check file exists
ls -la $HOME/nadfunagent/.env

# Check permissions
chmod 600 $HOME/nadfunagent/.env

# Verify file content (don't expose private key!)
cat $HOME/nadfunagent/.env | grep -v PRIVATE_KEY
```

### Issue: Rate limit errors (HTTP 429)

**Solution**:
- Increase cron interval from 10 minutes to 15 minutes
- Check API rate limits
- Add delays between API calls (already implemented)

### Issue: Telegram notifications not working

**Solution**:
1. Verify bot token is correct
2. Verify user ID is correct
3. Start conversation with bot first (`/start`)
4. Check bot has permission to send messages

## Next Steps

After successful installation:

1. **Monitor First Run**: Watch logs during first execution
2. **Check Positions**: Verify agent is checking existing positions
3. **Review Found Tokens**: Check `found_tokens.json` for scanned tokens
4. **Adjust Settings**: Modify `.env` if needed
5. **Set Up Alerts**: Configure Telegram notifications

## Support

For issues:
- Open GitHub issue: [Your GitHub Repo]/issues
- Check logs: `/tmp/openclaw/openclaw-*.log`
- Review documentation: `README.md`

---

**Happy Trading! 🚀**
