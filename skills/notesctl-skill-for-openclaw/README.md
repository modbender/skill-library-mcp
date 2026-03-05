# notesctl (Apple Notes skill)

A small, deterministic Apple Notes helper skill for OpenClaw.

It wraps Apple Notes operations in scripts so the agent can reliably create/search/export notes without fragile quoting or UI automation.

Why: this was built to replace the original OpenClaw Apple Notes skill, which can occasionally create a note titled "New Notes" and can be token-expensive; notesctl keeps the system logic deterministic and minimizes LLM usage (ideally a single call to produce the final output).

## Requirements (macOS)

- `python3`
- `osascript`
- `memo` (CLI used by the scripts)

## What’s inside

- `SKILL.md` — the skill metadata + concise operating instructions
- `scripts/`
  - `notes_new.sh` — create a new note with title/body/folder
  - `notes_post.sh` — create a new note via JSON stdin (recommended for automation)
  - `notes_list.sh` — list notes in a folder
  - `notes_search.sh` — search notes (optionally within a folder)
  - `notes_export.sh` — interactively select a matching note and export it to a directory

## Usage

### 1) Create a new note (recommended: JSON stdin)

```bash
baseDir=/path/to/notesctl

echo '{"title":"标题","body":"第一行\n第二行","folder":"Notes"}' \
  | "$baseDir/scripts/notes_post.sh"
```

### 2) Create a new note (direct args)

```bash
baseDir=/path/to/notesctl

"$baseDir/scripts/notes_new.sh" \
  "标题" \
  $'正文第一行\n正文第二行' \
  "Notes"
```

### 3) List notes in a folder

```bash
baseDir=/path/to/notesctl

"$baseDir/scripts/notes_list.sh" "Notes"
```

### 4) Search notes

```bash
baseDir=/path/to/notesctl

# search all folders
"$baseDir/scripts/notes_search.sh" "keyword"

# search within a specific folder
"$baseDir/scripts/notes_search.sh" "keyword" "Notes"
```

### 5) Export a note

This is interactive: it searches, then prompts you to choose which note to export.

```bash
baseDir=/path/to/notesctl

"$baseDir/scripts/notes_export.sh" "keyword" "Notes" "/tmp"
```

## Notes / gotchas

- Editing existing notes is intentionally not the default workflow (fragile). Prefer append workflows or creating a new note.
- If you do need manual editing, use `memo notes -e` (interactive selection + editor).

## License

Internal / personal use (adjust as needed).
