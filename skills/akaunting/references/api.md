# Akaunting API Reference

## Authentication

HTTP Basic Auth with user email and password.

```bash
curl -u "email:password" http://localhost:8080/api/ping
```

User must have `read-api` permission. Admin role has this by default.

## Endpoints

### Ping
```
GET /api/ping
```
Returns `{"status": "ok", "timestamp": "..."}` if authenticated.

### Accounts
```
GET /api/accounts              # List all accounts
GET /api/accounts/{id}         # Get single account
POST /api/accounts             # Create account
PUT /api/accounts/{id}         # Update account
DELETE /api/accounts/{id}      # Delete account
```

**Create account:**
```json
{
  "name": "Checking",
  "type": "bank",
  "number": "001",
  "currency_code": "USD",
  "opening_balance": 0
}
```

### Categories
```
GET /api/categories            # List all categories
POST /api/categories           # Create category
```

**Create category:**
```json
{
  "name": "Consulting",
  "type": "income",
  "color": "#6da252"
}
```
Types: `income`, `expense`, `item`, `other`

### Transactions
```
GET /api/transactions          # List all transactions
GET /api/transactions?search=type:income   # Filter by type
POST /api/transactions         # Create transaction
```

**Create income:**
```json
{
  "type": "income",
  "number": "INC-0001",
  "account_id": 1,
  "category_id": 3,
  "amount": 100.00,
  "currency_code": "USD",
  "currency_rate": 1.0,
  "paid_at": "2026-02-07",
  "payment_method": "offline-payments.cash.1",
  "description": "Payment received"
}
```

**Create expense:**
```json
{
  "type": "expense",
  "number": "EXP-0001",
  "account_id": 1,
  "category_id": 4,
  "amount": 50.00,
  "currency_code": "USD",
  "currency_rate": 1.0,
  "paid_at": "2026-02-07",
  "payment_method": "offline-payments.cash.1",
  "description": "Office supplies"
}
```

**Payment methods:**
- `offline-payments.cash.1` - Cash
- `offline-payments.bank_transfer.2` - Bank Transfer

### Items
```
GET /api/items                 # List all items
POST /api/items                # Create item
```

**Create item:**
```json
{
  "name": "Consulting Hour",
  "sale_price": 150.00,
  "purchase_price": 0,
  "category_id": 5,
  "enabled": true
}
```

### Other Endpoints

| Endpoint | Description | Notes |
|----------|-------------|-------|
| `/api/contacts` | Customers/Vendors | Requires extra permissions |
| `/api/documents` | Invoices/Bills | Requires extra permissions |
| `/api/currencies` | Currency list | |
| `/api/taxes` | Tax rates | |
| `/api/transfers` | Account transfers | |
| `/api/reports` | Financial reports | |

## Response Format

All responses are JSON with pagination:

```json
{
  "data": [...],
  "links": {
    "first": "...",
    "last": "...",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "per_page": 25,
    "total": 5
  }
}
```

## Error Responses

```json
{
  "message": "Error description",
  "errors": {
    "field": ["Validation error"]
  },
  "status_code": 422
}
```

Common status codes:
- `401` - Invalid credentials
- `403` - Missing permissions
- `422` - Validation error
- `500` - Server error
