# /setup — Configure API Keys & Wallets

Interactive setup wizard for configuring exchange connections and user profile.

## Behavior

1. Run `npx tsx <skill-path>/scripts/data-store.ts load-config` to get current config
2. Show current configuration status:

```
Portfolio Tracker Setup

Configured wallets:
  1. Binance "My Binance" ✓
  2. IBKR "My IBKR" ✓
  3. Wallet "0x1234...5678" (ETH, BSC) ✓

User Profile: Configured ✓ (Age: 30, Risk: Moderate)

What would you like to configure?
  a) Add Binance API keys
  b) Add IBKR Flex Query credentials
  c) Add blockchain wallet
  d) Set up user profile (for /advise)
  e) Edit existing wallet
  f) Remove a wallet
```

3. Based on user choice, gather the required information:

### Binance Setup
- Ask for API Key and API Secret
- Validate via `npx tsx <skill-path>/scripts/binance-sync.ts validate <apiKey> <apiSecret>`
- Ask for a display name (default: "My Binance")
- Save to config

### IBKR Setup
- Ask for Flex Query Token and Query ID
- Explain: "You can create a Flex Query at IBKR's Account Management > Reports > Flex Queries"
- Validate via `npx tsx <skill-path>/scripts/ibkr-sync.ts validate <token> <queryId>`
- Ask for a display name (default: "My IBKR")
- Save to config

### Blockchain Wallet Setup
- Ask for EVM wallet address
- Validate via `npx tsx <skill-path>/scripts/blockchain-sync.ts validate <address>`
- Ask which chains to monitor (ETH, BSC, POLYGON, ARBITRUM, OPTIMISM) — default: all
- Ask for a display name (default: truncated address)
- Save to config

### User Profile Setup (for /advise)
- Ask for: age, risk tolerance (Conservative/Moderate/Aggressive/Growth), monthly cash flow, investment goal, max acceptable drawdown %
- Save to config under `userProfile`

## Security Notes

- API keys are stored locally in `~/.portfolio-tracker/config.json`
- Never log or display full API keys — always truncate
- Recommend read-only API keys for exchanges
- Config file permissions: suggest `chmod 600 ~/.portfolio-tracker/config.json`

## Notes

- After saving config, remind users they can now use `/sync-binance`, `/sync-ibkr`, or `/sync-wallet`
- If validation fails, show the error and ask if they want to retry or save anyway
