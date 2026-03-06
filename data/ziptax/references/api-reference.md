# ZipTax API Reference

## Base URL
`https://api.zip-tax.com`

## Authentication
All requests require an API key via **one** of:
- Header: `X-API-KEY: <your-key>`
- Query param: `?key=<your-key>`

Get a free key at https://platform.zip.tax (DEVELOP > API Keys). Free tier: 100 calls/month.

## Endpoints

### Tax Rate Lookup

**`GET /request/{version}`** where version is `v10`–`v60`.

Use **v60** (latest) unless a specific version is needed. Returns jurisdiction-level breakdowns, service/freight taxability, origin/destination rules, and address normalization.

#### Lookup by Address (recommended — door-level accuracy)
```
GET /request/v60?address=200+Spectrum+Center+Drive+Irvine+CA+92618
```
Returns a single result with exact rates for that location.

#### Lookup by Lat/Lng
```
GET /request/v60?lat=33.6525&lng=-117.7479
```
Returns a single door-level result.

#### Lookup by Postal Code
```
GET /request/v60?postalcode=92618
```
Returns **all** applicable rates for the ZIP code (may be multiple). Not adjusted for unincorporated areas — use address or lat/lng for precision.

#### Optional Parameters
| Param | Description |
|-------|-------------|
| `address` | Full street address |
| `postalcode` | 5-digit ZIP code |
| `lat` / `lng` | Geographic coordinates |
| `state` | 2-letter state code (e.g., CA) |
| `city` | City name |
| `format` | `json` (default) or `xml` |
| `taxabilityCode` | TIC code for product-specific rates |

### v60 Response Structure
```json
{
  "metadata": { "version": "v60", "response": { "code": 100, "name": "RESPONSE_CODE_SUCCESS" } },
  "baseRates": [
    { "rate": 0.0725, "jurType": "US_STATE_SALES_TAX", "jurName": "CA", "jurDescription": "...", "jurTaxCode": "06" },
    { "rate": 0.005, "jurType": "US_COUNTY_SALES_TAX", "jurName": "ORANGE", ... },
    { "rate": 0, "jurType": "US_CITY_SALES_TAX", "jurName": "IRVINE", ... }
  ],
  "service": { "adjustmentType": "SERVICE_TAXABLE", "taxable": "N", "description": "Services non-taxable" },
  "shipping": { "adjustmentType": "FREIGHT_TAXABLE", "taxable": "N", "description": "Freight non-taxable" },
  "sourcingRules": { "adjustmentType": "ORIGIN_DESTINATION", "value": "D", "description": "Destination Based" },
  "taxSummaries": [
    { "rate": 0.0775, "taxType": "SALES_TAX", "summaryName": "Total Base Sales Tax" },
    { "rate": 0.0775, "taxType": "USE_TAX", "summaryName": "Total Base Use Tax" }
  ],
  "addressDetail": { "normalizedAddress": "...", "incorporated": "true", "geoLat": 33.65253, "geoLng": -117.74794 }
}
```

### Older Versions (v10–v50)
- **v10**: 8 fields — combined rates only (taxSales, taxUse, geo fields, freight/service flags)
- **v20**: 16 fields — adds state/city/county breakdowns + tax codes
- **v30**: Same as v20 (compatibility)
- **v40**: 21 fields — adds district-level taxes (district1)
- **v50**: 33+ fields — adds districts 2-5, addressDetail, Tennessee SAT support

### Account Metrics
```
GET /account/metrics
```
Returns: `core_request_count`, `core_request_limit`, `core_usage_percent`, `geo_enabled`, `is_active`. Does NOT count against usage.

### TIC Codes (Product Taxability)
```
GET /data/tic
```
Returns all Taxability Information Codes. Use a TIC code in the `taxabilityCode` parameter for product-specific rate adjustments.

### System Health
```
GET /system/health
GET /system/metadata
```

## Response Codes
| Code | Name | Meaning |
|------|------|---------|
| 100 | SUCCESS | OK |
| 101 | INVALID_KEY | Bad or missing key |
| 104 | INVALID_POSTAL_CODE | Bad ZIP format |
| 108 | REQUEST_LIMIT_MET | Quota exceeded |
| 109 | ADDRESS_INCOMPLETE | Bad/missing address |
| 110 | NO_RESULT | Valid params, no data |

## Code Samples

### cURL
```bash
curl -X GET "https://api.zip-tax.com/request/v60?address=200+Spectrum+Center+Drive+Irvine+CA+92618" \
  -H "X-API-KEY: YOUR_API_KEY"
```

### Python
```python
import requests
resp = requests.get(
    "https://api.zip-tax.com/request/v60",
    params={"address": "200 Spectrum Center Drive Irvine CA 92618"},
    headers={"X-API-KEY": "YOUR_API_KEY"}
)
data = resp.json()
total_rate = data["taxSummaries"][0]["rate"]
```

### JavaScript
```javascript
const resp = await fetch(
  "https://api.zip-tax.com/request/v60?address=200+Spectrum+Center+Drive+Irvine+CA+92618",
  { headers: { "X-API-KEY": "YOUR_API_KEY" } }
);
const data = await resp.json();
```

## OpenAPI Spec
Full machine-readable spec: https://raw.githubusercontent.com/ZipTax/ziptax-reference/main/openapi/openapi.json

## SDKs
- Python: https://github.com/ZipTax/ziptax-python
- Go: https://github.com/ZipTax/ziptax-go
- Node.js: https://github.com/ZipTax/ziptax-node

## Key Facts
- 12,000+ US tax jurisdictions, 80,000+ geographic boundaries
- Rates auto-update monthly (1st of month)
- <200ms typical latency
- Door-level accuracy via address/lat-lng geocoding
- Canadian GST/HST/PST rates available
- EU VAT in development
- Free tier: 100 calls/month
- Sign up: https://platform.zip.tax
