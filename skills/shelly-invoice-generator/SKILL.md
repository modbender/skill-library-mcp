# Invoice Generator

Generate professional invoices in Markdown or HTML from simple inputs.

## Usage

```bash
./generate-invoice.sh \
  --client "Acme Corp" \
  --email "billing@acme.com" \
  --date "2026-02-22" \
  --due "2026-03-22" \
  --item "Web Development|40|150.00" \
  --item "Design Review|5|120.00" \
  --tax 10 \
  --currency USD \
  --invoice-number INV-001 \
  --from "Shelly Labs" \
  --format html
```

### Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `--client` | Client name (required) | — |
| `--email` | Client email | — |
| `--date` | Invoice date | today |
| `--due` | Due date | +30 days |
| `--item` | `"Description\|Qty\|Rate"` (repeatable) | — |
| `--tax` | Tax percentage | 0 |
| `--currency` | Currency code | USD |
| `--invoice-number` | Invoice ID | INV-{timestamp} |
| `--from` | Your name/company | — |
| `--format` | `md` or `html` | md |
| `--output` | Output file path | stdout |

### Output

- **Markdown**: Clean table-based invoice
- **HTML**: Uses `template.html` — professional, print-ready

### Examples

```bash
# Quick markdown invoice
./generate-invoice.sh --client "Bob" --item "Consulting|10|100" --format md

# HTML invoice saved to file
./generate-invoice.sh --client "Acme" --item "Dev|40|150" --format html --output invoice.html
```
