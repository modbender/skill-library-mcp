---
name: farmos-land-portfolio
description: Query land ownership, leases, landlord info, and land payments. Write operations for payment management and lease renewals.
tags: [farming, land, leases, landlords]
---

# FarmOS Land Portfolio

Track owned and leased land, lease terms, landlord relationships, payments, and annual land costs.

## CRITICAL: Data Completeness Rules

**NEVER use partial or truncated data. These rules are non-negotiable:**

1. **NEVER use `/api/integration/dashboard`** — it truncates results to 5 items. Partial payment data is worse than no data because it creates a false sense of completeness.
2. **ALWAYS use the `/all` endpoints** listed below for complete data.
3. **If an endpoint returns an error or empty results, REPORT THE FAILURE to the user.** Do not silently fall back to a different endpoint or present partial data.
4. **ALWAYS state the total count** of records returned so the user knows the data is complete. Example: "Found 11 payments due in March totaling $175,058."
5. **If you cannot get complete data, say so explicitly.** "I was unable to retrieve complete payment data" is infinitely better than showing 5 of 11 payments.

## When This Skill Triggers

- "When do our leases expire?"
- "What's the rent on the Smith ground?"
- "Total land costs this year?"
- "Show overdue payments"
- "Landlord contact info"
- "Cost per acre by parcel"
- "List all leased parcels"
- "What payments are due in March?"
- "Cash requirements for next month"
- "Mark payment [X] as paid"
- "Mark all March payments paid"
- "Renew the Smith lease"
- "Preview lease renewals"

## Access Control

Lease terms, rent amounts, and landlord info are sensitive business data. Restrict to admin or manager roles only.

**Role mapping:** Check the sender's role in `~/.openclaw/farmos-users.json`. If the user is not admin or manager, tell them they don't have access to land portfolio data.

## API Base

http://100.102.77.110:8009

## Integration Endpoints (No Auth Required) — READ OPERATIONS ONLY

**IMPORTANT: Use auth endpoints for WRITE operations (mark-paid, renewals). Use integration `/all` endpoints for READ operations (listing payments, leases, landlords).**

### Payments (FULL — use this, not dashboard)
GET /api/integration/payments/all
- Returns ALL payments with full details — parcel names, landlord names, overdue status
- Query parameters:
  - `status` — pending, paid, overdue, scheduled
  - `payment_type` — rent, mortgage, property_tax, insurance, improvement, other
  - `parcel_id` — filter by specific parcel
  - `due_date_from` — YYYY-MM-DD range start
  - `due_date_to` — YYYY-MM-DD range end
  - `crop_year` — filter by crop year
- Examples:
  - All overdue: `/api/integration/payments/all?status=overdue`
  - March 2026 payments: `/api/integration/payments/all?due_date_from=2026-03-01&due_date_to=2026-03-31`
  - All rent payments: `/api/integration/payments/all?payment_type=rent`

### Upcoming Payments (next N days)
GET /api/integration/payments/upcoming?days=30
- Returns ALL upcoming payments within N days (no truncation)
- Use `days=60` or `days=90` for longer lookahead

### Leases (FULL)
GET /api/integration/leases/all
- Returns ALL leases with landlord contact info, rent terms, expiration status
- Query parameters:
  - `status` — active, expired
  - `landlord_id` — filter by landlord

### Expiring Leases
GET /api/integration/leases/expiring?days=90
- Returns ALL leases expiring within N days

### Landlords (FULL)
GET /api/integration/landlords/all
- Returns ALL landlords with contact info, active lease count, total acres, total rent

### Parcels
GET /api/integration/parcels
- Returns ALL parcels with ownership type, acres, county
- Query parameter: `ownership_type` — owned, leased

### Summary Stats
GET /api/integration/summary
- Total acres, owned/leased breakdown, parcel/lease/landlord counts, annual cost

### Annual Land Costs (by month and entity)
GET /api/integration/finance/costs?year=2026
- Monthly cost breakdown by category (rent, mortgage, tax, insurance)
- Entity breakdown
- Query parameters: `year`, `entity_id`

### Cost Per Field (for P&L)
GET /api/integration/finance/cost-per-field?year=2026
- Land costs allocated to production fields
- Query parameters: `year`, `entity_id`

### Overdue Items
GET /api/integration/tasks/overdue
- All overdue payments and reminders — high priority items

### Actionable Items
GET /api/integration/tasks/actionable?days_ahead=30
- Upcoming payments, expiring leases, pending reminders

## Authenticated Endpoints — WRITE OPERATIONS

These require JWT auth. See Authentication section below.

### Authentication

This skill accesses protected FarmOS endpoints that require a JWT token.

**To get a token:** Run the auth helper with the appropriate role:
```bash
TOKEN=$(~/clawd/scripts/farmos-auth.sh admin)
```

**To use the token:** Include it as a Bearer token:
```bash
curl -H "Authorization: Bearer $TOKEN" http://100.102.77.110:8009/api/endpoint
```

**Token expiry:** Tokens last 15 minutes. If you get a 401 response, request a new token.

### Mark Single Payment Paid
POST /api/payments/{id}/mark-paid
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "paid_date": "2026-02-15",
  "notes": "Check #1234"
}
```

### Mark Multiple Payments Paid (Bulk)
POST /api/payments/bulk/mark-paid
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "payment_ids": [12, 34, 56],
  "paid_date": "2026-02-15",
  "notes": "Batch check run"
}
```

### Mark Payments Paid by Date Range
POST /api/payments/bulk/mark-paid-by-date
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "due_date_from": "2026-03-01",
  "due_date_to": "2026-03-31",
  "paid_date": "2026-02-15",
  "payment_type": "rent",
  "notes": "March rent payments"
}
```

Use this when the user says "mark all March payments as paid" or similar bulk date-based operations.

### Preview Lease Renewal
POST /api/leases/renewal-preview
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "lease_ids": [5, 12],
  "new_start_date": "2027-03-01",
  "rent_increase_percent": 3.0
}
```

Returns: Preview of what the renewed leases would look like, including new payment schedules. Use this BEFORE executing bulk renewals so the user can confirm.

### Execute Bulk Lease Renewal
POST /api/leases/bulk-renew
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "lease_ids": [5, 12],
  "new_start_date": "2027-03-01",
  "new_end_date": "2028-02-28",
  "new_rent_amount": 52000.00,
  "rent_increase_percent": 3.0,
  "notes": "Annual renewal with 3% increase"
}
```

**IMPORTANT:** Always preview first, confirm with user, then execute.

### Year-End Rollover Preview
POST /api/payments/year-end-rollover/preview
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "from_year": 2026,
  "to_year": 2027
}
```

Returns: Preview of payment schedules that would be created for the new crop year.

### Year-End Rollover Execute
POST /api/payments/year-end-rollover/execute
Authorization: Bearer {token}
Content-Type: application/json

Body:
```json
{
  "from_year": 2026,
  "to_year": 2027,
  "apply_rent_increase": true,
  "rent_increase_percent": 2.5
}
```

**IMPORTANT:** This creates next year's payment schedules based on current year leases. Always preview first.

## FORBIDDEN Endpoints — Do NOT Use

| Endpoint | Why |
|----------|-----|
| `GET /api/integration/dashboard` | **Truncates to 5 items. NEVER use this.** |

## Key Concepts

- **Parcel:** A land unit — either owned or leased.
- **Lease types:** Cash rent, crop share, flex rent.
- **Lease expiration:** Critical to track — approaching expirations need proactive attention.
- **Land payments:** Rent, mortgage, property tax, insurance — each with due dates.

## Usage Notes

- Lease expiration tracking is the highest-value query — always flag leases expiring within 6 months.
- Payment status (due/overdue) is critical — flag overdue payments immediately.
- Cost per acre analysis helps compare owned vs leased economics.
- Landlord contact info is private — never share outside admin/manager channels.
- When asked about "cash requirements" or "what do we owe", always use `/api/integration/payments/all` with date filtering to get the COMPLETE picture.
- For financial planning questions, combine `/api/integration/payments/all` with `/api/integration/finance/costs` for the full view.
- **Write operations:** Always use authenticated endpoints for marking payments paid or renewing leases. Preview first when doing bulk operations.
- **Bulk payment marking:** When user says "mark all March payments paid", use the bulk-by-date endpoint rather than individual calls.
