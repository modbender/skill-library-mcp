# Joplin API Reference

Complete API endpoints and command reference. Official docs: https://joplinapp.org/help/api/references/rest_api/

---

## API Endpoints

### Basic
- `GET /ping` - Test service availability
- `GET /search?query=KEYWORD` - Search notes

### Notes
- `GET /notes` - Get all notes
- `GET /notes/:id` - Get single note
- `POST /notes` - Create note
- `PUT /notes/:id` - Update note
- `DELETE /notes/:id` - Delete note

### Folders (Notebooks)
- `GET /folders` - Get all notebooks
- `GET /folders/:id` - Get single notebook
- `GET /folders/:id/notes` - Get notes in notebook
- `POST /folders` - Create notebook
- `PUT /folders/:id` - Update notebook
- `DELETE /folders/:id` - Delete notebook

### Tags
- `GET /tags` - Get all tags
- `POST /tags` - Create tag
- `DELETE /tags/:id` - Delete tag
- `POST /tags/:id/notes/:note_id` - Add tag to note
- `DELETE /tags/:id/notes/:note_id` - Remove tag from note

---

## Commands

### Query

```bash
# Test connection
python3 joplin.py ping

# Statistics
python3 joplin.py stats

# Recent notes
python3 joplin.py recent --limit 5

# List
python3 joplin.py list --type notes|folders|tags --limit 10

# Notes in notebook
python3 joplin.py folder-notes --folder "Work"

# Search
python3 joplin.py search "keyword" --type note|folder|tag

# Get note details
python3 joplin.py get --id <note_id>
```

### Edit

```bash
# Create
python3 joplin.py create --title "Title" --body "Content" --folder "Notebook"

# Update
python3 joplin.py update --id <id> --title "New Title" --body "New Content"

# Move
python3 joplin.py move --note-id <id> --to-folder <folder_id|name>

# Delete
python3 joplin.py delete --id <id> [--permanent]
```

### Notebook Management

```bash
python3 joplin.py folders list
python3 joplin.py folders create --name "Name"
python3 joplin.py folders rename --id <id> --name "New Name"
python3 joplin.py folders delete --id <id> [--permanent]
```

### Tag Management

```bash
python3 joplin.py tags list
python3 joplin.py tags create --name "tag-name"
python3 joplin.py tags add --note-id <id> --tag "tag-name"
python3 joplin.py tags remove --note-id <id> --tag-id <tag_id>
python3 joplin.py tags delete --id <tag_id>
```

### Import/Export

```bash
# Export
python3 joplin.py export --note-id <id> -o output.md
python3 joplin.py export --all -o ./backup

# Import
python3 joplin.py import file.md --folder "Notebook"
python3 joplin.py import ./notes_dir --folder "Batch Import"
```

---

## Security Restrictions

### Path Validation
- Import: Only reads from `JOPLIN_IMPORT_DIR`
- Export: Only writes to `JOPLIN_EXPORT_DIR`
- Default: `/root/.openclaw/workspace`

### Blocked Directories
`/etc`, `/proc`, `/sys`, `/dev`, `/boot`, `/usr`, `/bin`, `/sbin`, `/var/log`, `/var/spool`, `/home`

### Custom Directories
```bash
JOPLIN_IMPORT_DIR=/path/to/safe/dir
JOPLIN_EXPORT_DIR=/path/to/safe/dir
```

---

## Troubleshooting

### Cannot Connect
1. Check if Joplin is running
2. Verify Web Clipper is enabled
3. Check `JOPLIN_BASE_URL` is correct

### Authentication Failed
- Check `JOPLIN_TOKEN` is correct
- Regenerate token in Joplin settings

### Permission Issues
```bash
chmod +x scripts/*.py
```

---

## Resources

- Official API: https://joplinapp.org/help/api/references/rest_api/
- Search Syntax: https://joplinapp.org/help/apps/search
- Plugin API: https://joplinapp.org/help/api/