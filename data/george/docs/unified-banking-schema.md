# Unified Banking Schema (George + Raiffeisen ELBA)

Goal: make **George** (Erste/Sparkasse) and **Raiffeisen ELBA** expose the *same core functions* and (optionally) the *same JSON output schema*, so downstream tooling (dashboards, accounting exports, automation) can treat them uniformly.

This doc proposes a **canonical schema** for:
- `accounts` (including balances/value)
- `transactions`

It also documents **field mapping** from each bank source and highlights which fields are **identical**, **missing**, or **bank-specific**.

---

## Core functions (target parity)

Both skills should ideally support these commands (same flags + output):

1) `login` / `logout`
2) `accounts` (includes balances/value; no separate `balances` command)
3) `transactions --account <id|iban> --from <date> --until <date>`
4) `documents` / `statements` (PDF download + listing)
5) `export` (machine exports, e.g. CAMT53/MT940/CSV/JSON where supported)

For every command:
- default output is **human-readable**
- `--json` prints canonical JSON

---

## Common types

### Money

```json
{ "amount": 123.45, "currency": "EUR" }
```

Notes:
- keep `currency` as ISO 4217 (`EUR`, `USD`, …)
- amounts are signed (expenses negative, income positive) unless the source is explicitly unsigned

### Dates
- canonical JSON uses ISO-8601 dates: `YYYY-MM-DD`
- canonical JSON uses ISO-8601 timestamps with timezone where available

---

## Canonical `accounts` schema

### Canonical JSON (proposed)

```json
{
  "institution": "george" | "elba",
  "fetchedAt": "2026-01-28T10:00:00+01:00",
  "accounts": [
    {
      "id": "string",                 // stable internal id (bank product id, depot id, etc)
      "type": "checking"|"savings"|"debt"|"creditcard"|"depot"|"other",
      "name": "string",
      "iban": "AT..." ,               // null for products without IBAN
      "currency": "EUR",

      "balances": {
        "booked": {"amount": 0.0, "currency": "EUR"},
        "available": {"amount": 0.0, "currency": "EUR"},
        "asOf": "2026-01-28"           // optional, if bank provides
      },

      "securities": {
        "value": {"amount": 0.0, "currency": "EUR"},
        "profitLoss": {
          "amount": 0.0,
          "currency": "EUR",
          "percent": 0.0
        }
      },

      "raw": { }
    }
  ]
}
```

Rules:
- `balances` is present for bank accounts/cards/loans.
- `securities` is present for depot/portfolio style products.
- `raw` is optional and should contain the bank-native object (useful for debugging/migration).

### Human-readable output (proposed)

One line per account, consistent across both skills:

- `Name` — `IBAN (short)` — `booked` (and `available` if differs) — currency — type

Example:

- Main Account — AT12…7890 — 1,234.56 EUR (avail 1,100.00) — checking
- Depot — AT98…4321 — value 10,000.00 EUR (P/L +120.00 / +1.2%) — depot

---

## Canonical `transactions` schema

### Canonical JSON (proposed)

```json
{
  "institution": "george" | "elba",
  "account": {
    "id": "string",
    "iban": "AT..."
  },
  "range": { "from": "2026-01-01", "until": "2026-01-31" },
  "fetchedAt": "2026-01-28T10:00:00+01:00",
  "transactions": [
    {
      "id": "string",                    // bank transaction id if available
      "status": "booked" | "pending",

      "bookingDate": "2026-01-10",       // Buchungstag
      "valueDate": "2026-01-10",         // Valuta, if available

      "amount": {"amount": -12.34, "currency": "EUR"},

      "counterparty": {
        "name": "string",
        "iban": "AT...",
        "bic": "string"
      },

      "description": "string",           // short label
      "purpose": "string",               // remittance / Verwendungszweck

      "references": {
        "paymentReference": "string",    // Zahlungsreferenz
        "endToEndId": "string",
        "mandateId": "string",
        "creditorId": "string",
        "bankReference": "string"
      },

      "category": {
        "code": "string",                // provider category code (e.g. ELBA kategorieCode)
        "label": "string"
      },

      "raw": { }
    }
  ]
}
```

### Human-readable output (proposed)

One line per transaction:

`YYYY-MM-DD  ±amount CCY  Counterparty — Description (optional short purpose)`

Example:

`2026-01-10  -12.34 EUR  BILLA — groceries`

---

## Mapping: Raiffeisen ELBA → canonical

ELBA already has a **reference schema** and the API returns a relatively rich transaction object.

### Accounts

ELBA outputs two shapes:
- **Non-Depot**: `{type, name, iban, balance, available, ...}`
- **Depot**: `{type:"Depot", name, iban, value, profit_loss, ...}`

Mapping:
- `iban` → `iban`
- `name` → `name`
- `type`:
  - `Depot` → `depot`
  - other strings (e.g. Giro/Kredit/etc.) → map via lookup to canonical `type`
- `balance` → `balances.booked`
- `available` → `balances.available`
- `value` → `securities.value`
- `profit_loss` → `securities.profitLoss`

### Transactions

ELBA reference schema includes at least:
- `id`
- `buchungstag` (booking date)
- `valuta` (value date)
- `betrag.amount` + `betrag.currencyCode`
- plus lots of additional properties (examples seen in `download_transactions.py`):
  - `transaktionsteilnehmer`
  - `verwendungszweck`
  - `zahlungsreferenz`
  - `kategorieCode`
  - `auftraggeberIban`, `auftraggeberBic`

Mapping:
- `id` → `id`
- `buchungstag` → `bookingDate`
- `valuta` → `valueDate`
- `betrag` → `amount`
- `transaktionsteilnehmer` → `counterparty.name`
- `auftraggeberIban` → `counterparty.iban` (when present)
- `auftraggeberBic` → `counterparty.bic` (when present)
- `verwendungszweck` → `purpose`
- `zahlungsreferenz` → `references.paymentReference`
- `kategorieCode` → `category.code`

ELBA-specific data likely available (worth preserving in `raw`):
- category tags/hashtags
- pending/booked indicators (ELBA request predicate includes `pending:true`)
- internal references: `bestandreferenz`, `ersterfasserreferenz`

---

## Mapping: George (Erste/Sparkasse) → canonical

George supports two modes today:
- **UI scraping** for overview balances + IBAN extraction
- **API calls** by capturing an `Authorization` header during an authenticated browser session

### Accounts / balances

George currently has both:
- `accounts` (list accounts)
- `balances` (list balances)

Target: merge them into a single `accounts` output.

Likely source fields:
- account identifiers: from dashboard URLs: `/{type}/{id}`
- `iban`: extracted via regex from card text or detail page
- `balance`/`available`: parsed from overview card text
- (optional, preferred) fetch via George internal API using captured bearer token for more reliable numbers

Mapping:
- `id` → `id`
- `type` (currentAccount/saving/loan/credit/creditcard) → canonical `type`
- `name` → `name`
- `iban` → `iban`
- parsed overview `balance` → `balances.booked`
- parsed overview `available` → `balances.available`

### Transactions

George downloads transactions as exports (CSV/JSON/OFX/XLSX) and also supports CAMT53 / MT940 exports.

Canonical mapping strategy:
- Prefer a **bank-native JSON export** if available and stable.
- Otherwise parse from CSV/OFX or CAMT53 (XML) into canonical fields.

Typical George export fields (expected across formats):
- booking date / value date
- amount + currency
- counterparty name
- purpose / remittance information
- references (varies by format; CAMT53 has very rich reference info)

---

## Field comparison: identical vs unique

### Largely identical / common

Accounts:
- `name`
- `iban`
- currency (directly or implied)
- booked balance
- available balance (often)

Transactions:
- booking date
- value date
- amount + currency
- counterparty name (sometimes missing or merged into purpose)
- purpose / remittance text

### Likely richer in ELBA (useful fields George may not expose directly)

- stable `kategorieCode` classification (if George doesn’t provide categories)
- explicit `zahlungsreferenz`
- explicit `auftraggeberIban` / `auftraggeberBic`
- internal references like `bestandreferenz`, `ersterfasserreferenz`
- explicit pagination cursors (`idBis`, `neuanlageBis`) and `pending` support

### Likely richer in George (useful fields ELBA may not expose directly)

Depending on export type (especially CAMT53):
- SEPA structured reference blocks (EndToEndId, MandateId, CreditorId) may be present
- statement/document exports with standardized formats (CAMT53, MT940, OFX)

Recommendation: always keep `raw` for both.

---

## Session + token reuse (avoid re-login on immediate follow-up)

Desired behavior: once a login succeeds, a following command should *not* require another pushTAN / phone approval.

### Proposed standard

Each skill keeps a token cache in its state dir:

`<STATE_DIR>/.pw-profile/token.json`

```json
{
  "accessToken": "...",
  "expiresAt": "2026-01-28T12:00:00Z",
  "scopes": ["..."],
  "obtainedAt": "2026-01-28T10:00:00Z",
  "source": "auth_header" | "url_fragment" | "local_storage"
}
```

Rules:
- Never log the token.
- If `expiresAt` is in the future, reuse it.
- If expired/missing, attempt a lightweight session validation in the existing Playwright profile.
- Only if session validation fails: perform interactive login.

Status:
- **ELBA** already has a `TOKEN_CACHE_FILE` (`token.json`) concept.
- **George** currently captures tokens but does not clearly standardize persistence; align it to the same cache format.

---

## Next steps (implementation)

1) Implement canonical models in a small shared Python module (even if kept duplicated per-skill initially).
2) Update **George**:
   - merge `balances` into `accounts`
   - add `--json` output for accounts + transactions using canonical schema
   - persist bearer token in `token.json` for immediate follow-up calls
3) Update **ELBA**:
   - ensure `accounts --json` and `transactions --json` match canonical schema (wrap existing raw output)
   - keep current bank-native output in `raw`
