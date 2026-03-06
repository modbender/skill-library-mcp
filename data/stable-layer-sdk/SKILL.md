---
name: Stable Layer SDK
description: A TypeScript SDK for interacting with the Stable Layer protocol on
  the Sui blockchain. It supports minting and burning stablecoins, and claiming
  yield farming rewards.
---

# Stable Layer SDK

A TypeScript SDK for interacting with the Stable Layer protocol on the Sui blockchain. It supports minting and burning stablecoins, and claiming yield farming rewards.

## Installation

```bash
npm install stable-layer-sdk @mysten/sui @mysten/bcs
```

## API Reference

### StableLayerClient

```typescript
import { StableLayerClient } from "stable-layer-sdk";

const client = new StableLayerClient({
  network: "mainnet" | "testnet",
  sender: "0xYOUR_SUI_ADDRESS",
});
```

### Transaction Methods

#### `buildMintTx(options)`

Mint stablecoins by depositing USDC. Automatically deposits into vault farm.

| Parameter       | Type          | Description                                      |
| --------------- | ------------- | ------------------------------------------------ |
| `tx`            | `Transaction` | Sui transaction object                           |
| `stableCoinType`| `string`      | Target stablecoin type (e.g. `0x...::btc_usdc::BtcUSDC`) |
| `usdcCoin`      | `Coin`        | Input USDC coin reference                        |
| `amount`        | `bigint`      | Amount to mint                                   |
| `autoTransfer`  | `boolean?`    | If `false`, returns the resulting Coin object     |

#### `buildBurnTx(options)`

Burn stablecoins to redeem USDC.

| Parameter       | Type          | Description                          |
| --------------- | ------------- | ------------------------------------ |
| `tx`            | `Transaction` | Sui transaction object               |
| `stableCoinType`| `string`      | Stablecoin type to burn              |
| `amount`        | `bigint?`     | Specific amount to burn              |
| `all`           | `boolean?`    | If `true`, burn entire balance       |

#### `buildClaimTx(options)`

Claim accumulated yield farming rewards.

| Parameter       | Type          | Description                          |
| --------------- | ------------- | ------------------------------------ |
| `tx`            | `Transaction` | Sui transaction object               |
| `stableCoinType`| `string`      | Stablecoin type to claim rewards for |

### Query Methods

#### `getTotalSupply()`

Returns the total stablecoin supply across all coin types.

#### `getTotalSupplyByCoinType(type: string)`

Returns the supply for a specific stablecoin type.

## Usage Examples

### Mint Stablecoins

```typescript
import { Transaction, coinWithBalance } from "@mysten/sui/transactions";
import { SuiClient, getFullnodeUrl } from "@mysten/sui/client";
import { Ed25519Keypair } from "@mysten/sui/keypairs/ed25519";
import { StableLayerClient } from "stable-layer-sdk";

const client = new StableLayerClient({
  network: "mainnet",
  sender: "0xYOUR_ADDRESS",
});

const suiClient = new SuiClient({ url: getFullnodeUrl("mainnet") });
const keypair = Ed25519Keypair.fromSecretKey(YOUR_PRIVATE_KEY);

const tx = new Transaction();
await client.buildMintTx({
  tx,
  stableCoinType: "0x6d9fc...::btc_usdc::BtcUSDC",
  usdcCoin: coinWithBalance({
    balance: BigInt(1_000_000),
    type: "0xdba34...::usdc::USDC",
  })(tx),
  amount: BigInt(1_000_000),
});

const result = await suiClient.signAndExecuteTransaction({
  transaction: tx,
  signer: keypair,
});
```

### Burn Stablecoins

```typescript
const tx = new Transaction();
await client.buildBurnTx({
  tx,
  stableCoinType: "0x6d9fc...::btc_usdc::BtcUSDC",
  amount: BigInt(500_000),
});

await suiClient.signAndExecuteTransaction({ transaction: tx, signer: keypair });
```

### Claim Rewards

```typescript
const tx = new Transaction();
await client.buildClaimTx({
  tx,
  stableCoinType: "0x6d9fc...::btc_usdc::BtcUSDC",
});

await suiClient.signAndExecuteTransaction({ transaction: tx, signer: keypair });
```

### Query Supply

```typescript
const totalSupply = await client.getTotalSupply();
const btcUsdcSupply = await client.getTotalSupplyByCoinType("0x6d9fc...::btc_usdc::BtcUSDC");
```
