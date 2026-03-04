---
name: StonebornBot
description: High-speed NFT mint bot for Ethereum and EVM chains. Use when the user wants to snipe NFT mints, speed-mint collections, set up multi-wallet minting bots, configure mint sniping with pre-signed transactions, or automate NFT minting across multiple wallets. Supports ERC721A, Archetype contracts, Flashbots, war mode gas, WebSocket monitoring, mempool watching, and batch minting with 100+ wallets.
---

# NFT Mint Bot

Sub-100ms NFT mint sniping bot with multi-wallet support, pre-signed transactions, and multi-RPC broadcasting.

## Quick Start

```bash
# 1. Setup
cd scripts && bash setup.sh && cd ..

# 2. Configure
cp assets/config-template.json scripts/config.json
# Edit scripts/config.json with your RPC URLs, contract, wallets, gas settings

# 3. Run (instant mode — fire immediately)
node scripts/mint-bot.js

# 4. Run (monitor mode — wait for mint to go live)
node scripts/mint-bot.js --mode monitor
```

## Config Overview

Edit `scripts/config.json`. Key sections:

- **rpcUrl / rpcUrls**: Primary and backup RPC endpoints. All used for multi-broadcast.
- **wsRpcUrl**: WebSocket RPC for block subscriptions and mempool watching.
- **contract**: Target contract address, mint function signature, args, price, max per wallet, ABI.
- **gas**: EIP-1559 gas settings (maxFeePerGas, maxPriorityFeePerGas, gasLimit). See [gas-optimization.md](references/gas-optimization.md).
- **wallets**: Array of `{privateKey, label}`. See [wallet-management.md](references/wallet-management.md).
- **monitoring**: Mode (`instant` or `monitor`), interval, WebSocket/mempool options.
- **archetype**: Archetype ERC721a invite-based minting. See [archetype.md](references/archetype.md).
- **flashbots**: Flashbots Protect relay for private tx submission.
- **bankr**: Bankr API integration for managed wallets.
- **retry**: Max retries and delay between attempts.

## Modes

### Instant Mode (`"mode": "instant"`)
Fire transactions immediately. Use when mint is already live or you know the exact block.

### Monitor Mode (`"mode": "monitor"`)
Poll the contract to detect when minting goes live, then fire. Supports:
- **Polling** (`intervalMs`): Check every N ms via staticCall
- **WebSocket blocks** (`useWebSocket: true`): React on new blocks
- **Mempool watching** (`mempoolWatch: true`): Watch pending txs for the mint function

Set `mintLiveCheck` to `"staticCall"` or use `flagFunction` to check a specific view function.

## Archetype ERC721a Support

Enable for Archetype contracts requiring invite-based minting with auth keys and Merkle proofs. See [archetype.md](references/archetype.md).

## War Mode Gas

When `gas.warMode.enabled` is true, the bot auto-escalates gas when the network is congested, capping at configured maximums. See [gas-optimization.md](references/gas-optimization.md).

## Multi-Wallet

Supports 200+ wallets with batched signing. Pre-signs all transactions before broadcast. See [wallet-management.md](references/wallet-management.md).

## Batch Testing

Use `scripts/batch-test.js` to test wallet signing speed and RPC connectivity without sending real transactions.

## Architecture

- **Pre-signed transactions**: All wallets sign before any broadcast
- **Multi-RPC broadcast**: Every signed tx sent to all endpoints simultaneously
- **Raw JSON-RPC**: Bypasses ethers.js overhead for sends
- **Nanosecond timing**: `process.hrtime.bigint()` for precise measurement
- **Configurable batch sizes**: Control parallel signing load
