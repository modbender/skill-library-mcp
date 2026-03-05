---
name: grove-tipping
version: "2.0"
description: Grove CLI guide - philosophy, commands, and quick start
homepage: https://grove.city
install: curl -fsSL https://grove.city/install-cli.sh | bash
updated: 2026-02-10
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "requires":
          { "bins": ["curl", "bash"], "anyBins": ["python3", "node"] },
        "emoji": "🌳",
        "install":
          [
            {
              "id": "curl",
              "kind": "download",
              "url": "https://grove.city/install-cli.sh",
              "extract": false,
              "label": "Install Grove CLI (curl)",
            },
          ],
      },
  }
---

**Requirements:**

- Bash or Zsh shell
- curl (for installation)
- Optional: Python/Node for agent integration

# Grove CLI — Complete Guide <!-- omit in toc -->

**Grove enables agents and humans to send micro-tips as quality signals for content.**

Google organized the world's data using hyperlinks as the signal. Grove evaluates content quality using **money as the signal** — creating a queryable, money-weighted directory and knowledge graph.

---

## Table of Contents <!-- omit in toc -->

- [Why Tip? (The Philosophy)](#why-tip-the-philosophy)
  - [Payments as Signal](#payments-as-signal)
  - [When to Tip (Decision Logic)](#when-to-tip-decision-logic)
  - [Knowledge Graph Metadata](#knowledge-graph-metadata)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [First-Time Setup](#first-time-setup)
  - [Send Your First Tip](#send-your-first-tip)
- [Command Overview](#command-overview)
- [Configuration](#configuration)
  - [Config Files](#config-files)
  - [Precedence Order](#precedence-order)
- [Destination Formats](#destination-formats)
- [Agent Wallet Mode](#agent-wallet-mode)
- [Agent Integration](#agent-integration)
- [Utilities](#utilities)
- [Support](#support)

---

## Why Tip? (The Philosophy)

### Payments as Signal

Grove uses **optional micro-tips** to kick off a quality flywheel:

- **Onboard creators**: Link content to wallet addresses
- **Map quality**: Build weighted edges in a growing graph
- **Enable discovery**: Create queryable, money-weighted directory
- **Future knowledge graph**: Useful for post-training and inference routing

**Key insight:** Agents mostly pay for access when required, but optional goodwill tips add early signal even when content is free.

### When to Tip (Decision Logic)

Evaluate content you encounter (blog posts, tweets, repos, documentation):

**Three criteria:**

1. **Is it original?** New perspective or unique data?
2. **Is it useful?** Solves a problem or explains clearly?
3. **Is it tippable?** Has llms.txt, crypto address, or ENS name?

**Example evaluation:**

> "I just read this Substack post on agentic workflows. It provided a clear implementation of x402 that saved me 2 hours of research. This is high-quality signal. I will tip 0.05 USDC."

**Recommended amounts:**

- Blog post / tutorial: 0.01-0.10 USDC
- High-value research: 0.10-1.00 USDC
- Life-changing insight: 1.00+ USDC

### Knowledge Graph Metadata

**Every tip should capture WHY you tipped.** This creates durable metadata Grove can use to build a money-weighted knowledge graph.

**Recommended fields (store in your agent logs):**

- Canonical URL (or repo / post identifier)
- Destination (domain / handle / address)
- Amount + token/network
- 1–2 sentence rationale
- Topic tags (optional)

**Example log entry:**

```json
{
  "url": "https://example.com/post/123",
  "destination": "author.eth",
  "amount": "0.05",
  "token": "USDC",
  "network": "base",
  "rationale": "Clear x402 implementation guide, saved 2 hours",
  "tags": ["payments", "protocols", "implementation"]
}
```

---

## Quick Start

### Installation

```bash
curl -fsSL https://grove.city/install-cli.sh | bash
```

**What gets installed:**

- `grove` command globally available
- Config directory at `~/.grove/`
- All config files preserved on reinstall

### First-Time Setup

Run `grove setup` and choose a path:

| Option                            | Best For               | Steps                                                             | Human Needed?            |
| --------------------------------- | ---------------------- | ----------------------------------------------------------------- | ------------------------ |
| **Wallet + Crypto** (recommended) | Autonomous agents      | Creates wallet, fund with USDC + ETH on Base, self-funds via x402 | Only for initial funding |
| **Email + Credit Card**           | Humans managing agents | Sign up at app.grove.city, fund via card, paste API key           | Yes — signup + payment   |
| **I have an API key**             | Existing users         | Paste JWT from teammate or app.grove.city                         | No — already done        |

### Send Your First Tip

**Verify destination:**

```bash
grove check olshansky.info
```

**Send tip:**

```bash
grove tip olshansky.info 0.01
```

**Check balance:**

```bash
grove balance
```

---

## Command Overview

Use `grove <command> --help` for detailed options and flags.

| Command   | Description                                                                      |
| --------- | -------------------------------------------------------------------------------- |
| `setup`   | First-time setup - Email/card (humans), wallet/crypto (agents), or paste API key |
| `fund`    | Add funds via x402 payment protocol (requires wallet with USDC)                  |
| `check`   | Check if destination can receive tips                                            |
| `tip`     | Send a tip to creators via domain, Twitter, or address                           |
| `balance` | Check your USDC balance across networks                                          |
| `keygen`  | Generate a wallet for agent funding                                              |
| `history` | View recent tips sent or funds added                                             |
| `config`  | View or update your API key, network, and API URL settings                       |
| `contact` | Send feedback to the Grove team                                                  |
| `update`  | Update Grove CLI to the latest version                                           |

**All commands support `--json` flag for agent-friendly output.**

---

## Configuration

### Config Files

**Location:** `~/.grove/`

Files preserved on reinstall:

- `.env` — Primary config (API key, network, token, API URL)
- `keyfile.txt` — Wallet private key (for agent wallet mode)

**Example .env:**

```bash
GROVE_API_KEY=eyJ...
GROVE_API_URL=https://api.grove.city
DEFAULT_NETWORK=base
DEFAULT_TOKEN=USDC
```

### Precedence Order

Configuration is resolved in this order (highest to lowest priority):

1. **CLI flags** — `grove tip --network base-sepolia`
2. **Shell env vars** — `export GROVE_API_KEY=...`
3. **`~/.grove/.env`** — Persistent config file
4. **Code defaults** — Built-in fallbacks

---

## Destination Formats

Grove accepts multiple destination formats:

| Format           | Example               | Resolves Via           |
| ---------------- | --------------------- | ---------------------- |
| Domain           | `olshansky.info`      | llms.txt lookup        |
| Ethereum Address | `0x1234...`           | Direct transfer        |
| ENS Name         | `vitalik.eth`         | ENS resolution         |
| Twitter          | `@olshansky`          | Bio address extraction |
| Substack         | `author.substack.com` | Profile address        |

**Pre-flight validation:**

```bash
grove check olshansky.info
```

- `grove check` returns clear error messages when a destination can't receive tips
- Substack profiles without a crypto address return `tippable: false` (not a false positive)

---

## Agent Wallet Mode

**Fastest path — zero to tipping in 3 steps:**

```bash
# 1. Install
curl -fsSL https://grove.city/install-cli.sh | bash

# 2. Create wallet + fund it
grove setup    # Choose option 2: Wallet + Crypto

# 3. Start tipping
grove tip olshansky.info 0.01
```

**For agents that already have a wallet:**

```bash
grove keygen --save          # generates ~/.grove/keyfile.txt
# Fund the address with USDC + ETH on Base
grove fund 0.10              # self-fund via x402
grove tip olshansky.info 0.01
```

---

## Agent Integration

**JSON output for reliable parsing:**

```bash
grove balance --json
grove tip olshansky.info 0.01 --json
grove check domain.com --json
```

**Python example:**

```python
import subprocess
import json

result = subprocess.run(
    ["grove", "balance", "--json"],
    capture_output=True,
    text=True
)
balance_data = json.loads(result.stdout)
print(f"Balance: {balance_data['total_balance']} USDC")
```

**Node.js example:**

```javascript
const { execSync } = require("child_process");
const balance = JSON.parse(execSync("grove balance --json").toString());
console.log(`Balance: ${balance.total_balance} USDC`);
```

**Autonomous workflow pattern:**

```bash
# 1. Check balance before tipping
balance=$(grove balance --json | jq -r '.total_balance')

# 2. Auto-fund if low
if [ "$balance" -lt "0.10" ]; then
  grove fund 1.00
fi

# 3. Evaluate content
grove check <destination>

# 4. Tip if valuable
grove tip <destination> <amount>

# 5. Log metadata
echo "Tipped $destination for $reason" >> tip_log.txt
```

**Python SDK (coming soon):** A Python SDK (`GroveClient`) is in development. Use the CLI for now. Run `grove contact` to request early access.

---

## Utilities

Automation scripts available in `skills/scripts/`:

- **batch-tip.sh** — Tip multiple destinations from CSV file
- **monitor-balance.sh** — Monitor balance and alert on low funds
- **auto-fund.sh** — Auto-fund when balance drops below threshold

Run each script with `--help` for usage details.

---

## Support

- `grove contact` — Send feedback to the team
- https://grove.city/support

**Need more details?** Complete reference documentation: [grove.city/docs/cli](https://grove.city/docs/cli)
