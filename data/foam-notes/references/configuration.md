# Foam Notes Configuration

The foam-notes skill can be configured via `config.json` in the skill directory.

## Config Location

`~/.openclaw/workspace/skills/foam-notes/config.json`

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `foam_root` | string | `""` | Path to your Foam workspace root. If empty, auto-detects by looking for `.foam` or `.vscode` directories. |
| `default_template` | string | `""` | Default template name for new notes (e.g., `"new-note"`). |
| `default_notes_folder` | string | `""` | Default folder for new notes (e.g., `"notes"`, `"pages"`). Empty means create in `foam_root`. |
| `daily_note_folder` | string | `"journals"` | Subdirectory for daily notes, relative to `foam_root`. |

## Example Config

```json
{
  "foam_root": "/home/thomas/foam-notes",
  "default_template": "new-note",
  "default_notes_folder": "notes",
  "daily_note_folder": "journals"
}
```

With this config:
- `create_note.py "My Idea"` → creates in `/home/thomas/foam-notes/notes/`
- `daily_note.py` → creates in `/home/thomas/foam-notes/journals/`

## Folder Structure Example

Many users organize with separate folders:

```
foam-workspace/
├── journals/          # Daily notes (daily_note_folder)
├── notes/             # Regular notes (default_notes_folder)
├── literature-notes/  # Reference notes
└── .foam/
    └── templates/
```

## Environment Variables

Config options can be overridden via environment variable:

- `FOAM_WORKSPACE` — sets `foam_root`

## How Scripts Find Your Foam Workspace

Scripts use this priority order:

1. `--foam-root` CLI argument (highest priority)
2. `FOAM_WORKSPACE` environment variable
3. `foam_root` in config.json
4. Auto-detect by looking for `.foam` or `.vscode` directories
5. Current working directory (fallback)

## Multiple Foam Workspaces

If you have multiple Foam workspaces:

- Use the `--foam-root` argument: `python3 create_note.py "Title" --foam-root ~/work-notes`
- Or set `FOAM_WORKSPACE` environment variable per session
- Keep config.json empty (or set your most-used workspace as default)

## Per-Command Overrides

Even with `default_notes_folder` set, you can always override:

```bash
# Uses default_notes_folder from config
python3 create_note.py "My Idea"

# Override with --dir
python3 create_note.py "My Idea" --dir literature-notes/

# Create in root (bypass default_notes_folder)
python3 create_note.py "My Idea" --dir .
```

## Recommended Setup

1. Set `foam_root` to your primary Foam workspace
2. Set `default_notes_folder` to your preferred notes subdirectory (or leave empty for root)
3. Set `daily_note_folder` to where you keep daily notes (default: `journals`)
4. Create your preferred default template at `.foam/templates/new-note.md`
5. Run `init_templates.py` to get started with official Foam templates
