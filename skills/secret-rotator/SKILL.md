---
description: Audit and rotate API keys, tokens, and secrets with expiry tracking and safe handling.
---

# Secret Rotator

Audit, track, and rotate API keys, tokens, and secrets safely.

## Requirements

- File system access to scan `.env` and config files
- No API keys needed (this tool manages other tools' keys)

## Instructions

### Step 1: Inventory secrets (with user consent)

**⚠️ Always ask the user which directories to scan before running.**

```bash
# Find .env files in specified directories
find ~/projects -maxdepth 3 -name ".env*" -type f 2>/dev/null

# Common config locations
ls -la ~/.config/*/config* ~/.ssh/config 2>/dev/null
```

Report for each secret found:
- File path
- Key name (e.g., `OPENAI_API_KEY`)
- Last modified date and age in days
- **NEVER print actual secret values**

### Step 2: Age analysis

```
## 🔐 Secret Inventory — <timestamp>

| File | Key | Age | Status |
|------|-----|-----|--------|
| ~/project/.env | OPENAI_API_KEY | 45d | 🟢 OK |
| ~/app/.env | DB_PASSWORD | 120d | 🟡 Rotate Soon |
| ~/.config/app/config | API_TOKEN | 200d | 🔴 Overdue |

**Policy**: 🟢 < 90 days | 🟡 90–180 days | 🔴 > 180 days
```

### Step 3: Rotation guidance

For each key needing rotation:
1. Identify the service (OpenAI, AWS, Stripe, etc.)
2. Provide the dashboard URL for key regeneration
3. List all files that reference this key (need updating after rotation)

### Step 4: Post-rotation verification

1. Test the new key works (e.g., `curl` a health endpoint with the new key)
2. Confirm old key is invalidated
3. Update file timestamps
4. Verify `.gitignore` includes all secret files

## Security Rules

- ❌ **NEVER** display full secret values — mask as `sk-...XXXX` (last 4 only)
- ❌ **NEVER** send secrets via chat, logs, or messaging
- ❌ **NEVER** commit secrets to git
- ✅ Always `chmod 600` on secret files
- ✅ Verify `.gitignore` entries exist for `.env*` files
- ✅ Show only key names and metadata, never values

## Edge Cases

- **Symlinked .env files**: Follow symlinks but report the real path.
- **Docker secrets**: Check `docker secret ls` if Docker is available.
- **Env vars only (no file)**: Some keys exist only in environment — note these can't be age-tracked.
- **Shared secrets**: Warn if the same key appears in multiple files (update all on rotation).
- **No secrets found**: Report clean scan — still suggest setting up a rotation policy.
