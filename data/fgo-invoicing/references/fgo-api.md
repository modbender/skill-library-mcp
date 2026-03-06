# FGO API Notes (v7.1)

## Base URLs

| Environment | URL |
|---|---|
| Production | `https://api.fgo.ro/v1` |
| Test / UAT | `https://api-testuat.fgo.ro/v1` |

Testing UI: `https://api.fgo.ro/v1/testing.html`

## Authentication

FGO does **not** use HTTP headers for auth. Every POST request includes a `Hash` field in the request body computed as a **SHA-1 hash (uppercase hex)** of specific fields concatenated together.

### Hash Formulas

| Scenario | Formula |
|---|---|
| Invoice issuance (`/factura/emitere`) | `SHA1(CodUnic + CheiePrivata + Client[Denumire]).toUpperCase()` |
| All other invoice operations | `SHA1(CodUnic + CheiePrivata + NumarFactura).toUpperCase()` |
| Article operations | `SHA1(CodUnic + CheiePrivata).toUpperCase()` |

**Example** (issuance):
- CodUnic: `2864518`
- CheiePrivata: `1234567890`
- DenumireClient: `Ionescu Popescu`
- Input string: `28645181234567890Ionescu Popescu`
- Result: `8C3A7726804C121C6933F7D68494B439463996E2`

### Obtaining Credentials

1. Go to FGO platform → Setari → Utilizatori → Generate API user
2. Copy the **Cheie Privata** (Private Key) shown in the popup
3. `CodUnic` = your company's CUI (Romanian tax ID)

CLI environment variables:
- `FGO_COD_UNIC` — company CUI
- `FGO_CHEIE_PRIVATA` — private API key

## Request Format

All POST endpoints use `application/x-www-form-urlencoded` (form-encoded) bodies, not JSON. Nested fields use bracket notation:

- Object: `Client[Denumire]=Acme SRL`
- Array item: `Continut[0][CodArticol]=PROD001`

## Rate Limits

| Method Group | Limit |
|---|---|
| `/factura/*` operations | 1 request / 1 second |
| `/articol/list` | 1 request / 30 seconds (changed 01.07.2023) |
| `/articol/get`, `/articol/getlist`, `/articol/gestiune` | 1 request / 5 seconds |
| `/articol/articolemodificate` | 1 request / 30 minutes |

**Invoice issuance timeout**: max 15 seconds from receipt to response.
**Requests must be sequential** — do not parallelize FGO API calls.

## Endpoints

### POST `/factura/emitere` — Issue Invoice

Rate limit: 1 req/sec. Timeout: 15 seconds.

#### Request Fields

| Parameter | Type | Required | Description |
|---|---|---|---|
| `CodUnic` | string | YES | CUI of the issuing company |
| `Hash` | string | YES | SHA-1 hash: `SHA1(CodUnic + CheiePrivata + Client[Denumire])` |
| `Valuta` | string(3) | YES | Currency — see `/nomenclator/valuta` (e.g. `RON`, `EUR`) |
| `TipFactura` | string(50) | YES | Invoice type — see `/nomenclator/tipfactura` (e.g. `Factura`) |
| `Serie` | string(50) | YES | Invoice series as defined in FGO → Setari → Serii documente |
| `Client[Tip]` | string(2) | YES | `PF` (individual) or `PJ` (legal entity) |
| `Client[Tara]` | string(128) | YES | Country — see `/nomenclator/tara`. If Romania, `Client[Judet]` is mandatory |
| `Continut[i][CodArticol]` | string(128) | YES | Article/product code (zero-indexed) |
| `Continut[i][UM]` | string(5) | YES | Unit of measure (e.g. `buc`, `ore`) |
| `Continut[i][NrProduse]` | decimal | YES | Quantity. Must not be 0. Use negative for storno/reversal items |
| `Continut[i][CotaTVA]` | decimal | YES | VAT rate as number: `19` for 19%, `9` for 9%, `0` for 0% |
| `Numar` | string(50) | NO | Invoice number. If omitted, auto-generated from series register |
| `DataEmitere` | string | NO | Issue date. Format: `yyyy-mm-dd`. Default: current date |
| `DataScadenta` | string | NO | Due date. Format: `yyyy-mm-dd`. Default: from FGO account settings |
| `TvaLaIncasare` | bool | NO | VAT upon collection (`true`/`false`) |
| `VerificareDuplicat` | bool | NO | Enable duplicate check (requires `IdExtern` or `Serie+Numar`) |
| `ValideazaCodUnicRo` | bool | NO | Validate Romanian CUI/CNP. Default `true` from 01.07.2024 for PJ+Romania |
| `IdExtern` | string(36) | NO | External order ID for duplicate detection |
| `Text` | string(2000) | NO | Additional info shown on invoice (e.g. delegate name) |
| `Explicatii` | string(2000) | NO | Additional explanations on invoice |
| `PlatformaUrl` | string | NO | Caller platform root URL (recommended) |
| `Client[Denumire]` | string(255) | NO | Client name |
| `Client[CodUnic]` | string(128) | NO | Client CUI (company) or CNP (individual) |
| `Client[NrRegCom]` | string(128) | NO | Trade register number |
| `Client[Email]` | string(100) | NO | Client email |
| `Client[Telefon]` | string(100) | NO | Client phone |
| `Client[Judet]` | string(100) | NO | County. **Mandatory** if `Client[Tara]` = Romania |
| `Client[Localitate]` | string(100) | NO | Locality. Must match nomenclator if Romania; free text if foreign |
| `Client[Adresa]` | string(500) | NO | Street address |
| `Client[IdExtern]` | int | NO | External client ID (must be > 0). Enable in FGO → Setari → eCommerce |
| `Client[ContBancar]` | string(100) | NO | Client bank account (IBAN) |
| `Client[PlatitorTVA]` | bool | NO | VAT payer status. If omitted for PJ, FGO looks up Romanian tax DB |
| `Continut[i][Denumire]` | string(1000) | NO | Product/service name |
| `Continut[i][Descriere]` | string(4000) | NO | Description on invoice. Special: `[[descriere]]` inserts FGO article description |
| `Continut[i][PretUnitar]` | decimal | NO | Unit price (classic calc — do NOT combine with `PretTotal`) |
| `Continut[i][PretTotal]` | decimal | NO | Total price incl. VAT × qty (reverse calc — do NOT combine with `PretUnitar`) |
| `Continut[i][CodGestiune]` | string(128) | NO | Warehouse code for accounting discharge |
| `Continut[i][CodCentruCost]` | string | NO | Cost center code |

**Price calculation modes:**
- Classic: provide `PretUnitar`, system calculates `PretTotal`
- Reverse: provide `PretTotal` (total incl. VAT × quantity), system calculates `PretUnitar`
- Never provide both.

#### Success Response
```json
{
  "Success": true,
  "Message": "",
  "Factura": {
    "Numar": "001",
    "Serie": "BV",
    "Link": "",
    "LinkPlata": ""
  },
  "InfoStoc": [
    { "CodConta": "A1", "Nume": "Produs 1", "Stoc": 10.0 }
  ]
}
```

#### Error Response
```json
{ "Success": false, "Message": "Mesaj eroare" }
```

---

### POST `/factura/print` — Get Invoice Print Link

Hash: `SHA1(CodUnic + CheiePrivata + Numar)`.

| Parameter | Required |
|---|---|
| `CodUnic` | YES |
| `Hash` | YES |
| `Numar` | YES |
| `Serie` | YES |
| `PlatformaUrl` | YES |

**Response:**
```json
{
  "Success": true,
  "Factura": { "Numar": "001", "Serie": "BV", "Link": "https://..." }
}
```

---

### POST `/factura/stergere` — Delete Invoice

Hash: `SHA1(CodUnic + CheiePrivata + Numar)`.

| Parameter | Required |
|---|---|
| `CodUnic` | YES |
| `Hash` | YES |
| `Numar` | YES |
| `Serie` | YES |
| `PlatformaUrl` | YES |

**Response:** `{ "Success": true, "Message": "Factura a fost stearsa" }`

---

### POST `/factura/anulare` — Cancel Invoice

Hash: `SHA1(CodUnic + CheiePrivata + Numar)`.

| Parameter | Required |
|---|---|
| `CodUnic` | YES |
| `Hash` | YES |
| `Numar` | YES |
| `Serie` | YES |
| `PlatformaUrl` | YES |

**Response:** `{ "Success": true, "Message": "Factura a fost anulata." }`

---

### POST `/factura/getstatus` — Get Invoice Status

Hash: `SHA1(CodUnic + CheiePrivata + Numar)`.

**Response:**
```json
{
  "Success": true,
  "Factura": {
    "Numar": "1",
    "Serie": "X",
    "Valoare": "167.69",
    "ValoareAchitata": "167.69",
    "Incasari": [
      { "SumaIncasata": 150.00, "DataIncasare": "2025-02-02", "Valuta": "RON" }
    ]
  }
}
```

---

### POST `/factura/incasare` — Add Payment

**Availability:** Premium & Enterprise only.

Hash: `SHA1(CodUnic + CheiePrivata + NumarFactura)`.

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `CodUnic` | string | YES | |
| `Hash` | string | YES | |
| `NumarFactura` | string(50) | YES | Invoice number |
| `SerieFactura` | string(50) | YES | Invoice series |
| `TipIncasare` | string(50) | YES | See `/nomenclator/tipincasare` |
| `SumaIncasata` | decimal | YES | Format: `XXXX.XX` |
| `DataIncasare` | datetime | YES | Format: `yyyy-mm-dd hh:mm:ss` |
| `PlatformaUrl` | string | YES | |
| `SerieChitanta` | string(50) | NO | Receipt series |
| `ContIncasare` | string(50) | NO | Accounting collection account |
| `TipFactura` | string | NO | Document type (if series is shared) |

---

### POST `/factura/stornare` — Reverse Invoice (Storno)

Hash: `SHA1(CodUnic + CheiePrivata + Numar)`.

| Parameter | Required | Notes |
|---|---|---|
| `CodUnic` | YES | |
| `Hash` | YES | |
| `Numar` | YES | Number of the original invoice to reverse |
| `Serie` | YES | Series of the original invoice |
| `SerieStorno` | NO | Series of the storno invoice |
| `NumarStorno` | NO | Number of the storno invoice |
| `DataEmitere` | NO | Issue date (yyyy-mm-dd). Default: current date |
| `PlatformaUrl` | YES | |

---

### GET `/nomenclator/<resource>` — Nomenclature Lists

No authentication required. Returns lookup lists for invoice fields.

| Resource | Description |
|---|---|
| `tara` | Countries |
| `judet` | Counties/Districts |
| `tva` | VAT rates |
| `banca` | Banks |
| `tipincasare` | Payment types |
| `tipfactura` | Invoice types |
| `tipclient` | Client types (PF/PJ) |
| `valuta` | Currencies |

**Response:**
```json
{ "Success": true, "List": [{ "Nume": "Valoare" }] }
```

---

## Invoice Types (TipFactura)

| Value | Description |
|---|---|
| `Factura` | Standard tax invoice |
| `Proforma` | Proforma invoice |
| `Comanda` | Order |
| `Deviz` | Estimate/Quote |
| `Aviz` | Delivery note |
| `S` | Exempt with deduction (Scutit cu deducere) |
| `U` | Services per art. 311 |
| `H` | Sales per art. 312 |
| `N` | Non-taxable operations |
| `X` | Special regime art. 314-315 (auto-set for OSS foreign clients) |

## Key Field Summary

| Concept | Exact Field Name |
|---|---|
| Invoice number | `Numar` |
| Invoice series | `Serie` |
| Client name | `Client[Denumire]` |
| Client VAT code / CUI | `Client[CodUnic]` |
| Line items array | `Continut[i][...]` |
| Quantity | `Continut[i][NrProduse]` |
| Unit price | `Continut[i][PretUnitar]` |
| Total price (reverse) | `Continut[i][PretTotal]` |
| VAT rate per line | `Continut[i][CotaTVA]` |
| Issue date | `DataEmitere` |
| Due date | `DataScadenta` |
| Currency | `Valuta` |
| Product name | `Continut[i][Denumire]` |
| Unit of measure | `Continut[i][UM]` |
| Product code | `Continut[i][CodArticol]` |

## Error Response Format

All endpoints return errors as:
```json
{ "Success": false, "Message": "Human-readable Romanian error message" }
```

HTTP 200 is returned even for business-logic errors — always check the `Success` field.

## Operational Rules

- **Never parallelize** FGO API calls — make requests sequentially.
- Invoice issuance has a **15-second timeout**. If exceeded, the invoice was NOT issued; retry.
- Check the `Success` field in every response before treating it as a success.
- Store the returned `Numar` verbatim — FGO may return zero-padded strings (e.g. `"001"`). Never cast to integer.
- Use the UAT environment (`https://api-testuat.fgo.ro/v1`) for testing.
- Production requires a paid FGO subscription (PRO or PREMIUM).
