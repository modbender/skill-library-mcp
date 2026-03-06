---
name: rollhub-bot-builder
description: "Build and deploy autonomous gambling bots for Telegram, Discord, and Twitter using Agent Casino API. Create crypto casino bots, dice bots, coinflip bots with provably fair verification. Bot templates for python-telegram-bot, Discord.js, Twitter API. Automated betting, slash commands, inline keyboards, tweet results. Deploy gambling bot, casino bot builder, Telegram dice bot, Discord casino bot, Twitter betting bot, autonomous trading bot, crypto gambling automation, agent.rollhub.com API integration, real-time bet notifications, provably fair bot."
metadata:
  { "openclaw": { "emoji": "🤖" } }
---
# Casino Bot Builder

Build and deploy autonomous gambling bots for Telegram, Discord, and Twitter using Agent Casino API. Create crypto casino bots, dice bots, coinflip bots with provably fair verification. Bot templates for python-telegram-bot, Discord.js, Twitter API. Automated betting, slash commands, inline keyboards, tweet results. Deploy gambling bot, casino bot builder, Telegram dice bot, Discord casino bot, Twitter betting bot, autonomous trading bot, crypto gambling automation, agent.rollhub.com API integration, real-time bet notifications, provably fair bot.

## Overview

This skill helps you create and deploy gambling bots for **Telegram**, **Discord**, and **Twitter** that interact with the [Agent Casino API](https://agent.rollhub.com/api/v1). Every bot registers with referral tracking and supports provably fair betting.

## API Base

```
https://agent.rollhub.com/api/v1
```

## Step 1: Register an Agent

Every bot must first register on Agent Casino:

```bash
curl -X POST https://agent.rollhub.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-bot", "ref": "ref_27fcab61"}'
```

Save the returned `agent_id` and `api_key`.

## Step 2: Choose Your Platform

### Telegram Bot
Full template: [references/telegram-bot.md](references/telegram-bot.md)

Features:
- `/bet <amount> <game>` — Place a bet
- `/coinflip <amount>` — Quick coinflip
- `/dice <amount>` — Roll dice
- `/balance` — Check balance
- `/history` — Bet history
- `/autoplay <game> <amount> <rounds>` — Auto-play mode
- Inline keyboards for quick betting
- Real-time result notifications

### Discord Bot
Full template: [references/discord-bot.md](references/discord-bot.md)

Features:
- `/bet amount:100 game:coinflip` — Slash command betting
- `/leaderboard` — Server leaderboard
- `/autoplay` — Automated betting rounds
- Embed messages with bet results
- Role-based access control

### Twitter Bot
Full template: [references/twitter-bot.md](references/twitter-bot.md)

Features:
- Tweet bet results automatically
- Reply-based betting (mention bot + amount)
- Daily summary tweets
- Thread-based betting sessions

## Step 3: Place Bets via API

```bash
# Coinflip
curl -X POST https://agent.rollhub.com/api/v1/bet \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"game": "coinflip", "amount": 100, "choice": "heads"}'

# Dice
curl -X POST https://agent.rollhub.com/api/v1/bet \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"game": "dice", "amount": 100, "target": 50, "over": true}'
```

## Step 4: Verify Results (Provably Fair)

Every bet returns a `server_seed_hash`, `client_seed`, and `nonce`. Verify:

```bash
curl https://agent.rollhub.com/api/v1/verify/<bet_id>
```

## Step 5: Auto-Play Mode

All bot templates include auto-play functionality:
1. Set game, bet amount, and number of rounds
2. Bot places bets automatically with configurable delay
3. Stop conditions: max loss, target profit, or round limit
4. Results logged and reported

## Quick Setup

Run the setup helper:

```bash
bash scripts/setup-bot.sh telegram  # or discord, twitter
```

## Keywords

Casino bot builder, Telegram dice bot, Discord casino bot, Twitter betting bot, crypto gambling bot, autonomous betting, provably fair bot, Agent Casino API, coinflip bot, dice bot, gambling automation, bot deployment, slash commands, inline keyboards, auto-play bot, real-time notifications, agent.rollhub.com.
