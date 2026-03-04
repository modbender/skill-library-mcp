---
name: approve-pairing
description: Approve a pending DM pairing request without the openclaw CLI, by directly editing credential files. Use when `openclaw pairing approve` is unavailable (CLI not in PATH, elevated access not configured, sandbox environment). Supports telegram, whatsapp, signal, imessage, discord, slack, feishu.
---

# approve-pairing

Approve pending DM pairing requests by writing directly to OpenClaw credential files — no CLI required.

## How It Works

Pairing state lives in two files under `~/.openclaw/credentials/`:

- **`<channel>-pairing.json`** — pending requests (sender ID, code, accountId)
- **`<channel>-<accountId>-allowFrom.json`** — approved senders allowlist

Approving = add sender ID to allowFrom file + remove code from pairing file.

## Quick Approval (script)

```bash
python3 skills/approve-pairing/scripts/approve_pairing.py <channel> <code>
```

Example:
```bash
python3 skills/approve-pairing/scripts/approve_pairing.py telegram PWVW264M
```

The script:
1. Reads `~/.openclaw/credentials/<channel>-pairing.json`
2. Finds the request matching the code
3. Appends the sender ID to the allowFrom file
4. Removes the code from pending requests

## Manual Steps (if script unavailable)

1. Read `~/.openclaw/credentials/<channel>-pairing.json` to get `id` and `meta.accountId`
2. Write/update `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json`:
   ```json
   { "version": 1, "allowFrom": ["<sender_id>"] }
   ```
3. Clear the pending request from `<channel>-pairing.json`

## Notes

- Codes expire after 1 hour — check `createdAt` if approval fails
- A gateway restart may be needed: `openclaw gateway restart`
- If `accountId` is `"default"` or empty, the file is `<channel>-default-allowFrom.json`
- Pending requests capped at 3 per channel; old ones must expire before new ones are created
