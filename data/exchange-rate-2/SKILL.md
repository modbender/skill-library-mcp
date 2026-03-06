---
name: exchange-rate
description: Use when users need to query daily currency exchange rates between two currencies.
---

# Exchange Rate Skill

This skill helps AI agents fetch daily currency exchange rates from the 60s API.

## When to Use This Skill

Use this skill when users:
- Ask for current exchange rates between two currencies.
- Want to know the value of one currency in another.
- Need the latest currency conversion rate.

## How to Use

Execute the associated `scripts/exchange_rate.sh` script to fetch the exchange rate.

```bash
./scripts/exchange_rate.sh [options]
```

### Options

- `--currency, -c <currency>`: Optional. The base currency ISO 4217 code. Defaults to `CNY`.
- `--target, -t <target>`: Optional. The target currency ISO 4217 code. Defaults to `USD`. If set to `AAA`, it returns all available exchange rates for the base currency.

### Return Values

The script outputs the exchange rate value of the `target` currency relative to 1 unit of the `base` currency.
If the `target` is `AAA`, it outputs the full JSON response containing all rates.
If the `target` currency is not found, an error message is returned.

### Usage Examples

```bash
# Get the exchange rate from CNY to USD (default)
./scripts/exchange_rate.sh

# Get the exchange rate from EUR to JPY
./scripts/exchange_rate.sh --currency EUR --target JPY

# Get all exchange rates for GBP
./scripts/exchange_rate.sh -c GBP -t AAA
```
