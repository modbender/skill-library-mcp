# bitclawden

An [OpenClaw](https://openclaw.ai/) skill for managing credentials in a [Bitwarden](https://bitwarden.com/) vault via the `bw` CLI.

## What it does

- Look up usernames, passwords, and TOTP codes
- Create new vault items (logins, secure notes, cards, identities)
- Edit existing items
- Generate strong passwords and passphrases
- Sync vault changes

## Requirements

- [`bw` CLI](https://bitwarden.com/help/cli/) installed and in PATH
- [`jq`](https://jqlang.github.io/jq/) for editing vault items
- An active Bitwarden session (`BW_SESSION` environment variable)
- `curl` and `unzip` (needed only if using the built-in install script)

## Installation

Copy or symlink the `bitclawden` folder into your OpenClaw skills directory:

```bash
# Local install
cp -r bitclawden ~/.openclaw/skills/bitclawden

# Or via ClawHub
clawhub install bitclawden
```

## Security

This skill accesses your Bitwarden vault. Passwords are never shown unless explicitly requested. Treat `BW_SESSION` as a secret — do not commit it or expose it in logs.

## License

MIT
