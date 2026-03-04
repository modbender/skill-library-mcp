# Credex Protocol Contract Reference

## Contract Addresses (Arc Testnet, Chain ID: 1328)

```typescript
export const CONTRACTS = {
  // Core Protocol
  CREDEX_POOL: "0x32239e52534c0b7e525fb37ed7b8d1912f263ad3",

  // Tokens
  USDC_ARC: "0x3600000000000000000000000000000000000000",
  USDC_BASE_SEPOLIA: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",

  // Agent (Operator)
  CREDEX_AGENT: "0x...", // Set to your deployed agent wallet
} as const;
```

---

## CredexPool ABI

```typescript
export const CREDEX_POOL_ABI = [
  // ═══════════════════════════════════════════════════════════════
  //                         READ FUNCTIONS
  // ═══════════════════════════════════════════════════════════════

  // Get agent state (includes pending interest)
  {
    name: "getAgentState",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "agent", type: "address" }],
    outputs: [
      { name: "debt", type: "uint256" },
      { name: "principal", type: "uint256" },
      { name: "creditLimit", type: "uint256" },
      { name: "lastAccrued", type: "uint256" },
      { name: "lastRepayment", type: "uint256" },
      { name: "frozen", type: "bool" },
      { name: "active", type: "bool" },
    ],
  },

  // Available borrowing power
  {
    name: "availableCredit",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "agent", type: "address" }],
    outputs: [{ name: "", type: "uint256" }],
  },

  // LP share balance
  {
    name: "lpShares",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "provider", type: "address" }],
    outputs: [{ name: "", type: "uint256" }],
  },

  // Pool metrics
  {
    name: "totalLiquidity",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    name: "totalAssets",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    name: "totalShares",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    name: "totalDebt",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },

  // ═══════════════════════════════════════════════════════════════
  //                        WRITE FUNCTIONS
  // ═══════════════════════════════════════════════════════════════

  // LP Functions
  {
    name: "deposit",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [{ name: "assets", type: "uint256" }],
    outputs: [{ name: "shares", type: "uint256" }],
  },
  {
    name: "withdraw",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [{ name: "shares", type: "uint256" }],
    outputs: [{ name: "assets", type: "uint256" }],
  },

  // Agent Functions (onlyAgent modifier)
  {
    name: "onboardAgent",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "agent", type: "address" },
      { name: "creditLimit", type: "uint256" },
    ],
    outputs: [],
  },
  {
    name: "borrow",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "agent", type: "address" },
      { name: "amount", type: "uint256" },
    ],
    outputs: [],
  },
  {
    name: "repay",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "agent", type: "address" },
      { name: "amount", type: "uint256" },
    ],
    outputs: [],
  },
  {
    name: "setCreditLimit",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "agent", type: "address" },
      { name: "newLimit", type: "uint256" },
    ],
    outputs: [],
  },

  // ═══════════════════════════════════════════════════════════════
  //                           EVENTS
  // ═══════════════════════════════════════════════════════════════

  {
    name: "LiquidityDeposited",
    type: "event",
    inputs: [
      { name: "provider", type: "address", indexed: true },
      { name: "assets", type: "uint256" },
      { name: "shares", type: "uint256" },
    ],
  },
  {
    name: "LiquidityWithdrawn",
    type: "event",
    inputs: [
      { name: "provider", type: "address", indexed: true },
      { name: "assets", type: "uint256" },
      { name: "shares", type: "uint256" },
    ],
  },
  {
    name: "AgentOnboarded",
    type: "event",
    inputs: [
      { name: "agent", type: "address", indexed: true },
      { name: "creditLimit", type: "uint256" },
    ],
  },
  {
    name: "Borrowed",
    type: "event",
    inputs: [
      { name: "agent", type: "address", indexed: true },
      { name: "amount", type: "uint256" },
    ],
  },
  {
    name: "Repaid",
    type: "event",
    inputs: [
      { name: "agent", type: "address", indexed: true },
      { name: "amount", type: "uint256" },
    ],
  },
  {
    name: "InterestAccrued",
    type: "event",
    inputs: [
      { name: "agent", type: "address", indexed: true },
      { name: "interest", type: "uint256" },
    ],
  },
] as const;
```

---

## TypeScript Types

```typescript
// Agent state from getAgentState()
interface AgentState {
  debt: bigint; // Total debt including pending interest
  principal: bigint; // Original borrowed amount
  creditLimit: bigint; // Max borrowing capacity
  lastAccrued: bigint; // Timestamp of last interest accrual
  lastRepayment: bigint; // Timestamp of last repayment
  frozen: boolean; // Account frozen status
  active: boolean; // Account active status
}

// Pool metrics
interface PoolStatus {
  totalLiquidity: bigint; // Available USDC for borrowing
  totalAssets: bigint; // Liquidity + Outstanding Debt
  totalShares: bigint; // Total LP shares issued
  totalDebt: bigint; // Sum of all agent debts
  exchangeRate: bigint; // Assets per share (18 decimals)
}

// LP position
interface LPPosition {
  shares: bigint; // LP shares owned
  value: bigint; // Current USDC value
}
```

---

## Protocol Constants

```typescript
export const PROTOCOL = {
  // Interest
  INTEREST_RATE_BP: 10, // 0.1% per interval
  ACCRUAL_INTERVAL: 60, // 1 minute (testnet)

  // Credit Limits
  INITIAL_CREDIT_BASE: 5_000_000n, // 5 USDC (6 decimals)
  GROWTH_FACTOR_BP: 110, // 1.1x per repayment
  MAX_CREDIT_LIMIT: 10_000_000_000n, // 10,000 USDC

  // Token decimals
  USDC_DECIMALS: 6,
  SHARE_DECIMALS: 6,
} as const;
```

---

## RPC Endpoints

```typescript
export const RPC = {
  ARC_TESTNET: "https://rpc.testnet.arc.network",
  BASE_SEPOLIA: "https://sepolia.base.org",
} as const;
```

---

## Circle Bridge Integration

For cross-chain USDC transfers between Arc and Base:

```typescript
import { BridgeKit } from "@circle-fin/bridge-kit";
import { createViemAdapterFromPrivateKey } from "@circle-fin/adapter-viem-v2";

const kit = new BridgeKit();
const adapter = createViemAdapterFromPrivateKey({
  privateKey: PRIVATE_KEY as `0x${string}`,
});

// Bridge from Arc to Base
await kit.bridge({
  from: { adapter, chain: "Arc_Testnet" },
  to: { adapter, chain: "Base_Sepolia" },
  amount: "10", // USDC amount as string
});

// Bridge from Base to Arc
await kit.bridge({
  from: { adapter, chain: "Base_Sepolia" },
  to: { adapter, chain: "Arc_Testnet" },
  amount: "10",
});
```

---

## ERC20 ABI (USDC)

```typescript
export const ERC20_ABI = [
  "function balanceOf(address owner) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
] as const;
```
