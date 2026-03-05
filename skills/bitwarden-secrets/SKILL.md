---
name: bitwarden-secrets
description: Safely access Bitwarden or Vaultwarden secrets via the bw CLI with redacted outputs by default. Use for vault sync, item search, metadata retrieval, and (only with explicit confirmation) revealing a single secret field.
---

# Bitwarden Secrets (safe-by-default)

Use this skill to interact with Bitwarden/Vaultwarden through `bw` while minimizing accidental secret leakage.

## Prerequisites
- `bw` CLI installed.
- Server configured (`bw config server <url>`).
- Logged in (`bw login --apikey`) and unlocked (`bw unlock`) so `BW_SESSION` is available.

## Commands
```bash
cd skills/bitwarden-secrets
python3 scripts/vw_cli.py status
python3 scripts/vw_cli.py sync
python3 scripts/vw_cli.py search --query google
python3 scripts/vw_cli.py get --id <item_id>
```

### Bootstrap helper (optional)
Load runtime vars + refresh session + sync in one step:
```bash
source scripts/vw_bootstrap.sh
# or after shell reload:
vw-openclaw-ready
```

### Reveal (explicit only)
By default, do not reveal secret values in chat.
Use reveal only with explicit user consent and temporary policy override:
```bash
export VW_REVEAL_ALLOW=1
python3 scripts/vw_cli.py reveal --id <item_id> --field password --confirm YES_REVEAL
unset VW_REVEAL_ALLOW
```

## Safety policy
- Default outputs are redacted/metadata-only.
- No bulk secret dumps.
- Prefer IDs + labels and retrieve only the minimum needed field.
- Reveal requires BOTH `VW_REVEAL_ALLOW=1` and `--confirm YES_REVEAL`.
