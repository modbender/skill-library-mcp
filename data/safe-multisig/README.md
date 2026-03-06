# safe-multisig-skill

Operate a Safe multisig smart account from the CLI (TypeScript strict):
- **create-safe** — predict address + optionally deploy a new Safe
- **safe-info** — read Safe state (owners/threshold/nonce)
- **list-pending** — list pending (queued) multisig transactions
- **propose-tx** — propose transactions (off-chain signatures via Transaction Service)
- **approve-tx** — add confirmations
- **execute-tx** — execute transactions onchain

## Requirements

- Node.js 18+
- Internet access to the Safe Transaction Service for your chain
- For propose/approve/execute/deploy: a signer private key for a Safe **owner**

## Install

```bash
./scripts/bootstrap.sh
```

## Tests

```bash
npm test          # vitest unit + CLI tests (70+ tests)
npm run test:smoke # live integration smoke tests
```

## TypeScript

```bash
npm run typecheck  # tsc --noEmit --strict
```

## Usage

### Check tx service connectivity

```bash
./scripts/safe_about.sh --chain base
```

### Create / predict a new Safe

```bash
npx tsx scripts/create-safe.ts \
  --chain base \
  --owners 0xOwner1,0xOwner2 \
  --threshold 2

# With on-chain deployment:
export SAFE_SIGNER_PRIVATE_KEY="..."
npx tsx scripts/create-safe.ts \
  --chain base --deploy \
  --owners 0xOwner1,0xOwner2 \
  --threshold 2
```

### Get Safe info

```bash
npx tsx scripts/safe-info.ts --chain base --safe 0xYourSafe
```

### List pending transactions

```bash
npx tsx scripts/list-pending.ts --chain base --safe 0xYourSafe
```

### Propose tx

```bash
export SAFE_SIGNER_PRIVATE_KEY="..."
npx tsx scripts/propose-tx.ts \
  --chain base \
  --rpc-url "$BASE_RPC_URL" \
  --tx-file references/example.tx.json
```

### Approve (confirm) tx

```bash
export SAFE_SIGNER_PRIVATE_KEY="..."
npx tsx scripts/approve-tx.ts \
  --chain base \
  --safe 0xYourSafe \
  --safe-tx-hash 0x...
```

### Execute tx

```bash
export SAFE_SIGNER_PRIVATE_KEY="..."
npx tsx scripts/execute-tx.ts \
  --chain base \
  --rpc-url "$BASE_RPC_URL" \
  --safe 0xYourSafe \
  --safe-tx-hash 0x...
```

## Supported Chains

Base, Ethereum, Optimism, Arbitrum, Polygon, BSC, Gnosis, Avalanche, and their testnets.

See `references/tx_service_slugs.md` for the full list.

## Security rules

- **Never paste private keys into chat.** Use env vars or files.
- Prefer low-privilege signers and spending limits.
- Always verify Safe address, chainId, and nonce before signing.
