---
name: opend
description: Agentic trading and market-data workflows for Futu OpenD (MooMoo/Futu OpenAPI), including OpenClaw-compatible secret-ref credential loading, account discovery, position queries, and simulated or live order placement. Use when tasks require calling local OpenD through Python/Bash automation with structured JSON output and explicit trading-safety guardrails.
---

# OpenD Skill

Use this skill to execute local OpenD operations through a single CLI surface.

## Quick Start

- Ensure OpenD is running on `127.0.0.1:11111`, or override with `OPEND_HOST` and `OPEND_PORT`.
- Install one provider SDK: `moomoo` or `futu`.
- Prefer OpenClaw-managed secret refs for hosted use:
  - `export OPEND_PASSWORD_SECRET_REF='{"source":"env","id":"MOOMOO_PASSWORD"}'`
  - Provide the actual `MOOMOO_PASSWORD` through OpenClaw gateway secret injection, not plain shell export.
- Optional local-only helpers: `pip install keyring cryptography`.

## Primary Interface

Use Bash CLI `./openclaw` for routine operations. If the wrapper is unavailable in a published bundle, use `python3 opend_cli.py` directly and treat that as a packaging bug.

Examples:
- Snapshot:
  - `./openclaw snapshot --codes HK.00700,US.AAPL`
- Accounts:
  - `./openclaw accounts`
- Positions:
  - `./openclaw --trd-env SIMULATE positions`
- Place simulated order:
  - `./openclaw --market HK --trd-env SIMULATE place-order --code HK.00700 --price 100 --qty 100 --side BUY`
- Cancel order:
  - `./openclaw --market HK --trd-env SIMULATE cancel-order --order-id <ORDER_ID>`

## Credential Methods

- Default: `openclaw`
  - Reads `OPEND_PASSWORD_SECRET_REF` first.
  - Current local resolver accepts OpenClaw-style env refs only: `{"source":"env","id":"ENV_VAR_NAME"}`.
  - `file` and `exec` refs must be resolved by the OpenClaw gateway before launching this skill.
- Legacy compatibility:
  - `env`: reads `MOOMOO_PASSWORD`
  - `config`: reads `MOOMOO_CONFIG_KEY` and decrypts `config.enc`
  - `keyring`: prompts once and stores password in the OS keyring
- Deliberate warning:
  - `env`, `config`, and `keyring` bypass the preferred OpenClaw secret-ref audit path. Use them only for local development or controlled offline workflows.

## Agentic Defaults

- Prefer `--output json` so downstream steps can parse results.
- Prefer `SIMULATE` unless the user explicitly requests live trading.
- Query `accounts` first for unknown environments, then pass explicit `--acc-id`.
- For live trading, unlock is required. Simulated accounts skip unlock automatically.

## Safety and Secret Handling

- This repository is an open-source wrapper around a commercial trading API provider. Users are expected to inspect and modify it as needed.
- Hosted or shared deployments should use OpenClaw secret management, not raw shell environment variables.
- `setup_config.py` and `config.enc` are legacy compatibility helpers. They no longer print reusable keys to stdout, but they still create local secret material and should be treated as sensitive.
- `keyring` stores credentials in the OS keychain. Confirm that storage model is acceptable before using it.
- `OPEND_SDK_PATH` changes where Python imports `moomoo` or `futu` from. Only point it at trusted code.

## Environment and Runtime Inputs

Secrets:
- `OPEND_PASSWORD_SECRET_REF`
- `MOOMOO_PASSWORD`
- `MOOMOO_CONFIG_KEY`

Non-secret overrides:
- `OPEND_HOST`
- `OPEND_PORT`
- `OPEND_MARKET`
- `OPEND_SECURITY_FIRM`
- `OPEND_TRD_ENV`
- `OPEND_CREDENTIAL_METHOD`
- `OPEND_OUTPUT`
- `OPEND_SDK_PATH`

## Files

- `openclaw`: Bash CLI entrypoint.
- `opend_cli.py`: structured command interface.
- `opend_core.py`: shared OpenD logic.
- `credentials.py`: secret-ref, env, keyring, and config password loading.
- `references/api_docs.md`: official API links and key limits.
- `references/release_checklist.md`: pre-publish validation checklist.

## Legacy Compatibility

Older scripts delegate to `opend_cli.py`:
- `get_market_snapshot.py`
- `query_positions.py`
- `place_order.py`
- `place_order_env.py`
- `place_order_keyring.py`
- `place_order_config.py`
