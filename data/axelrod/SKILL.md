---
name: axelrod
description: AI-powered Base-chain trading and on-chain query agent via natural language. Use when the user wants to trade crypto (buy/sell/swap tokens), set up automated strategies (DCA, limit orders, RSI), check portfolio balances, view token prices, query token info/analysis, check order status, manage take-profit/stop-loss orders, or ask about crypto/DeFi topics on Base chain. Always run scripts/axelrod_chat.py to fetch real-time results.
---

# Axelrod

Execute Base-chain trading and on-chain queries using natural language through the AIxVC AI Automation.

## Quick Start

### First-Time Setup

1. **Configure credentials** in OpenClaw config under `skills.entries.axelrod.env`:

```json
{
  "skills": {
    "entries": {
      "axelrod": {
        "enabled": true,
        "env": {
          "AIXVC_ACCESS_KEY": "your_access_key",
          "AIXVC_SECRET_KEY": "your_secret_key"
        }
      }
    }
  }
}
```

2. **Install dependencies**:

```bash
pip install -r skills/axelrod/requirements.txt
```

3. **Verify setup**:

```bash
python skills/axelrod/scripts/axelrod_chat.py --message "check my balance"
```

## Core Usage

### Simple Query

For straightforward requests that complete quickly:

```bash
python skills/axelrod/scripts/axelrod_chat.py --message "check my ETH balance"
python skills/axelrod/scripts/axelrod_chat.py --message "what is ETH price now"
```

### JSON Debug Mode

For inspecting the full API response:

```bash
python skills/axelrod/scripts/axelrod_chat.py --message "check my balance" --json
```

## Mandatory Workflow

1. **Check AK/SK** — If `AIXVC_ACCESS_KEY` or `AIXVC_SECRET_KEY` is missing, ask the user to configure them. Do not guess or fabricate credentials.
2. **Run the script** — Whenever the request needs real-time on-chain data or execution, always run the CLI. Do not answer from model memory alone.
3. **Return stdout** — Capture the script's stdout and return it to the user. Light formatting is fine, but do not omit key results (amounts, tx hashes, confirm keys, error messages).
4. **Handle confirmation** — If the response includes `confirmKey`, guide the user to confirm or cancel (see Confirmation Flow below).

## Capabilities Overview

### Trading Operations

- **Spot Buy/Sell/Swap**: Exchange tokens on Base chain
- **DCA**: Dollar-cost averaging automation (e.g. "DCA 20u into ETH every day")
- **Limit/Trigger Orders**: Execute at target prices or PnL rates
- **RSI Strategy**: Conditional trading based on RSI indicators (e.g. "if 1h RSI < 30, buy 100u BTC")
- **Take-Profit / Stop-Loss**: Automated risk management via `QUERY_ALGO`

**Reference**: [references/api.md](references/api.md)

### Query Operations

- **Balance Query**: Single token or all-asset portfolio
- **Token Info & Analysis**: Contract details, decimals, analytics
- **Price Query**: Real-time prices with 24h change
- **Order Query**: Active order list and details
- **TP/SL Order Query**: Take-profit/stop-loss order status

### Blockchain Assistant

- Crypto/DeFi domain Q&A and execution guidance
- Trading plan suggestions on Base chain

## Confirmation Flow

Orders usually require risk-control confirmation; small orders (approximately ≤ $10) may skip confirmation. `confirmKey` is valid for about **10 minutes**.

When the response includes `confirmKey`, ask the user to send one of:

```text
yes, please execute <confirmKey>
no, please cancel <confirmKey>
```

If the key has expired, the user must submit the original request again.

## Current Limitations

| Limitation | Details |
| ---------- | ------- |
| Chain | Base only |
| Multiple trades | One trade per message; ask user to split if needed |
| Not supported | Leverage/futures/options, lending, cross-chain, NFT, fiat on/off-ramp |

## Common Patterns

### Check Before Trading

```bash
# Check balance
python skills/axelrod/scripts/axelrod_chat.py --message "check my ETH balance"

# Check price
python skills/axelrod/scripts/axelrod_chat.py --message "what is ETH price now"

# Then trade
python skills/axelrod/scripts/axelrod_chat.py --message "buy 50u of ETH"
```

### Automated Strategies

```bash
# DCA strategy
python skills/axelrod/scripts/axelrod_chat.py --message "DCA 20u into ETH every day"

# RSI conditional strategy
python skills/axelrod/scripts/axelrod_chat.py --message "if 1h RSI < 30, buy 100u BTC"

# Limit order
python skills/axelrod/scripts/axelrod_chat.py --message "buy ETH when price drops to 2500"
```

### Portfolio Review

```bash
# Full portfolio
python skills/axelrod/scripts/axelrod_chat.py --message "check my balance"

# Token analysis
python skills/axelrod/scripts/axelrod_chat.py --message "analyze AXR token for me"

# Order status
python skills/axelrod/scripts/axelrod_chat.py --message "show my recent orders"
```

## Error Handling

### Exit Codes

| Code | Meaning | Resolution |
| ---- | ------- | ---------- |
| `0` | Success | — |
| `2` | Missing AK/SK | Ask user to configure `AIXVC_ACCESS_KEY` and `AIXVC_SECRET_KEY` |
| `3` | HTTP failure or invalid/non-JSON response | Check network, verify endpoint is reachable |
| `4` | API business error (`code` not in success set) | Read the error message, guide user to fix |

### Common Issues

| Issue | Resolution |
| ----- | ---------- |
| "Please login first" | AK/SK is incorrect — reconfigure credentials |
| Authentication error | Verify AK/SK are correct and not expired |
| Insufficient balance | Reduce trade amount or add funds |
| Token not found | Check token symbol or contract address |
| confirmKey expired | Re-submit the original trade request |
| Multiple trades in one message | Split into separate requests |

## Prompt Examples by Category

### Trading

- `"buy 50u of AXR"`
- `"sell 50% of my ETH"`
- `"swap 10 SOL to ETH"`

### Automated Strategies

- `"DCA 20u into ETH every day"`
- `"if 1h RSI < 30, buy 100u BTC"`
- `"buy ETH when price drops to 2500"`

### Portfolio & Queries

- `"check my balance"`
- `"show AXR token info"`
- `"what is ETH price now"`
- `"show my recent orders"`
- `"show my TP/SL orders"`

### Blockchain Assistant

- `"analyze AXR token for me"`
- `"help me make a Base trading plan"`

## Best Practices

### Security

1. Never share your AK/SK credentials
2. Start with small test amounts
3. Verify token addresses before large trades
4. Review confirmation details carefully before executing

### Trading

1. Check balance before trades
2. Specify amounts clearly (`50u`, `50%`, `0.1 ETH`)
3. Start small, scale up after validation
4. Use limit orders for better entry prices
5. Set TP/SL for risk management

## API Reference

For the full API contract, SigV4 signing protocol, request/response format, and response field details, see:

**Reference**: [references/api.md](references/api.md)

## Implementation Notes

- The script uses AK/SK with SigV4-style signing to call the AIxVC.
- Current endpoint: `https://api.aixvc.io/gw/openapi/v2/public/twa/agent/chat` (`chain-id=base`).
- If documentation conflicts with code behavior, follow the script implementation.

## File Structure

- **SKILL.md** — Agent instructions (this file). The agent reads this to understand how to use the skill.
- **README.md** — Human-facing setup and usage guide.
- **scripts/axelrod_chat.py** — CLI client. Always invoke with `python skills/axelrod/scripts/axelrod_chat.py --message "<instruction>"`.
- **references/api.md** — Full API contract and signing reference.
- **requirements.txt** — Python dependencies (`requests`).

## Troubleshooting

### Script Not Working

```bash
# Ensure Python 3 is available
python --version

# Install dependencies
pip install -r skills/axelrod/requirements.txt

# Test connectivity
curl -I https://api.aixvc.io
```

### API Errors

See exit codes and common issues tables above. If an error persists:

1. Check the error message from stderr
2. Use `--json` mode to inspect the full API response
3. Verify AK/SK configuration
4. Test with a simple query first (`"check my balance"`)

---

**💡 Pro Tip**: The most common issue is missing or incorrect AK/SK. Always verify credentials first when encountering errors.

**⚠️ Security**: Keep your AK/SK private. Never commit credentials to version control. Only trade amounts you can afford to lose.

**🚀 Quick Win**: Start by checking your balance to verify setup, then try a small trade like `"buy 1u of ETH"` to get familiar with the flow.
