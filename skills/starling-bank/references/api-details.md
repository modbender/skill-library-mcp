# Starling Bank API Details

## Available Tools (24 total)

### Account Management
| Tool | Description |
|------|------------|
| `accounts_list` | List all accounts for the account holder |
| `account_balance_get` | Get cleared and effective balance |
| `account_holder_get` | Get account holder personal details |
| `account_identifiers_get` | Get sort code, account number, BIC, IBAN |

### Transactions
| Tool | Description |
|------|------------|
| `transactions_list` | List feed items for a date range (requires accountUid, categoryUid, min/max timestamps) |
| `feed_item_get` | Get single transaction with attachments |
| `feed_item_spending_category_update` | Recategorise a transaction |
| `feed_item_note_update` | Add/update a note on a transaction |
| `feed_item_attachment_upload` | Attach a file (image/PDF) to a transaction |
| `feed_item_attachment_download` | Download an attachment (returns base64) |

### Payments
| Tool | Description |
|------|------------|
| `payees_list` | List all saved payees |
| `payee_create` | Create a new payee (INDIVIDUAL or BUSINESS) |
| `payee_delete` | Delete a payee |
| `payment_create` | Send money to a payee |

### Savings Goals
| Tool | Description |
|------|------------|
| `savings_goals_list` | List all savings goals |
| `savings_goal_create` | Create a new goal (optional target amount) |
| `savings_goal_update` | Update goal name/target |
| `savings_goal_delete` | Delete a goal |
| `savings_goal_deposit` | Move money into a goal |
| `savings_goal_withdraw` | Move money out of a goal |

### Direct Debits & Standing Orders
| Tool | Description |
|------|------------|
| `direct_debits_list` | List all direct debit mandates |
| `standing_orders_list` | List all standing orders |

### Cards
| Tool | Description |
|------|------------|
| `cards_list` | List all cards |
| `card_lock_update` | Enable or disable (lock/unlock) a card |

## Amount Format

All monetary amounts use this structure:
```json
{
  "currency": "GBP",
  "minorUnits": 1050
}
```
`minorUnits` = pence. So £10.50 = 1050, £1.00 = 100.

## Common Patterns

### Get balance in pounds
Response `effectiveBalance.minorUnits` / 100 = balance in £.

### Transaction date ranges
Both `minTransactionTimestamp` and `maxTransactionTimestamp` are required.
Format: ISO 8601 with timezone, e.g. `2026-02-01T00:00:00.000Z`

### Payee types
- `INDIVIDUAL` — personal accounts
- `BUSINESS` — business accounts

### Bank identifier types
- `SORT_CODE` — UK sort code (6 digits)
- `SWIFT_BIC` — international SWIFT/BIC code
