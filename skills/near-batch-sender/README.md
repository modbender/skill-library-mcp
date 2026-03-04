# NEAR Batch Sender Skill

Batch operations for NEAR sends and NFT transfers.

## Installation

The skill is installed in `~/.openclaw/skills/near-batch-sender/`

## Usage

### Batch Send NEAR

Create `recipients.json`:
```json
{
  "recipients": [
    {"account": "account1.near", "amount": "1.5"},
    {"account": "account2.near", "amount": "0.5"}
  ]
}
```

Run:
```bash
node scripts/batch.js send myaccount.near recipients.json
```

### Batch Transfer NFTs

Create `nfts.json`:
```json
{
  "transfers": [
    {"token_id": "123", "receiver": "account1.near", "contract": "nft.example.near"},
    {"token_id": "456", "receiver": "account2.near", "contract": "nft.example.near"}
  ]
}
```

Run:
```bash
node scripts/batch.js nft myaccount.near nfts.json
```

### Estimate Costs

```bash
node scripts/batch.js estimate myaccount.near recipients.json send
```

## Requirements

- NEAR CLI installed and configured
- Sufficient balance for all transfers

## License

MIT
