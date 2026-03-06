---
name: exchange-rate
description: "Currency exchange rate conversion using exchangerate-api.com. Use when: (1) converting between currencies, (2) checking current exchange rates, (3) viewing currency conversion tables, or (4) any forex/currency related queries. Supports 150+ currencies with real-time rates."
---

# Exchange Rate Tool

Convert currencies and view exchange rates using free API from exchangerate-api.com. No API key required.

## When to Use

- Convert between any currencies
- Check current exchange rates
- View rate tables for multiple currencies
- Calculate cross-currency conversions

## Quick Start

### Convert Currency
```bash
python3 scripts/exchange-rate.py convert 100 USD CNY
# Output: $100.0000 = ¥692.0000
```

### View Exchange Rates
```bash
python3 scripts/exchange-rate.py rate USD
# Shows rates for major currencies against USD
```

### List Supported Currencies
```bash
python3 scripts/exchange-rate.py list
```

## Commands

### `convert <amount> <from> <to>`
Convert an amount from one currency to another.

**Examples:**
```bash
# USD to CNY
python3 scripts/exchange-rate.py convert 100 USD CNY

# EUR to USD
python3 scripts/exchange-rate.py convert 50 EUR USD

# JPY to CNY
python3 scripts/exchange-rate.py convert 10000 JPY CNY
```

### `rate <base_currency>`
View exchange rates for major currencies against a base currency.

**Examples:**
```bash
# Rates against USD (default)
python3 scripts/exchange-rate.py rate USD

# Rates against CNY
python3 scripts/exchange-rate.py rate CNY

# Rates against EUR
python3 scripts/exchange-rate.py rate EUR
```

### `list`
List all supported currency codes (150+ currencies).

```bash
python3 scripts/exchange-rate.py list
```

## Common Currency Codes

| Code | Currency | Code | Currency |
|------|----------|------|----------|
| USD | US Dollar | CNY | Chinese Yuan |
| EUR | Euro | JPY | Japanese Yen |
| GBP | British Pound | KRW | South Korean Won |
| AUD | Australian Dollar | HKD | Hong Kong Dollar |
| CAD | Canadian Dollar | TWD | New Taiwan Dollar |
| CHF | Swiss Franc | SGD | Singapore Dollar |
| INR | Indian Rupee | RUB | Russian Ruble |
| BRL | Brazilian Real | MXN | Mexican Peso |

## Notes

- Rates are updated daily (typically around 00:00 UTC)
- API is free and requires no authentication
- Results include the date of the rate data
- Supports 150+ world currencies

## Data Source

This skill uses the free tier of exchangerate-api.com, which provides:
- Daily updated rates
- 150+ supported currencies
- No API key required
- Rate limits apply (be reasonable with usage)

## Example Output

```
💱 汇率转换
$100.0000 = ¥692.0000
汇率: 1 USD = 6.920000 CNY
日期: 2026-02-24
```
