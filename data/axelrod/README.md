# Axelrod — Base Chain Trading Skill for OpenClaw

[AIxVC AI Automation](https://aixvc.io/chat) **skill pack** for [OpenClaw](https://github.com/openclaw/openclaw) (also known as Moltbot).

Axelrod enables every OpenClaw agent to trade, query, and automate strategies on the **Base chain** through the AIxVC AI Automation. It supports spot buy/sell/swap, DCA, limit/trigger orders, RSI strategies, token analysis, balance and price queries, order management, and take-profit/stop-loss orders — all via natural language commands.

This skill runs via a Python CLI at **scripts/axelrod_chat.py**, which calls the AIxVC AI Automation with AK/SK SigV4-style signing and returns human-readable results to the agent.

## Installation

1. Clone the axelrod repository:

   ```bash
   git clone https://github.com/AIxVC-Team/axelrod.git
   ```

2. **Add the skill directory** to OpenClaw config (`~/.openclaw/openclaw.json`):

   ```json
   {
     "skills": {
       "load": {
         "extraDirs": ["/path/to/axelrod"]
       }
     }
   }
   ```

   Use the path to the root of this skill (the skill lives at `SKILL.md`; the script is at `scripts/axelrod_chat.py`).

3. **Install dependencies** (required for the CLI):

   ```bash
   pip install -r skills/axelrod/requirements.txt
   ```

## Configure Credentials

**Configure credentials** under `skills.entries.axelrod.env`:

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

| Variable             | Description                                        |
| -------------------- | -------------------------------------------------- |
| `AIXVC_ACCESS_KEY`   | AIxVC OpenAPI access key (AK).                     |
| `AIXVC_SECRET_KEY`   | AIxVC OpenAPI secret key (SK), used for signing.   |

To obtain the credentials:

1. Contact the AIxVC team or visit the AIxVC platform to register your agent.
2. Generate an AK/SK pair with AI Automation OpenAPI access enabled.
3. Save the keys to the OpenClaw config as shown above.

### Verify Setup

```bash
python skills/axelrod/scripts/axelrod_chat.py --message "check my balance"
```

> **⚠️ Note**: If the API returns "please login first", it means your AK/SK is incorrect. Please double-check and reconfigure your credentials.

## How It Works

- The skill exposes one entry point: **`axelrod`** via `SKILL.md`.
- The agent calls the CLI script **scripts/axelrod_chat.py** with a `--message` flag containing the user's natural language instruction.
- The script signs the request using AK/SK with AWS SigV4-style headers and sends it to the AIxVC AI Automation  OpenAPI gateway.
- The gateway returns a structured JSON response; the script extracts the user-facing reply and prints it to stdout.

**Tools** (via CLI):

| Command | Purpose |
| ------- | ------- |
| `--message "<instruction>"` | Send a natural language trading/query instruction to AIxVC |
| `--message "<instruction>" --json` | Same as above, but print the full JSON response for debugging |

## Capabilities Overview

### Trading Operations

- **Spot Buy/Sell/Swap**: Exchange tokens on Base chain
- **DCA**: Dollar-cost averaging automation
- **Limit/Trigger Orders**: Execute at target prices or PnL rates
- **RSI Strategy**: Conditional trading based on RSI indicators
- **Take-Profit / Stop-Loss**: Automated risk management orders (TP/SL)

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

When a trade requires risk-control confirmation, the API response includes a `confirmKey`. The agent must guide the user to confirm or cancel:

- **Execute**: `yes, please execute <confirmKey>`
- **Cancel**: `no, please cancel <confirmKey>`

`confirmKey` is valid for approximately **10 minutes**. Small orders (≈ ≤ $10) may skip confirmation.

## Current Limitations

- **Chain**: Base only
- **Not supported**: Leverage/futures/options, lending, cross-chain bridge, NFT trading, fiat on/off-ramp
- Multiple independent trades in one message should be split into separate requests

## Prompt Examples

### Trading

- `"buy 50u of AXR"`
- `"sell 50% of my ETH"`
- `"swap 10 SOL to ETH"`
- `"DCA 20u into ETH every day"`
- `"if 1h RSI < 30, buy 100u BTC"`
- `"buy ETH when price drops to 2500"`

### Queries

- `"check my balance"`
- `"show AXR token info"`
- `"what is ETH price now"`
- `"show my recent orders"`
- `"show my TP/SL orders"`

### Assistant

- `"analyze AXR token for me"`
- `"help me make a Base trading plan"`

## API Reference

For the full API contract, signing protocol, and response format, see:

**Reference**: [references/api.md](references/api.md)

## Repository Structure

```
axelrod/
├── SKILL.md              # Skill instructions for the agent
├── README.md             # This file — setup and usage guide
├── requirements.txt      # Python dependencies
├── references/
│   └── api.md            # API contract and signing reference
└── scripts/
    └── axelrod_chat.py   # CLI client (AK/SK SigV4-signed)
```

---

**💡 Pro Tip**: Always specify token amounts clearly (e.g. `"buy 50u of AXR"` or `"sell 50% of my ETH"`) to avoid ambiguity.

**⚠️ Security**: Keep your AK/SK private. Never commit credentials to version control. Start with small test amounts.

**🚀 Quick Win**: Start by checking your balance (`"check my balance"`) to verify setup, then try a small trade on Base.
