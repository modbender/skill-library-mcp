---
name: discogs-cli
description: An OpenClaw skill to manage a user's vinyl record collection on Discogs.
metadata: {"clawdbot":{"emoji":"Vinyl","requires":{"bins":["go"]}}}
---

# Discogs Collection Manager Skill for OpenClaw

This skill provides a command-line interface to interact with a user's record collection on Discogs.com. It is designed specifically for use within the OpenClaw assistant and uses a subcommand structure similar to `git` or `gog`.

## Prerequisites

This skill is a Go program and requires the Go toolchain to be installed.

**Installation (Debian/Ubuntu):**
`sudo apt-get update && sudo apt-get install -y golang-go`

## One-Time Setup

Before first use, you must run the included installer script. This will compile the Go binary and place it in a predictable location within the skill's directory.

1.  **Run the installer:**
    ```bash
    skills/discogs-cli/install.sh
    ```

2.  **Configure Credentials:**
    This command saves your Discogs token and username to a configuration file (`~/.config/discogs-cli/config.yaml`).
    ```bash
    skills/discogs-cli/bin/discogs-cli config set -u "YourUsername" -t "YourSecretToken"
    ```

## Usage

All commands must be prefixed with the full path to the binary.

### Fetch Album Art

Downloads the album art for a given release and displays it in the chat.

```bash
skills/discogs-cli/bin/discogs-cli release art <release_id>
```

### List Collection Folders

Shows all folders and their record counts.

```bash
skills/discogs-cli/bin/discogs-cli collection list-folders
```

### List Releases in a Folder

Shows all records within a specific folder. The output is a formatted table.

```bash
# List all releases from the "All" folder (default)
skills/discogs-cli/bin/discogs-cli collection list

# List all releases from a specific folder by ID
skills/discogs-cli/bin/discogs-cli collection list --folder 8815833
```

## Search the Discogs Database

Search for releases, artists, or labels.

```bash
# Search for a release (default type)
skills/discogs-cli/bin/discogs-cli search "Daft Punk - Discovery"

# Search for an artist
skills/discogs-cli/bin/discogs-cli search --type artist "Aphex Twin"
```

## Manage Your Wantlist

Work with your Discogs wantlist.

### List Your Wantlist

Displays all items in your wantlist.

```bash
skills/discogs-cli/bin/discogs-cli wantlist list
```

### Add to Your Wantlist

Adds a release to your wantlist by its ID.

```bash
skills/discogs-cli/bin/discogs-cli wantlist add 12345
```

### Remove from Your Wantlist

Removes a release from your wantlist by its ID.

```bash
skills/discogs-cli/bin/discogs-cli wantlist remove 12345
```

## Caching and Valuation Commands

These commands rely on a local cache for performance. You must run `sync` first to populate the cache.

### Sync Collection Details (Slow)

Fetches detailed data for every item in the collection and builds a local cache. This command is slow and should be run in the background. Inform the user that this will take time.

```bash
skills/discogs-cli/bin/discogs-cli collection sync
```

### Get Collection Value (Fast)

Reads the local cache to provide the estimated market value for each item and the total collection. This command is fast. If it fails, the cache is likely missing, and you need to run the `sync` command.

```bash
skills/discogs-cli/bin/discogs-cli collection value
```

### Get Single Release Details (Fast)

Provides a detailed view of a single release, including tracklist.

```bash
skills/discogs-cli/bin/discogs-cli collection get 35198584
```
