---
name: 1password-sa
description: Securely inject secrets from 1Password into agent workflows. Uses service accounts with op run/.env.tpl as the primary pattern, op read as fallback. Includes hardened security rules, input validation, and troubleshooting for auth/permission failures. Use when accessing API keys, credentials, or any 1Password secret.
homepage: https://developer.1password.com/docs/cli/get-started/
metadata:
  {
    "openclaw":
      {
        "emoji": "🔐",
        "requires": { "bins": ["op"] },
        "env": ["OP_SERVICE_ACCOUNT_TOKEN"],
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "1password-cli",
              "bins": ["op"],
              "label": "Install 1Password CLI (brew)",
            },
          ],
      },
  }
---

# 1Password CLI (Hardened)

Secure secret access via 1Password CLI (`op`) for OpenClaw agents. Service accounts are the canonical approach.

## References

- `references/get-started.md` — install + baseline setup
- `references/cli-examples.md` — safe command patterns
- `references/troubleshooting.md` — failure/recovery runbook

## Security Rules (must follow)

1. **Prefer `op run` over all alternatives** for secret injection.
2. **Never enable shell tracing** around secret commands (`set -x`, `bash -x`).
3. **Never print secrets to stdout/logs** (`echo`, `cat` on secret values/files). `printf` piped directly to stdin of another command (e.g., `printf ... | curl -H @-`) is acceptable when the output never reaches a log or terminal.
4. **Never dump environment** inside/after secret-bearing runs (`env`, `printenv`, `set`).
5. **Never pass secrets as CLI args** (arguments can appear in process lists).
6. **Never pipe secret output to logs/files** (`tee`, `>`, `>>`) unless explicitly writing a protected temporary file for `op inject`.
7. **Never pipe `op read` output into logging pipelines.**
8. **Use `op inject` only with locked-down temp files:** `umask 077`, `chmod 600`, `trap` cleanup.
9. **Never include secret values in chat, tool output, or agent responses.** If a command outputs a secret, do not echo or reference its value.

### Banned Flags/Patterns

- **`--no-masking`** — never use in agent workflows. Masking redacts accidental secret output and must stay on.
- **`--reveal`** — never use in routine workflows. Outputs field values in cleartext.
- **`op signin --raw`** — outputs raw session token to stdout.
- **Bare `op read`** — never run without capturing into a variable. It prints secrets to stdout.
- **`set -x`** — never enable around any `op` command.
- **`curl -v`** — verbose mode logs auth headers. Use `curl -sSf` instead.
- **`script`** / **terminal recorders** — session recording captures all secret output.

### Untrusted Input

- Never interpolate user-provided or external text into shell commands without strict quoting.
- Always use `--` to separate `op` flags from command arguments.
- Vault/item/field names from untrusted sources must be validated (alphanumeric, hyphens, underscores, and spaces only).
- Never use `eval`, backtick substitution, or string-built shell commands with secret references.
- If an item name looks suspicious (contains `$`, backticks, semicolons, or pipes), stop and verify with the user.

**Safe dynamic input template:**

```bash
VAULT="my-vault"
ITEM="my-item"

# Validate: reject names with dangerous characters
for NAME in "$VAULT" "$ITEM"; do
  if ! LC_ALL=C [[ "$NAME" =~ ^[a-zA-Z0-9\ _-]+$ ]]; then
    echo "ERROR: invalid vault/item name: $NAME" >&2; exit 1
  fi
done

VALUE="$(op read "op://${VAULT}/${ITEM}/password")"
# use $VALUE, then:
unset VALUE
```

Always double-quote variable expansions. Never build `op://` references from untrusted input without validation. Reject names containing `/`, `$`, backticks, semicolons, pipes, or other shell metacharacters.

### `.env.tpl` Security

- Treat as code: verify ownership, review changes, restrict permissions (`chmod 600`).
- Do not accept `.env.tpl` files from untrusted sources.
- Do not commit to public repos — references reveal vault/item structure.
- Add to `.gitignore` if in a repo.
- After creating/editing: `chmod 600 .env.tpl`
- Only define expected variable names — reject templates containing dangerous env vars (`PATH`, `LD_PRELOAD`, `BASH_ENV`, `NODE_OPTIONS`, etc.).

---

## Service Account Workflow (Primary)

Service accounts are the default for agents. No interactive auth needed.

### 1) Load and scope token

Load the token from your platform's secure store:

```bash
# macOS Keychain:
#   security find-generic-password -a <account> -s OP_SERVICE_ACCOUNT_TOKEN -w
# Linux (GNOME Keyring / libsecret):
#   secret-tool lookup service OP_SERVICE_ACCOUNT_TOKEN
# Last resort (interactive prompt, not automatable):
#   read -rs OP_SERVICE_ACCOUNT_TOKEN

OP_SERVICE_ACCOUNT_TOKEN="$(__REPLACE_WITH_SECURE_STORE_COMMAND__)"
[ -z "$OP_SERVICE_ACCOUNT_TOKEN" ] && { echo "ERROR: token retrieval failed" >&2; exit 1; }
```

**Preferred: single-command scope** (token never persists in shell env):

```bash
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" \
  op run --env-file=.env.tpl -- <command>
unset OP_SERVICE_ACCOUNT_TOKEN
```

**If multiple commands needed:** export briefly with trap cleanup:

```bash
export OP_SERVICE_ACCOUNT_TOKEN
trap 'unset OP_SERVICE_ACCOUNT_TOKEN' EXIT
op run --env-file=.env.tpl -- <command-1>
op run --env-file=.env.tpl -- <command-2>
unset OP_SERVICE_ACCOUNT_TOKEN
```

### 2) Use `.env.tpl` + `op run` (preferred)

Create `.env.tpl` with 1Password references (not raw secrets):

```
API_KEY=op://my-vault/my-item/api-key
DB_PASSWORD=op://my-vault/my-item/password
```

Run:

```bash
op run --env-file=.env.tpl -- <command>
```

Masking is on by default and must stay on. Note: masking is defense-in-depth, not primary protection — transformed or partial secrets may evade redaction. The primary defense is never outputting secrets.

### 3) One-off fallback: `op read`

Use only when `op run` doesn't fit. Use a subshell for automatic cleanup:

```bash
(
  trap 'unset VALUE' EXIT
  VALUE="$(op read 'op://my-vault/my-item/field')"
  # use $VALUE here — auto-cleaned on exit
)
```

For API calls, prefer `op run` with a wrapper script to avoid `sh -c`:

```bash
# api-call.sh (chmod +x)
#!/usr/bin/env bash
set -euo pipefail
printf "Authorization: Bearer %s\n" "$API_TOKEN" | curl -sSf -H @- https://api.example.com/resource
```

```bash
op run --env-file=.env.tpl -- ./api-call.sh
```

### 4) Diagnostics

> **All diagnostic output contains metadata** (account emails, vault names, item IDs, URLs) that should be treated as sensitive in logged/recorded agent sessions.

```bash
op whoami
op vault list --format json
```

### 5) Service account lifecycle

- **Scope is policy-driven:** read-only vs read-write depends on configuration and vault permissions.
- **If access fails:** verify vault grants and item permissions.
- **If token expired/revoked:** regenerate in 1Password admin, update secure store, retry.
- **Limitation:** service accounts may not support item creation depending on org policy.

---

## `op inject` (restricted use)

Use only when a file must be materialized temporarily:

```bash
set -euo pipefail
set +x
umask 077

TMP_FILE="$(mktemp)"
cleanup() { rm -f "$TMP_FILE"; }
trap cleanup EXIT ERR INT TERM HUP QUIT

op inject -i config.tpl -o "$TMP_FILE"
chmod 600 "$TMP_FILE"

# use "$TMP_FILE" briefly, then auto-cleanup via trap
```

Never persist injected secret files beyond immediate use.
