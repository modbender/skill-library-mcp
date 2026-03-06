# opend-skill

OpenClaw skill for local OpenD market-data and trading workflows against the MooMoo/Futu OpenAPI.

## Security posture

The preferred hosted deployment path is OpenClaw secret management. This repo supports `OPEND_PASSWORD_SECRET_REF` as the default credential method and keeps `MOOMOO_PASSWORD`, `MOOMOO_CONFIG_KEY` plus `config.enc`, and OS keyring storage only for local compatibility workflows.

This project is an open-source wrapper around a commercial API provider. Review the code before using real credentials or live accounts, and keep `SIMULATE` as the default unless you have intentionally validated the live trading path.

## Entrypoints

- Primary wrapper: `./openclaw`
- Fallback Python CLI: `python3 opend_cli.py`

## Release validation

Run `python3 scripts/release_smoke_test.py` and follow `references/release_checklist.md` before publishing to ClawHub.
