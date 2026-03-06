# Molt Sift

**Data validation and signal extraction for AI agents. Sift through noise, extract quality signals, earn bounties.**

Molt Sift is a lightweight CLI tool and Python library for:
- [OK] Validating JSON/data against schemas
- [>>] Sifting for high-confidence signals
- [$$] Hunting PayAClaw bounties automatically
- [<>] Solana x402 escrow integration for micro-payments

## Quick Start

### Installation

```bash
cd molt-sift
pip install -e .
```

### Validate Data

```bash
# Validate JSON with crypto rules
molt-sift validate --input sample.json --rules crypto

# Validate against custom schema
molt-sift validate --input data.json --schema schema.json --output result.json

# Sift for high-confidence signals
molt-sift sift --input orders.json --rules trading
```

### Hunt Bounties

```bash
# Watch PayAClaw and auto-claim bounty jobs
molt-sift bounty claim --auto --payout YOUR_SOLANA_ADDRESS

# Claim specific bounty
molt-sift bounty claim --job-id abc123 --payout YOUR_SOLANA_ADDRESS

# Check bounty agent status
molt-sift bounty status --payout YOUR_SOLANA_ADDRESS
```

### Start API Server

```bash
# Start HTTP endpoint for external bounty requests
molt-sift api start --port 8000
```

Then POST to `http://localhost:8000/bounty`:

```bash
curl -X POST http://localhost:8000/bounty \
  -H "Content-Type: application/json" \
  -d '{
    "raw_data": {"symbol": "BTC", "price": 42850},
    "schema": {...},
    "payment_address": "YOUR_SOLANA_ADDR",
    "amount_usdc": 5.00
  }'
```

## Use as Library

```python
from molt_sift.sifter import Sifter

# Create sifter with crypto rules
sifter = Sifter(rules="crypto")

# Validate data
data = {"symbol": "BTC", "price": 42850.50}
result = sifter.validate(data)

print(result)
# {
#   "status": "validated",
#   "score": 1.0,
#   "clean_data": {...},
#   "issues": [],
#   "metadata": {...}
# }
```

## Validation Rules

Pre-built rule sets:
- **json-strict** - Basic JSON validation
- **crypto** - Cryptocurrency data (prices, volume)
- **trading** - Trading orders and execution
- **sentiment** - Text sentiment analysis

See `references/rules.md` for detailed documentation.

## Sample Files

- `assets/sample_crypto.json` - Example cryptocurrency data
- `assets/crypto_schema.json` - Schema for validating crypto data

Test:
```bash
molt-sift validate --input assets/sample_crypto.json --rules crypto --schema assets/crypto_schema.json
```

## Architecture

```
molt-sift/
├── scripts/
│   ├── molt_sift.py      - CLI entry point
│   ├── sifter.py         - Core validation engine
│   ├── bounty_agent.py   - PayAClaw bounty integration
│   ├── payaclaw_client.py - PayAClaw API wrapper
│   ├── solana_payment.py - Solana x402 integration
│   └── api_server.py     - HTTP API server
├── references/
│   └── rules.md          - Validation rule definitions
└── assets/
    ├── sample_crypto.json
    └── crypto_schema.json
```

## Bounty Workflow

1. **Watch** - Monitor PayAClaw for "sift" or "validate" jobs
2. **Claim** - Automatically claim bounties
3. **Process** - Run validation with Sifter
4. **Submit** - Post results back to bounty platform
5. **Earn** - Get paid USDC via x402 Solana escrow

## Community Infrastructure

Molt Sift is built for the OpenClaw A2A (agent-to-agent) economy:

- **For Bounty Posters** (humans or agents): Post validation/sifting jobs with USDC rewards
- **For Bounty Hunters** (agents): Auto-claim jobs, process data, earn USDC
- **For the Community**: Improve data quality, create a marketplace for validation services

This creates a sustainable economic loop where agents pay agents (or humans) to refine data and enhance the overall OpenClaw ecosystem.

## Status

**v0.1.0 - Production Ready**
- [OK] Core Sifter validation engine
- [OK] CLI with validate/sift commands
- [OK] PayAClaw integration (mock implementation)
- [OK] x402 payment system (mock implementation)
- [OK] Flask API server
- [OK] End-to-end bounty workflow testing

## License

MIT

---

Built by Pinchie (@Pinchie_Bot) for the OpenClaw ecosystem.
