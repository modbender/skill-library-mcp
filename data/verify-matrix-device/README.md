# verify-matrix-device

OpenClaw skill and scripts to verify and cross-sign active Matrix devices for OpenClaw-managed accounts.

## Purpose

- Resolve one OpenClaw-managed Matrix account from `openclaw.json`
- Resolve the active `device_id` via `/whoami` using the stored OpenClaw access token
- Restore the self-signing key from secret storage using the recovery key
- Sign the active device directly and confirm the signature server-side

## Requirements

- Node.js 20+
- Access to an `openclaw.json` file, or use direct test mode
- An interactive terminal (the script prompts for secrets securely)

## Installation

```bash
npm install
```

## Usage

```bash
npm run verify-account
```

Direct test mode:

```bash
npm run verify-direct
```

Password-only mode:

```bash
npm run verify-password
```

The script prompts for:

- `homeserver`
- `recovery key` (hidden)

Default mode prompts:

- `username` (OpenClaw account id, full Matrix user id, or unique localpart)

Access-token mode prompts:

- `Matrix user ID`
- `access token` (hidden)

Password mode prompts:

- `Matrix user ID`
- `password` (hidden)
- `target device ID`

Optional flags:

- `--homeserver` pre-fills the homeserver prompt
- `--username` pre-fills the username prompt
- `--user-id` pre-fills the Matrix user ID in access-token mode or password mode
- `--device-id` pre-fills the target device ID in password mode
- `--openclaw-json` overrides the default config path
- `--access-token` bypasses `openclaw.json` and uses a Matrix user + access token flow
- `--direct` and `-t` are compatibility aliases for `--access-token`
- `--password` or `-p` logs in with the Matrix password, signs the specified target device ID, then logs out the temporary helper session

Test without `openclaw.json`:

```bash
npm run verify-direct
```

If you do not have an access token but you know the device to sign:

```bash
npm run verify-password
```

Default config path:

- `OPENCLAW_JSON` if set
- otherwise `~/.openclaw/openclaw.json`

## Security

- No secrets are embedded in the repository
- No default homeserver is hardcoded
- Access tokens, passwords, and recovery keys are hidden while typed
- `verify-account` and `verify-direct` run through `scripts/verify_matrix_device.mjs` and do not create a helper login or temporary Matrix device
- `verify-direct` now runs access-token mode
- `verify-password` runs through `scripts/verify_matrix_device.mjs`, creates a temporary helper session only to fetch account data and upload the signature, then logs it out
- Tokens are not printed in clear text

## License

MIT (see `LICENSE`)
