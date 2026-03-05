---
name: lmfiles
description: Upload files to lmfiles.com and return public download links via API. Use when a user wants CLI-based file hosting, quick share links, bot-accessible file upload, account registration with bootstrap token, file metadata lookup, listing account files, or deleting uploaded files.
---

# lmfiles

Use lmfiles.com as a lightweight file host for OpenClaw/LLM workflows.

## Provenance & trust

- Service docs: https://lmfiles.com/docs
- OpenAPI schema: https://lmfiles.com/openapi.json
- API host: https://lmfiles.com

Primary credential:
- `LMFILES_API_KEY` (required for authenticated operations)

Bootstrap credential:
- `LMFILES_BOOTSTRAP_TOKEN` (used only for first-time account registration)

Security notes:
- Treat credentials as secrets and avoid logging/pasting them.
- Rotate bootstrap token if exposed.
- `401 Unauthorized` usually means missing/invalid `LMFILES_API_KEY`.

## Before first use (required)

1. Register an account once with a bootstrap token.
2. Save returned `api_key` as `LMFILES_API_KEY`.
3. Use `LMFILES_API_KEY` for all authenticated operations.

Quick setup:

```bash
export LMFILES_BOOTSTRAP_TOKEN="<bootstrap-token>"

curl -sS -X POST https://lmfiles.com/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -d '{"username":"my-bot","bootstrap_token":"'"$LMFILES_BOOTSTRAP_TOKEN"'"}'

# Copy api_key from response, then:
export LMFILES_API_KEY="lmf_..."
```

Common auth error:
- `401 Unauthorized` = missing/invalid `LMFILES_API_KEY`.

## Required env vars

- `LMFILES_API_KEY` for authenticated file operations (primary credential).
- `LMFILES_BOOTSTRAP_TOKEN` only for account registration (bootstrap credential).

## Register account (one-time)

```bash
curl -sS -X POST https://lmfiles.com/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -d '{"username":"my-bot","bootstrap_token":"'"$LMFILES_BOOTSTRAP_TOKEN"'"}'
```

Or use helper script:

```bash
bash scripts/register.sh my-bot
```

Save returned `api_key` as `LMFILES_API_KEY`.

## Upload file (max 100 MB)

```bash
curl -sS -X POST https://lmfiles.com/api/v1/files/upload \
  -H "X-API-Key: $LMFILES_API_KEY" \
  -F "file=@/absolute/path/to/file.ext"
```

Expected response includes:
- `file_id`
- `url` (public download link)

## Download (public)

```bash
curl -L "https://lmfiles.com/f/<file_id>" -o downloaded.file
```

## File metadata (public)

```bash
curl -sS "https://lmfiles.com/api/v1/files/<file_id>"
```

## Account info and usage

```bash
curl -sS https://lmfiles.com/api/v1/accounts/me \
  -H "X-API-Key: $LMFILES_API_KEY"
```

## List account files

```bash
curl -sS https://lmfiles.com/api/v1/accounts/me/files \
  -H "X-API-Key: $LMFILES_API_KEY"
```

Or helper script:

```bash
bash scripts/list.sh
```

## Delete file (owner only)

```bash
curl -sS -X DELETE https://lmfiles.com/api/v1/files/<file_id> \
  -H "X-API-Key: $LMFILES_API_KEY"
```

Or helper script:

```bash
bash scripts/delete.sh <file_id>
```

## Constraints

- Max upload size: 100 MB.
- Executable file types are rejected (for example `.php`, `.sh`, `.py`, `.exe`).
- Files expire after 90 days of inactivity; downloads reset the expiry clock.
- Downloads are public for anyone with the URL.

## Safety checks before upload

- Confirm file is safe to publish publicly.
- Avoid uploading secrets or credentials.
- If uncertain, ask user before upload.
