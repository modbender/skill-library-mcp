# CLAUDE.md

This repository contains a Clawdbot/OpenClaw skill for earning yield on USDC via the Moonwell Flagship USDC vault on Morpho (Base network).

## Repository Structure

```
openclaw-morpho-earn/
├── SKILL.md              # Main skill definition (loaded by agents)
├── scripts/              # Executable TypeScript scripts
│   ├── config.ts         # Shared configuration and utilities
│   ├── setup.ts          # Interactive setup wizard
│   ├── status.ts         # Check position and vault stats
│   ├── report.ts         # Generate formatted reports
│   ├── deposit.ts        # Deposit USDC into vault
│   ├── withdraw.ts       # Withdraw USDC from vault
│   ├── rewards.ts        # Check/claim Merkl rewards
│   └── compound.ts       # Auto-compound (claim → swap → deposit)
├── references/           # Additional documentation
│   └── setup.md          # Detailed setup instructions
├── README.md             # Human-readable documentation
└── CLAUDE.md             # This file (agent instructions)
```

## Key Concepts

### Vault
- **Address:** `0xc1256Ae5FF1cf2719D4937adb3bbCCab2E00A2Ca`
- **Chain:** Base (8453)
- **Asset:** USDC
- The vault is an ERC-4626 vault on Morpho, curated by Moonwell

### Rewards
- WELL and MORPHO tokens are distributed via Merkl
- Rewards accrue over time and must be claimed
- The compound script swaps rewards to USDC via Odos aggregator

### Configuration
- Wallet config: `~/.config/morpho-yield/config.json`
- Preferences: `~/.config/morpho-yield/preferences.json`

## Common Tasks

### Check Position
```bash
cd scripts && npx tsx status.ts
```

### Generate Report for User
```bash
cd scripts && npx tsx report.ts          # Telegram/Discord format
cd scripts && npx tsx report.ts --json   # JSON for automation
```

### Deposit Funds
```bash
cd scripts && npx tsx deposit.ts <amount>
```

### Compound Rewards
```bash
cd scripts && npx tsx compound.ts
```
This will:
1. Check for claimable Merkl rewards and claim them
2. Swap WELL and MORPHO to USDC via Odos
3. Deposit the USDC into the vault

### Withdraw Funds
```bash
cd scripts && npx tsx withdraw.ts <amount>
cd scripts && npx tsx withdraw.ts all    # Withdraw everything
```

## Important Notes

### Gas Buffer
The Odos aggregator sometimes underestimates gas for complex swap routes. The compound script adds a 50% gas buffer automatically.

### Nonce Management
When executing multiple transactions rapidly, be aware of nonce conflicts. The scripts wait for transaction confirmation before proceeding.

### RPC
Default RPC is `https://rpc.moonwell.fi/main/evm/8453`. This is more reliable than public RPCs which may rate-limit.

### Minimum Compound Threshold
Default is $0.50 in rewards before compounding. This ensures gas costs don't exceed the reward value for small positions.

## Branding

When mentioning Moonwell, use the double moon emoji: 🌜🌛

Example: "🌜🌛 Moonwell Yield Report"

## Security

- Never log or expose private keys
- Always show transaction previews before execution
- This skill handles real funds — test with small amounts first
- The wallet should be a dedicated hot wallet, not a user's main wallet
