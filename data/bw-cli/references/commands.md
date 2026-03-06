# Bitwarden CLI Command Reference

Complete reference for `bw` commands. Generated from official Bitwarden documentation.

## Global Options

| Option | Description |
|--------|-------------|
| `--pretty` | Format output with 2-space tabs |
| `--raw` | Return raw output instead of descriptive message |
| `--response` | Return JSON formatted response |
| `--quiet` | Don't return anything to stdout (use for piping credentials) |
| `--nointeraction` | Do not prompt for interactive user input |
| `--session <key>` | Pass session key instead of reading from env var |
| `-v, --version` | Output version number |
| `-h, --help` | Display help text |

## Authentication Commands

### login

```bash
bw login [email] [password] [options]
bw login --apikey
bw login --sso
```

**Options:**
- `--method <0|1|3>` - Two-step login method (0=authenticator, 1=email, 3=yubikey)
- `--code <code>` - Two-step login code
- `--apikey` - Use personal API key
- `--sso` - Use SSO authentication

**Environment variables:**
- `BW_CLIENTID` - API key client_id
- `BW_CLIENTSECRET` - API key client_secret

### unlock

```bash
bw unlock [password] [options]
```

**Options:**
- `--passwordenv <name>` - Read password from environment variable
- `--passwordfile <path>` - Read password from file (first line)

**Output:** Returns `export BW_SESSION="..."` command to copy/paste.

### lock

```bash
bw lock
```

Locks vault (destroys session key, keeps authentication).

### logout

```bash
bw logout
```

**⚠️ DESTRUCTIVE:** Fully logs out, requires re-authentication.

### status

```bash
bw status
```

Returns JSON:
```json
{
  "serverUrl": "https://vault.bitwarden.com",
  "lastSync": "2024-01-15T10:30:00.000Z",
  "userEmail": "user@example.com",
  "userId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "unlocked|locked|unauthenticated"
}
```

## Vault Management Commands

### list

```bash
bw list (items|folders|collections|organizations|org-collections|org-members) [options]
```

**Filters (OR when combined):**
- `--folderid <id>` - Items in folder
- `--collectionid <id>` - Items in collection
- `--organizationid <id>` - Objects in organization
- `--url <url>` - Items matching URL
- `--trash` - Items in trash
- Any filter accepts `null` or `notnull`

**Search (AND with filters):**
- `--search <term>` - Search string

### get

```bash
bw get (item|username|password|uri|totp|exposed|attachment|folder|collection|organization|org-collection|template|fingerprint|notes) <id-or-search> [options]
```

**Notes:**
- Returns single result only
- Use exact UUID or search string
- `totp` returns current 2FA code

**Attachment options:**
- `--itemid <id>` - Required for attachments
- `--output <path>` - Download directory (must end with `/`)

### create

```bash
bw create (item|attachment|folder|org-collection) [encodedJson] [options]
```

**Workflow:** `get template` → `jq` modify → `bw encode` → `create`

**Item types:**
- Login: `.type=1`
- Secure Note: `.type=2`
- Card: `.type=3`
- Identity: `.type=4`

**Attachment options:**
- `--file <path>` - File to attach
- `--itemid <id>` - Target item

### edit

```bash
bw edit (item|item-collections|folder|org-collection) <id> [encodedJson] [options]
```

**Options:**
- `--organizationid <id>` - Required for org-collection edits

Performs full object replacement.

### delete

```bash
bw delete (item|attachment|folder|org-collection) <id> [options]
```

**Options:**
- `-p, --permanent` - **IRREVERSIBLE** - Skip trash, delete immediately

### restore

```bash
bw restore (item) <id>
```

Restores item from trash (within 30 days).

## Item Templates

Retrieve JSON templates for create operations:

```bash
bw get template (item|item.field|item.login|item.login.uri|item.card|item.identity|item.securenote|folder|collection|item-collections|org-collection)
```

## Utility Commands

### encode

```bash
bw encode
```

Base64 encodes stdin. Used with `jq` for create/edit operations.

### generate

```bash
bw generate [options]
```

**Password options:**
- `-l, --lowercase` - Include lowercase
- `-u, --uppercase` - Include uppercase
- `-n, --number` - Include numbers
- `-s, --special` - Include special characters
- `--length <n>` - Length (min 5)

**Passphrase options:**
- `--passphrase` - Generate passphrase instead of password
- `--words <n>` - Number of words
- `--separator <char>` - Word separator
- `-c, --capitalize` - Title-case words
- `--includeNumber` - Include number in passphrase

### import

```bash
bw import <format> <path>
bw import --formats  # List supported formats
```

**Options:**
- `--organizationid <id>` - Import to organization vault

### export

```bash
bw export [options]
```

**Options:**
- `--output <path>` - Output directory
- `--format <csv|json|encrypted_json|zip>` - Export format
- `--password <pw>` - Password for encrypted_json (uses account key if omitted)
- `--organizationid <id>` - Export organization vault
- `--raw` - Output to stdout instead of file

### sync

```bash
bw sync
bw sync --last  # Show last sync timestamp only
```

Pulls vault from server. Push is automatic on create/edit/delete.

### config

```bash
bw config server <url> [options]
bw config server  # Read current server
```

**Options for self-hosted:**
- `--web-vault <url>`
- `--api <url>`
- `--identity <url>`
- `--icons <url>`
- `--notifications <url>`
- `--events <url>`
- `--key-connector <url>`

### update

```bash
bw update
```

Checks for updates (does not auto-update).

### serve

```bash
bw serve [options]
```

Starts REST API server.

**Options:**
- `--port <n>` - Default 8087
- `--hostname <host>` - Default localhost
- `--disable-origin-protection` - **NOT RECOMMENDED**

## Organization Commands

### move

```bash
bw move <itemid> <organizationid> [encodedJson]
```

Moves item to organization. `encodedJson` is collection IDs array.

### confirm

```bash
bw confirm org-member <userid> --organizationid <orgid>
```

Confirms invited member. **Verify fingerprint phrase first!**

### device-approval

```bash
bw device-approval list --organizationid <id>
bw device-approval approve <requestid> --organizationid <id>
bw device-approval approve-all --organizationid <id>
bw device-approval deny <requestid> --organizationid <id>
bw device-approval deny-all --organizationid <id>
```

## Send Commands (Bitwarden Send)

### send create

```bash
# Text send
bw send -n "Name" -d <days> --hidden "Content"

# File send
bw send -n "Name" -d <days> -f /path/to/file
```

**Options:**
- `-n, --name` - Send name
- `-d, --deleteInDays` - Deletion after N days
- `--hidden` - Hide text by default
- `-f, --file` - File to send
- `--password` - Password protection

### receive

```bash
bw receive <url> [--password <pw>]
```

## Enums

### Two-step login methods

| Name | Value |
|------|-------|
| Authenticator | 0 |
| Email | 1 |
| YubiKey | 3 |

*FIDO2 and Duo not supported in CLI*

### Item types

| Name | Value |
|------|-------|
| Login | 1 |
| Secure Note | 2 |
| Card | 3 |
| Identity | 4 |

### URI match detection

| Name | Value |
|------|-------|
| Domain | 0 |
| Host | 1 |
| Starts With | 2 |
| Exact | 3 |
| Regular Expression | 4 |
| Never | 5 |

### Field types

| Name | Value |
|------|-------|
| Text | 0 |
| Hidden | 1 |
| Boolean | 2 |

### Organization user types

| Name | Value |
|------|-------|
| Owner | 0 |
| Admin | 1 |
| User | 2 |
| Manager | 3 |
| Custom | 4 |

### Organization user statuses

| Name | Value |
|------|-------|
| Invited | 0 |
| Accepted | 1 |
| Confirmed | 2 |
| Revoked | -1 |
