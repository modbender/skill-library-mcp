# Agent Wallet

> On-chain spend limits for autonomous AI agents on Base.

Deploy a smart contract wallet with enforced per-transaction and daily budget caps. Your agent transacts freely within limits — anything over-limit queues for your approval.

[![Tests](https://img.shields.io/badge/tests-163%2F163-brightgreen)]() [![Base Mainnet](https://img.shields.io/badge/Base-Mainnet-blue)]() [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

## Quick Start

```bash
npm install @agentwallet/sdk
```

```typescript
import { createWallet, agentTransferToken } from '@agentwallet/sdk';

// 1. Connect to the agent's wallet
const wallet = createWallet({
  accountAddress: '0x...',
  chain: 'base',
  walletClient
});

// 2. Set spend limits (owner)
await wallet.setSpendLimit({
  token: USDC,
  maxPerTx: parseUnits('100', 6),    // $100 max per transaction
  periodLimit: parseUnits('500', 6),  // $500/day budget
  periodDuration: 86400               // 24h rolling period
});

// 3. Agent spends autonomously within limits
await agentTransferToken(wallet, { token: USDC, to: recipient, amount });

// 4. Over-limit? Auto-queued for approval
wallet.onTransactionQueued((tx) => {
  notify(`Approval needed: $${tx.amount}`);
});
```

## Deployed Addresses

| Network | Contract | Address |
|---------|----------|---------|
| **Base Mainnet** | AgentAccountFactoryV2 | [`0x700e9Af71731d707F919fa2B4455F27806D248A1`](https://basescan.org/address/0x700e9Af71731d707F919fa2B4455F27806D248A1) |
| **Base Sepolia** | AgentAccountFactoryV2 | [`0x337099749c516B7Db19991625ed12a6c420453Be`](https://sepolia.basescan.org/address/0x337099749c516B7Db19991625ed12a6c420453Be) |

Source verified on BaseScan (both networks).

## Architecture

```
NFT (ERC-721)
  └── Token Bound Account (ERC-6551)
       ├── Owner: NFT holder (full control)
       ├── Operators: Scoped access with epoch invalidation
       ├── Spend Limits: Per-token, per-period, enforced on-chain
       ├── Approval Queue: Over-limit txs via ERC-4337
       └── Factory: CREATE2 deterministic addresses
```

### Key Design Decisions

- **ERC-6551 Token Bound Accounts** — Wallet ownership tied to an NFT. Transfer the NFT, transfer the wallet.
- **ERC-4337 Account Abstraction** — Gasless transactions via paymasters. Agents never need ETH for gas.
- **Operator Epochs** — All operator permissions auto-invalidate when the NFT transfers. Prevents stale access after ownership change.
- **Fixed-Window Periods** — Budget periods use floor division to prevent boundary double-spend.

## Security

### What's Enforced On-Chain
- Per-transaction spend limits per token
- Rolling period budget caps per token
- Operator permission scoping with epoch invalidation
- Reentrancy guards on all mutating functions
- NFT burn protection (clean revert, no fund lock)

### Audit Status

> **Security reviewed internally (2 rounds of AI-assisted adversarial review). No third-party audit has been performed.**

- **Round 1:** Standard security review — reentrancy vectors, access control, input validation
- **Round 2:** Adversarial red-team — flash-loan NFT hijack, stale operators, 4337 queue DoS, period boundary double-spend, NFT burn fund lock

All findings fixed and verified with exploit-specific tests. Reports:
- [`AUDIT_REPORT.md`](./AUDIT_REPORT.md)
- [`AUDIT_REPORT_V2.md`](./AUDIT_REPORT_V2.md)

### Test Results
- **129/129 Solidity tests passing** (Unit, Exploit, Invariant, Factory, Router, 4337, Escrow, Entitlements, CCTP, A2A)
- **34/34 SDK tests passing** (wallet creation, spend limits, operators, transactions, edge cases)
- Foundry-based (`forge test`)

## Project Structure

```
smart-contracts/
  src/
    AgentAccountV2.sol          — Core wallet contract
    AgentAccountV2_4337.sol     — ERC-4337 variant
    AgentAccountFactoryV2.sol   — CREATE2 factory
  test/
    AgentAccountV2.t.sol        — Unit tests (26)
    ExploitTests.t.sol          — Exploit verification (7)
    InvariantTests.t.sol        — Invariant violation tests (3)
agent-wallet-sdk/               — TypeScript SDK (@agentwallet/sdk)
  src/                          — SDK source
  test/                         — SDK tests (25)
  examples/                     — Usage examples
  landing/                      — Landing page
```

## Known Issues

See [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for a transparent list of limitations, unfixable dependency vulnerabilities, and items we're monitoring.

## License

MIT — see [LICENSE](./LICENSE)
