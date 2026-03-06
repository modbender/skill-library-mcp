---
name: gworkspace-cli
description: >
  Interact with Google Workspace (Drive, Docs, Sheets) via the `gw` CLI.
  Use when an agent needs to browse, read, create, search, or manage files
  in Google Drive, read or write Google Docs, or read/write Google Sheets —
  all from the terminal. Works with both My Drive and Shared Drives.
required_binaries:
  - gw
required_env:
  - name: GOOGLE_CLIENT_ID
    description: Google OAuth client ID (optional — embedded credentials used by default)
    required: false
  - name: GOOGLE_CLIENT_SECRET
    description: Google OAuth client secret (optional — embedded credentials used by default)
    required: false
  - name: GW_CLIENT_ID
    description: Alias for GOOGLE_CLIENT_ID
    required: false
  - name: GW_CLIENT_SECRET
    description: Alias for GOOGLE_CLIENT_SECRET
    required: false
config_paths:
  - ~/.11x/gworkspace/token.json
  - ~/.11x/gworkspace/config.json
install: npm i -g @11x.agency/gworkspace
source: https://github.com/robinfaraj/gworkspace-cli
---

# gworkspace-cli

Manage Google Drive, Docs, and Sheets from the terminal with `gw`.

## Do This First

- Ensure `gw` is installed: `npm i -g @11x.agency/gworkspace`
- Ensure authenticated: run `gw auth --status`. If not authenticated, run `gw auth`.
- If targeting a Shared Drive, get the drive ID first: `gw drive shared`

## Authentication

```bash
gw auth                 # Opens browser for Google sign-in
gw auth --status        # Check current auth (email, scopes, expiry)
gw logout               # Remove stored credentials
```

Token stored at `~/.11x/gworkspace/token.json`. OAuth credentials via env vars or `.env` file:
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `GW_CLIENT_ID` / `GW_CLIENT_SECRET` (aliases)

## Commands

### Drive

```bash
# List files
gw drive ls                              # Root of My Drive
gw drive ls /Projects                    # By path
gw drive ls --folder <id>               # By folder ID
gw drive ls --type doc                  # Filter: doc, sheet, folder, all
gw drive ls --limit 50                  # Pagination

# Create folder
gw drive mkdir "Folder Name"
gw drive mkdir "Subfolder" --folder <parent-id>

# Search
gw drive search "quarterly report"
gw drive search "budget" --type sheet

# Upload
gw drive upload ./file.pdf
gw drive upload ./data.csv --folder <id> --name "Q4 Data"

# List Shared Drives
gw drive shared
```

### Shared Drives

Use the global `--drive <id>` flag before any subcommand:

```bash
gw --drive <shared-drive-id> drive ls
gw --drive <shared-drive-id> drive ls /Projects
gw --drive <shared-drive-id> drive mkdir "New Folder"
gw --drive <shared-drive-id> drive search "report"
gw --drive <shared-drive-id> drive upload ./file.pdf
```

To create docs/sheets in a Shared Drive, use `--folder` with a Shared Drive folder ID:

```bash
gw doc create "Title" --folder <shared-drive-folder-id>
gw sheet create "Title" --folder <shared-drive-folder-id>
```

### Docs

```bash
gw doc read <id|url>                    # Plain text output
gw doc read <id|url> --markdown         # Markdown output
gw doc create "Title"                   # Create empty doc, returns ID + URL
gw doc create "Title" --folder <id>     # Create in specific folder
gw doc append <id|url> "text"           # Append text to end of doc
gw doc append <id|url> --file ./notes.txt  # Append from file
```

### Sheets

```bash
gw sheet read <id|url>                  # Read entire first sheet (JSON rows)
gw sheet read <id|url> "Sheet1!A1:C10"  # Read specific range
gw sheet write <id|url> "A1:B2" '[["Name","Score"],["Alice","95"]]'
gw sheet write <id|url> "A1" --file ./data.csv
gw sheet append <id|url> '[["Bob","88"]]'
gw sheet append <id|url> --file ./more.csv
gw sheet create "Title"                 # Create spreadsheet
gw sheet create "Title" --folder <id>
gw sheet list <id|url>                  # List tabs/sheets
```

## Output Modes

All commands support three output modes:

| Flag       | Output                     | Use case           |
|------------|----------------------------|--------------------|
| *(default)* | JSON                       | Piping, scripting  |
| `--pretty` | Human-readable table       | Terminal viewing    |
| `--quiet`  | IDs only, one per line     | Chaining commands  |

## I/O Contract

- **stdout**: Data output (JSON, table, or IDs)
- **stderr**: Errors, status messages, progress
- **Exit 0**: Success
- **Exit 1**: Any error (auth, not found, permission, network)

## URLs and IDs

All commands accept either format — paste a full Google URL or just the ID:

```bash
gw doc read https://docs.google.com/document/d/1abc.../edit
gw doc read 1abc...
```

## Error Messages

| Condition              | Message                                                    |
|------------------------|------------------------------------------------------------|
| No token               | `Error: Not authenticated. Run 'gw auth' to get started.` |
| Token expired          | `Error: Session expired. Run 'gw auth' to re-authenticate.` |
| File not found         | `Error: File not found.`                                   |
| Permission denied      | `Error: No access to this file. Make sure it's shared with your account.` |
| Network error          | `Error: Could not reach Google APIs. Check your connection.` |

## Common Agent Workflows

### Browse a Shared Drive and read a doc

```bash
gw drive shared --quiet                          # Get drive IDs
gw --drive <id> drive ls --pretty                # Browse root
gw --drive <id> drive ls --folder <folder-id>    # Drill into folder
gw doc read <doc-id>                             # Read the doc
```

### Create a doc with content in a specific folder

```bash
gw drive mkdir "Project X"                       # Create folder, get ID
gw doc create "Requirements" --folder <id>       # Create doc, get ID
gw doc append <doc-id> "# Requirements\n\n..."   # Write content
```

### Export sheet data for processing

```bash
gw sheet read <id> --quiet > data.tsv            # Tab-separated to file
gw sheet read <id> "Sheet1!A1:D100" | jq '.'     # JSON for processing
```

### Upload and organize files

```bash
gw drive mkdir "Reports" --folder <parent-id>
gw drive upload ./q4-report.pdf --folder <new-folder-id> --name "Q4 Report 2026"
```
