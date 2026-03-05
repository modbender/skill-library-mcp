---
name: fluora-balance
description: Check USDC balance on Base Mainnet for your Fluora wallet. Use when the user asks about their Fluora balance, wallet balance, USDC balance, or how much money they have in their Fluora account.
---

# Fluora Balance

Check your USDC balance on Base Mainnet for the wallet configured in Fluora.

## Quick Start

Run the balance check script:

```bash
cd scripts/
npm install  # First time only
node check_balance.js
```

The script will:
1. Read your mainnet wallet address from `~/.fluora/wallets.json`
2. Query the USDC balance on Base Mainnet
3. Display the formatted balance

## Script Details

**Location:** `scripts/check_balance.js`

**What it does:**
- Reads wallet address from `~/.fluora/wallets.json` (USDC_BASE_MAINNET.address field)
- Connects to Base Mainnet via `https://mainnet.base.org`
- Queries USDC contract at `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Returns formatted balance in USDC

**Output format:**
```
Checking USDC balance on Base Mainnet...

Wallet: 0x7DC445b40719ab482090...
Balance: 1.234567 USDC
```

**JSON output:** Add `--json` flag for programmatic parsing:
```bash
node check_balance.js --json
```

## Dependencies

The script requires `ethers` (v6+) for blockchain interaction:
```bash
cd scripts/
npm install
```

Dependencies are listed in `scripts/package.json`.

## Troubleshooting

**Error: ~/.fluora/wallets.json not found**
- Ensure Fluora is properly set up
- Run the fluora-setup skill if needed

**Error: No USDC_BASE_MAINNET wallet address found**
- Check that `wallets.json` contains a `USDC_BASE_MAINNET.address` field
- Regenerate wallet if necessary

**Network errors**
- Verify internet connection
- Base Mainnet RPC may be temporarily unavailable (retry)
