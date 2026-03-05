---
name: arkade
description: Guide for developing with the Arkade TypeScript SDK (@arkade-os/sdk) — Bitcoin wallets, Lightning, smart contracts, and stablecoin swaps.
read_when:
  - user wants to develop or build with Arkade
  - user wants to use the @arkade-os/sdk TypeScript SDK
  - user asks about Arkade wallet SDK or API
  - user wants to create a Bitcoin wallet application
  - user mentions VTXOs, virtual UTXOs, or offchain Bitcoin development
  - user wants to integrate Lightning Network with Arkade
  - user asks about Arkade smart contracts
  - user wants to send or receive Bitcoin programmatically with Arkade
  - user asks about onboarding or offboarding Bitcoin
  - user mentions arkade.computer or Ark protocol SDK
  - user mentions Ark protocol
requires: []
metadata:
  emoji: "₿"
---

# Arkade SDK Development Guide

Arkade is a programmable Bitcoin execution layer. It uses VTXOs (Virtual Transaction Outputs) to enable instant offchain Bitcoin transactions with near-zero fees, while users retain full self-custody and unilateral exit rights. No changes to Bitcoin are required.

## SDK Installation & Setup

```bash
npm install @arkade-os/sdk
```

Requires Node.js >= 22.

```typescript
import { SingleKey, Wallet } from "@arkade-os/sdk";

// Create an identity (private key)
const identity = SingleKey.fromHex("your-private-key-hex");
// Or generate a new one:
// const identity = SingleKey.fromRandomBytes();

const wallet = await Wallet.create({
  identity,
  arkServerUrl: "https://arkade.computer",
});

const address = await wallet.getAddress();
console.log("Ark Address:", address);
```

For production, always use a secure key management solution rather than hardcoded keys.

## Core Wallet Operations

### Addresses

```typescript
// Offchain Ark address (ark1.../tark1...) — for instant payments
const arkAddress = await wallet.getAddress();

// Boarding address — for receiving onchain BTC to be onboarded later
const boardingAddress = await wallet.getBoardingAddress();
```

### Balances

```typescript
const balance = await wallet.getBalance();

console.log("Available:", balance.available, "sats"); // spendable now
console.log("Total:", balance.total, "sats"); // includes recoverable
console.log("Settled:", balance.settled, "sats"); // Bitcoin-anchored
console.log("Preconfirmed:", balance.preconfirmed, "sats"); // cosigned

// Pending onchain deposits
console.log("Boarding:", balance.boarding.total, "sats");
```

### Sending Payments

```typescript
// Send to an Ark address — instant, near-zero fees
const txid = await wallet.sendBitcoin({
  address: "ark1...",
  amount: 50000, // satoshis
});
```

For onchain destinations (`bc1...`/`tb1...`), use the Ramps offboard flow below. For Lightning invoices, use `@arkade-os/boltz-swap`.

### Receiving Payments

```typescript
const address = await wallet.getAddress();
// Share this address with the sender

// Monitor for incoming funds
const stop = wallet.notifyIncomingFunds(async (notification) => {
  if (notification.type === "vtxo") {
    for (const vtxo of notification.vtxos) {
      console.log(`Received ${vtxo.amount} sats`);
    }
  }
});

// Call stop() when done listening
```

### VTXOs

```typescript
const vtxos = await wallet.getVtxos();
for (const vtxo of vtxos) {
  console.log(vtxo.txid, vtxo.amount, vtxo.status);
}
```

## Onchain Ramps (Onboard / Offboard)

Convert between onchain Bitcoin UTXOs and offchain Arkade VTXOs. Best for large transfers; for everyday amounts, Lightning swaps have lower overhead.

```typescript
import { Ramps } from "@arkade-os/sdk";

const ramps = new Ramps(wallet);

// Get fee info from the Ark server
const info = await wallet.arkProvider.getInfo();

// Onboard: convert boarding UTXOs to VTXOs
const commitmentTxid = await ramps.onboard(info.fees);

// Offboard: convert VTXOs to onchain BTC
const exitTxid = await ramps.offboard(
  "bc1q...", // destination onchain address
  info.fees,
  // amount, // optional — defaults to all available
);
```

## Lightning Network

```bash
npm install @arkade-os/boltz-swap
```

Lightning integration uses Boltz submarine swaps to bridge between Arkade and the Lightning Network.

```typescript
import { ArkadeLightning, BoltzSwapProvider } from "@arkade-os/boltz-swap";

const swapProvider = new BoltzSwapProvider({
  apiUrl: "https://api.ark.boltz.exchange",
  network: "bitcoin",
});

const lightning = new ArkadeLightning({
  wallet,
  swapProvider,
});

// Receive via Lightning (reverse swap)
const { invoice, paymentHash } = await lightning.createLightningInvoice({
  amount: 25000,
});
console.log("Pay this:", invoice);

// Send via Lightning (submarine swap)
const result = await lightning.sendLightningPayment({
  invoice: "lnbc...",
});
console.log("Preimage:", result.preimage);
```

### Boltz API Endpoints

| Network | URL |
|---------|-----|
| Bitcoin mainnet | `https://api.ark.boltz.exchange` |
| Mutinynet | `https://api.boltz.mutinynet.arkade.sh` |
| Regtest (local) | `http://localhost:9069` |

## Skill Classes (this package)

This package (`@arkade-os/skill`) provides higher-level wrapper classes over the SDK:

```bash
npm install @arkade-os/skill
```

```typescript
import { Wallet, SingleKey } from "@arkade-os/sdk";
import {
  ArkadeBitcoinSkill,
  ArkaLightningSkill,
  LendaSwapSkill,
} from "@arkade-os/skill";

const wallet = await Wallet.create({
  identity: SingleKey.fromHex(privateKeyHex),
  arkServerUrl: "https://arkade.computer",
});

// Bitcoin: addresses, balances, send/receive, onboard/offboard
const bitcoin = new ArkadeBitcoinSkill(wallet);
const balance = await bitcoin.getBalance();
await bitcoin.send({ address: "ark1...", amount: 50000 });

// Lightning: invoices, payments via Boltz
const lightning = new ArkaLightningSkill({ wallet, network: "bitcoin" });
const inv = await lightning.createInvoice({ amount: 25000 });

// Stablecoin swaps: BTC <-> USDC/USDT
const lendaswap = new LendaSwapSkill({ wallet });
const quote = await lendaswap.getQuoteBtcToStablecoin(100000, "usdc_pol");
```

### ArkadeBitcoinSkill

- `getArkAddress()` / `getBoardingAddress()` — get addresses
- `getBalance()` — balance breakdown (offchain + onchain)
- `send({ address, amount })` — send sats offchain
- `getTransactionHistory()` — transaction list
- `onboard(params)` / `offboard(params)` — onchain ramps
- `waitForIncomingFunds(timeout?)` — wait for incoming payment

### ArkaLightningSkill

- `createInvoice({ amount, description? })` — Lightning invoice (reverse swap)
- `payInvoice({ bolt11 })` — pay Lightning invoice (submarine swap)
- `getFees()` / `getLimits()` — swap fees and limits
- `getPendingSwaps()` / `getSwapHistory()` — swap tracking

### LendaSwapSkill

- `getQuoteBtcToStablecoin(amount, token)` / `getQuoteStablecoinToBtc(amount, token)`
- `swapBtcToStablecoin(params)` / `swapStablecoinToBtc(params)`
- `getSwapStatus(swapId)` / `getPendingSwaps()` / `getSwapHistory()`
- `claimSwap(swapId)` / `refundSwap(swapId)`
- `getAvailablePairs()`

## Stablecoin Swaps (LendaSwap)

Non-custodial BTC/stablecoin atomic swaps via HTLCs.

**Supported tokens:** `usdc_pol`, `usdc_eth`, `usdc_arb`, `usdt0_pol`, `usdt_eth`, `usdt_arb`

**Supported chains:** `polygon`, `ethereum`, `arbitrum`

```typescript
const lendaswap = new LendaSwapSkill({ wallet });

// Get quote
const quote = await lendaswap.getQuoteBtcToStablecoin(100000, "usdc_pol");
console.log("You'll receive:", quote.targetAmount, "USDC");

// Execute swap (BTC -> USDC)
const swap = await lendaswap.swapBtcToStablecoin({
  targetAddress: "0x...", // EVM address
  targetToken: "usdc_pol",
  targetChain: "polygon",
  sourceAmount: 100000,
});
console.log("Swap ID:", swap.swapId);

// Check status
const status = await lendaswap.getSwapStatus(swap.swapId);

// Claim completed swap
const claim = await lendaswap.claimSwap(swap.swapId);
```

## Smart Contracts

Arkade supports any valid Tapscript as VTXO locking conditions, enabling programmable offchain Bitcoin.

```bash
npm install @arkade-os/sdk @scure/base
```

```typescript
import {
  RestArkProvider,
  RestIndexerProvider,
  SingleKey,
  VtxoScript,
  MultisigTapscript,
  CSVMultisigTapscript,
} from "@arkade-os/sdk";
import { hex } from "@scure/base";

const arkProvider = new RestArkProvider("https://mutinynet.arkade.sh");
const indexerProvider = new RestIndexerProvider("https://mutinynet.arkade.sh");
const info = await arkProvider.getInfo();
const serverPubkey = hex.decode(info.signerPubkey).slice(1);
```

**Available contract primitives:**
- **MultisigTapscript** — N-of-N multisig
- **CLTVMultisigTapscript** — Multisig with absolute timelocks
- **CSVMultisigTapscript** — Multisig with relative timelocks
- **VtxoScript** — Combine spending paths into Taproot trees

**Contract patterns in docs:** HTLC/Hashlock, Escrow (3-path), Spilman channels, Dryja-Poon channels, Lightning channels, chain swaps, Oracle DLC.

Use `@scure/base` for encoding, NOT `bitcoinjs-lib`.

See: https://docs.arkadeos.com/contracts/overview

## Networks & Resources

| Network | Server URL | Explorer |
|---------|-----------|----------|
| Bitcoin mainnet | `https://arkade.computer` | https://arkade.space |
| Mutinynet (testnet) | `https://mutinynet.arkade.sh` | https://explorer.mutinynet.arkade.sh |
| Signet | `https://signet.arkade.sh` | https://explorer.signet.arkade.sh |
| Regtest (local) | `http://localhost:7070` | — |

**Local development:**

```bash
nigiri start --ark
```

This starts a Bitcoin regtest node with an Arkade operator at `http://localhost:7070`.

## Key Concepts

- **VTXOs**: Virtual Transaction Outputs — self-custodial offchain Bitcoin coins. States: preconfirmed, settled, recoverable, spent.
- **Batch Swaps**: How VTXOs achieve Bitcoin finality — multiple transactions batched into a single onchain settlement.
- **Preconfirmation**: Instant confirmation cosigned by the operator, before onchain settlement.
- **Virtual Mempool**: DAG-based offchain execution engine that processes Arkade transactions.
- **Unilateral Exit**: Users can always withdraw their funds onchain without operator cooperation.
- **Ark Addresses**: `ark1...` (mainnet) / `tark1...` (testnet) — bech32m-encoded addresses containing server + user keys.

## Documentation

- Full docs: https://docs.arkadeos.com
- Technical primer: https://docs.arkadeos.com/primer
- Wallet SDK v0.3: https://docs.arkadeos.com/wallets/v0.3/setup
- Smart contracts: https://docs.arkadeos.com/contracts/overview
- Lightning swaps: https://docs.arkadeos.com/contracts/lightning-swaps
- LLM-friendly index: https://docs.arkadeos.com/llms.txt
- GitHub: https://github.com/arkade-os/skill
