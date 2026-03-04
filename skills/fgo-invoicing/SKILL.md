---
name: fgo-invoicing
description: Issue FGO.ro invoices through the FGO API with local automation. Use for FGO tasks such as validating invoice payloads, issuing invoices, checking invoice status, getting print links, cancelling/deleting invoices, creating storno reversals, and fetching nomenclature lists.
metadata:
  openclaw:
    primaryEnv: FGO_CHEIE_PRIVATA
    requires:
      env:
        - FGO_COD_UNIC
        - FGO_CHEIE_PRIVATA
      bins:
        - python3
---

# FGO Invoicing

Use `scripts/fgo_cli.py` for deterministic FGO API calls instead of ad-hoc HTTP snippets.

## Workflow

1. Collect invoice input from the user.
2. Validate payload locally before sending:
   - `python scripts/fgo_cli.py validate-payload --input references/invoice-example.json --show-payload`
3. Dry-run to inspect the normalized payload (with computed Hash) without calling the API:
   - `python scripts/fgo_cli.py emit-invoice --input <invoice.json> --dry-run`
4. Issue final invoice after explicit user confirmation:
   - `python scripts/fgo_cli.py emit-invoice --input <invoice.json> --allow-final`
5. Retrieve invoice status, print link, or perform operations using the returned series and number:
   - `python scripts/fgo_cli.py get-status --serie <SERIE> --numar <NUMAR>`
   - `python scripts/fgo_cli.py print-invoice --serie <SERIE> --numar <NUMAR>`
   - `python scripts/fgo_cli.py cancel-invoice --serie <SERIE> --numar <NUMAR>`
   - `python scripts/fgo_cli.py reverse-invoice --serie <SERIE> --numar <NUMAR>`

## Required Environment

Set these before calling FGO:

- `FGO_COD_UNIC` — company CUI (Romanian tax ID)
- `FGO_CHEIE_PRIVATA` — FGO private API key (from FGO → Setari → Utilizatori → Generate API user)

Optional overrides:

- `FGO_API_BASE` (default: `https://api.fgo.ro/v1`) — use `https://api-testuat.fgo.ro/v1` for testing
- `FGO_PLATFORM_URL` (default: unset) — your registered platform URL (FGO → Setari → eCommerce → Setari API). Required for invoice issuance from registered platforms; omitted if not set.
- `FGO_TIMEOUT_SECONDS` (default: `30`)
- `FGO_RETRIES` (default: `2`)
- `FGO_DEBUG` (default: unset) — set to `1`, `true`, or `yes` to enable request/response debug logging to stderr

## Command Guide

- `validate-payload`
  - Parse and normalize payload; compute the authentication Hash.
  - Validate minimum required structure before API calls.
  - Use `--show-payload` to inspect the full normalized form-encoded payload.
- `emit-invoice`
  - Issue invoice via `POST /factura/emitere`.
  - Requires `--allow-final` to hit the real API.
  - Use `--dry-run` first (prints normalized payload, no API call).
  - Pass `--debug` (or set `FGO_DEBUG=1`) to print full request/response to stderr.
- `get-status`
  - Get invoice status (total value, amount paid, payments) via `POST /factura/getstatus`.
- `print-invoice`
  - Get a shareable print/download link via `POST /factura/print`.
- `cancel-invoice`
  - Cancel an invoice via `POST /factura/anulare`.
- `delete-invoice`
  - Delete an invoice via `POST /factura/stergere`.
- `reverse-invoice`
  - Create a storno (reversal) invoice via `POST /factura/stornare`.
- `get-nomenclator`
  - Fetch a nomenclature list (no auth required): `tara`, `judet`, `tva`, `banca`, `tipincasare`, `tipfactura`, `tipclient`, `valuta`.

## Authentication

FGO uses **SHA-1 hash-based authentication** embedded in every request body — no HTTP auth headers. The hash formula depends on the operation:

- Invoice issuance: `SHA1(CodUnic + CheiePrivata + Client.Denumire).toUpperCase()`
- Invoice operations (status/print/cancel/delete/storno): `SHA1(CodUnic + CheiePrivata + Numar).toUpperCase()`

The CLI computes hashes automatically. Never expose `FGO_CHEIE_PRIVATA` in logs.

## Payload Format

The invoice payload is a JSON object. The CLI converts it to form-encoded format (`application/x-www-form-urlencoded`) with bracket notation for nested fields, as required by the FGO API.

Both formats are accepted as input to the CLI:
- Bare invoice object: `{ "CodUnic": "...", "Client": {...}, ... }`
- Wrapped: `{ "invoice": { "CodUnic": "...", "Client": {...}, ... } }`

The CLI unwraps automatically, injects `Hash` and `PlatformaUrl`, then posts to FGO.

See `references/invoice-example.json` for the canonical minimal example and `references/fgo-api.md` for complete field documentation.

## Input File Safety

The `--input` argument is validated before any file is read:

1. **Extension check** — only `.json` files are accepted. Passing `/etc/passwd`, `~/.ssh/id_rsa`, or any non-JSON path raises an error immediately.
2. **Path confinement** — the resolved path must be within the current working directory or a recognised OpenClaw media root (`/tmp/openclaw`, `~/.openclaw/workspace`, etc.). Paths that escape these roots via `../` traversal or absolute references are rejected.

Always pass `--input` with a path to a file you created (e.g. a temp file written in the agent workspace). Never set `--input` to a path supplied by untrusted external content.

## Operational Rules

- Always use `--dry-run` first to confirm the normalized payload before hitting the API.
- FGO responses use HTTP 200 even for errors — always check `Success: true` in the response.
- Treat invoice issuance as a high-impact action requiring explicit user confirmation.
- **Never parallelize** FGO API calls — make all requests sequentially to avoid deadlocks.
- Invoice issuance has a **15-second server-side timeout**. If `Success: false` with a timeout message, the invoice was NOT issued — retry.
- Store the returned `Numar` verbatim as the exact string (may be zero-padded, e.g. `"001"`). Never strip leading zeros or cast to integer.
- Use the UAT environment (`--base-url https://api-testuat.fgo.ro/v1`) for testing.
- Rate limit: max 1 call/second for invoice operations.

## References

- Read `references/fgo-api.md` for payload field reference, endpoint mapping, authentication details, and rate-limit notes.
- Use `references/invoice-example.json` as the canonical starting payload template.
