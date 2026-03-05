---
name: bitwarden-bw
description: Access and manage Bitwarden passwords securely using the official bw CLI.
metadata: {"clawdbot":{"emoji":"🔒","os":["linux","macos"],"requires":{"bins":["bw"]}}}
---

# Bitwarden Skill

Interact with Bitwarden vaults using the official `bw` CLI.

## Prerequisites

- `bw` CLI installed: `npm install -g @bitwarden/cli`
- `BW_SESSION` env var set (saved in `~/.zshrc`)

## Usage

### Get a password
```bash
bw get password "site_name"
```

### Get username
```bash
bw get username "site_name"
```

### Get full item (JSON)
```bash
bw get item "site_name" --pretty
```

### Search
```bash
bw list items --search "query" | python3 -c "import json,sys; [print(f'{i[\"name\"]} ({i.get(\"login\",{}).get(\"username\",\"\")})')for i in json.load(sys.stdin)]"
```

### Sync vault
```bash
bw sync
```
*Always sync before getting details to ensure accuracy.*

### TOTP code
```bash
bw get totp "site_name"
```

## Notes

- Session key is in `BW_SESSION` env var (persisted in ~/.zshrc)
- If session expires, user must re-login interactively (`bw login` requires OTP)
- `bw unlock` can refresh an expired session without full re-login
