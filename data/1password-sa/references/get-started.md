# 1Password CLI get started (safe baseline)

## 1) Install and verify

Install `op` using your platform package manager (see official docs), then verify:

```bash
op --version
```

## 2) Configure service account

Load token from your platform's secure store (see SKILL.md §1 for platform examples):

```bash
OP_SERVICE_ACCOUNT_TOKEN="$(__REPLACE_WITH_SECURE_STORE_COMMAND__)"
[ -z "$OP_SERVICE_ACCOUNT_TOKEN" ] && { echo "ERROR: token retrieval failed" >&2; exit 1; }
```

Single-command scope:

```bash
OP_SERVICE_ACCOUNT_TOKEN="$OP_SERVICE_ACCOUNT_TOKEN" op whoami
unset OP_SERVICE_ACCOUNT_TOKEN
```

Multiple commands — export briefly with trap cleanup:

```bash
export OP_SERVICE_ACCOUNT_TOKEN
trap 'unset OP_SERVICE_ACCOUNT_TOKEN' EXIT
op whoami
# ... do work ...
unset OP_SERVICE_ACCOUNT_TOKEN
```

## 3) Preferred secret injection (`op run`)

Create `.env.tpl` in project/skill directory:

```
SECRET_NAME=op://my-vault/my-item/field
ANOTHER_SECRET=op://my-vault/another-item/password
```

Run command:

```bash
op run --env-file=.env.tpl -- <command>
```

Masking is on by default and must stay on.

## 4) One-off fallback (`op read`)

Always capture in a subshell for automatic cleanup:

```bash
(
  trap 'unset VALUE' EXIT
  VALUE="$(op read 'op://my-vault/my-item/field')"
  # use $VALUE here — auto-cleaned on exit
)
```

## 5) Safety reminders

- Never log or print secrets.
- Never use `set -x` around secret commands.
- Never pass secrets as command-line arguments.
- Never use `--no-masking` or `--reveal`.
- Prefer `op run` for everything; `op read` into variable as last resort.
