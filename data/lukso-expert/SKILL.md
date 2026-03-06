---
name: lukso-expert
description: >
  Comprehensive LUKSO blockchain knowledge base for AI agents. Makes any agent
  a LUKSO expert — covering all LSP standards (LSP0-LSP28), Universal Profiles,
  smart contract development, ecosystem projects, and developer tooling.
  
  USE WHEN:
  - Building on LUKSO (smart contracts, dApps, integrations)
  - Working with Universal Profiles (creation, permissions, metadata)
  - Deploying or interacting with LSP7/LSP8 tokens
  - Setting up gasless relay transactions (LSP25)
  - Managing KeyManager permissions (LSP6)
  - Working with The Grid (LSP28), Followers (LSP26), or any LSP standard
  - Answering questions about LUKSO ecosystem, projects, or architecture
  - Looking up contract addresses, ABIs, or API endpoints
  - Debugging LUKSO-specific issues (permissions, encoding, gas)
  
  DON'T USE WHEN:
  - Working with non-LUKSO EVM chains (use standard Ethereum patterns)
  - General Solidity questions unrelated to LSP standards
---

# LUKSO Expert

Complete knowledge base for building on LUKSO — the blockchain for creative economies,
digital identity, and new social standards.

## Quick Facts

- **Chain ID**: 42 (mainnet) / 4201 (testnet)
- **Native token**: LYX
- **Consensus**: Proof of Stake (32 LYX per validator)
- **EVM compatible**: Yes, unmodified Ethereum execution layer
- **Unique**: Universal Profiles (smart contract accounts) instead of EOAs
- **Founder**: Fabian Vogelsteller (also created ERC-20 and ERC-725)

## Core Concepts

LUKSO extends Ethereum with **LSP standards** (LUKSO Standard Proposals) that enable:
- **Smart accounts** (Universal Profiles) with built-in permissions, metadata, and social features
- **Flexible tokens** (LSP7/LSP8) with safety features like `force` parameter and universal receiver hooks
- **Gasless transactions** via relay service (LSP25)
- **On-chain social graph** via followers system (LSP26)
- **Profile customization** via The Grid (LSP28)

## Architecture Overview

```
Universal Profile (LSP0/ERC725Account)
├── KeyManager (LSP6) — permission layer
│   ├── Controllers — addresses with specific permissions
│   └── Allowed calls/addresses — fine-grained access control
├── Profile Data (LSP3) — name, description, avatar, links
├── Universal Receiver (LSP1) — hooks for incoming transactions
├── Owned Assets (LSP5) — registry of tokens/NFTs owned
├── Issued Assets (LSP12) — registry of tokens/NFTs created
└── The Grid (LSP28) — customizable profile layout
```

## Reference Files

Load these based on what you need:

### LSP Standards (`references/lsp-standards.md`)
Complete reference for ALL LSP standards (LSP0-LSP28+). Includes interfaces, 
function signatures, and implementation details. Read when working with any 
specific LSP or needing to understand the standards architecture.

### Developer Patterns (`references/dev-patterns.md`)
Practical code examples and implementation guides. Covers UP creation, token 
operations, permissions, gasless transactions, and common pitfalls. Read when 
writing code or debugging LUKSO-specific issues.

### Ecosystem (`references/ecosystem.md`)
Projects, team, community channels, grants, and chain infrastructure. Read when 
answering ecosystem questions or looking for project information.

### Contracts & Repos (`references/contracts-and-repos.md`)
Deployed contract addresses, GitHub repositories, NPM packages, and API endpoints.
Read when looking up addresses, ABIs, or integration endpoints.

## Key Contract Addresses (Mainnet)

| Contract | Address |
|----------|---------|
| LSP26 Follower System | `0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA` |
| Envio GraphQL | `https://envio.lukso-mainnet.universal.tech/v1/graphql` |

> Full address list in `references/contracts-and-repos.md`

## Common Operations Quick Reference

### Resolve username to UP address
```graphql
# Envio GraphQL
query { Profile(where: {name: {_eq: "username"}}) { id name } }
```

### Check UP count
```graphql
query { Profile_aggregate { aggregate { count } } }
```

### Follow a profile (LSP26)
```javascript
const LSP26 = "0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA";
const calldata = lsp26Contract.methods.follow(targetAddress).encodeABI();
await universalProfile.methods.execute(0, LSP26, 0, calldata).send({from: controller});
```

## Important Gotchas

1. **`force` parameter (LSP7/LSP8)**: Set to `true` to send tokens to any address. 
   Set to `false` (default) to only send to UPs with a Universal Receiver — prevents 
   accidental sends to EOAs or contracts that can't handle them.

2. **LSP6 Permissions**: Permissions are bitmask-based. Common mistake: granting 
   `CALL` permission but forgetting `EXECUTE_RELAY_CALL` for gasless transactions.

3. **ERC725Y data encoding**: Use `@erc725/erc725.js` for encoding — manual encoding 
   is error-prone, especially for VerifiableURI and array types.

4. **Gas estimation**: UP transactions go through KeyManager proxy, so gas estimates 
   can be off. Add 20-30% buffer.

## Developer Resources

- **Docs**: https://docs.lukso.tech
- **GitHub**: https://github.com/lukso-network
- **Medium**: https://medium.com/lukso
- **Discord**: https://discord.gg/lukso
- **Testnet faucet**: https://faucet.testnet.lukso.network
