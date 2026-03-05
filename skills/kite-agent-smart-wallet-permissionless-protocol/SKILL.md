# Kite AI Agent Smart Wallet Permissionless Protocol

> Version: 1.0.0
> Build on Kite AI Testnet
> Smart wallet protocol for AI agents with modular architecture

## Overview

Kite AI Agent Wallet Protocol enables AI agents to create and manage smart wallets on Kite AI network. Inspired by Biconomy Nexus design, this protocol provides extensible, secure wallet infrastructure for autonomous AI agents.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              AgentSmartWalletFactory                         │
│         (Wallet Factory - Batch Creation)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              AgentSmartWallet                                │
│  - owner: Human user (root authority)                      │
│  - agent: AI agent (delegated authority)                  │
│  - sessionKeys: Temporary keys (automation)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│SpendingLimit    │    │SessionKey       │
│Module           │    │Module           │
└─────────────────┘    └─────────────────┘
```

## Core Features

- 🔐 **Session Keys** - Temporary authorization keys with fine-grained permissions
- 💰 **Spending Limits** - Programmable transaction limits
- 🧩 **Modular Architecture** - Extensible module system
- 🔄 **Iterative Capability** - Support for upgrades and new modules

## Security Features

1. **Layered Permissions**: Owner > Agent > Session Key
2. **Limit Protection**: Transactions cannot exceed set limits
3. **Revocable**: Owner can revoke session keys anytime
4. **Module Isolation**: Functional modules can be replaced

## Deployed Contracts (Testnet)

| Contract | Address |
|----------|---------|
| ModuleRegistry | `0xfdf654b7dDbdFf0C7ec9017Aece166a75a5197B5` |
| SpendingLimitModule | `0x00E593eA476DfC0b22d9DF0A8fe436e5323Ae05F` |
| SessionKeyModule | `0x5b6C45EC7C9d7C688413d6bB2CC3B0A35f5B79B8` |
| AgentSmartWalletFactory | `0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a` |

## Network Configuration

### Testnet (Ozone)
- Chain ID: 2368
- RPC: https://rpc-testnet.gokite.ai
- Explorer: https://testnet.kitescan.ai
- Faucet: https://faucet.gokite.ai

### Mainnet
- Chain ID: 2366
- RPC: https://rpc.gokite.ai
- Explorer: https://kitescan.ai

## Usage

### 1. Create Wallet

```javascript
const factory = await ethers.getContractFactory("AgentSmartWalletFactory");
const wallet = await factory.createWallet(agentAddress, ethers.utils.parseEther("1"));
```

### 2. Add Session Key

```javascript
const wallet = await ethers.getContractAt("AgentSmartWallet", walletAddress);
await wallet.addSessionKey(
    sessionKeyAddress,      // Agent's session key
    ethers.utils.parseEther("0.1"), // Limit
    [bytes4("0x...")]     // Allowed function selectors
);
```

### 3. Agent Executes Transaction

```javascript
// Agent uses session key to execute
await wallet.executeWithSessionKey(
    encodedData,  // (target, value, callData)
    signature     // Owner signature
);
```

## Expandability

Protocol supports:
- Add new modules (TimeLock, MultiSig)
- Upgrade wallet logic
- Cross-chain compatibility (Via Protocol Bridge)

## References

- [Kite AI Docs](https://docs.gokite.ai)
- [Biconomy Nexus](https://docs.biconomy.io/new/learn-about-biconomy/nexus)
- [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)
- [ERC-7579](https://eips.ethereum.org/EIPS/eip-7579)

---

**Version History**
- v1.0.0 (2026-02-25): Initial deployment on Kite AI Testnet
