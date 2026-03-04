# Finance Skill for OpenClaw

Personal finance memory layer for OpenClaw. Parse bank statements, store transactions, query your spending with natural language.

## Features

- **Statement Parsing** — Upload PDF statements, AI extracts transactions automatically
- **Transaction Storage** — Local JSON store, no cloud, your data stays yours
- **Natural Queries** — "How much did I spend on food?" / "Show my biggest expenses"
- **Category Breakdown** — Auto-categorizes: groceries, restaurants, transport, entertainment, etc.

## Installation

```bash
# Clone into your OpenClaw skills directory
cd ~/.openclaw/skills
git clone https://github.com/safaiyeh/finance-skill.git finance
```

Or with ClawHub (coming soon):
```bash
clawhub install finance
```

## Usage

**Parse a statement:**
Share a PDF statement with your OpenClaw agent. It will:
1. Extract all transactions using pypdf
2. Categorize them automatically
3. Store in `~/.openclaw/workspace/finance/transactions.json`

**Query your spending:**
- "How much did I spend last month?"
- "What did I spend on food?"
- "Show my biggest expenses"
- "How much on Uber this year?"

## Data Storage

All data is stored locally:
- `~/.openclaw/workspace/finance/transactions.json` — your transactions
- `~/.openclaw/workspace/finance/statements/` — original statements

No cloud. No sync. Your financial data stays on your machine.

## Scripts

```bash
# Add transactions from JSON
echo '[{"date":"2026-01-15","merchant":"Starbucks","amount":-5.50,"category":"food"}]' | ./scripts/add-transactions.sh "manual"

# Query spending summary
./scripts/query.sh summary

# Query by category
./scripts/query.sh category food

# Search merchants
./scripts/query.sh search starbucks

# Recent transactions
./scripts/query.sh recent 10
```

## Requirements

- OpenClaw
- `jq` (`apt install jq` / `brew install jq`)
- Python 3 with `pypdf` (`pip3 install pypdf`)

## Roadmap

- [ ] Plaid integration for real-time bank sync
- [ ] Multi-currency support
- [ ] Budget tracking & alerts
- [ ] Export to CSV

## License

MIT

---

Built by [@jsontsx](https://x.com/jsontsx) while dogfooding personal finance automation.
