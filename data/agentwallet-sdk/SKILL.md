---
name: Agent Wallet SDK Skill
description: Non-custodial wallet SDK for autonomous AI agents. Handles x402
  payments, CCTP V2 cross-chain bridge transfers, ERC-8004 agent identity, and
  Uniswap V3 token swaps — all without holding user keys.
---

# Agent Wallet SDK Skill

Non-custodial wallet SDK for autonomous AI agents. Handles x402 payments, CCTP V2 cross-chain bridge transfers, ERC-8004 agent identity, and Uniswap V3 token swaps — all without holding user keys.

## When to Use

Use this skill when an AI agent needs to:
- Create or manage a non-custodial wallet (ERC-4337 smart account)
- Make x402 HTTP payments to APIs
- Bridge tokens cross-chain via CCTP V2 (Circle)
- Swap tokens via Uniswap V3
- Register or verify agent identity via ERC-8004
- Sign transactions autonomously without custodial risk

## Installation

```bash
npm install agentwallet-sdk
```

Current version: **v2.4.1** on npm (158 tests passing, 0 compile errors)

## Core Modules

### WalletModule — Account Abstraction (ERC-4337)
```typescript
import { AgentWallet } from 'agentwallet-sdk';

const wallet = await AgentWallet.create({
  chain: 'base',
  signer: privateKey, // Agent's own key — never custodied
});

// Send ETH
await wallet.transfer({ to: recipient, value: '0.01' });

// Get balance
const balance = await wallet.getBalance();
```

### PaymentModule — x402 HTTP Payments
```typescript
// Pay for API access automatically
const response = await wallet.x402Pay({
  url: 'https://api.example.com/data',
  maxPayment: '0.001', // ETH
});
```

### BridgeModule — CCTP V2 Cross-Chain
```typescript
// Bridge USDC from Base to Ethereum
await wallet.bridge({
  token: 'USDC',
  amount: '100',
  fromChain: 'base',
  toChain: 'ethereum',
});
```

### SwapModule — Uniswap V3
```typescript
// Swap ETH for USDC
await wallet.swap({
  tokenIn: 'ETH',
  tokenOut: 'USDC',
  amount: '0.5',
  slippage: 0.5, // 0.5%
});
```

### IdentityModule — ERC-8004
```typescript
// Register agent identity on-chain
await wallet.registerIdentity({
  name: 'MyTradingAgent',
  capabilities: ['x402-payment', 'swap', 'bridge'],
});

// Verify another agent
const verified = await wallet.verifyAgent(agentAddress);
```

## Security Model

- **Non-custodial**: Agent holds its own private key. No server stores keys
- **ERC-4337 Smart Accounts**: Gas abstraction, batch transactions, session keys
- **No oracle dependencies**: No external price feed reliance (prevents oracle manipulation attacks)
- **Audited**: forge test suite 129/129 passing on smart contracts

## Integration with Other Skills

### With Mastra (AI Framework)
```bash
npm install @agent-wallet/mastra-plugin
```
Provides 10 Mastra tools: `getBalance`, `transfer`, `swap`, `bridge`, `x402Pay`, `registerIdentity`, `verifyAgent`, `getTransactionHistory`, `estimateGas`, `getChainInfo`.

### With ClawPay MCP
```bash
npm install clawpay-mcp
```
Exposes wallet operations as MCP tools for any MCP-compatible agent.

## Links

- npm: [agentwallet-sdk](https://www.npmjs.com/package/agentwallet-sdk)
- Mastra plugin: [@agent-wallet/mastra-plugin](https://www.npmjs.com/package/@agent-wallet/mastra-plugin)
- ClawPay MCP: [clawpay-mcp](https://www.npmjs.com/package/clawpay-mcp)
