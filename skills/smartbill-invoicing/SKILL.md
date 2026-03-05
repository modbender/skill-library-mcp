---
name: smartbill-invoicing
description: Issue SmartBill invoices through the SmartBill.ro API with local automation. Use for SmartBill tasks such as validating invoice payloads, creating invoices, listing available document series, and downloading invoice PDFs by series and number.
metadata:
  openclaw:
    primaryEnv: SMARTBILL_TOKEN
    requires:
      env:
        - SMARTBILL_USERNAME
        - SMARTBILL_TOKEN
        - SMARTBILL_COMPANY_VAT_CODE
      bins:
        - python3
---

# SmartBill Invoicing

Use `scripts/smartbill_cli.py` for deterministic SmartBill API calls instead of ad-hoc HTTP snippets.

## Workflow

1. Collect invoice input from the user.
2. Validate payload locally before sending:
   - `python scripts/smartbill_cli.py validate-payload --input references/invoice-example.json --show-payload`
3. Dry-run to inspect the normalized payload without calling the API:
   - `python scripts/smartbill_cli.py create-invoice --input <invoice.json> --dry-run`
4. Issue final invoice after explicit user confirmation:
   - `python scripts/smartbill_cli.py create-invoice --input <invoice.json> --allow-final`
5. Retrieve PDF once series and number are known:
   - `python scripts/smartbill_cli.py download-invoice-pdf --series-name <SERIES> --number <NO> --output <file.pdf>`
   - **Use the exact `number` string returned by SmartBill (zero-padded, e.g. `"0123"`). Do not strip leading zeros or convert to an integer.**
   - **`--output` accepts absolute or relative paths and must end in `.pdf`.**

## Required Environment

Set these before calling SmartBill:

- `SMARTBILL_USERNAME` - SmartBill login email
- `SMARTBILL_TOKEN` - SmartBill API token
- `SMARTBILL_COMPANY_VAT_CODE` - default CIF (optional but recommended)

Optional overrides:

- `SMARTBILL_API_BASE` (default: `https://ws.smartbill.ro/SBORO/api`)
- `SMARTBILL_TIMEOUT_SECONDS` (default: `30`)
- `SMARTBILL_RETRIES` (default: `2`)
- `SMARTBILL_DEBUG` (default: unset) — set to `1`, `true`, or `yes` to enable request/response debug logging to stderr

## Command Guide

- `validate-payload`
  - Parse and normalize payload shape (bare invoice object or `{ "invoice": {...} }` wrapper both accepted).
  - Validate minimum required structure before API calls.
- `create-invoice`
  - Create invoice via `POST /invoice`.
  - Requires `--allow-final` to issue a final invoice.
  - Supports `--dry-run` (prints normalized payload, no API call) and `--force-draft`.
  - Pass `--debug` (or set `SMARTBILL_DEBUG=1`) to print full request/response payloads to stderr.
- `get-series`
  - Query available SmartBill series via `GET /series`.
- `download-invoice-pdf`
  - Fetch PDF via `GET /invoice/pdf` using CIF + series + number.
  - `--output` accepts an absolute or relative `.pdf` path. Relative paths are resolved against the current working directory. The resolved path must fall within an OpenClaw-allowed media root or the current working directory.

## Payload Format

The invoice payload is a flat JSON object sent directly to the SmartBill API. See `references/invoice-example.json` for the canonical minimal example and `references/smartbill-api.md` for field documentation.

Both formats are accepted as input to the CLI:
- Bare invoice object: `{ "companyVatCode": "...", "client": {...}, ... }`
- Wrapped: `{ "invoice": { "companyVatCode": "...", "client": {...}, ... } }`

The CLI unwraps automatically and sends the invoice object directly to the API.

## Operational Rules

- Always use `--dry-run` first to confirm the normalized payload before hitting the API.
- Treat final invoice issuance (`isDraft: false`) as a high-impact action requiring explicit user confirmation.
- Set `client.saveToDb: false` and `products[].saveToDb: false` to avoid persisting test data.
- Preserve SmartBill response data (series, number, message) in run logs. Store `number` verbatim as returned — it is zero-padded (e.g. `"0123"`) and must never be stripped of leading zeros or cast to an integer.
- Respect SmartBill rate limits: max 30 calls per 10 seconds.

## References

- Read `references/smartbill-api.md` for payload field reference, endpoint mapping, and auth/rate-limit notes.
- Use `references/invoice-example.json` as the canonical starting payload template.
