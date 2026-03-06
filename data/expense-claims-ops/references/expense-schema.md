# Expense Item Schema

Use this normalized row format:

- item_id
- date
- merchant
- amount
- currency
- category (transport / meal / lodging / software / office / misc)
- payment_method (card / cash / transfer)
- business_purpose
- project_or_client (optional)
- receipt_status (attached / missing / unreadable)
- policy_risk (none / low / medium / high / policy not provided)
- claim_status (ready / blocked)
- block_reason (if blocked)

## Block Rules (default)
- Missing receipt => blocked
- Missing business purpose => blocked
- Unreadable receipt => blocked
- Suspected duplicate (same date+merchant+amount) => blocked until confirmed

## Totals
Always compute:
- total_claim_ready (by currency)
- total_blocked (by currency)
- category totals (by currency)
- blocked_count
