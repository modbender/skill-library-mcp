# Invoice Data Extraction

## Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `provider` | Company name | "Hetzner Online GmbH" |
| `invoice_number` | Unique identifier | "INV-12345" |
| `date` | Issue date | "2026-02-13" |
| `total` | Final amount | 89.50 |
| `currency` | ISO currency | "EUR" |

## Optional Fields (extract if present)

| Field | Description |
|-------|-------------|
| `provider_id` | Tax ID (CIF/NIF/VAT) |
| `provider_address` | Full address |
| `due_date` | Payment deadline |
| `subtotal` | Before tax |
| `tax_rate` | Percentage (21%, 10%, etc.) |
| `tax_amount` | Tax in currency |
| `line_items` | Array of {description, quantity, unit_price, total} |
| `payment_method` | Bank transfer, card, etc. |
| `iban` | For bank transfers |
| `reference` | Payment reference |

## Provider Normalization

Maintain aliases in `providers/index.json`:
```json
{
  "hetzner": {
    "canonical": "Hetzner",
    "aliases": ["Hetzner Online GmbH", "HETZNER ONLINE GMBH"],
    "tax_id": "DE812871812",
    "category": "hosting",
    "expected_day": 1
  }
}
```

## Category Detection

Auto-assign category based on provider or keywords:

| Category | Triggers |
|----------|----------|
| hosting | Hetzner, AWS, Google Cloud, DigitalOcean |
| software | Figma, Notion, GitHub, JetBrains |
| telecom | Vodafone, Movistar, Orange |
| utilities | electricity, gas, water |
| insurance | "seguro", "insurance", "policy" |
| office | "material", "supplies", "papelería" |
| professional | "consultoría", "asesoría", "legal" |

## Tax ID Validation

| Country | Format | Regex |
|---------|--------|-------|
| Spain (NIF) | 12345678A or X1234567A | `^[XYZ]?\d{7,8}[A-Z]$` |
| Spain (CIF) | A12345678 | `^[A-Z]\d{8}$` |
| Germany (VAT) | DE123456789 | `^DE\d{9}$` |
| EU (VIES) | XX + 8-12 chars | Validate via VIES API |

## Extraction Confidence

Rate each field:
- `high`: Clear text, validated format
- `medium`: OCR successful but unvalidated
- `low`: Partial match, needs review

Flag invoice for review if any required field is `low` confidence.
