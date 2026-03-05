---
name: clawhub-krump-verify
description: Enables AI agents (e.g. OpenClaw) to understand and use Krump Verify for on-chain move verification against Story IP. Use when the user or agent needs to verify a dance move, pay via USDC.k or x402/EVVM receipt, call KrumpVerify contracts, integrate with ClawHub (clawhub.ai), or build similar EVVM/x402 apps on Story Aeneid.
---

# ClawHub & Krump Verify for Agents

Use this skill when working with [ClawHub](https://clawhub.ai/) and Krump Verify: on-chain verification of dance moves against registered Story IP, with payment in USDC.k or via x402/EVVM payment receipts. Agents can perform verifications autonomously; humans can audit on-chain.

**Building a similar app?** See **[docs/BUILDING_WITH_EVVM_X402_STORY_AENEID.md](../../../docs/BUILDING_WITH_EVVM_X402_STORY_AENEID.md)** for step-by-step EVVM/x402/USDC.k on Story Aeneid: architecture, failures (EVVM payment failed, IP registry, funding UX), and fixes.

---

## What Krump Verify Does

- **Verification**: Prove a move (hash of move/video data) against a registered Story IP asset. Fee is paid to treasury; a receipt is recorded on-chain and `Verified(ipId, verifier, receiptHash, timestamp)` is emitted.
- **Chain**: Story Aeneid (chain ID **1315**). Explorer: `https://aeneid.storyscan.io`.
- **Fee**: USDC.k (6 decimals). Default `verificationFee` = 1e6 (1 USDC.k). Read from contract `verificationFee()`.

---

## Two Payment Flows

### 1. Direct (wallet pays on-chain)

1. User/agent approves USDC.k for KrumpVerify: `approve(KrumpVerify, verificationFee)` on USDC.k contract.
2. Call **`verifyMove(ipId, moveDataHash, proof)`** on KrumpVerify. Contract does `transferFrom(msg.sender, treasury, verificationFee)` then records receipt.

### 2. Receipt (x402 / EVVM; agent-friendly)

1. **Fund EVVM (one-time per payer):** Approve USDC.k for **EVVM Treasury**, then call **Treasury.deposit(USDC.k, amount)** so the payer has EVVM internal balance.
2. **Sign x402 + EVVM:** User signs EIP-712 TransferWithAuthorization (domain = adapter) and an EVVM message: hash payload must include **`"pay"`** and **(to, '', token, amount, 0n)**; executor **`address(0)`**; use **getNextCurrentSyncNonce(payer)** and **isAsyncExec: false**.
3. **Relayer** (with RECEIPT_SUBMITTER_ROLE) calls adapter **payViaEVVMWithX402(...)** then **submitPaymentReceipt(receiptId, payer, amount)**.
4. Payer calls **`verifyMoveWithReceipt(ipId, moveDataHash, proof, paymentReceiptId)`**. No on-chain transfer; receipt is consumed once. `msg.sender` must equal the receipt’s `payer`.

Use the receipt flow when the agent or user has already paid via x402 and has a `receiptId` (bytes32) to use.

---

## EVVM / x402 Pitfalls (Reference)

- **"EVVM payment failed"** on adapter: Hash payload must encode **`"pay"`** then (to, identity, token, amount, priorityFee); executor must be **0x0**; use **sync nonce** from Core and **isAsyncExec: false**.
- **"IP registry not set"**: Contract’s IP Asset Registry (and License/Royalty if used) must be set at deploy or via setter.
- **No EVVM balance**: Payer must complete Fund EVVM (approve + deposit to EVVM Treasury) before Pay via x402.

---

## Key Data Shapes

| Term | Type | Description |
|------|------|-------------|
| **ipId** | address | Story IP account address (from IP Asset Registry). Must be registered. |
| **moveDataHash** | bytes32 | `keccak256` of move/video data (e.g. `keccak256(toHex(utf8MoveData))`). |
| **proof** | bytes | Optional; e.g. signature or reference. Can be `0x`. |
| **paymentReceiptId** / **receiptId** | bytes32 | For receipt flow: id of the payment receipt submitted by relayer (0x + 64 hex). |
| **receiptHash** | bytes32 | Returned from verify; unique per (ipId, verifier, moveDataHash, timestamp, fee, proof). |

---

## Contract Surface (KrumpVerify)

- **Read**: `verificationFee()`, `paymentReceipts(bytes32)` → (payer, amount, used), `receiptUsed(bytes32)`.
- **Write (anyone)**: `verifyMove(ipId, moveDataHash, proof)`, `verifyMoveWithReceipt(ipId, moveDataHash, proof, paymentReceiptId)`.
- **Write (RECEIPT_SUBMITTER_ROLE)**: `submitPaymentReceipt(receiptId, payer, amount)`.
- **Events**: `Verified(ipId, verifier, receiptHash, timestamp)`, `PaymentReceiptSubmitted(receiptId, payer, amount)`.

Agents can discover a user’s unused receipts by querying `PaymentReceiptSubmitted(payer=user)` and filtering with `paymentReceipts(receiptId).used == false`.

---

## Default Addresses (Story Aeneid)

- **KrumpVerify**: `0x012eD5BfDd306Fa7e959383A8dD63213b7c7AeA5` (override with `VITE_KRUMP_VERIFY_ADDRESS`).
- **KrumpVerifyNFT**: `0x602789919332d242A1Cb70d462CEbb570a53A6Ac`.
- **KrumpTreasury**: `0xa2e9245cE7D7B89554E86334a76fbE6ac5dc4617`.
- **USDC.k**: `0xd35890acdf3BFFd445C2c7fC57231bDE5cAFbde5`.
- **EVVM Treasury**: `0x977126dd6B03cAa3A87532784E6B7757aBc9C1cc`.
- **EVVM Core**: `0xa6a02E8e17b819328DDB16A0ad31dD83Dd14BA3b`. **EVVM Native x402 Adapter**: `0xDf5eaED856c2f8f6930d5F3A5BCE5b5d7E4C73cc`.

---

## Relayer

- **Local**: `relayer/` — `RELAYER_PRIVATE_KEY`, `KRUMP_VERIFY_ADDRESS`; runs on port 7350. Frontend `VITE_X402_RELAYER_URL` for local: `http://localhost:7350`.
- **Production**: Fly.io app **krump-x402-relayer** at `https://krump-x402-relayer.fly.dev`. Set `fly secrets set RELAYER_PRIVATE_KEY=0x...`; frontend `VITE_X402_RELAYER_URL=https://krump-x402-relayer.fly.dev`.

---

## Deploy (Contracts)

- **Script**: `script/DeployAll.s.sol` — deploys KrumpTreasury, KrumpVerify (with Story IP/License/Royalty set), KrumpVerifyNFT; deployer gets RECEIPT_SUBMITTER_ROLE. Optional `RELAYER_ADDRESS` in env to grant role to another address.
- **Command**: `./deploy.sh` or `forge script script/DeployAll.s.sol:DeployAll --rpc-url https://aeneid.storyrpc.io --broadcast --gas-price 10000000000 --legacy`. See [DEPLOY.md](../../DEPLOY.md).

---

## Agent Autonomy and Human Oversight

- **Autonomous use**: An agent with a wallet (or delegated signing) can pay via x402 (after Fund EVVM), have a relayer submit a receipt, then call `verifyMoveWithReceipt`. Or it can approve USDC.k and call `verifyMove`.
- **Human check**: All verifications and payment receipts are on-chain; humans can audit via explorer, `Verified` / `PaymentReceiptSubmitted` events, and `receiptUsed` / `paymentReceipts` state.
- **Repo**: Contract and frontend in this repo; frontend supports Fund EVVM, “Pay via x402”, “Load my receipts”, and “Verify with receipt”.

---

## Quick Reference

- **Verify with wallet payment**: `approve(USDC.k)` then `verifyMove(ipId, moveDataHash, proof)`.
- **Verify with receipt**: `verifyMoveWithReceipt(ipId, moveDataHash, proof, paymentReceiptId)` (payer must be `msg.sender`).
- **Submit receipt (relayer only)**: `submitPaymentReceipt(receiptId, payer, amount)`; require `amount >= verificationFee`, payer != 0, receipt not already submitted.
- **EVVM/x402 build guide**: [docs/BUILDING_WITH_EVVM_X402_STORY_AENEID.md](../../../docs/BUILDING_WITH_EVVM_X402_STORY_AENEID.md).

For full contract and env details, see repo [README](../../../README.md) and [DEPLOY.md](../../../DEPLOY.md) and `src/KrumpVerify.sol`.
