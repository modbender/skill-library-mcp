# SmartBill API Notes

## Base URL

- `https://ws.smartbill.ro/SBORO/api`

## Authentication

- SmartBill uses HTTP Basic authentication.
- Build header from `username:token` (username is the SmartBill login email).
- CLI expects:
  - `SMARTBILL_USERNAME`
  - `SMARTBILL_TOKEN`

## Rate Limits

- Documented limit: `30` calls / `10` seconds.
- If limit is exceeded repeatedly, SmartBill may block requests for around `10` minutes.
- Relevant response headers:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Endpoints Used by This Skill

- `POST /invoice` - create invoice
- `GET /series?cif=<CIF>&type=<type>` - list document series
- `GET /invoice/pdf?cif=<CIF>&seriesName=<series>&number=<number>` - download invoice PDF

## Payload Shape for `POST /invoice`

```json
{
  "companyVatCode": "RO12345678",
  "client": {
    "name": "SC Company SA",
    "vatCode": "RO12345678",
    "isTaxPayer": true,
    "address": "Str. Iasomiei nr 2",
    "city": "Cluj-Napoca",
    "county": "Cluj-Napoca",
    "country": "Romania",
    "email": "emailclient@domain.ro",
    "saveToDb": false
  },
  "issueDate": "2026-02-21",
  "seriesName": "SMBT",
  "isDraft": false,
  "dueDate": "2026-02-21",
  "deliveryDate": "2026-02-21",
  "products": [
    {
      "name": "Produs 1",
      "code": "codProdus1",
      "isDiscount": false,
      "measuringUnitName": "buc",
      "currency": "RON",
      "quantity": 1,
      "price": 10,
      "isTaxIncluded": true,
      "taxName": "Normala",
      "taxPercentage": 19,
      "saveToDb": false,
      "isService": false
    }
  ]
}
```

### Key Field Notes

| Field | Notes |
|-------|-------|
| `companyVatCode` | **Required.** Your company CIF/VAT code. |
| `client.name` | **Required.** Client company name. |
| `client.saveToDb` | Set `false` to avoid saving client to SmartBill contacts. |
| `seriesName` | Invoice series configured in SmartBill (e.g. `SMBT`). |
| `isDraft` | `false` = final invoice; `true` = draft (safe for testing). |
| `issueDate` | Format: `YYYY-MM-DD`. Defaults to current date if omitted. |
| `dueDate` | Format: `YYYY-MM-DD`. |
| `deliveryDate` | Format: `YYYY-MM-DD`. |
| `products[].code` | Product code. Required if account uses product codes. |
| `products[].isTaxIncluded` | `true` = price is gross (VAT included); `false` = net price. |
| `products[].taxName` | VAT rate name as configured in SmartBill (e.g. `Normala`). |
| `products[].taxPercentage` | VAT percentage (e.g. `19`). |
| `products[].saveToDb` | Set `false` to avoid saving product to catalog. |

## Response Format

**Success (200):**
```json
{
  "errorText": "",
  "message": "Factura a fost emisa.",
  "number": "1234",
  "series": "SMBT",
  "url": ""
}
```

**Error (4xx):**
```json
{
  "errorText": "Descriere eroare"
}
```

## Operational Rules

- Set `client.saveToDb: false` and `products[].saveToDb: false` to avoid side effects.
- Persist the returned `series` and `number` from the SmartBill response for PDF retrieval.
- Log request intent and final SmartBill response for auditability.
- Respect rate limits: max 30 calls per 10 seconds.
