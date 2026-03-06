---
name: near-batch-sender
description: Batch operations for NEAR tokens - send to multiple recipients, transfer NFTs, claim rewards with cost estimation.
---
# NEAR Batch Sender Skill

Batch operations for NEAR sends, NFT transfers, and claims with cost estimation.

## Description

This skill provides batch operations for sending NEAR tokens, transferring NFTs, and claiming rewards. Includes cost estimation before execution.

## Features

- Batch send NEAR to multiple addresses
- Batch transfer NFTs
- Batch claim operations
- Cost estimation before execution
- Progress tracking for batch operations

## Commands

### `near-batch send <sender_account> <file.json>`
Batch send NEAR to multiple recipients.

**JSON format:**
```json
{
  "recipients": [
    {"account": "account1.near", "amount": "1.5"},
    {"account": "account2.near", "amount": "0.5"}
  ]
}
```

### `near-batch nft <sender_account> <file.json>`
Batch transfer NFTs.

**JSON format:**
```json
{
  "transfers": [
    {"token_id": "123", "receiver": "account1.near", "contract": "nft.near"},
    {"token_id": "456", "receiver": "account2.near", "contract": "nft.near"}
  ]
}
```

### `near-batch estimate <sender_account> <file.json> [type]`
Estimate gas costs for a batch operation.

**Parameters:**
- `type` - Operation type: send, nft, claim (default: send)

### `near-batch claim <file.json>`
Batch claim rewards/airdrops.

## References

- NEAR CLI: https://docs.near.org/tools/near-cli
- NEAR Batch Actions: https://docs.near.org/api/rpc/transactions/batch-actions
