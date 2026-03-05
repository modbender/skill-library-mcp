---
name: receipt-manager
description: Receipt management skill. Use when: (1) User sends a receipt image, (2) User asks about expenses or receipts, (3) User wants monthly spending summary.
---

# Receipt Manager

Store and query receipt data locally.

## Trigger

- receipt, expense, invoice, spending, claim

## How to Use

### 1. Initialize (first time)

```bash
python3 scripts/receipt_db.py init
```

### 2. Add Receipt

After OpenClaw recognizes the receipt image, the data is saved automatically via handler.

### 3. Query

```bash
# List all
python3 scripts/receipt_db.py list

# Search
python3 scripts/receipt_db.py search --q "walmart"

# Monthly summary
python3 scripts/receipt_db.py summary --month 2026-02
```

## Files

- `scripts/receipt_db.py` - Main CLI tool
- `scripts/handler.py` - Receives JSON from OpenClaw, saves to DB
- `data/receipts/` - Local SQLite DB and images

## Privacy

All data stored locally on your machine. No cloud upload.
