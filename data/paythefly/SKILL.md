---
name: paythefly
description: Create crypto payment & withdrawal links for your app. Works with BSC, Ethereum, TRON. Users pay via PayTheFlyPro gateway - you get shareable URLs with built-in signature verification.
homepage: https://pro.paythefly.com
metadata: {"clawdbot":{"emoji":"💸","requires":{"bins":["node","npm"],"env":["PTF_PROJECT_ID","PTF_CONTRACT_ADDRESS","PTF_SIGNER_KEY","PTF_CHAIN_ID"]},"primaryEnv":"PTF_PROJECT_ID"}}
---

# PayTheFlyPro

Generate EIP-712 signed payment and withdrawal links for [PayTheFlyPro](https://pro.paythefly.com) crypto payment gateway. Supports BSC, Ethereum, and TRON networks.

## Security Notice

**The signer private key (`PTF_SIGNER_KEY`) is used ONLY for signing order authorization messages (EIP-712/TIP-712). It does NOT have access to any funds.**

Recommendations:
- Generate a **dedicated wallet** for signing - do NOT use your main wallet
- The signer wallet does not need to hold any funds
- Register the signer address in PayTheFlyPro dashboard as your project's authorized signer

## Install Dependencies

```bash
npm install ethers tronweb
```

## Create Payment Link

```bash
node {baseDir}/scripts/payment.mjs --amount "0.01" --serialNo "ORDER001"
node {baseDir}/scripts/payment.mjs --amount "100" --serialNo "ORDER002" --token "0x55d398326f99059fF775485246999027B3197955"
node {baseDir}/scripts/payment.mjs --amount "50" --serialNo "ORDER003" --redirect "https://mystore.com/success" --brand "MyStore"
```

### Options

- `--amount <value>`: Payment amount (required)
- `--serialNo <value>`: Unique order number (required)
- `--token <address>`: Token contract address (omit for native token)
- `--redirect <url>`: URL to redirect after payment
- `--brand <name>`: Custom brand name
- `--lang <code>`: UI language (en, zh, ko, ja)
- `--deadline <hours>`: Signature validity hours (default: 24)

## Create Withdrawal Link

```bash
node {baseDir}/scripts/withdrawal.mjs --amount "100" --serialNo "WD001" --user "0x1234567890123456789012345678901234567890"
node {baseDir}/scripts/withdrawal.mjs --amount "50" --serialNo "WD002" --user "0xabcd..." --token "0x55d398..."
```

### Options

- `--amount <value>`: Withdrawal amount (required)
- `--serialNo <value>`: Unique withdrawal number (required)
- `--user <address>`: Recipient wallet address (required)
- `--token <address>`: Token contract address (omit for native)
- `--redirect <url>`: URL to redirect after withdrawal
- `--brand <name>`: Custom brand name
- `--lang <code>`: UI language
- `--deadline <hours>`: Signature validity hours (default: 24)

## Query Order Status

```bash
node {baseDir}/scripts/query.mjs --type payment --serialNo "ORDER001"
node {baseDir}/scripts/query.mjs --type withdrawal --serialNo "WD001"
```

### Options

- `--type <value>`: Order type: `payment` or `withdrawal` (required)
- `--serialNo <value>`: Serial number to query (required)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PTF_PROJECT_ID` | Yes | PayTheFlyPro project identifier |
| `PTF_CONTRACT_ADDRESS` | Yes | Project smart contract address |
| `PTF_SIGNER_KEY` | Yes | Private key for signing (dedicated wallet, no funds needed) |
| `PTF_CHAIN_ID` | Yes | Chain ID (56, 97, 1, tron:mainnet, tron:nile) |
| `PTF_CUSTOM_RPC` | No | Custom RPC endpoint |

## Supported Chains

| Chain | chainId | Native Token |
|-------|---------|--------------|
| BSC Mainnet | 56 | BNB |
| BSC Testnet | 97 | BNB |
| Ethereum | 1 | ETH |
| TRON Mainnet | tron:mainnet | TRX |
| TRON Nile | tron:nile | TRX |

## Notes

- Each serial number can only be used once
- Withdrawal signatures expire after deadline (default 24 hours)
- For TRON, addresses use Base58 format (starting with T)
- Native token payments omit the `--token` parameter
