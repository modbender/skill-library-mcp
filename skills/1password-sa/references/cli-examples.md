# 1Password CLI examples (safe patterns)

All examples use generic placeholders (`my-vault`, `my-item`, `user@example.com`).

## Identity check

```bash
op whoami
```

## Vault and item discovery

> **Note:** These commands output vault/item names and metadata. In logged/recorded agent sessions, treat this output as sensitive — it reveals infrastructure structure.

```bash
op vault list --format json
op item list --vault "my-vault" --format json
```

## Get item metadata (without secret values)

```bash
op item get "my-item" --vault "my-vault" --format json
```

Returns metadata and field labels but not secret values (unless `--reveal` is used, which is banned). Output may contain usernames, URLs, and item IDs — treat as sensitive in logged contexts.

## Read single secret into variable

Always capture in a subshell for automatic cleanup:

```bash
(
  trap 'unset VALUE' EXIT
  VALUE="$(op read 'op://my-vault/my-item/password')"
  # use $VALUE here — auto-cleaned on exit
)
```

## Safe dynamic input pattern

When vault/item names come from variables, validate and double-quote:

```bash
VAULT="my-vault"
ITEM="my-item"
FIELD="password"

# Validate: reject names with dangerous characters
for NAME in "$VAULT" "$ITEM" "$FIELD"; do
  if ! LC_ALL=C [[ "$NAME" =~ ^[a-zA-Z0-9\ _-]+$ ]]; then
    echo "ERROR: invalid name: $NAME" >&2; exit 1
  fi
done

VALUE="$(op read "op://${VAULT}/${ITEM}/${FIELD}")"
# use $VALUE here
unset VALUE  # or wrap in subshell for auto-cleanup
```

## Run command with `.env.tpl` (preferred)

`.env.tpl` contents:

```
API_TOKEN=op://my-vault/my-item/api-token
```

Single-command scoped token + run:

```bash
# api-call.sh (chmod +x)
#!/usr/bin/env bash
set -euo pipefail
printf "Authorization: Bearer %s\n" "$API_TOKEN" | curl -sSf -H @- https://api.example.com/health
```

```bash
OP_SERVICE_ACCOUNT_TOKEN="$(__REPLACE_WITH_SECURE_STORE_COMMAND__)"
[ -z "$OP_SERVICE_ACCOUNT_TOKEN" ] && { echo "ERROR: token retrieval failed" >&2; exit 1; }
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" \
  op run --env-file=.env.tpl -- ./api-call.sh
unset OP_SERVICE_ACCOUNT_TOKEN
```

## Run with inline env-file (temporary)

```bash
umask 077
TMPFILE=$(mktemp "${TMPDIR:-/tmp}/op-env.XXXXXX")
trap 'rm -f "$TMPFILE"' EXIT ERR INT TERM HUP
cat > "$TMPFILE" <<'EOF'
SECRET=op://my-vault/my-item/credential
EOF
chmod 600 "$TMPFILE"
op run --env-file="$TMPFILE" -- my-command
```

## Banned patterns (never use)

- `op run --no-masking` — disables output redaction
- `op item get --reveal` — outputs secret values in cleartext
- `op signin --raw` — outputs raw session token to stdout
- `op read "op://..."` without variable capture — prints secret to stdout
- `set -x` before any `op` command — logs secrets to trace output
- `curl -v` with secret headers — verbose mode logs auth headers
- `script` / terminal recorders — records all output including secrets
