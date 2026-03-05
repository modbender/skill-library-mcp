---
name: managing-apple-notes
description: "Manage Apple Notes from the terminal using the inotes CLI. Use when asked to list, read, create, edit, delete, or search notes in Notes.app on macOS."
homepage: https://github.com/wangwalk/inotes
url: https://github.com/wangwalk/inotes
emoji: 📝
metadata:
  clawdbot:
    os: ["darwin"]
    requires:
      bins: ["inotes"]
    install:
      - "brew install wangwalk/tap/inotes"
    cliHelp: |
      inotes --version
      inotes status
---

# Managing Apple Notes with inotes

`inotes` is a macOS CLI for Apple Notes. It communicates with Notes.app via AppleScript and supports all CRUD operations plus search. Output defaults to a human-readable table; use `--json` for machine-readable output.

## 🔒 Privacy & Security

- ✅ **Open source**: Full source code at https://github.com/wangwalk/inotes
- ✅ **Local-only**: All operations run locally via AppleScript; no data leaves your machine
- ✅ **No network calls**: `inotes` does not connect to any remote servers
- ✅ **Auditable install**: Binary installed via Homebrew from signed release or GitHub Releases
- ✅ **MIT Licensed**: Free and open for inspection and contributions
- ⚠️ **Requires macOS Automation permission** for Notes.app (user grants via System Settings)
- 📦 **Universal binary**: Supports both Apple Silicon (arm64) and Intel (x86_64)

## Prerequisites

**System Requirements:**
- macOS 14+ (Sonoma or later)
- Apple Notes.app (comes with macOS)

**Install via Homebrew (recommended):**

```bash
brew install wangwalk/tap/inotes
```

**Verify installation:**

```bash
inotes --version  # Should show: 0.1.2
which inotes      # Should be in /opt/homebrew/bin/ or /usr/local/bin/
```

**Manual installation from GitHub Releases:**

Download from [GitHub Releases](https://github.com/wangwalk/inotes/releases) and verify SHA256:

```bash
curl -LO https://github.com/wangwalk/inotes/releases/download/v0.1.2/inotes-0.1.2-universal-apple-darwin.tar.gz
# Verify checksum from release notes
tar xzf inotes-0.1.2-universal-apple-darwin.tar.gz
sudo cp inotes /usr/local/bin/
sudo chmod +x /usr/local/bin/inotes
```

**Check permission:**

```bash
inotes status
```

If permission is denied, the user must enable Automation access for their terminal in **System Settings > Privacy & Security > Automation > Notes**.

## Commands

### List notes

```bash
inotes                            # recent iCloud notes (default)
inotes today                      # modified today
inotes show week                  # modified this week
inotes show all                   # all notes
inotes show --folder Work         # notes in a specific folder
inotes show recent --limit 10    # limit results
```

### List folders

```bash
inotes folders
```

### List accounts

```bash
inotes accounts
```

### Create a folder

```bash
inotes mkfolder "Projects"
inotes mkfolder "Work Notes" --account Exchange
```

### Read a note

```bash
inotes read 1        # by index from last show output
inotes read A3F2     # by ID prefix (4+ characters)
```

### Create a note

```bash
inotes add --title "Meeting Notes" --body "Action items" --folder Work
```

### Edit a note

```bash
inotes edit 1 --title "Updated Title"
inotes edit 2 --body "New content" --folder Projects
```

### Delete a note

```bash
inotes delete 1              # with confirmation
inotes delete 1 --force      # skip confirmation
```

### Search notes

```bash
inotes search "quarterly review"
inotes search "TODO" --folder Work --limit 10
```

## Multi-account support

By default only iCloud notes are shown. Use `--account <name>` or `--all-accounts` to access other accounts.

```bash
inotes accounts                    # list available accounts
inotes show all --account Exchange
inotes show all --all-accounts
```

## Output formats

| Flag | Description |
|------|-------------|
| *(default)* | Human-readable table |
| `--json` / `-j` | JSON |
| `--plain` | Tab-separated |
| `--quiet` / `-q` | Count only |

## Agent usage guidelines

- Always use `--json` when you need to parse output programmatically.
- Use `--no-input` to disable interactive prompts in non-interactive contexts.
- Use `--no-color` when capturing output to avoid ANSI escape sequences.
- Identify notes by **index** (from the last `show` output) or by **ID prefix** (first 4+ hex characters of the note ID).
- Run `inotes status` first to verify automation permission before attempting other commands.
- The CLI automatically filters out notes in "Recently Deleted" folders across all supported languages.

## Examples for common tasks

**Create daily note:**
```bash
inotes add --title "Daily Notes $(date +%Y-%m-%d)" --body "## TODO\n\n## Done\n"
```

**Export all notes to JSON:**
```bash
inotes show all --json > notes-backup.json
```

**Find notes with specific tag:**
```bash
inotes search "#important" --json | jq '.[] | select(.folder == "Work")'
```

**Archive completed notes:**
```bash
inotes search "DONE" --folder Inbox --json | jq -r '.[].id' | while read id; do
  inotes edit "$id" --folder Archive
done
```

## Troubleshooting

**"Automation permission denied"**
- Go to System Settings > Privacy & Security > Automation
- Find your terminal app (e.g., Terminal.app, iTerm.app)
- Enable access to "Notes"

**"Command not found"**
- Run `which inotes` to check if it's in your PATH
- If using Homebrew: `brew doctor` and check for warnings
- Try `brew reinstall wangwalk/tap/inotes`

**"Note not found" when using index**
- Run `inotes show` again to get fresh indices
- Use ID prefix instead: `inotes read A3F2`

**Performance issues with many notes**
- Use `--limit` flag to reduce result set
- Filter by folder: `--folder "Work"`
- Use date filters: `today`, `week`, `recent`

## Additional resources

- **GitHub**: https://github.com/wangwalk/inotes
- **Releases**: https://github.com/wangwalk/inotes/releases
- **Issues**: https://github.com/wangwalk/inotes/issues
- **License**: MIT
