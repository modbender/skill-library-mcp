# Kite AI Agent Smart Wallet Permissionless Protocol - README

## Overview

**Kite AI Agent Smart Wallet Permissionless Protocol** (v1.0.0)

A smart wallet protocol for AI agents built on Kite AI network. Inspired by Biconomy Nexus design, providing extensible, secure wallet infrastructure for autonomous AI agents.

## Features

- 🔐 Session Keys - Temporary authorization with fine-grained permissions
- 💰 Spending Limits - Programmable transaction limits
- 🧩 Modular Architecture - Extensible module system
- 🔄 Upgradable - Support for future enhancements

## Architecture

```
User (Owner) ──授权──► Agent ──使用──► Session Key (临时)
                              └── 可添加多个session key，每个有限额
```

## Deployed Contracts (Kite Testnet)

| Contract | Address |
|----------|---------|
| ModuleRegistry | 0xfdf654b7dDbdFf0C7ec9017Aece166a75a5197B5 |
| SpendingLimitModule | 0x00E593eA476DfC0b22d9DF0A8fe436e5323Ae05F |
| SessionKeyModule | 0x5b6C45EC7C9d7C688413d6bB2CC3B0A35f5B79B8 |
| AgentSmartWalletFactory | 0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a |

## Network

- **Testnet**: Chain ID 2368, RPC https://rpc-testnet.gokite.ai
- **Mainnet**: Chain ID 2366, RPC https://rpc.gokite.ai

## Quick Start

```javascript
// Create wallet
const factory = await ethers.getContractFactory("AgentSmartWalletFactory");
const wallet = await factory.createWallet(agentAddress, limit);

// Add session key
await wallet.addSessionKey(sessionKey, limit, functions);
```

## Documentation

See SKILL.md for detailed documentation.

## Version History

- v1.0.0 (2026-02-25): Initial deployment on Kite AI Testnet
