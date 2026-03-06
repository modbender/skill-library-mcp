---
name: confcli
description:
  Interact with Confluence Cloud from the command line. Use when reading,
  creating, updating, or searching Confluence pages, managing attachments,
  labels, comments, or exporting content.
---

# confcli

CLI for Confluence Cloud.

## Installation

Check if confcli is installed:

```bash
command -v confcli
```

If not installed, install via:

```bash
curl -fsSL https://raw.githubusercontent.com/hochej/confcli/main/install.sh | sh
```

To install a specific version or to a custom directory:

```bash
curl -fsSL https://raw.githubusercontent.com/hochej/confcli/main/install.sh | VERSION=0.2.3 sh
curl -fsSL https://raw.githubusercontent.com/hochej/confcli/main/install.sh | INSTALL_DIR=~/.bin sh
```

## Authentication

Check auth status first:

```bash
confcli auth status
```

If not authenticated, ask the user to configure authentication. They can either:

1. Run `confcli auth login` interactively in their own terminal, or
2. Set environment variables before starting the session:
   - `CONFLUENCE_DOMAIN` — e.g. `yourcompany.atlassian.net`
   - `CONFLUENCE_EMAIL`
   - `CONFLUENCE_TOKEN` (or `CONFLUENCE_API_TOKEN`)

API tokens are generated at
https://id.atlassian.com/manage-profile/security/api-tokens

> **Never ask the user to paste a token into the conversation.** Tokens must be
> set via environment variables or `confcli auth login`.

## Page References

Pages can be referenced by:

- ID: `12345`
- URL: `https://company.atlassian.net/wiki/spaces/MFS/pages/12345/Title`
- Space:Title: `MFS:Overview`

## Important

Write operations (create, update, delete, purge, edit, label add/remove,
attachment upload/delete, comment add/delete, copy-tree) require explicit user
intent. Never perform these based on assumptions.

Use `--dry-run` to preview destructive operations without executing them.

## Common Commands

```bash
# Spaces
confcli space list
confcli space get MFS
confcli space pages MFS --tree
confcli space create --key PROJ --name "Project" -o json --compact-json
confcli space delete MFS --yes

# Pages
confcli page list --space MFS --title "Overview"
confcli page get MFS:Overview                  # metadata (table)
confcli page get MFS:Overview --show-body      # include body in table output
confcli page get MFS:Overview -o json          # full JSON
confcli page body MFS:Overview                 # markdown content
confcli page body MFS:Overview --format storage
confcli page children MFS:Overview
confcli page children MFS:Overview --recursive
confcli page history MFS:Overview
confcli page open MFS:Overview                 # open in browser
confcli page edit MFS:Overview                 # edit in $EDITOR

# Search
confcli search "query"
confcli search "type=page AND title ~ Template"
confcli search "confluence" --space MFS

# Write
confcli page create --space MFS --title "Title" --body "<p>content</p>"
confcli page update MFS:Overview --body-file content.html
confcli page delete 12345

# Attachments
confcli attachment list MFS:Overview
confcli attachment upload MFS:Overview ./file.png ./other.pdf
confcli attachment download att12345 --dest file.png

# Labels
confcli label add MFS:Overview tag1 tag2 tag3
confcli label remove MFS:Overview tag1 tag2
confcli label pages "tag"

# Comments
confcli comment list MFS:Overview
confcli comment add MFS:Overview --body "LGTM"
confcli comment delete 123456

# Export
confcli export MFS:Overview --dest ./exports --format md

# Copy Tree
confcli copy-tree MFS:Overview MFS:TargetParent
```

## Output Formats

Use `-o` flag: `json`, `table`, `md`

```bash
confcli space list -o json
confcli page get MFS:Overview -o json
```

## Pagination

Add `--all` to fetch all results, `-n` to set limit:

```bash
confcli space list --all
confcli search "query" --all -n 100
```
