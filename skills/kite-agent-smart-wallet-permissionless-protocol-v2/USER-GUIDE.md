# Kite AI Agent Wallet - User Guide

## What is this?

A tool to manage your crypto wallet directly from Telegram.

- Bot runs on YOUR machine
- Your private key stays with YOU
- Operates on Kite AI testnet

## Prerequisites

### 1. Install Node.js
Check if installed:
```bash
node --version
```
If not, download from: https://nodejs.org

### 2. Get Testnet KITE
Go to: https://faucet.gokite.ai

### 3. Create Telegram Bot
1. Open Telegram → @BotFather
2. Send `/newbot`
3. Name your bot
4. Copy the **Bot Token**

## Setup

### 1. Download Code
```bash
git clone <repo-url>
cd kite-wallet
```

### 2. Install
```bash
npm install
```

### 3. Configure
Create `.env` file:
```env
PRIVATE_KEY=your_private_key
TELEGRAM_BOT_TOKEN=your_bot_token
```

### 4. Run
```bash
node telegram-bot.js
```

## Commands

| Command | Function | Example |
|---------|----------|---------|
| `/create` | Create wallet | `/create` |
| `/wallet` | Get address | `/wallet` |
| `/balance` | Check balance | `/balance` |
| `/session add <addr> <limit>` | Add key | `/session add 0xABC 0.5` |
| `/limit set <amount>` | Set limit | `/limit set 1` |
| `/send <addr> <amount>` | Send | `/send 0xABC 0.1` |
| `/help` | Help | `/help` |

## Links

- Website: https://gokite.ai
- Explorer: https://testnet.kitescan.ai
- Faucet: https://faucet.gokite.ai
