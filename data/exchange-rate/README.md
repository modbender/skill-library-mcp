# Exchange Rate

Real-time currency exchange rate and conversion skill for OpenClaw/ClawHub agents, powered by QVeris.

## Highlights

- **Rate lookup**: Current exchange rate for any supported currency pair (e.g. USD/EUR, CNY/JPY).
- **Amount conversion**: Convert an amount from one currency to another at current rates.
- **QVeris-only**: Discovers and calls tools via QVeris search + execute (Alpha Vantage, Twelve Data, etc.) with fallback.
- **Optional historical**: Use `--date YYYY-MM-DD` when the underlying tool supports it.
- **Output**: Human-readable markdown or JSON.

## Requirements

- Node.js 18+
- `QVERIS_API_KEY`

```bash
export QVERIS_API_KEY="your-api-key"
```

## Install as an Independent Skill

```bash
npx skills add <repo-url> --skill exchange-rate
```

Or copy the `exchange-rate` folder into your agent skill directory.

## Usage

### Get exchange rate (no amount)

```bash
node scripts/exchange_rate.mjs rate --from USD --to EUR
node scripts/exchange_rate.mjs rate --from CNY --to USD
```

### Convert amount

```bash
node scripts/exchange_rate.mjs convert --from USD --to JPY --amount 1000
node scripts/exchange_rate.mjs convert --from EUR --to GBP --amount 500
```

### Optional options

- `--date YYYY-MM-DD` – Use rate from this date (if tool supports it).
- `--format json` – Output machine-readable JSON.
- `--timeout N` – Request timeout in seconds (default 5).

## Prompt Examples

- "What is the USD to EUR exchange rate?"
- "Convert 1000 USD to JPY"
- "CNY to USD rate"
- "100 EUR to GBP"

## Notes

- Currency codes are normalized to uppercase (USD, EUR, CNY, GBP, JPY, etc.).
- If one provider fails, the script tries the next candidate from the search results.
- Data is for reference only; not financial or contractual advice.

## Security

- Uses only `QVERIS_API_KEY`; never hardcode in committed files.
- All requests go to `qveris.ai` over HTTPS; no extra packages or arbitrary commands.
