---
name: splitxch
description: Create SplitXCH royalty split addresses from plain language descriptions. Use when the user wants to split XCH payments, royalties, or revenue between multiple recipients. Triggers on "split royalties", "royalty split", "splitxch", "split XCH between", "revenue share", "payment split", "basis points split", or any request to divide Chia payments among wallets. Supports nested/cascading splits for complex hierarchies and 128+ recipients.
---

# SplitXCH Royalty Split Builder

Create complex XCH royalty distribution addresses from natural language descriptions.

## How It Works

SplitXCH creates special Chia blockchain addresses that automatically split incoming payments to multiple recipients based on configured percentages. The API computes a puzzle address; any XCH sent to that address gets distributed automatically on-chain.

## Workflow

1. Parse the user's plain-language split description into recipients with percentages
2. Convert percentages to basis points (scale to 9850 total, API adds 150 bps / 1.5% fee)
3. For nested splits (splits-of-splits), build bottom-up: create leaf splits first, then use their addresses as recipients in parent splits
4. Call the SplitXCH API via `scripts/splitxch.sh` or direct curl
5. Return the generated split address and a summary

## Basis Points Conversion

- 10,000 bps = 100%. API fee = 150 bps (1.5%). Recipients get 9,850 bps total.
- Formula: `points = round(percentage / 100 * 9850)`
- Adjust last recipient so points sum to exactly 9850.

Example: "Split 60/40 between Alice and Bob"
- Alice: round(0.60 * 9850) = 5910
- Bob: 9850 - 5910 = 3940

## Building the API Payload

```json
{
  "recipients": [
    {"name": "Alice", "address": "xch1...", "points": 5910, "id": 1},
    {"name": "Bob", "address": "xch1...", "points": 3940, "id": 2}
  ]
}
```

Save to a temp file and run:
```bash
bash <skill_dir>/scripts/splitxch.sh /tmp/split-payload.json
```

## Nested Splits (>128 recipients or hierarchies)

When the user describes groups within groups:
1. Create each leaf-level split first via the API
2. Use the returned `address` as a recipient in the parent split
3. Each split level incurs its own 150 bps fee

Example: "Team A (Alice 50%, Bob 50%) gets 70%, Charlie gets 30%"
1. Create Team A split: Alice 4925 + Bob 4925 = 9850 → returns `xch1teamA...`
2. Create parent split: TeamA address 6895 + Charlie 2955 = 9850

## Validation Rules

- All addresses must start with `xch1` and be valid bech32m
- Max 128 recipients per split
- All addresses unique within a split
- Each recipient's points > 0
- Points must sum to exactly 9850

## Output Format

After creating a split, present:
1. **Split Address**: The generated `xch1...` address
2. **Summary Table**: Each recipient's name, address (truncated), and percentage
3. **Fee Note**: "SplitXCH takes a 1.5% platform fee per split level"
4. **Usage**: "Send XCH to this address and it will automatically distribute to all recipients"

If nested, show the full tree structure.

## API Reference

For detailed API docs, validation rules, and error handling, see [references/api.md](references/api.md).

## Important Notes

- The user MUST provide valid XCH wallet addresses for all recipients. If addresses are missing, ask for them before calling the API.
- If the user only provides names and percentages without addresses, list what's needed and ask.
- For dry runs / previews, show the calculated basis points without calling the API.
