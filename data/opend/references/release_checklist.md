# Release Checklist

Use this checklist before publishing to ClawHub or another hosted registry.

## Package truthfulness

- The published bundle includes `openclaw`, `opend_cli.py`, `credentials.py`, and `SKILL.md`.
- The registry metadata declares these secret inputs:
  - `OPEND_PASSWORD_SECRET_REF`
  - `MOOMOO_PASSWORD`
  - `MOOMOO_CONFIG_KEY`
- The registry metadata declares these non-secret runtime overrides:
  - `OPEND_HOST`
  - `OPEND_PORT`
  - `OPEND_MARKET`
  - `OPEND_SECURITY_FIRM`
  - `OPEND_TRD_ENV`
  - `OPEND_CREDENTIAL_METHOD`
  - `OPEND_OUTPUT`
  - `OPEND_SDK_PATH`

## Secret handling

- Hosted docs show `OPEND_PASSWORD_SECRET_REF` as the default credential path.
- Legacy `env`, `config`, and `keyring` modes are marked as local compatibility paths.
- No script prints a reusable secret or encryption key to stdout.
- `config.enc` and `config.key` are excluded from version control.

## Runtime safety

- `SIMULATE` remains the default trading environment.
- Live trading examples require explicit user intent.
- `OPEND_SDK_PATH` is documented as trusted-code-only.
- The fallback Python CLI is documented in case the shell wrapper is omitted from a bundle.

## Validation

- Run `python3 scripts/release_smoke_test.py`.
- Run `./openclaw --help`.
- If publishing through a packaging tool, inspect the produced file list and confirm `openclaw` is present.
