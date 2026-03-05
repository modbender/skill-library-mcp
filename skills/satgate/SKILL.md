---
name: satgate
description: Manage your API's economic firewall from the terminal. Mint tokens, track spend, revoke agents, enforce budgets. The server-side counterpart to lnget.
homepage: https://satgate.io
---

# SatGate CLI

SatGate CLI manages API access, budgets, and monetization for the agent economy. Use it when you need to control what agents can access and how much they can spend.

**They're the wallet. We're the register.**

If the agent needs to *pay* for L402 APIs, install `lnget` from Lightning Labs. SatGate is for the *server side* — enforcement, attribution, and governance.

## Setup

Run `scripts/configure.sh` if no `~/.satgate/config.yaml` exists. Or set environment variables:

```bash
# For self-hosted gateway
export SATGATE_GATEWAY=http://localhost:9090
export SATGATE_ADMIN_TOKEN=sgk_your_token

# For SatGate Cloud
export SATGATE_SURFACE=cloud
export SATGATE_GATEWAY=https://satgate-gateway.fly.dev
export SATGATE_BEARER_TOKEN=sg_your_api_key
export SATGATE_TENANT=your-tenant-slug
```

Always run `satgate status` first to confirm you're targeting the right gateway.

## Safety Rules

1. **Check target first** — run `satgate status` before any operation to verify gateway URL and surface.
2. **Use `--dry-run`** on destructive operations (`revoke`, `mint` with large budgets).
3. **Never use `--yes`** without explicit user approval.
4. **Revocation is irreversible** — always confirm token name before revoking.

## Commands

### Check gateway health
```bash
satgate status    # Full status (version, surface, uptime)
satgate ping      # Quick liveness check (exit 0/1)
```

### Mint a token for a new agent
```bash
# Interactive (prompts for all fields)
satgate mint

# Non-interactive
satgate mint --agent "my-bot" --budget 500 --expiry 30d --routes "/api/openai/*"

# With parent (delegation under existing token)
satgate mint --agent "child-bot" --budget 100 --parent "parent-token-id"

# Preview without executing
satgate mint --agent "my-bot" --budget 500 --dry-run
```

### Check agent spend
```bash
satgate spend                   # Org-wide cost center rollups
satgate spend --agent "cs-bot"  # Per-agent breakdown
satgate spend --period 7d       # Time-scoped
```

### List and inspect tokens
```bash
satgate tokens                  # All tokens with status, spend, budget
satgate token <id>              # Detail: scope, delegation chain, spend
```

### Revoke a compromised agent
```bash
satgate revoke <token-id>           # Interactive confirmation
satgate revoke <token-id> --dry-run # Preview only
```

### View security threats
```bash
satgate report threats          # Blocked requests, anomalies
```

### Check policy modes
```bash
satgate mode                    # Current mode per route (read-only)
```

## Common Workflows

**"New agent needs API access"**
→ `satgate mint --agent "agent-name" --budget 500 --routes "/api/openai/*"`

**"How much are agents spending?"**
→ `satgate spend`

**"Agent is misbehaving"**
→ `satgate revoke <token-id>`

**"Board wants AI spend report"**
→ `satgate spend --json > report.json`

**"Is the gateway healthy?"**
→ `satgate ping`

## Output Formats

All commands support `--json` for machine-readable output:
```bash
satgate tokens --json | jq '.[] | select(.status == "active")'
satgate spend --json > monthly-report.json
```

## Pairing with lnget

SatGate (server-side) + lnget (client-side) = complete agent commerce stack.

- **lnget**: Agents pay for L402-gated APIs automatically
- **SatGate CLI**: Operators mint tokens, set budgets, revoke access, view spend

An agent using `lnget` hits your SatGate-protected endpoint → SatGate enforces the budget and attributes the cost → you see it in `satgate spend`.

Install lnget: `claude plugin marketplace add lightninglabs/lightning-agent-tools`
