---
name: foam-notes
description: Work with Foam note repositories. Create, edit, link, and tag notes. Get intelligent wikilink and tag suggestions. Skill supports backlinks discovery, daily notes, templates, graph visualization, note deletion, and renaming. Full Foam documentation included for easy querying.
---

# Foam Notes

Work with Foam note-taking workspaces in VS Code. [Foam](https://foamnotes.com) is a free, open-source personal knowledge management system using standard Markdown files with wikilinks.

## Quick Reference

- **Wikilinks**: `[[note-name]]` — connect notes bidirectionally
- **Embeds**: `![[note-name]]` — include content from other notes
- **Backlinks**: Automatically discovered connections to current note
- **Tags**: `#tag` or frontmatter `tags: [tag1, tag2]`
- **Daily Notes**: `Alt+D` or command "Foam: Open Daily Note"

## Configuration

Copy `config.json.template` to `config.json` and edit to taste:

```json
{
  "foam_root": "/path/to/your/foam-workspace",
  "default_template": "new-note",
  "default_notes_folder": "notes",
  "daily_note_folder": "journals",
  "author": "Your Name",
  "wikilinks": {
    "title_stopwords": ["home", "index", "readme", "draft", "template"],
    "suffixes": ["-hub"],
    "min_length": 3
  },
  "tags": {
    "editorial_stopwords": ["notes", "note", "foam", "markdown", "file", "page", "section"]
  }
}
```

**Location**: `config.json` in the skill directory (next to `SKILL.md`).

### Config keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `foam_root` | string | `""` (auto-detect) | Path to your Foam workspace |
| `default_template` | string | `"new-note"` | Template for new notes |
| `default_notes_folder` | string | `"notes"` | Subfolder for new notes |
| `daily_note_folder` | string | `"journals"` | Subfolder for daily notes |
| `author` | string | `""` | Author name for note creation |
| `wikilinks.title_stopwords` | list | `[]` | Note titles to never match as wikilinks (e.g. `"home"`, `"index"`, `"todo"`). Add any generic filenames from your workspace that produce false positives. |
| `wikilinks.suffixes` | list | `[]` | Filename suffixes whose base stem should also register as a match key. For example, if you name your hub/MOC notes `docker-hub.md`, add `"-hub"` here so that "docker" in prose matches `docker-hub.md`. |
| `wikilinks.min_length` | int | `3` | Minimum key length to consider for wikilink matching |
| `tags.editorial_stopwords` | list | `[]` | Domain-specific words to exclude from tag suggestions (in addition to standard English stopwords). |

### Foam root priority order (highest to lowest)

1. `--foam-root` CLI argument
2. `FOAM_WORKSPACE` environment variable
3. `foam_root` in config.json
4. Auto-detect by finding `.foam` or `.vscode` directory
5. Current working directory

See references/configuration.md for complete documentation.

## Scripts

All scripts support `--foam-root` to override the workspace path.

### init_templates.py

Initialize `.foam/templates/` with starter templates from the official Foam template:

```bash
python3 scripts/init_templates.py              # Copy to current workspace
python3 scripts/init_templates.py --foam-root ~/notes
python3 scripts/init_templates.py --list      # Show available templates
python3 scripts/init_templates.py --force     # Overwrite existing
python3 scripts/init_templates.py --dry-run   # Preview what would be copied
```

**Templates included:**
- `new-note.md` — Default template for new notes
- `daily-note.md` — Template for daily notes
- `your-first-template.md` — Example template demonstrating VS Code snippets

### create_note.py

Create a new note from template:

```bash
python3 scripts/create_note.py "My New Idea"
python3 scripts/create_note.py "Meeting Notes" --template meeting
python3 scripts/create_note.py "Research Topic" --dir research/
```

### find_backlinks.py

Find all notes that link to a given note:

```bash
python3 scripts/find_backlinks.py "Machine Learning"
python3 scripts/find_backlinks.py "ml-basics" --format json
```

### search_tags.py

Find notes by tag:

```bash
python3 scripts/search_tags.py "#research"
python3 scripts/search_tags.py machine-learning --include-frontmatter
```

### list_tags.py

List all tags with usage counts:

```bash
python3 scripts/list_tags.py
python3 scripts/list_tags.py --hierarchy --min-count 3
```

### graph_summary.py

Analyze the knowledge graph:

```bash
python3 scripts/graph_summary.py
python3 scripts/graph_summary.py --format json
```

### daily_note.py

Create daily notes:

```bash
python3 scripts/daily_note.py
python3 scripts/daily_note.py --yesterday
python3 scripts/daily_note.py --template custom-daily
python3 scripts/daily_note.py --print-path   # Just output the path
```

### suggest_wikilinks.py

Suggest wikilinks by finding text in a note that matches existing note titles:

```bash
python3 scripts/suggest_wikilinks.py my-note.md              # Interactive mode
python3 scripts/suggest_wikilinks.py my-note.md --apply 1,3,5  # Auto-apply
python3 scripts/suggest_wikilinks.py my-note.md --auto-apply   # Apply all
python3 scripts/suggest_wikilinks.py my-note.md --dry-run      # Preview only
python3 scripts/suggest_wikilinks.py my-note.md --with-aliases # Create [[target|text]] format
```

The script scans the note content and identifies words/phrases that match existing note titles in the archive. It presents them as a numbered list:

```
1. Line 12, col 8
   Text: "machine learning"
   Link to: [[machine-learning]]
   Context: ...working on machine learning projects...
```

**Wikilink formats:**
- **Default**: `[[target]]` — clean, simple links
- **With `--with-aliases`**: `[[target|display text]]` — preserves original text as alias

Respond with:
- Numbers to implement (e.g., `1 3 5`)
- `all` to apply all suggestions
- `none` to cancel

### suggest_tags.py

Suggest tags for a note based on content and existing tags in the archive:

```bash
python3 scripts/suggest_tags.py my-note.md              # Interactive mode
python3 scripts/suggest_tags.py my-note.md --apply all  # Add all suggested
python3 scripts/suggest_tags.py my-note.md --apply existing  # Only existing tags
python3 scripts/suggest_tags.py my-note.md --frontmatter     # Add to frontmatter
```

The script:
1. Extracts keywords from note content
2. Finds matching existing tags (with usage counts)
3. Suggests new tags based on content analysis

Presented as numbered list with two sections:
- **Existing Tags** — Already used in your archive
- **New Suggestions** — Extracted from current note content

Respond with:
- Numbers (e.g., `1 3 5`)
- `all` — all suggestions
- `existing` — only existing tags
- `new` — only new suggestions
- `none` — cancel
- Or type custom tags: `#mytag #project`

### delete_note.py

Delete notes with optional backup and automatic backlink handling:

```bash
python3 scripts/delete_note.py "Old Note"                    # Interactive deletion
python3 scripts/delete_note.py "Old Note" --force          # Skip confirmation
python3 scripts/delete_note.py "Old Note" --backup         # Move to .foam/trash/
python3 scripts/delete_note.py "Old Note" --fix-links      # Remove wikilinks from other notes
```

**Features:**
- **Backup mode**: Moves note to `.foam/trash/` instead of permanent deletion
- **Backlink detection**: Shows which notes link to the one being deleted
- **Link fixing**: Automatically removes wikilinks from other notes
- **Confirmation**: Prompts before deletion (skip with `--force`)

### rename_note.py

Rename notes and automatically update all wikilinks:

```bash
python3 scripts/rename_note.py "Old Name" "New Name"       # Interactive rename
python3 scripts/rename_note.py "Old Name" "New Name" --force  # Skip confirmation
```

**Features:**
- **Automatic wikilink updates**: Finds and updates all `[[old-name]]` references
- **File rename**: Changes filename from `old-name.md` to `new-name.md`
- **Title preservation**: Keeps note content intact, only updates links
- **Confirmation**: Shows affected notes before proceeding

## When to Use This Skill

Use this skill when:
- Creating or editing notes in a Foam workspace
- Working with wikilinks, backlinks, or the knowledge graph
- Analyzing note relationships and connections
- Setting up or configuring Foam templates
- Working with daily notes or tags
- Publishing Foam workspaces to static sites

## Foam Workspace Structure

```
foam-workspace/
├── .vscode/
│   ├── extensions.json      # Recommended extensions
│   └── settings.json        # VS Code settings
├── .foam/
│   └── templates/           # Note templates (.md and .js)
├── journals/                # Daily notes (default location)
├── attachments/             # Images and files
├── *.md                     # Your notes
└── foam.json (optional)     # Foam configuration
```

## Core Concepts

### Wikilinks

Create connections between notes using double brackets:

```markdown
See also [[related-concept]] for more information.
```

- Autocomplete with `[[` + type note name
- Navigate with `Ctrl+Click` (or `Cmd+Click` on Mac)
- Create new notes by clicking non-existent links
- Link to sections: `[[note-name#Section Title]]`

See references/wikilinks.md for complete documentation.

### Backlinks

Backlinks show which notes reference the current note — discovered automatically by Foam.

Access via:
- Command palette: "Explorer: Focus on Connections"
- Shows forward links, backlinks, or both

Use backlinks for:
- Finding unexpected connections between ideas
- Identifying hub concepts (notes with many backlinks)
- Building context around ideas across domains

See references/backlinks.md for complete documentation.

### Tags

Organize notes beyond wikilinks:

```markdown
# Inline tags
#machine-learning #research #in-progress

# Frontmatter tags
---
tags: [machine-learning, research, in-progress]
---
```

- Hierarchical: `#programming/python`
- Browse in Tag Explorer panel
- Search: "Foam: Search Tag"

See references/tags.md for complete documentation.

### Daily Notes

Quick daily journaling:

- **Shortcut**: `Alt+D`
- **Command**: "Foam: Open Daily Note"
- **Snippets**: `/today`, `/yesterday`, `/tomorrow`

Template: `.foam/templates/daily-note.md`

See references/daily-notes.md for complete documentation.

### Templates

Customize note creation. Foam looks for templates in `.foam/templates/`.

**To initialize starter templates:**

```bash
python3 scripts/init_templates.py
```

This copies official Foam templates to your workspace:
- `new-note.md` — Default template
- `daily-note.md` — Daily notes template
- `your-first-template.md` — Example with VS Code snippets

**Markdown templates** (`.md`):
```markdown
---
foam_template:
  filepath: '$FOAM_CURRENT_DIR/$FOAM_SLUG.md'
---

# $FOAM_TITLE

Created: $FOAM_DATE_YEAR-$FOAM_DATE_MONTH-$FOAM_DATE_DATE

$FOAM_SELECTED_TEXT
```

**JavaScript templates** (`.js`) — for smart, context-aware templates.

See references/templates.md for complete documentation.

## Common Tasks

### Creating a New Note

When creating notes programmatically (not via VS Code), always read the workspace template in `.foam/templates/new-note.md` first and follow its structure exactly.

In VS Code:
1. Use "Foam: Create New Note" for default template
2. Use "Foam: Create New Note From Template" to choose template
3. Or click a non-existent wikilink `[[new-note]]`

### Finding Note Relationships

1. **Backlinks**: Check Connections panel for linked notes
2. **Graph View**: Command "Foam: Show Graph" for visual network
3. **Tag Explorer**: Browse notes by tag

### Working with Embeds

Include content from other notes:

```markdown
![[glossary]]

See the full definition above.
```

### Publishing

Foam can publish to static sites:
- GitHub Pages (built-in template)
- Netlify
- Vercel
- GitLab Pages
- Custom static site generators (Gatsby, MkDocs, etc.)

See recipes in Foam documentation for publishing options.

## Foam vs Obsidian

| Feature | Foam | Obsidian |
|---------|------|----------|
| Wikilinks | `[[note]]` | `[[note]]` |
| Embeds | `![[note]]` | `![[note]]` |
| Platform | VS Code | Dedicated app |
| Plugin ecosystem | Minimal (VS Code extensions) | Extensive |
| File format | Standard Markdown | Markdown with extensions |
| Configuration | `.vscode/settings.json` | `.obsidian/` folder |
| Price | Free | Freemium |

Both use the same core linking syntax. Foam prioritizes simplicity and standard formats.

## Configuration

Key `.vscode/settings.json` options:

```json
{
  "foam.openDailyNote.onStartup": true,
  "foam.dateSnippets.format": "yyyy-mm-dd",
  "markdown.styles": [".foam/css/custom.css"]
}
```

## Foam CLI Commands

Key VS Code commands:

- `Foam: Open Daily Note` — Create/open today's note
- `Foam: Create New Note` — Create from default template
- `Foam: Create New Note From Template` — Choose template
- `Foam: Create New Template` — Create new template
- `Foam: Show Graph` — Visualize knowledge graph
- `Foam: Search Tag` — Search for tagged notes
- `Explorer: Focus on Connections` — Show backlinks panel

## Reference Documentation

- **foam-overview.md** — General Foam introduction and philosophy
- **wikilinks.md** — Complete wikilinks guide
- **backlinks.md** — Backlinks and knowledge discovery
- **tags.md** — Tag organization and filtering
- **daily-notes.md** — Daily note workflows
- **templates.md** — Template creation (Markdown and JavaScript)

Read these files for detailed information on specific features.

## External Resources

- **Official site**: https://foamnotes.com
- **GitHub**: https://github.com/foambubble/foam
- **Discord**: https://foambubble.github.io/join-discord/w

## Tips

1. **Start small**: Foam works best with consistent note-taking habits
2. **Link liberally**: Create wikilinks even to non-existent notes (placeholders)
3. **Use the graph**: Visualize your knowledge network to find gaps
4. **Trust the process**: Backlinks reveal connections you didn't plan
5. **Keep it standard**: Foam uses standard Markdown — your notes remain portable
