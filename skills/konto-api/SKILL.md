# Konto — Personal Finance API

Query personal finance data from Konto (bank accounts, investments, assets, loans, transactions).

## Setup
```bash
# ~/.openclaw/secrets/konto.env
export KONTO_API_KEY="konto_xxxxxxxxxxxx"
export KONTO_URL="https://konto.angelstreet.io"
```

## Quick Answers

### "How much BTC do I have?"
```bash
source ~/.openclaw/secrets/konto.env
curl -s -H "Authorization: Bearer $KONTO_API_KEY" "$KONTO_URL/api/v1/investments" | jq '.investments[] | select(.code | test("BTC|bitcoin"; "i")) | {label, quantity, current_value}'
```

### "What's my net worth?"
```bash
curl -s -H "Authorization: Bearer $KONTO_API_KEY" "$KONTO_URL/api/v1/summary" | jq '{patrimoine_net, accounts: .accounts.total_balance, investments: .investments.total_value, assets: .assets.total_value, loans: .loans.total_remaining}'
```

### "When does my loan end?"
```bash
curl -s -H "Authorization: Bearer $KONTO_API_KEY" "$KONTO_URL/api/v1/loans" | jq '.loans[] | {name, remaining_amount, end_date, monthly_payment}'
```

### "What are my subscriptions?"
```bash
curl -s -H "Authorization: Bearer $KONTO_API_KEY" "$KONTO_URL/api/v1/summary" | jq '{count: .subscriptions.count, monthly: .subscriptions.monthly}'
```

### "How much do I spend on housing?"
```bash
curl -s -H "Authorization: Bearer $KONTO_API_KEY" "$KONTO_URL/api/v1/transactions?months=6&category=logement" | jq '{total: .total, transactions: [.transactions[] | {date, label, amount}]}'
```

### "Financial overview"
```bash
curl -s -H "Authorization: Bearer $KONTO_API_KEY" "$KONTO_URL/api/v1/summary"
```

## Helper Script
```bash
bash ~/.openclaw/workspace/skills/konto/scripts/konto.sh summary
bash ~/.openclaw/workspace/skills/konto/scripts/konto.sh investments
bash ~/.openclaw/workspace/skills/konto/scripts/konto.sh transactions 3  # last 3 months
bash ~/.openclaw/workspace/skills/konto/scripts/konto.sh loans
bash ~/.openclaw/workspace/skills/konto/scripts/konto.sh assets
bash ~/.openclaw/workspace/skills/konto/scripts/konto.sh accounts
```

## Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/summary` | Full financial overview (start here) |
| `GET /api/v1/accounts` | Bank accounts list |
| `GET /api/v1/transactions?months=6&category=X` | Categorized transactions |
| `GET /api/v1/investments` | Portfolio (ETFs, stocks, crypto) |
| `GET /api/v1/assets` | Real estate, vehicles |
| `GET /api/v1/loans` | Active loans |

## Full API Reference
See `~/shared/projects/konto/docs/api.md` for complete docs including analytics endpoints.

## Scope
This skill uses a **personal** scope key (free). For cross-user analytics (pro), see the `konto-analytics` skill.
