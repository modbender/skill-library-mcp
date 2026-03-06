# Ordiscan

Inscribe content on Bitcoin and query ordinals data via the Ordiscan API. Pays per-request with USDC on Base using the x402 protocol — no API key needed.

## Install from ClawHub

```bash
clawhub install ordiscan
```

## Install from git

Clone into your OpenClaw skills directory:

```bash
git clone https://github.com/ordiscan/ordiscan-skill.git ~/.openclaw/skills/ordiscan
```

## Requirements

The [`awal` CLI](https://github.com/coinbase/awal) (Coinbase Agentic Wallet) must be installed and authenticated. Verify with:

```bash
npx awal status
```

If not authenticated, run `npx awal` and follow the setup flow.

## Docs

Full API documentation: https://ordiscan.com/docs/api
