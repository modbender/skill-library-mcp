# Apple Notes Extraction System - Usage Guide

## Quick Start

### 1. Initial Setup
```bash
cd apple-notes-extractor
./scripts/setup.sh
```

This will:
- Check system requirements
- Create directory structure  
- Set up default configurations
- Test basic Apple Notes access

### 2. Grant Permissions

macOS may prompt you to grant permissions:

1. **System Preferences → Security & Privacy → Privacy → Automation**
2. Enable your terminal app to control "Notes"
3. If prompted, also allow access to "System Events"

### 3. Basic Extraction

```bash
# Simple text extraction (fast)
python3 scripts/extract-notes.py --method simple

# Full extraction with attachments (slower, requires Ruby setup)
python3 scripts/extract-notes.py --method full

# Automatic method selection
python3 scripts/extract-notes.py --method auto
```

### 4. View Results

Extracted content is saved to:
- `output/json/` - Structured JSON data
- `output/markdown/` - Human-readable markdown files
- `output/index.json` - Master index of all extractions

## Advanced Usage

### Automated Monitoring

Monitor your notes for changes and automatically extract new content:

```bash
# Run one-time check
python3 scripts/monitor-notes.py --check-once

# Start background monitoring daemon
python3 scripts/monitor-notes.py --daemon
```

### Workflow Integration

Process extracted notes for various downstream uses:

```bash
# Export to multiple formats
python3 scripts/workflow-integrator.py

# Dry run to see what would happen
python3 scripts/workflow-integrator.py --dry-run

# Export specific workflow only
python3 scripts/workflow-integrator.py --workflow markdown
```

### Custom Configuration

Edit configuration files in `configs/`:

- `extractor.json` - Extraction settings and privacy filters
- `monitor.json` - Monitoring intervals and triggers  
- `workflows.json` - Export formats and destinations

## Example Workflows

### Export to Obsidian

1. Edit `configs/workflows.json`:
```json
{
  "workflows": {
    "obsidian": {
      "enabled": true,
      "vault_path": "/path/to/your/obsidian/vault",
      "subfolder": "Apple Notes"
    }
  }
}
```

2. Run the workflow:
```bash
python3 scripts/workflow-integrator.py --workflow obsidian
```

### Daily Automated Export

1. Extract notes: 
```bash
python3 scripts/extract-notes.py --method auto
```

2. Process for workflows:
```bash
python3 scripts/workflow-integrator.py
```

3. Automate with cron:
```bash
# Add to crontab for daily export at 9 AM
0 9 * * * cd /path/to/apple-notes-extractor && python3 scripts/extract-notes.py --method auto && python3 scripts/workflow-integrator.py
```

### Selective Export

Use privacy filters to exclude sensitive notes:

Edit `configs/extractor.json`:
```json
{
  "privacy": {
    "exclude_patterns": ["password", "secret", "private", "confidential"],
    "encrypt_sensitive": false
  }
}
```

## Troubleshooting

### Permission Issues

If you get "operation not permitted" errors:

1. Check **System Preferences → Security & Privacy → Privacy → Full Disk Access**
2. Add your terminal app or Python executable
3. Restart your terminal

### Notes App Not Responding

1. Quit and restart the Notes app
2. Try: `osascript -e 'tell application "Notes" to get name'`
3. Check if Notes is syncing (wait for sync to complete)

### Ruby Parser Installation Failed

For full extraction with attachments:

1. Install Homebrew: `curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash`
2. Install Ruby: `brew install ruby`
3. Install bundler: `gem install bundler`
4. Re-run: `python3 scripts/extract-notes.py --method full`

### Empty or Missing Notes

1. Verify Notes app has content: Open Notes.app manually
2. Check account settings: Make sure iCloud/local notes are synced
3. Try simple extraction first: `--method simple`

## Testing Your Setup

Run the comprehensive test suite:

```bash
python3 scripts/test-system.py
```

This will verify:
- System requirements
- Apple Notes access
- Extraction functionality
- Configuration validity
- Workflow integration

## Output Formats

### JSON Structure
```json
[
  {
    "id": "abc123...",
    "title": "My Note",
    "body": "Note content here...",
    "created": "2024-01-15 10:30:00",
    "modified": "2024-01-15 11:45:00",
    "folder": "Personal",
    "account": "iCloud",
    "extraction_method": "simple",
    "extraction_date": "2024-01-15T12:00:00",
    "attachments": []
  }
]
```

### Markdown Structure
```markdown
# Apple Notes Export - Simple Method

Extracted on: 2024-01-15T12:00:00
Total notes: 42

---

## My Note

- **Created:** 2024-01-15 10:30:00
- **Modified:** 2024-01-15 11:45:00
- **Folder:** Personal
- **Account:** iCloud

Note content here...

---
```

## Privacy & Security

- All processing happens locally on your machine
- No data is sent to external services
- Configurable exclusion patterns for sensitive content
- Optional encryption for extracted data

## Integration with Existing Workflows

The system integrates well with:

- **Note-taking apps**: Obsidian, Notion, Roam Research
- **Documentation systems**: GitBook, MkDocs, Sphinx
- **Search engines**: Elasticsearch, Algolia
- **AI processing**: GPT analysis, sentiment analysis
- **Backup systems**: Version control, cloud storage

## Performance

- **Simple extraction**: ~1-5 seconds for 100 notes
- **Full extraction**: ~30-300 seconds depending on attachments
- **Memory usage**: ~50-200MB for typical note collections
- **Storage**: JSON ~1-5MB per 1000 notes