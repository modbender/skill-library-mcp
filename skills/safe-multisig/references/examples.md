# Examples

## 1) Propose a simple ETH transfer

1) Encode the call (for ETH transfer, calldata is `0x`).
2) Create a tx file:

```json
{
  "safe": "0xYourSafe",
  "transactions": [
    {
      "to": "0xRecipient",
      "data": "0x",
      "value": "1000000000000000",
      "operation": 0
    }
  ]
}
```

3) Propose:

```bash
export SAFE_SIGNER_PRIVATE_KEY=...
npx tsx scripts/propose-tx.ts --chain base --rpc-url $BASE_RPC_URL --tx-file /path/to/tx.json
```

## 2) Confirm a proposed tx

```bash
export SAFE_SIGNER_PRIVATE_KEY=...
npx tsx scripts/approve-tx.ts --chain base --safe 0xYourSafe --safe-tx-hash 0x...
```

## 3) Execute

```bash
export SAFE_SIGNER_PRIVATE_KEY=...
npx tsx scripts/execute-tx.ts --chain base --rpc-url $BASE_RPC_URL --safe 0xYourSafe --safe-tx-hash 0x...
```

## 4) Create a new 2-of-3 Safe

```bash
npx tsx scripts/create-safe.ts \
  --chain base \
  --owners 0xAlice,0xBob,0xCarol \
  --threshold 2
```
