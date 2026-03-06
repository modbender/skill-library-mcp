---
name: zoho-mail
description: Read, search, send, and manage Zoho Mail from the terminal. JSON
  output for scripting and agents. Requires the 'zoho' binary (install via
  brew/uv/pipx), one-time OAuth setup (zoho config init; zoho login), and stores
  credentials locally (config file and OS keyring). Optional env ZOHO_ACCOUNT,
  ZOHO_CONFIG, ZOHO_TOKEN_PASSWORD. No third-party service required.
---


# zoho — Zoho Mail CLI

**Requirements:** the `zoho` binary (install via brew/uv/pipx below), one-time OAuth setup, and local credential storage (config + OS keyring).

`zoho` is a command-line tool for Zoho Mail. All output is **JSON by default** — structured, pipe-friendly, and agent-ready. Use `--md` for markdown tables.

## Install

**Requires Python 3.11+. Works on macOS, Linux, and Windows.**

```bash
# Homebrew (macOS / Linux)
brew install robsannaa/tap/zoho-cli

# uv (all platforms)
uv tool install git+https://github.com/robsannaa/zoho-cli

# pipx (all platforms)
pipx install git+https://github.com/robsannaa/zoho-cli
```

After install, run the one-time setup:

```bash
zoho config init   # save your Zoho OAuth client_id / client_secret
zoho login         # open browser, region auto-detected
```

See the full setup guide in the [README](https://github.com/robsannaa/zoho-cli#setup).

---

## Prerequisites

- `zoho` must be installed and authenticated (`zoho login` completed).
- Check: `zoho config show` — must return a JSON object with `default_account` and a non-empty `accounts` map.
- If not logged in: tell the user to follow the setup in the README.

## Output

- **stdout** → JSON (default) or Markdown (`--md`). Always machine-readable.
- **stderr** → errors (as JSON), debug logs, interactive prompts. Never in stdout.
- **Exit 0** = success. **Exit 1** = error (JSON error object on stderr).

```bash
# errors land on stderr, not stdout
zoho mail list 2>/dev/null          # stdout empty on error
zoho mail list 2>&1 >/dev/null      # see error JSON
```

## Authentication

Tokens are stored in the OS keyring and refreshed automatically before every command. No manual token management needed.

**Credential storage (sensitive):** Users must be aware that the CLI stores sensitive data locally:
- **OAuth client_id and client_secret** — saved via `zoho config init` in the config file (e.g. `~/.config/zoho-cli/config.json`).
- **Access and refresh tokens** — stored in the OS keyring (or, if `ZOHO_TOKEN_PASSWORD` is set, in an encrypted file). These are used to access Zoho Mail on the user's behalf.

Do not expose config files or keyring entries to untrusted parties.

If a command fails with `not_logged_in` or `token_refresh_failed`, tell the user to run:
```bash
zoho login
```

## Global flags

```
--account EMAIL    select account (env: ZOHO_ACCOUNT)
--config PATH      config file path (env: ZOHO_CONFIG)
--md               markdown table output instead of JSON
--debug            HTTP + debug logs to stderr
```

---

## Commands

### `zoho mail list`

List messages in a folder.

```bash
zoho mail list                               # Inbox, 50 messages
zoho mail list --folder Sent --limit 20
zoho mail list -f "My Project" -n 100
```

**Output** — array of message summaries:
```json
[
  {
    "messageId": "1771333290108014300",
    "folderId": "8072279000000002014",
    "subject": "Q1 invoice",
    "from": "billing@acme.com",
    "to": ["you@example.com"],
    "date": "1740067200000",
    "unread": true,
    "hasAttachments": true,
    "tags": []
  }
]
```

`date` is a Unix timestamp in **milliseconds**.

### `zoho mail search`

```bash
zoho mail search "invoice 2025"
zoho mail search "from:boss@example.com" --limit 10
```

Same output shape as `mail list`.

### `zoho mail get`

Full message content including body.

```bash
zoho mail get MESSAGE_ID
zoho mail get MESSAGE_ID --folder-id FOLDER_ID    # faster: skips auto-scan
zoho mail get MESSAGE_ID | jq '.textBody'
```

**Output:**
```json
{
  "messageId": "...",
  "folderId": "...",
  "subject": "Q1 invoice",
  "from": "billing@acme.com",
  "to": ["you@example.com"],
  "cc": [],
  "bcc": [],
  "date": "1740067200000",
  "unread": false,
  "hasAttachments": true,
  "tags": [],
  "textBody": "Please find the invoice attached.",
  "htmlBody": "<p>Please find...</p>"
}
```

### `zoho mail attachments`

```bash
zoho mail attachments MESSAGE_ID
zoho mail attachments MESSAGE_ID --folder-id FOLDER_ID
```

**Output:**
```json
[
  { "attachmentId": "256063600000020001", "fileName": "invoice.pdf", "size": 123456 }
]
```

### `zoho mail download-attachment`

```bash
zoho mail download-attachment MESSAGE_ID ATTACHMENT_ID --out /tmp/invoice.pdf
```

**Output:**
```json
{ "status": "ok", "path": "/tmp/invoice.pdf", "size": 123456 }
```

### `zoho mail send`

```bash
zoho mail send --to alice@example.com --subject "Hi" --text "Hello!"

# HTML + multiple recipients + attachments
zoho mail send \
  --to alice@example.com --to bob@example.com \
  --cc manager@example.com \
  --subject "Report" \
  --html-file report.html \
  --attach report.pdf --attach data.csv
```

**Output:**
```json
{ "status": "ok", "messageId": "..." }
```

### Flag / move / delete operations

All accept one or more `MESSAGE_ID` arguments.

```bash
zoho mail mark-read   ID [ID …]
zoho mail mark-unread ID [ID …]
zoho mail move        ID [ID …] --to "Archive"
zoho mail spam        ID [ID …]
zoho mail not-spam    ID [ID …]
zoho mail archive     ID [ID …]
zoho mail unarchive   ID [ID …]
zoho mail delete      ID [ID …]              # → Trash
zoho mail delete      ID [ID …] --permanent  # hard delete
```

**Output:**
```json
{ "status": "ok", "updated": ["ID1", "ID2"], "failed": [] }
```

### `zoho folders list`

```bash
zoho folders list
```

**Output:**
```json
[
  { "folderId": "8072279000000002014", "folderName": "Inbox", "folderType": "Inbox",
    "path": "/Inbox", "isArchived": 0, "unreadCount": 3, "messageCount": 42 }
]
```

### `zoho folders create / rename / delete`

```bash
zoho folders create "Project X" [--parent-id FOLDER_ID]
zoho folders rename FOLDER_ID "New Name"
zoho folders delete FOLDER_ID
```

### `zoho config show / path / init`

```bash
zoho config show     # JSON config dump (secret redacted)
zoho config path     # {"config_path": "...", "exists": true}
zoho config init     # interactive wizard (prompts on stderr)
```

---

## Common patterns for agents

```bash
# All unread message subjects
zoho mail list | jq -r '.[] | select(.unread) | .subject'

# Get the latest message ID
zoho mail list -n 1 | jq -r '.[0].messageId'

# Get plain-text body of a specific message
zoho mail get "$MSG_ID" | jq -r '.textBody'

# Download all attachments from a message
zoho mail attachments "$MSG_ID" | jq -r '.[].attachmentId' | while read id; do
  zoho mail download-attachment "$MSG_ID" "$id" --out "/tmp/${id}"
done

# Find unread emails from a sender
zoho mail search "from:boss@example.com" | jq '[.[] | select(.unread)]'

# Mark all results as read
zoho mail search "invoice" | jq -r '.[].messageId' | xargs zoho mail mark-read

# Move search results to a folder
zoho mail search "newsletter" | jq -r '.[].messageId' | xargs zoho mail move --to "Archive"

# Send with computed body
zoho mail send \
  --to report-reader@example.com \
  --subject "Daily digest $(date +%F)" \
  --text "$(zoho mail list | jq -r '.[].subject' | head -10 | nl)"
```

## Error response shape

All errors are JSON on stderr:

```json
{
  "status": "error",
  "error": "not_logged_in",
  "details": "No stored token for you@example.com. Run: zoho login --account you@example.com"
}
```

Common error codes:

| Code | Meaning |
|---|---|
| `not_logged_in` | No token stored — user must run `zoho login` |
| `token_refresh_failed` | Token revoked — user must run `zoho login` |
| `no_account_id` | accountId not saved — run `zoho login` again |
| `folder_not_found` | Folder name doesn't match any folder |
| `message_not_found` | Message ID not found in any folder |
| `api_error` | Upstream Zoho API error (details in message) |
