# ProxyBase Skill for OpenClaw

Purchase and manage residential SOCKS5 proxies through ProxyBase — directly from your OpenClaw agent.

## Features

- **Crypto-only payments** — BTC, ETH, USDCSOL (TRC-20/ERC-20), LTC, SOL, and more
- **Residential SOCKS5 proxies** — US-based, bandwidth-metered
- **Automatic polling** — monitors payment and proxy status
- **Lobster pipeline** — one-call purchase workflow with approval gate
- **Proxy injection** — ENV-based routing for curl, wget, Python, and exec tools

## Installation

### Via ClawHub (recommended)

```bash
clawhub install proxybase
```

### Manual

```bash
# Clone or copy into your skills directory
cp -r proxybase-openclaw-skill/ ~/.openclaw/skills/proxybase/

# Or symlink
ln -s /path/to/proxybase-openclaw-skill ~/.openclaw/skills/proxybase
```

## Zero-Configuration Setup

This skill is designed for **zero configuration**.

You do **not** need to manually register for an API key. 
You do **not** need to edit the `openclaw.json` config file.

The first time you run a ProxyBase command, the skill will automatically register an agent account for you and securely store your API key in its internal state directory.

## Usage

### Quick start (conversational)

Tell your agent:

> "Buy me a 1GB residential proxy and pay with USDCSOL"

The agent will:
1. Register with ProxyBase (first time only)
2. Create an order for `us_residential_1gb`
3. Show you the payment address and amount
4. Poll until payment confirms and proxy activates
5. Give you the SOCKS5 credentials

### Via Lobster pipeline (Recommended)

```json
{
  "action": "run",
  "pipeline": "{baseDir}/pipelines/proxybase-purchase.lobster",
  "argsJson": "{\"package_id\":\"us_residential_5gb\",\"pay_currency\":\"btc\"}",
  "timeoutMs": 120000
}
```

**What is Lobster?**
Lobster is OpenClaw's native pipeline engine for executing multi-step operations that require human intervention. 

When you run this pipeline:
1. It automatically registers your agent (if it's your first time).
2. It generates a crypto payment invoice.
3. *The pipeline pauses and waits for your approval.*
4. Once you send the crypto and approve the step, it begins polling for activation.
5. Finally, it asks if you'd like to inject the proxy globally into your OpenClaw Gateway configuration (which will trigger a restart of your gateway).

### Direct script usage

```bash
# Register agent (first time)
bash proxybase.sh register

# List packages
curl -s "$PROXYBASE_API_URL/packages" -H "X-API-Key: $PROXYBASE_API_KEY"

# Create order
bash proxybase.sh order us_residential_1gb usdcsol

# Poll until active
bash proxybase.sh poll <order_id>

# Poll with extended timeout (BTC/slow chains)
bash proxybase.sh poll <order_id> --max-attempts 200

# Check all orders
bash proxybase.sh status

# Check specific order
bash proxybase.sh status <order_id>

# Remove expired/failed orders
bash proxybase.sh status --cleanup

# Top up bandwidth on active proxy
bash proxybase.sh topup <order_id> us_residential_1gb

# Rotate proxy IP
bash proxybase.sh rotate <order_id>

# Inject proxy into OpenClaw gateway
bash proxybase.sh inject-gateway <order_id>
```

## File Structure

```
proxybase-openclaw-skill/
├── SKILL.md                          # Skill definition (AgentSkills format)
├── README.md                         # This file
├── proxybase.sh                      # Unified CLI (all commands in one file)
├── pipelines/
│   └── proxybase-purchase.lobster    # End-to-end purchase workflow
├── config/
│   └── openclaw-config-snippet.json5 # OpenClaw config template
└── state/                            # Created at runtime
    ├── credentials.env               # Agent ID + API key (chmod 600)
    ├── orders.json                   # Tracked orders
    ├── .proxy-env                    # Active proxy ENV vars (most recent)
    └── .proxy-env-<order_id>         # Per-order proxy ENV vars
```

## Packages

| Package | Bandwidth | Price |
|---------|-----------|-------|
| `us_residential_1gb` | 1 GB | $10 |
| `us_residential_5gb` | 5 GB | $50 |
| `us_residential_10gb` | 10 GB | $100 |

## Supported Currencies

BTC, ETH, LTC, SOL, DOGE, XMR, USDCSOL, USDTERC20, USDTBEP20, USDCSOL, and more.

Default: `usdcsol` (fastest confirmation, lowest fees).

## Proxy Usage

Once active, you can use the proxy in multiple ways:

### 1. Automatic Global Injection (Systemd)

If you used the Lobster pipeline and approved the final step, the proxy credentials have been injected directly into your `~/.config/systemd/user/openclaw-gateway.service` file and the gateway has been restarted. All native OpenClaw Node.js requests and `exec` commands will automatically route through the proxy.

### 2. ENV variables (Targeted)

If you chose not to inject globally, you can dynamically source the proxy environment variables for specific shell executions:

```bash
source state/.proxy-env-<order_id>
curl https://lemontv.xyz/api/ip  # routed through proxy
```

### 3. Per-command

```bash
curl --proxy socks5://USER:PASS@api.proxybase.xyz:1080 https://lemontv.xyz/api/ip
```

### 4. Python

```python
import requests
proxies = {"http": "socks5://USER:PASS@api.proxybase.xyz:1080",
           "https": "socks5://USER:PASS@api.proxybase.xyz:1080"}
r = requests.get("https://lemontv.xyz/api/ip", proxies=proxies)
```

## Order Status Flow

```
payment_pending → confirming → paid → proxy_active
                                   ↘ expired
                                   ↘ failed
                                   ↘ partially_paid
proxy_active → bandwidth_exhausted (topup available)
```

| Problem | Solution |
|---------|----------|
| `jq: command not found` | Install jq: `brew install jq` (macOS) or `apt install jq` (Linux) |
| `curl: command not found` | Install curl from your package manager |
| Order stuck on `payment_pending` | Check the payment address — crypto may not have been sent yet |
| Order `expired` | Payment window closed (usually 60 min). Create a new order |
| `partially_paid` | Insufficient amount sent. Top up the remaining balance |
| Proxy not routing traffic | Check `state/.proxy-env` matches the active order |

## API Reference

Full API docs: `https://api.proxybase.xyz/v1`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | POST | Register new agent |
| `/packages` | GET | List available packages |
| `/currencies` | GET | List payment currencies |
| `/orders` | POST | Create proxy order |
| `/orders/{id}/status` | GET | Check order status |
| `/orders/{id}/topup` | POST | Top up bandwidth |
| `/orders/{id}/rotate` | POST | Rotate proxy credentials |

## License

MIT
