---
name: Crypto Alert Agent
description: A proactive agent that monitors cryptocurrency prices, tracks your portfolio, and sends alerts via Telegram.
metadata: {"openclaw": {"emoji": "📈"}}
---

# 📈 Crypto Alert Agent

Stay ahead of the market with the Crypto Alert Agent. This skill provides real-time price alerts, portfolio tracking, and instant notifications through Telegram, ensuring you never miss a critical market movement.

Supported cryptocurrencies include **BTC, ETH, SOL**, and many more via the CoinGecko API.

---

## 1. Features

- **Price Alerts**: Set custom price thresholds for any supported cryptocurrency. Get notified when the price goes above or below your target.
- **Portfolio Tracking**: Add your crypto holdings to track their total value in real-time.
- **Telegram Notifications**: Receive all alerts and updates directly in your Telegram chat for immediate action.
- **On-Demand Price Checks**: Instantly fetch the current price of any cryptocurrency.

---

## 2. Setup

Before using the agent, you need to configure your Telegram notifications.

1.  **Get your Telegram Chat ID**:
    - Talk to the `@userinfobot` on Telegram.
    - It will give you your unique Chat ID.

2.  **Set up Credentials**:
    - Create a file named `telegram_chat_id` inside the `{baseDir}/credentials/` directory.
    - Paste your Chat ID into this file.
    - Ensure your OpenClaw instance is configured with a Telegram bot token that has permission to send you messages.

---

## 3. Usage

The agent can be managed through a simple command-line interface. All commands are executed via the `run.sh` script.

### 3.1 Price Alerts

#### Add a Price Alert
Set an alert for a specific coin when it crosses a target price.

**Command:**
```bash
bash {baseDir}/run.sh alert add --coin <id> --condition <above|below> --price <usd_price>
```

- `--coin <id>`: The CoinGecko API ID for the cryptocurrency (e.g., `bitcoin`, `ethereum`, `solana`).
- `--condition <above|below>`: Notify when the price is `above` or `below` the target.
- `--price <usd_price>`: The target price in USD.

**Example:**
```bash
# Alert me when Bitcoin goes above $75,000
bash {baseDir}/run.sh alert add --coin bitcoin --condition above --price 75000

# Alert me when Solana drops below $150
bash {baseDir}/run.sh alert add --coin solana --condition below --price 150
```

#### List Active Alerts
View all the price alerts you have currently set.

```bash
bash {baseDir}/run.sh alert list
```

#### Remove a Price Alert
Delete an active alert using its ID (you can get the ID from the `list` command).

```bash
bash {baseDir}/run.sh alert remove --id <alert_id>
```

### 3.2 Portfolio Tracking

#### Add a Holding to Your Portfolio
Add a coin and the amount you hold to your portfolio.

**Command:**
```bash
bash {baseDir}/run.sh portfolio add --coin <id> --amount <quantity>
```

- `--coin <id>`: The CoinGecko API ID of the coin.
- `--amount <quantity>`: The number of coins you hold.

**Example:**
```bash
bash {baseDir}/run.sh portfolio add --coin ethereum --amount 2.5
```

#### View Your Portfolio
Get a summary of your current holdings and their total value in USD.

```bash
bash {baseDir}/run.sh portfolio view
```

#### Remove a Holding from Your Portfolio
Remove a coin from your portfolio using its ID.

```bash
bash {baseDir}/run.sh portfolio remove --id <holding_id>
```

### 3.3 Check Price

Get the current price of one or more cryptocurrencies instantly.

**Command:**
```bash
bash {baseDir}/run.sh price --coins <id1,id2,...>
```

- `--coins <id1,id2,...>`: A comma-separated list of CoinGecko API IDs.

**Example:**
```bash
bash {baseDir}/run.sh price --coins bitcoin,ethereum,solana
```

---

## 4. Automation (Agent Logic)

This skill is designed to be run on a schedule (e.g., via a cron job or a persistent agent loop) to check for alert conditions.

**Recommended Automation Schedule:** Every 5 minutes.

**Example Cron Job:**
```cron
*/5 * * * * /path/to/your/workspace/skills/crypto-alert-agent/run.sh agent run
```

The `agent run` command will:
1. Fetch the latest prices for all coins in active alerts and the portfolio.
2. Check if any price alert conditions have been met.
3. If an alert is triggered, send a notification to the configured Telegram chat ID and remove the alert to avoid spam.
4. (Optional) Send a periodic portfolio value update.
