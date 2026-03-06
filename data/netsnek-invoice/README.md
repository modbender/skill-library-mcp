# invoice

Creates and manages invoices as JSON files on GitHub. Supports sequential numbering, calculated preview before upload, and PDF generation via GitHub Actions.

## Features

- **Invoice Creation**: Guided workflow to create structured invoice JSON files
- **Sequential Numbering**: Automatically determines the next invoice number from existing files
- **Calculated Preview**: Uses `calc-preview.sh` to compute totals and format a Telegram preview (no LLM math needed)
- **Invoice Listing**: Browse and view existing invoices by year
- **Discount Support**: Per-item percentage discounts with correct calculations
- **German Formatting**: Displays amounts with comma decimals and period thousands separators

## Prerequisites

- OpenClaw >= 0.8.0
- GitHub repository for invoice storage (should be **private**)
- GitHub Token with `contents: write` permission
- Python 3 on the server (for calculations and JSON operations)
- `curl` and `base64` on the server

## Installation

```bash
openclaw skill install invoice
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub PAT with `contents: write` | Yes |
| `INVOICE_REPO` | GitHub repository in `owner/repo` format | Yes |

### Repository Structure

The target repository will have the following structure:

```
repo/
  data.json              (sender defaults)
  invoice.sty            (PDF template)
  main.tex               (LaTeX entry point)
  Kunden/
    1001.json            (customer data)
  RE-2026/
    RE-6001.json
    RE-6002.json
  AN-2026/
    AN-6001.json
```

### Invoice JSON Schema

The JSON stores raw data only. **All calculations are handled by `invoice.sty` (PDF) and `calc-preview.sh` (Telegram preview).**

```json
{
  "sender": { "company": "...", "line": "...", "address": [...], "contact": [...], "legal": [...], "bank": [...] },
  "meta": {
    "id": "RE-6001",
    "title": "Rechnung Nr. {id}",
    "date": "17.02.2026",
    "customerId": "1001",
    "contactPerson": "..."
  },
  "intro": { "greeting": "...", "text": "..." },
  "items": [
    { "title": "...", "description": "...", "qty": 1, "unitPrice": 1000.0, "discountPercent": 5 }
  ],
  "totals": { "taxNote": "..." },
  "payment": { "terms": "...", "status": "..." }
}
```

**Key points:**
- `items[].qty` can be a number or a string (e.g. `"pauschal"`, `"4,00 Stk"`)
- `items[].discountPercent` is optional (percentage, e.g. `5` for 5%)
- `totals` contains only `taxNote` (text) -- no calculated fields
- `sender` data is loaded from `data.json` or a previous invoice

## Usage

### Creating an Invoice

1. Send `/invoice` to the bot
2. Provide customer details and line items
3. Bot runs `calc-preview.sh` to compute totals and show preview
4. Confirm to upload JSON to GitHub
5. GitHub Action builds the PDF and sends it via email

### Commands

- `/invoice` -- Create a new invoice or offer
- `/rechnungen` -- List invoices for the current year
- `/rechnung 6001` -- Show a specific invoice

## Scripts

| Script | Purpose | Parameters |
|--------|---------|------------|
| `calc-preview.sh` | Calculate totals and generate Telegram preview | `'<JSON>'` |
| `push-invoice.sh` | Upload invoice JSON to GitHub | `<PREFIX> <YEAR> <NUMBER> '<JSON>'` |
| `get-invoices.sh` | List or fetch invoices | `[PREFIX] [YEAR] [NUMBER]` |
| `get-next-number.sh` | Get next sequential number | `[PREFIX] [YEAR]` |

## Security and Privacy

### Token Scope

Use a **fine-grained PAT** scoped to a single repository:

| Permission | Level | Reason |
|------------|-------|--------|
| Contents | Read & Write | Push invoice JSON files |

### Repository Privacy

The target repository **must be private**. It stores invoice data including:
- Company names and addresses
- VAT IDs and bank details (IBAN, BIC)
- Pricing and line item details

### Data Retention

Invoice data may need to be retained for tax compliance (typically 7 years in Austria/Germany). Ensure your repository retention policies align with legal requirements.

## License

MIT
