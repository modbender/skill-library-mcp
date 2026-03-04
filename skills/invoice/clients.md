# Client Database

## Schema

`clients/index.json`:
```json
{
  "clients": [
    {
      "id": "acme",
      "name": "Acme Corp S.L.",
      "tax_id": "B87654321",
      "address": {
        "street": "Av. Principal 456",
        "city": "Barcelona",
        "postal": "08001",
        "country": "ES"
      },
      "email": "contabilidad@acme.com",
      "payment_terms": 30,
      "default_rate": null,
      "notes": "Contact: María García",
      "created_at": "2025-01-15",
      "last_invoice": "2026-02-01"
    }
  ]
}
```

## Required Fields (B2B)

| Field | Required | Why |
|-------|----------|-----|
| name | ✓ | Legal name for invoice |
| tax_id | ✓ | Required for VAT deduction |
| address | ✓ | Legal requirement |
| email | Recommended | For delivery |

## Lookup and Matching

When user says "factura a Acme":
1. Search by name (case-insensitive, partial match)
2. If multiple matches → ask for clarification
3. If no match → offer to create new client

**Fuzzy matching:**
- "acme" → "Acme Corp S.L."
- "Hetzner" → "Hetzner Online GmbH"

## Creating New Client

Collect in order:
1. Legal name (exact as appears on their invoices)
2. Tax ID (validate format)
3. Address (street, city, postal, country)
4. Email (for sending invoices)
5. Payment terms (default: 30 days)

**Validation:**
- Tax ID format per country (see `legal.md`)
- Don't allow duplicate tax IDs

## Updating Client

"Cambia la dirección de Acme a..."
- Update in `index.json`
- Keep history? (optional)

## Client Reports

"¿Cuánto he facturado a Acme este año?"
- Sum all invoices where client.id = "acme" AND year = current
- Show breakdown by month
