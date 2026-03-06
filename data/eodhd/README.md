# eodhd-skill

Open source OpenClaw skill and Bash CLI wrapper for the public EODHD API.

## Status

The repository now includes:

- a Codex/OpenClaw skill definition in [SKILL.md](./SKILL.md)
- an MVP Bash CLI at [scripts/eodhd](./scripts/eodhd)
- smoke tests at [scripts/test-smoke.sh](./scripts/test-smoke.sh)
- implementation and security references in [references/](./references/)

## Current command coverage

The CLI currently exposes discovery plus documented REST families for:

- `services`, `docs`, `raw`
- `eod`, `real-time`, `live`, `live-v2`, `intraday`, `ticks`
- `dividends`, `splits`, `technical`, `fundamentals`, `bulk-last-day`
- `search`, `exchanges`, `exchange-symbols`
- `news`, `calendar`, `economic-events`, `macro-indicator`
- `screener`, `delisted`, `insider-transactions`

Use `./scripts/eodhd services` to inspect the current registry and doc links.

## Security stance

- Prefer `EODHD_API_KEY` injected by OpenClaw secrets management.
- Treat `EODHD_API_KEY` as the primary required credential in publish metadata and runtime checks.
- Do not store API keys in repo files or local artifacts.
- Mask `api_token` values in dry-run and verbose output.
- Keep the CLI stateless: no cache, no profile, no token store.

## Distribution contract

- Publish metadata lives in [agents/openai.yaml](./agents/openai.yaml).
- The packaged CLI entrypoint is [scripts/eodhd](./scripts/eodhd).
- The required runtime credential is `EODHD_API_KEY`.
- The only supported explicit override is `--api-key` for a single invocation.

## Release validation

Run the package contract check before publishing to Clawhub.ai:

```bash
./scripts/check-package.sh
```

## Quick start

```bash
./scripts/check-package.sh
EODHD_API_KEY=***REDACTED*** ./scripts/eodhd --dry-run eod AAPL.US
EODHD_API_KEY=***REDACTED*** ./scripts/eodhd services
EODHD_API_KEY=***REDACTED*** ./scripts/eodhd --dry-run macro-indicator USA --query indicator=gdp_current_usd
./scripts/test-smoke.sh
```
