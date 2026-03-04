# Config & Auth Commands

## `grvt setup`

Interactive setup wizard. Displays an ASCII banner and a full disclaimer box warning that this is a community project (not officially maintained by GRVT) with no security audit. The user must type `y` to accept the risks before the wizard proceeds.

After acceptance, it walks through: environment, API key, private key, and default sub-account ID, then authenticates automatically.

```bash
grvt setup
```

No options. All prompts are interactive (reads from stdin), which keeps sensitive values like private keys out of shell history.

**Not suitable for agents or non-interactive scripts** — use `config set` + `auth login` instead.

---

## `grvt config path`

Print the absolute path to the config file.

```bash
grvt config path
# Output: /Users/you/.config/grvt/config.toml
```

---

## `grvt config get [key]`

Get a config value. Without a key, prints the full config (secrets redacted).

| Argument | Required | Description |
|----------|----------|-------------|
| `key` | No | Config key, supports dot-notation (e.g. `http.timeoutMs`) |

```bash
grvt config get env
# Output: testnet

grvt config get outputDefaults.output
# Output: table

grvt config get
# Output: full config with secrets redacted
```

Secret keys (`apiKey`, `privateKey`, `cookie`) always print as `****`.

---

## `grvt config set <key> <value>`

Set a config value. The config is validated before saving.

| Argument | Required | Description |
|----------|----------|-------------|
| `key` | **Yes** | Config key (dot-notation) |
| `value` | **Yes** | Value to set |

Valid top-level keys: `env`, `apiKey`, `privateKey`, `subAccountId`, `accountId`, `cookie`.
Valid nested keys: `outputDefaults.output`, `outputDefaults.pretty`, `outputDefaults.silent`, `http.timeoutMs`, `http.retries`, `http.backoffMs`, `http.maxBackoffMs`.

```bash
grvt config set env testnet
grvt config set subAccountId 123456
grvt config set outputDefaults.output json
grvt config set http.timeoutMs 30000
grvt config set privateKey 0xYOUR_PRIVATE_KEY
```

---

## `grvt config unset <key>`

Remove a config value (resets to default).

| Argument | Required | Description |
|----------|----------|-------------|
| `key` | **Yes** | Config key to unset |

```bash
grvt config unset privateKey
grvt config unset http.timeoutMs
```

---

## `grvt config list`

Print the full config with secrets redacted. Equivalent to `grvt config get` with no key.

```bash
grvt config list
grvt config list --output json --pretty
```

---

## `grvt config export`

Export config to a TOML file.

| Option | Required | Description |
|--------|----------|-------------|
| `--file <path>` | **Yes** | Destination file path |
| `--include-secrets` | No | Include secret values (prompts for confirmation) |
| `--yes` | No | Skip confirmation prompt |

```bash
grvt config export --file backup.toml
grvt config export --file full-backup.toml --include-secrets --yes
```

---

## `grvt config import`

Import config from a TOML file. Overwrites all current config values.

| Option | Required | Description |
|--------|----------|-------------|
| `--file <path>` | **Yes** | Source file path |

```bash
grvt config import --file backup.toml
```

The file is validated against the config schema before saving.

---

## `grvt auth login`

Authenticate with GRVT API. Stores session cookie and account ID in config.

| Option | Required | Description |
|--------|----------|-------------|
| `--api-key <key>` | No (falls back to config) | GRVT API key |
| `--private-key <key>` | No | Ethereum private key for EIP-712 signing |
| `--env <env>` | No (falls back to config) | Environment override: `dev\|staging\|testnet\|prod` |

```bash
# Full login
grvt auth login --api-key YOUR_KEY --private-key 0xYOUR_KEY

# Using config values
grvt config set apiKey YOUR_KEY
grvt auth login

# Override environment for one login
grvt auth login --env testnet
```

On success, stores: `cookie` (session), `accountId`, and optionally `privateKey` in the config file.

---

## `grvt auth status`

Check if the current session is valid by making an API call.

```bash
grvt auth status
grvt auth status --output json
```

Returns session validity. If the session is expired, re-authenticate with `grvt auth login`.

---

## `grvt auth whoami`

Show current authentication state from local config. Does **not** make any API calls.

```bash
grvt auth whoami
grvt auth whoami --output json
```

Returns: `env`, `accountId`, `subAccountId`, `hasApiKey`, `hasPrivateKey`, `hasSession`.

---

## `grvt auth logout`

Clear all stored credentials (API key, private key, cookie, account ID) from config.

```bash
grvt auth logout
```
