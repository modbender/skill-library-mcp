---
name: safe-multisig-skill
description: Propose, confirm, and execute Safe multisig transactions using the Safe{Core} SDK (protocol-kit v6 / api-kit v4). TypeScript strict. Use when an agent needs to operate a Safe smart account — (1) create/predict a new Safe, (2) fetch Safe owners/threshold/nonce, (3) list pending multisig txs, (4) build + propose a tx, (5) add confirmations, (6) execute a tx onchain, or (7) troubleshoot Safe nonce/signature issues across chains (Base/Ethereum/Optimism/Arbitrum/Polygon/etc.).
---

# Safe Multisig Skill

TypeScript-strict scripts for interacting with Safe multisig accounts via:
- **Safe Transaction Service** (read state, propose txs, submit confirmations)
- **Safe{Core} SDK** (create Safes, create txs, compute hashes, sign, execute)

All scripts use `ethers v6`, validate inputs (addresses, tx hashes), and output JSON.

## Quick start

```bash
cd <this-skill>
./scripts/bootstrap.sh

# sanity check network + service
./scripts/safe_about.sh --chain base
```

## Core scripts

| Script | Description |
|--------|-------------|
| `create-safe.ts` | Predict address + optionally deploy a new Safe |
| `safe-info.ts` | Fetch Safe info (owners/threshold/nonce) |
| `list-pending.ts` | List pending (queued) multisig transactions |
| `safe_txs_list.ts` | List all multisig transactions (queued + executed) |
| `propose-tx.ts` | Create + propose a multisig tx |
| `approve-tx.ts` | Add an off-chain confirmation for a tx hash |
| `execute-tx.ts` | Execute a fully-confirmed tx onchain |

All scripts: `npx tsx scripts/<name>.ts --help`

## Common tasks

### 1) Create a new Safe

```bash
npx tsx scripts/create-safe.ts \
  --chain base \
  --owners 0xOwner1,0xOwner2,0xOwner3 \
  --threshold 2
```

Add `--deploy` + `SAFE_SIGNER_PRIVATE_KEY` to send the deployment tx.

### 2) Get Safe info

```bash
npx tsx scripts/safe-info.ts --chain base --safe 0xYourSafe
```

### 3) List pending transactions

```bash
npx tsx scripts/list-pending.ts --chain base --safe 0xYourSafe
```

### 4) Propose a new transaction

Create a tx request JSON (see `references/tx_request.schema.json` and `references/examples.md`).

```bash
export SAFE_SIGNER_PRIVATE_KEY="..."

npx tsx scripts/propose-tx.ts \
  --chain base \
  --rpc-url "$BASE_RPC_URL" \
  --tx-file ./references/example.tx.json
```

### 5) Confirm (approve) a proposed transaction

```bash
export SAFE_SIGNER_PRIVATE_KEY="..."

npx tsx scripts/approve-tx.ts \
  --chain base \
  --safe 0xYourSafe \
  --safe-tx-hash 0x...
```

### 6) Execute a confirmed transaction (onchain)

```bash
export SAFE_SIGNER_PRIVATE_KEY="..."

npx tsx scripts/execute-tx.ts \
  --chain base \
  --rpc-url "$BASE_RPC_URL" \
  --safe 0xYourSafe \
  --safe-tx-hash 0x...
```

## Configuration

All scripts accept:
- `--chain <slug>` (recommended): e.g. `base`, `base-sepolia`, `mainnet`, `arbitrum`, `optimism`
- `--tx-service-url <url>`: Override the transaction service URL
- `--rpc-url <url>`: RPC endpoint (or `RPC_URL` env var)
- `--api-key <key>`: Safe Transaction Service API key (or `SAFE_TX_SERVICE_API_KEY` env var)

## Security rules

- **Never paste private keys into chat.** Use env vars or files.
- Prefer low-privilege signers and spending limits.
- Always verify Safe address, chainId / RPC, and nonce before signing.

## References

- `references/examples.md` — example requests + workflows
- `references/tx_request.schema.json` — tx request JSON shape
- `references/tx_service_slugs.md` — chain slugs + notes
