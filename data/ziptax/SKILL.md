---
name: ziptax-sales-tax
description: >
  Look up U.S. sales tax rates using the ZipTax API. Use when the user asks about sales tax rates,
  tax calculations for a U.S. address/ZIP code/coordinates, freight or service taxability,
  jurisdiction-level tax breakdowns, use tax vs sales tax, or needs to integrate sales tax
  data into an application. Also handles account usage metrics and product taxability codes (TIC).
  Supports address-level (door-level), lat/lng, and postal code lookups across 12,000+ jurisdictions.
---

# ZipTax Sales Tax Lookup

## Setup

Set `ZIPTAX_API_KEY` env variable with your API key from https://platform.zip.tax (DEVELOP > API Keys).
Free tier gives 100 calls/month. **Never share your API key publicly.**

## Quick Start

### Address Lookup (most accurate)
```bash
curl -s "https://api.zip-tax.com/request/v60?address=200+Spectrum+Center+Drive+Irvine+CA+92618" \
  -H "X-API-KEY: $ZIPTAX_API_KEY"
```

### Postal Code Lookup
```bash
curl -s "https://api.zip-tax.com/request/v60?postalcode=92618" \
  -H "X-API-KEY: $ZIPTAX_API_KEY"
```

### Lat/Lng Lookup
```bash
curl -s "https://api.zip-tax.com/request/v60?lat=33.6525&lng=-117.7479" \
  -H "X-API-KEY: $ZIPTAX_API_KEY"
```

## Workflow

1. Determine lookup type: address (best), lat/lng, or postal code
2. Use **v60** (latest) for full jurisdiction breakdowns; use v10 for simple combined rate
3. Make GET request to `https://api.zip-tax.com/request/v60` with auth header
4. Check `metadata.response.code` — 100 means success
5. Read `taxSummaries[0].rate` for total sales tax rate
6. Read `baseRates` array for state/county/city/district breakdown
7. Check `service.taxable` and `shipping.taxable` for service/freight taxability

## Key Points

- **Address > Postal code**: Address gives one exact result; postal code returns all rates in that ZIP
- **Auth**: Header `X-API-KEY` or query param `key`
- **Rate format**: Decimal (0.0775 = 7.75%)
- **Response code 100** = success; check `metadata.response.code`
- **Metrics endpoint** (`/account/metrics`) does not count against quota

## Bundled Resources

- **`scripts/lookup.sh`** — CLI wrapper for quick lookups. Run with `--address`, `--lat`/`--lng`, `--postalcode`, or `--metrics`
- **`references/api-reference.md`** — Full API reference with all endpoints, response schemas, code samples, response codes, and SDK links. Read when you need endpoint details or response field definitions.
