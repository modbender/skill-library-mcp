# alpaca-markets-skill

OpenClaw skill for using the Alpaca Markets API.

## Provenance

- Distribution page: https://clawhub.ai/oscraters/alpaca-markets
- Source repository: https://github.com/oscraters/alpaca-markets-skill.git

The registry-facing metadata for this skill lives in `registry-metadata.json`.
The Clawhub-documented metadata source of truth lives in the `SKILL.md` frontmatter.
The Clawhub/OpenClaw interface manifest lives in `agents/openai.yaml`.

## Required Credentials

This skill requires the following environment variables:

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`

Optional:

- `ALPACA_BASE_URL`

Default base URL:

- `https://paper-api.alpaca.markets`

Live trading URL:

- `https://api.alpaca.markets`

## Security / Credential Use

- Use paper trading credentials first. Do not start with live funds.
- Only set `ALPACA_BASE_URL=https://api.alpaca.markets` after you have audited the code and intend to trade live.
- Prefer running this skill in an isolated environment if you are evaluating an unreviewed install.
- Never hardcode Alpaca credentials in source files, prompts, or logs.

## Validation

Run the metadata consistency check locally with:

```bash
python3 scripts/validate_registry_metadata.py
```

This check fails if `SKILL.md` frontmatter, `registry-metadata.json`, and the runtime-required environment variables drift apart, if provenance fields are missing, or if the optional Clawhub/OpenClaw interface manifest drifts from the expected format.
