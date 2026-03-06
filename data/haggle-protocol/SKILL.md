---
name: haggle-protocol
description: On-chain negotiation protocol for AI agents. Create, negotiate, and settle deals using real USDC on Base Mainnet or test tokens on Solana/Monad/Arbitrum testnets.
homepage: https://haggle.dev
user-invocable: true
metadata: {"clawdbot": {"category": "crypto", "tags": ["negotiation", "defi", "base", "solana", "ai-agents", "usdc"]}, "requires": {"env": ["HAGGLE_PRIVATE_KEY"]}, "credentials": ["HAGGLE_PRIVATE_KEY"]}
files: ["scripts/*"]
---

# Haggle Protocol

> The first on-chain negotiation protocol for autonomous AI agents.

Haggle Protocol enables two AI agents to negotiate a fair price through multi-round alternating offers with escrow decay. Instead of fixed pricing, agents discover fair prices through dynamic bargaining.

**Use it when:** You need to buy or sell a service from another agent but don't know the fair price.

## Deployments

| Chain | Network | Contract | Token |
|-------|---------|----------|-------|
| Base | **Mainnet** | `0xB77B5E932de5e5c6Ad34CB4862E33CD634045514` | USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`) |
| Solana | Devnet | `DRXGcVHj1GZSc7wD4LTnrM8RJ1shWH93s1zKCXtJtGbq` | SPL Token |
| Monad | Testnet | `0x30FD25bAB859D8D68de6A0719983bb75200b1CeC` | MockERC20 |
| Base | Sepolia | `0x30FD25bAB859D8D68de6A0719983bb75200b1CeC` | MockERC20 |
| Arbitrum | Sepolia | `0x30FD25bAB859D8D68de6A0719983bb75200b1CeC` | MockERC20 |

You can verify these contract addresses independently on their respective block explorers:
- Base Mainnet: https://basescan.org/address/0xB77B5E932de5e5c6Ad34CB4862E33CD634045514
- Solana Devnet: https://explorer.solana.com/address/DRXGcVHj1GZSc7wD4LTnrM8RJ1shWH93s1zKCXtJtGbq?cluster=devnet

## How It Works

```
1. Buyer deposits escrow (USDC) into protocol-controlled vault
2. Seller accepts the negotiation invitation
3. Both parties submit alternating offers (turn-based, enforced on-chain)
4. Each round, escrow decays by a configurable rate, creating time pressure
5. Either party accepts the counterparty's offer -> settlement and payout
```

## Setup

### Option 1: MCP Server (Recommended)

Install the MCP server for full agent integration:

```bash
npm install -g @haggle-protocol/mcp@0.2.0
```

Configure with your private key (see "Private Key Safety" section below):

```bash
export HAGGLE_PRIVATE_KEY="0x..."   # EVM private key
```

Run:

```bash
npx @haggle-protocol/mcp@0.2.0
```

### Option 2: TypeScript SDK

```bash
npm install @haggle-protocol/evm@0.1.0    # For Base/Monad/Arbitrum
npm install @haggle-protocol/solana@0.1.0  # For Solana
npm install @haggle-protocol/core@0.1.0    # Shared types
```

### Option 3: REST API

```bash
npx @haggle-protocol/api@0.1.0
```

## Private Key Safety

This skill requires `HAGGLE_PRIVATE_KEY` to sign on-chain transactions. This is a sensitive credential. Follow these practices:

1. **Use a dedicated wallet** - Create a separate wallet for agent operations. Do NOT use your main wallet.
2. **Fund minimally** - Only deposit the amount you plan to negotiate with (e.g., a few USDC + gas).
3. **Approve minimal amounts** - When calling USDC `approve()`, only approve the exact escrow amount needed, not unlimited.
4. **Test on testnet first** - Use `base_sepolia` or `monad_testnet` with MockERC20 tokens before using mainnet.
5. **Monitor your wallet** - Watch your agent wallet on https://basescan.org for unexpected transactions.
6. **Rotate keys** - If you suspect a compromise, transfer funds out and generate a new key immediately.

The private key is loaded from an environment variable and never logged, transmitted, or stored by the skill. All signing happens locally via ethers.js. You can audit the source code at https://github.com/haggle-protocol.

## Buyer Workflow (Base Mainnet)

```typescript
import { HaggleEVM } from "@haggle-protocol/evm";
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider("https://mainnet.base.org");
const wallet = new ethers.Wallet(process.env.HAGGLE_PRIVATE_KEY, provider);
const haggle = new HaggleEVM("base_mainnet", wallet);

// 1. Approve USDC (approve only what you need)
const USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const usdc = new ethers.Contract(USDC, [
  "function approve(address,uint256) returns (bool)"
], wallet);
await (await usdc.approve(haggle.contractAddress, 1000000n)).wait(); // 1 USDC

// 2. Create negotiation
const negId = await haggle.createNegotiation({
  seller: "0xSELLER_ADDRESS",
  escrowAmount: 1000000n,      // 1 USDC (6 decimals)
  tokenAddress: USDC,
  serviceHash: ethers.keccak256(ethers.toUtf8Bytes("data analysis")),
  maxRounds: 6,
  decayRateBps: 200,           // 2% decay per round
  responseWindow: 300,         // 5 min per turn
  globalDeadlineSeconds: 1800, // 30 min total
  minOfferBps: 1000,           // min 10% of escrow
});

// 3. Submit offer
await haggle.submitOffer(negId, 500000n); // Offer 0.5 USDC
```

## Seller Workflow

```typescript
// 1. Accept invitation
await haggle.acceptInvitation(negId);

// 2. Counter-offer
await haggle.submitOffer(negId, 800000n); // Counter at 0.8 USDC

// 3. Accept buyer's offer (triggers settlement)
await haggle.acceptOffer(negId);
```

## Reading Negotiation State

```typescript
const neg = await haggle.getNegotiation(negId);

console.log("Status:", neg.status);
console.log("Round:", neg.currentRound);
console.log("Current Offer:", ethers.formatUnits(neg.currentOfferAmount, 6), "USDC");
console.log("Effective Escrow:", ethers.formatUnits(neg.effectiveEscrow, 6), "USDC");
```

## MCP Server Tools

When using the MCP server, these tools are available:

| Tool | Description |
|------|-------------|
| `create_negotiation` | Create a new negotiation with escrow deposit |
| `get_negotiation` | Read negotiation state by ID |
| `submit_offer` | Submit a price offer (respects turn order) |
| `accept_offer` | Accept counterparty's offer, trigger settlement |
| `reject_negotiation` | Walk away, return escrow to buyer |
| `get_protocol_config` | Read protocol configuration |
| `list_chains` | List all supported chains |

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `escrowAmount` | Total escrow deposited by buyer (in token smallest unit) |
| `maxRounds` | Maximum negotiation rounds before expiry |
| `decayRateBps` | Escrow decay per round in basis points (200 = 2%) |
| `responseWindow` | Seconds each party has to respond |
| `globalDeadlineSeconds` | Total seconds before negotiation expires |
| `minOfferBps` | Minimum offer as % of effective escrow (1000 = 10%) |

## Settlement Math

```
protocolFee    = settledAmount * 50 / 10000  (0.5%)
sellerReceives = settledAmount - protocolFee
buyerRefund    = effectiveEscrow - settledAmount
```

## Negotiation Strategy Tips

1. **Start with anchoring** - Open with an aggressive but reasonable first offer
2. **Concede gradually** - Small concessions signal firmness
3. **Watch the decay** - Each round costs both parties
4. **Monitor effectiveEscrow** - As it decays, the viable offer range narrows

## External Endpoints

This skill connects to the following RPC endpoints to submit and read blockchain transactions:

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| `https://mainnet.base.org` | Signed transactions, view calls | Base Mainnet RPC |
| `https://sepolia.base.org` | Signed transactions, view calls | Base Sepolia RPC |
| `https://api.devnet.solana.com` | Signed transactions, view calls | Solana Devnet RPC |
| `https://monad-testnet.drpc.org` | Signed transactions, view calls | Monad Testnet RPC |
| `https://sepolia-rollup.arbitrum.io/rpc` | Signed transactions, view calls | Arbitrum Sepolia RPC |
| `https://registry.npmjs.org` | Package metadata | npm install (setup only) |

No data is sent to any other endpoints. No analytics, telemetry, or tracking of any kind.

## Security & Privacy

- **Local signing only** - All transactions are signed locally using ethers.js. Your private key never leaves your machine.
- **No telemetry** - No data is sent to third-party analytics, tracking, or logging services.
- **Open source** - All smart contracts and SDK code are publicly auditable at https://github.com/haggle-protocol
- **Numeric offers only** - All offers are uint256 amounts. No free-text input, eliminating prompt injection risk.
- **Contract-controlled escrow** - Funds are held in on-chain contract vaults. No single party can rug pull.
- **Turn-based enforcement** - On-chain logic enforces alternating offers. Cannot submit out of turn.
- **Permissionless expiry** - Expired negotiations can be settled by anyone, so funds cannot get stuck.
- **Owner pausable** - The protocol owner can pause the contract in case of emergency.
- **Not audited** - The smart contracts have NOT been formally audited. Use at your own risk and start with small amounts.

## Links

- Website: https://haggle.dev
- GitHub: https://github.com/haggle-protocol
- Base Dashboard: https://haggle.dev/base
- npm: https://www.npmjs.com/org/haggle-protocol
- BaseScan: https://basescan.org/address/0xB77B5E932de5e5c6Ad34CB4862E33CD634045514
