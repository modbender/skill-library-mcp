---
name: google-keep
description: Read, create, edit, search, and manage Google Keep notes and lists via CLI.
metadata:
  openclaw:
    requires:
      bins: ["python3", "uv"]
    install:
      - id: venv
        kind: shell
        command: "cd \"$SKILL_DIR\" && uv venv .venv && .venv/bin/pip install gkeepapi gpsoauth"
        label: "Create venv and install gkeepapi + gpsoauth"
---

# Google Keep CLI Skill

Manage Google Keep notes and lists from the command line using the unofficial gkeepapi.

## Setup

After installing, the CLI lives in the skill directory. Set up a convenience alias or wrapper:

```bash
SKILL_DIR="<path-to-this-skill>"  # e.g. skills/google-keep
alias gkeep="$SKILL_DIR/.venv/bin/python3 $SKILL_DIR/gkeep.py"
```

Or create a global wrapper:

```bash
cat > ~/.local/bin/gkeep << 'EOF'
#!/bin/bash
SKILL_DIR="$(dirname "$(readlink -f "$0")")/../.openclaw/workspace/skills/google-keep"
exec "$SKILL_DIR/.venv/bin/python3" "$SKILL_DIR/gkeep.py" "$@"
EOF
chmod +x ~/.local/bin/gkeep
```

## Authentication

### First-time setup (OAuth token exchange):

1. Go to https://accounts.google.com/EmbeddedSetup in your browser
2. Log in with your Google account
3. Click "I agree" on the consent screen (page may spin forever — ignore it)
4. Open DevTools: F12 → Application tab → Cookies → accounts.google.com
5. Copy the value of the `oauth_token` cookie
6. Run:

```bash
gkeep auth <email> <oauth_token>
```

### With pre-obtained master token:

```bash
gkeep auth-master <email> <master_token>
```

Credentials are stored in `<skill-dir>/.config/` (chmod 600). The master token has full account access — treat it like a password. It does **not expire** (unlike standard OAuth refresh tokens).

## Commands

### List notes

```bash
gkeep list                    # Active notes
gkeep list --archived         # Include archived
gkeep list --pinned           # Pinned only
gkeep list --label "Shopping" # Filter by label
gkeep list --json             # JSON output
gkeep list -v                 # Show IDs
```

### Search

```bash
gkeep search "grocery"
gkeep search "todo" --json
```

### Get a specific note

```bash
gkeep get <note-id>
gkeep get "Shopping List"     # By title (case-insensitive)
gkeep get <id> --json
```

### Create notes

```bash
gkeep create --title "Ideas" --text "Some thoughts"
gkeep create --title "Groceries" --list --items "Milk" "Eggs" "Bread"
gkeep create --title "Important" --pin --color Red --label "Work"
```

### Edit notes

```bash
gkeep edit <id-or-title> --title "New Title"
gkeep edit <id-or-title> --text "Updated text"
gkeep edit <id-or-title> --pin true
gkeep edit <id-or-title> --archive true
gkeep edit <id-or-title> --color Blue
```

### List operations

```bash
gkeep check "Groceries" "milk"           # Check off an item
gkeep check "Groceries" "milk" --uncheck # Uncheck
gkeep check "Groceries" "m" --all        # Check all matching
gkeep add-item "Groceries" "Butter" "Cheese"  # Add items
```

### Delete (trash)

```bash
gkeep delete <id-or-title>
```

### Labels

```bash
gkeep labels              # List all labels
gkeep labels --json
```

### Export / backup

```bash
gkeep dump                # All notes as JSON
gkeep dump > backup.json
```

## Colors

Valid colors: White, Red, Orange, Yellow, Green, Teal, Blue, DarkBlue, Purple, Pink, Brown, Gray

## How it works

- Uses [gkeepapi](https://github.com/kiwiz/gkeepapi) (1,600+ stars, actively maintained) — an unofficial reverse-engineered Google Keep client
- Auth via [gpsoauth](https://github.com/simon-weber/gpsoauth) — Google Play Services OAuth flow to obtain a master token
- State is cached locally (`.config/state.json`) for fast startup after the initial sync
- Master tokens don't expire, so no re-auth dance
- **Unofficial API** — Google could break compatibility at any time (but gkeepapi has been stable for years)

## Security notes

- The master token grants **full access** to the associated Google account
- Credentials are stored with 600 permissions in `.config/`
- Never commit `.config/` to version control
- `delete` moves notes to trash (recoverable) — it does not permanently delete
