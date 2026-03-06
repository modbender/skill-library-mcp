---
name: ClawPurse Skill
description: Local Timpi/NTMPI wallet for agentic AI, automation scripts, and
  individual users on the Neutaro chain.
---

# ClawPurse Skill

Local Timpi/NTMPI wallet for agentic AI, automation scripts, and individual users on the Neutaro chain.

## Overview

ClawPurse provides cryptocurrency wallet functionality for AI agents (including OpenClaw), automation pipelines, and human operators—enabling autonomous or manual handling of NTMPI tokens on the Neutaro blockchain.

## Capabilities

- **Check wallet balance** – Query current NTMPI holdings
- **Send tokens** – Transfer NTMPI to any Neutaro address
- **Receive tokens** – Get wallet address for incoming payments
- **View transaction history** – List recent send/receive activity
- **Verify chain status** – Check connectivity to Neutaro network
- **Stake tokens** – Delegate NTMPI to validators for rewards (v2.0)
- **Manage delegations** – View, redelegate, and unstake tokens (v2.0)

## Installation

```bash
# In the ClawPurse directory
npm install && npm run build && npm link
```

This makes the `clawpurse` CLI available globally.

## Setup

A wallet must be initialized before first use:

```bash
clawpurse init --password <secure-password>
```

> **Important**: Back up the mnemonic shown during init immediately!

## Environment

Set `CLAWPURSE_PASSWORD` to avoid passing password on every command:

```bash
export CLAWPURSE_PASSWORD=<password>
```

## Commands

### Status Check
```bash
clawpurse status
```
Returns chain connection status, chain ID, and current block height.

### Balance
```bash
clawpurse balance
```
Returns current NTMPI balance.

### Address
```bash
clawpurse address
```
Returns the wallet's Neutaro address.

### Send
```bash
clawpurse send <to-address> <amount> [--memo "text"] [--yes]
```
Sends NTMPI to the specified address. Use `--yes` to skip confirmation for amounts > 100 NTMPI.

### History
```bash
clawpurse history [--limit N]
```
Shows recent transactions.

### Allowlist Management
```bash
clawpurse allowlist list              # View trusted destinations
clawpurse allowlist add <addr>        # Add destination
clawpurse allowlist remove <addr>     # Remove destination
```

### Staking (v2.0)
```bash
clawpurse validators                  # List active validators
clawpurse delegations                 # View current delegations
clawpurse stake <validator> <amount>  # Delegate tokens
clawpurse unstake <validator> <amount> --yes  # Undelegate (22-day unbonding)
clawpurse redelegate <from> <to> <amount>     # Move stake between validators
clawpurse unbonding                   # Show pending unbonding
```

**Staking for agents:**
```
1. Run: clawpurse validators
2. Select validator with good uptime and reasonable commission
3. Run: clawpurse stake <validator> <amount> --yes
4. Monitor with: clawpurse delegations
5. Rewards auto-deposit to liquid balance on Neutaro
```

## Safety Features

- **Max send limit**: 1000 NTMPI per transaction (configurable)
- **Confirmation required**: Above 100 NTMPI
- **Address validation**: Only `neutaro1...` addresses accepted
- **Destination allowlist**: Optional enforcement of trusted recipients
- **Encrypted keystore**: AES-256-GCM with scrypt key derivation

## Agent Usage Patterns

### Check Balance Before Operations
```
Before any payment task, run:
clawpurse balance

Parse the output to get available funds.
```

### Making Payments
```
1. Verify recipient is in allowlist (or use --override-allowlist)
2. Run: clawpurse send <address> <amount> --memo "reason" --yes
3. Capture the tx hash from output
4. Share tx hash with recipient for verification
```

### Receiving Payments
```
1. Run: clawpurse address
2. Share the address with the sender
3. After expected payment, run: clawpurse balance
4. Or query chain directly to verify specific tx
```

## Programmatic API

For advanced integrations, import ClawPurse functions directly:

```typescript
import {
  loadKeystore,
  getBalance,
  send,
  getChainInfo,
} from 'clawpurse';

// Load wallet
const { wallet, address } = await loadKeystore(process.env.CLAWPURSE_PASSWORD);

// Check balance
const balance = await getBalance(address);
console.log(balance.primary.displayAmount);

// Send tokens
const result = await send(wallet, address, 'neutaro1...', '10.5', {
  memo: 'Service payment',
  skipConfirmation: true,
});
console.log(`Sent! TxHash: ${result.txHash}`);
```

## Security Notes

- **Never expose the mnemonic** in logs or outputs
- **Use environment variables** for the password, not command-line args in scripts
- **Enable allowlist enforcement** to prevent sends to unknown addresses
- **Monitor receipts** at `~/.clawpurse/receipts.json` for audit

## Files

| Path | Purpose |
|------|---------|
| `~/.clawpurse/keystore.enc` | Encrypted wallet (mode 0600) |
| `~/.clawpurse/receipts.json` | Transaction receipts |
| `~/.clawpurse/allowlist.json` | Trusted destinations |

## Documentation

- [OPERATOR-GUIDE.md](./docs/OPERATOR-GUIDE.md) – Full setup and usage guide
- [TRUST-MODEL.md](./docs/TRUST-MODEL.md) – Security and verification
- [ALLOWLIST.md](./docs/ALLOWLIST.md) – Destination allowlist system

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Wallet not found" | Run `clawpurse init` first |
| "Status: DISCONNECTED" | Check network; RPC may be down |
| "Amount exceeds limit" | Adjust `maxSendAmount` in config |
| "Destination blocked" | Add to allowlist or use `--override-allowlist` |
