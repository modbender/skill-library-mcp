# Apiosk - Keyless API Access with USDC Micropayments

**Pay-per-request API access for agents. No API keys. No accounts. Just pay and call.**

Apiosk enables agents to access production APIs using x402 protocol - USDC micropayments on Base blockchain. Stop managing API keys, start paying per request.

---

## 🎯 What This Skill Does

- **Discover APIs** - Browse 9+ production APIs (weather, prices, news, geocoding, etc.)
- **Pay per request** - Automatic USDC micropayments ($0.001-0.10 per call)
- **No setup** - No API keys, no accounts, no subscriptions
- **Instant access** - Call APIs immediately with x402 payment

---

## 📦 Installation

```bash
# Via ClawHub
clawhub install apiosk

# Or clone manually
git clone https://github.com/apiosk/apiosk-skill
```

---

## ⚙️ Configuration

### 1. Set Up Wallet (One-time)

```bash
# Generate new wallet (or import existing)
./setup-wallet.sh

# This creates ~/.apiosk/wallet.json with:
# - Private key (stored locally, chmod 600 for security)
# - Public address
# - Base mainnet RPC

**IMPORTANT:** The private key is stored in plaintext in `~/.apiosk/wallet.json` (with restrictive file permissions). Only fund this wallet with small amounts for testing. For production, use a hardware wallet or external key management.
```

**Important:** Fund your wallet with USDC on Base mainnet (minimum $1-10 recommended).

**How to fund:**
1. Bridge USDC to Base via https://bridge.base.org
2. Or buy USDC on Coinbase → withdraw to Base
3. Send to your Apiosk wallet address

### 2. Discover Available APIs

```bash
# List all APIs
./list-apis.sh

# Output:
# weather       $0.001/req   Get current weather and forecasts
# prices        $0.002/req   Crypto/stock/forex prices  
# news          $0.005/req   Global news by topic/country
# company       $0.01/req    Company info, financials, news
# geocode       $0.001/req   Address → Coordinates
# ...
```

---

## 🚀 Usage

### Basic API Call

```bash
# Call weather API
./call-api.sh weather --params '{"city": "Amsterdam"}'

# Output:
# {
#   "temperature": 12,
#   "condition": "Cloudy",
#   "forecast": [...]
# }
# 
# ✅ Paid: $0.001 USDC
```

### From Agent Code (Node.js)

```javascript
const { callApiosk } = require('./apiosk-client');

// Call weather API
const weather = await callApiosk('weather', {
  city: 'Amsterdam'
});

console.log(`Temperature: ${weather.temperature}°C`);
// ✅ Automatically paid $0.001 USDC
```

### From Agent Code (Python)

```python
from apiosk_client import call_apiosk

# Call prices API
prices = call_apiosk('prices', {
    'symbols': ['BTC', 'ETH']
})

print(f"BTC: ${prices['BTC']}")
# ✅ Automatically paid $0.002 USDC
```

---

## 📚 Available APIs

| API | Cost/req | Description | Example |
|-----|----------|-------------|---------|
| **weather** | $0.001 | Weather forecasts | `{"city": "NYC"}` |
| **prices** | $0.002 | Crypto/stock prices | `{"symbols": ["BTC"]}` |
| **news** | $0.005 | Global news articles | `{"topic": "AI"}` |
| **company** | $0.01 | Company data | `{"domain": "apple.com"}` |
| **geocode** | $0.001 | Address → Coordinates | `{"address": "Amsterdam"}` |
| **code-runner** | $0.05 | Execute code sandbox | `{"lang": "python", "code": "..."}` |
| **pdf-generator** | $0.02 | HTML → PDF | `{"html": "<h1>Hi</h1>"}` |
| **web-screenshot** | $0.03 | URL → Screenshot | `{"url": "example.com"}` |
| **file-converter** | $0.01 | Convert file formats | `{"from": "docx", "to": "pdf"}` |

**Full docs:** https://apiosk.com/#docs

---

## 🔧 Helper Scripts

### `list-apis.sh`
```bash
#!/bin/bash
# List all available APIs with pricing

curl -s https://gateway.apiosk.com/v1/apis | jq -r '.apis[] | "\(.id)\t$\(.price_usd)/req\t\(.description)"'
```

### `call-api.sh`
```bash
#!/bin/bash
# Call any Apiosk API with automatic payment
# Usage: ./call-api.sh <api-id> --params '{"key":"value"}'

API_ID=$1
PARAMS=$3

# Load wallet
WALLET_ADDRESS=$(jq -r '.address' ~/.apiosk/wallet.json)

# Make request (x402 payment happens via on-chain verification)
# The gateway validates payment on-chain, no client-side signature needed
curl -X POST "https://gateway.apiosk.com/$API_ID" \
  -H "Content-Type: application/json" \
  -H "X-Wallet-Address: $WALLET_ADDRESS" \
  -d "$PARAMS"
```

### `check-balance.sh`
```bash
#!/bin/bash
# Check USDC balance in your Apiosk wallet

WALLET_ADDRESS=$(jq -r '.address' ~/.apiosk/wallet.json)

curl -s "https://gateway.apiosk.com/v1/balance?address=$WALLET_ADDRESS" | jq
# Output: {"balance_usdc": 9.87, "spent_today": 0.13}
```

### `usage-stats.sh`
```bash
#!/bin/bash
# View your API usage stats

WALLET_ADDRESS=$(jq -r '.address' ~/.apiosk/wallet.json)

curl -s "https://gateway.apiosk.com/v1/usage?address=$WALLET_ADDRESS" | jq
# Output:
# {
#   "total_requests": 142,
#   "total_spent_usdc": 1.89,
#   "by_api": {
#     "weather": {"requests": 87, "spent": 0.087},
#     "prices": {"requests": 55, "spent": 0.11}
#   }
# }
```

---

## 🎓 Examples

### Example 1: Weather Bot

```javascript
const { callApiosk } = require('./apiosk-client');

async function getWeatherReport(city) {
  const weather = await callApiosk('weather', { city });
  
  return `🌤️ Weather in ${city}:
Temperature: ${weather.temperature}°C
Condition: ${weather.condition}
Forecast: ${weather.forecast.map(f => f.summary).join(', ')}
  
💰 Cost: $0.001 USDC`;
}

// Usage
console.log(await getWeatherReport('Amsterdam'));
```

### Example 2: Crypto Price Tracker

```python
from apiosk_client import call_apiosk
import time

def track_prices(symbols, interval=60):
    """Track crypto prices with Apiosk"""
    while True:
        prices = call_apiosk('prices', {'symbols': symbols})
        
        for symbol, price in prices.items():
            print(f"{symbol}: ${price:,.2f}")
        
        print(f"✅ Paid: $0.002 USDC\n")
        time.sleep(interval)

# Track BTC and ETH every minute
track_prices(['BTC', 'ETH'])
```

### Example 3: News Digest Agent

```javascript
const { callApiosk } = require('./apiosk-client');

async function getDailyDigest(topics) {
  const articles = [];
  
  for (const topic of topics) {
    const news = await callApiosk('news', { 
      topic, 
      limit: 3 
    });
    articles.push(...news.articles);
  }
  
  return `📰 Daily Digest (${articles.length} articles)
${articles.map(a => `- ${a.title} (${a.source})`).join('\n')}

💰 Total cost: $${(topics.length * 0.005).toFixed(3)} USDC`;
}

// Get tech + business news
console.log(await getDailyDigest(['technology', 'business']));
```

---

## 🔐 How x402 Works

**Traditional API:**
```
1. Sign up for account
2. Get API key
3. Store securely
4. Include in requests
5. Monitor rate limits
6. Pay monthly subscription
```

**Apiosk (x402):**
```
1. Make request
2. Gateway returns 402 Payment Required
3. Your wallet signs payment proof
4. Gateway verifies on-chain
5. Gateway forwards to API
6. You get response
```

**Time:** Milliseconds. **Cost:** Exact usage. **Setup:** Zero.

---

## 🛠️ Advanced Configuration

### Custom RPC Endpoint

```bash
# Edit ~/.apiosk/config.json
{
  "rpc_url": "https://mainnet.base.org",
  "chain_id": 8453,
  "usdc_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
}
```

### Set Spending Limits

```bash
# Set daily spending limit
./set-limit.sh --daily 10.00

# Set per-request max
./set-limit.sh --per-request 0.10
```

### Enable Notifications

```bash
# Get notified when balance is low
./configure.sh --alert-balance 1.00 --alert-webhook "https://hooks.slack.com/..."
```

---

## 📊 Monitoring & Analytics

### Check Spending

```bash
# Today's spending
./usage-stats.sh --today

# This month
./usage-stats.sh --month

# Per API breakdown
./usage-stats.sh --by-api
```

### Export Usage Data

```bash
# Export to CSV for accounting
./export-usage.sh --start 2026-01-01 --end 2026-01-31 --format csv > january_usage.csv
```

---

## 🆘 Troubleshooting

### "Insufficient USDC balance"

```bash
# Check balance
./check-balance.sh

# If low, fund your wallet:
# 1. Bridge USDC to Base: https://bridge.base.org
# 2. Send to: [your wallet address]
```

### "Payment verification failed"

```bash
# Verify wallet signature is working
./test-signature.sh

# If fails, regenerate wallet:
./setup-wallet.sh --regenerate
```

### "API not found"

```bash
# Refresh API list
./list-apis.sh --refresh

# Check if API is available
curl https://gateway.apiosk.com/v1/apis | jq '.apis[] | select(.id=="weather")'
```

---

## 🌐 For Developers: Add Your Own API

Want to monetize your API via Apiosk?

```bash
# 1. Sign up
curl -X POST https://dashboard.apiosk.com/api/register \
  -d '{"email":"you@example.com","api_name":"My API"}'

# 2. Add your API endpoint
curl -X POST https://dashboard.apiosk.com/api/add \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "my-api",
    "endpoint": "https://my-api.com",
    "price_usd": 0.01,
    "description": "My awesome API"
  }'

# 3. Start earning!
# Agents call your API via Apiosk gateway
# You get 90-95% of revenue, automatically
```

**More:** https://docs.apiosk.com/developers

---

## 📖 Resources

- **Website:** https://apiosk.com
- **Dashboard:** https://dashboard.apiosk.com
- **Docs:** https://docs.apiosk.com
- **GitHub:** https://github.com/apiosk
- **Support:** support@apiosk.com
- **Moltbook:** @ApioskAgent

---

## 💡 Why Apiosk?

**For Agents:**
- ✅ No API key management
- ✅ Pay only what you use
- ✅ Access 9+ APIs instantly
- ✅ Transparent pricing
- ✅ On-chain payment proofs

**For Developers:**
- ✅ Monetize any API
- ✅ No payment processing
- ✅ 90-95% revenue share
- ✅ Instant settlement
- ✅ Global reach

**Network effect:** More APIs → More agents → More revenue → More APIs

---

## 🦞 About

Built by the Apiosk team for the agent economy.

**x402 protocol:** Keyless API access with crypto micropayments.  
**Mission:** Make every API instantly accessible to every agent.

**"Stop managing API keys. Start paying per request."**

---

## 📝 License

MIT - Use freely in your agents!

---

## 🔗 Quick Links

```bash
# Install
clawhub install apiosk

# Setup
cd ~/.openclaw/skills/apiosk && ./setup-wallet.sh

# Use
./call-api.sh weather --params '{"city": "Amsterdam"}'

# Monitor
./usage-stats.sh
```

**Happy building! 🚀**
