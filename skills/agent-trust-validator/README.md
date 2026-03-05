# Agent Trust Validator 🛡️

Verify agent credentials across multiple trust protocols and get a unified trust score.

## Quick Start

```bash
# Install dependencies
pip install web3

# Verify by ERC-8004 address
python3 scripts/verify-agent.py --erc8004 0x7f0f...a3b8

# Generate full report
python3 scripts/verify-agent.py --erc8004 0x7f0f...a3b8 --full-report

# Export audit trail
python3 scripts/verify-agent.py --audit audit.json
```

## Features

✅ **Multi-protocol** — ERC-8004, ANS, DID (planned)  
✅ **Trust scoring** — Aggregates signals with custom weights  
✅ **Audit trail** — Logs all verification attempts  
✅ **Local-only** — No private keys stored  

## Trust Score

- **0.8–1.0** — Highly Trusted
- **0.6–0.8** — Trusted
- **0.4–0.6** — Moderate
- **0.0–0.4** — Low/Untrusted

## Protocols

| Protocol | Status |
|----------|---------|
| ERC-8004 | ✅ MVP |
| ANS | 🔄 Planned |
| A2A Registry | 🔄 Planned |
| DID | 🔄 Planned |

## Installation

```bash
git clone https://github.com/orosha-ai/agent-trust-validator
pip install web3
```

## License

MIT
