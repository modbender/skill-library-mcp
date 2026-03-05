# Registry Metadata Draft

Use this as the source of truth when filling ClawHub/OpenClaw registry fields.

## Purpose

Open-source wrapper skill for local OpenD market-data and trading automation against the commercial MooMoo/Futu OpenAPI. Supports account discovery, position queries, market snapshots, and order placement with `SIMULATE` as the default environment.

## Primary credential model

- Preferred hosted credential: `OPEND_PASSWORD_SECRET_REF`
- Description: OpenClaw-compatible SecretRef used to obtain the trade password through gateway-managed secret injection.

## Required or supported secret inputs

- `OPEND_PASSWORD_SECRET_REF`
  - Preferred for hosted use.
  - Current local resolver supports env-backed SecretRef objects such as `{"source":"env","id":"MOOMOO_PASSWORD"}`.
- `MOOMOO_PASSWORD`
  - Legacy compatibility path for local-only usage.
- `MOOMOO_CONFIG_KEY`
  - Legacy compatibility path used with `config.enc`.

## Supported non-secret overrides

- `OPEND_HOST`
- `OPEND_PORT`
- `OPEND_MARKET`
- `OPEND_SECURITY_FIRM`
- `OPEND_TRD_ENV`
- `OPEND_CREDENTIAL_METHOD`
- `OPEND_OUTPUT`
- `OPEND_SDK_PATH`

## User-facing warning text

This project is open source and intended to be inspectable and modifiable. For hosted use, secrets should be supplied through OpenClaw secret management. Raw environment variables, local encrypted config files, and OS keyring storage are retained only as compatibility paths and should be treated as less desirable from an audit perspective.
