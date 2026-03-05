---
name: akaunting
description: Interact with Akaunting open-source accounting software via REST API. Use for creating invoices, tracking income/expenses, managing accounts, and bookkeeping automation. Triggers on accounting, bookkeeping, invoicing, expenses, income tracking, or Akaunting mentions.
---

# Akaunting Skill

CLI and API integration for Akaunting, a free open-source accounting platform.

## Quick Start

```bash
# Test connection
akaunting ping

# List data
akaunting accounts
akaunting categories  
akaunting transactions

# Create transactions
akaunting income --amount 100 --category Sales --description "Payment received"
akaunting expense --amount 50 --category Other --description "Office supplies"
```

## Setup

### 1. Deploy Akaunting

```bash
# Use the provided docker-compose
cp skills/akaunting/assets/docker-compose.yml ~/akaunting/
cd ~/akaunting && docker compose up -d
```

Access web UI at `http://YOUR_IP:8080` and complete the setup wizard.

### 2. Apply Required Fix

**Critical:** Akaunting has a bug where module event listeners don't auto-register. Run:

```bash
python3 skills/akaunting/scripts/fix_event_listener.py
```

Or manually add to `/var/www/html/app/Providers/Event.php` in the `$listen` array:

```php
'App\Events\Module\PaymentMethodShowing' => [
    'Modules\OfflinePayments\Listeners\ShowAsPaymentMethod',
],
```

### 3. Configure Credentials

```bash
mkdir -p ~/.config/akaunting
cat > ~/.config/akaunting/config.json << EOF
{
  "url": "http://YOUR_IP:8080",
  "email": "your@email.com",
  "password": "your-password"
}
EOF
```

Or set environment variables: `AKAUNTING_URL`, `AKAUNTING_EMAIL`, `AKAUNTING_PASSWORD`

## CLI Commands

| Command | Description |
|---------|-------------|
| `akaunting ping` | Test API connection |
| `akaunting accounts` | List bank accounts |
| `akaunting categories [--type income\|expense]` | List categories |
| `akaunting transactions [--type income\|expense]` | List transactions |
| `akaunting items` | List products/services |
| `akaunting income --amount X --category Y` | Create income |
| `akaunting expense --amount X --category Y` | Create expense |
| `akaunting item --name X --price Y` | Create item |

Add `--json` to any command for JSON output.

## API Reference

See `references/api.md` for full endpoint documentation.

### Key Endpoints

- `GET /api/ping` - Health check
- `GET/POST /api/accounts` - Bank accounts
- `GET/POST /api/categories` - Income/expense categories
- `GET/POST /api/transactions` - Income/expense records
- `GET/POST /api/items` - Products/services

Authentication: HTTP Basic Auth with user email/password. User needs `read-api` permission (Admin role has this by default).

## Troubleshooting

**"Payment method is invalid" error:**
The event listener fix wasn't applied. Run `fix_event_listener.py`.

**401 Unauthorized:**
Check credentials in config.json. User must have API access permission.

**403 Forbidden on contacts/documents:**
User needs additional permissions for these endpoints.
