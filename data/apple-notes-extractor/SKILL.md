---
name: apple-notes
description: Extract and monitor Apple Notes content for workflow integration. Supports bulk extraction, real-time monitoring, and export to various formats.
metadata: {"openclaw": {"requires": {"bins": ["python3", "osascript"]}, "emoji": "📝"}}
---

# Apple Notes Skill

Extract and monitor Apple Notes content for workflow integration with support for bulk extraction, real-time monitoring, and export to various formats.

## Prerequisites

- macOS with Apple Notes app
- Python 3.8+ (for coordination scripts)
- osascript (built-in macOS)
- Proper macOS permissions for Notes access

## Installation

```bash
# Run the installation script
./scripts/setup.sh

# Or manual setup
chmod +x scripts/*.py
pip3 install -r requirements.txt
```

## Commands

### Extract Notes

```bash
# Basic extraction (all notes)
python3 scripts/extract-notes.py --method simple

# Full extraction with attachments
python3 scripts/extract-notes.py --method full

# Extract specific folder
python3 scripts/extract-notes.py --folder "Work Notes"

# Output to specific format
python3 scripts/extract-notes.py --format markdown --output ~/notes
```

### Monitor Notes

```bash
# Start monitoring daemon
python3 scripts/monitor-notes.py --daemon

# Single check for changes
python3 scripts/monitor-notes.py --check-once

# Monitor with custom interval (seconds)
python3 scripts/monitor-notes.py --interval 30
```

### Processing and Export

```bash
# Process extracted notes
python3 scripts/notes-processor.py output/raw -o output/processed

# Export to Obsidian
python3 scripts/export-obsidian.py --vault ~/MyVault

# Generate knowledge graph
python3 scripts/knowledge-graph.py --input output/processed
```

## Configuration

Edit `configs/extractor.json` for:
- Output formats (JSON, Markdown, HTML)
- Privacy filters
- Folder selection
- Processing options

Edit `configs/monitor.json` for:
- Monitoring intervals
- Change detection settings
- Auto-processing rules

## Features

- ✅ Extract text content from all notes
- ✅ Handle embedded images and attachments  
- ✅ Process note metadata (dates, folders)
- ✅ Multiple output formats (JSON, Markdown, SQLite)
- ✅ Real-time monitoring for changes
- ✅ Privacy-first design with local processing
- ✅ Integration with knowledge management tools
- ✅ Automatic deduplication
- ✅ Incremental updates

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `json` | Structured data with metadata | API integration |
| `markdown` | Human-readable text files | Documentation |
| `sqlite` | Database format | Searchable archive |
| `obsidian` | Obsidian vault format | Knowledge management |

## Examples

```bash
# Quick start - extract all notes to Markdown
python3 scripts/extract-notes.py --format markdown --output ~/extracted-notes

# Monitor and auto-export to Obsidian
python3 scripts/monitor-notes.py --daemon --auto-export obsidian

# Extract work notes with full content
python3 scripts/extract-notes.py --method full --folder "Work Notes" --format json

# Process and create knowledge graph
python3 scripts/extract-notes.py --method full
python3 scripts/notes-processor.py output/raw -o output/processed
python3 scripts/knowledge-graph.py --input output/processed --output knowledge-graph.json
```

## Security & Privacy

- All processing happens locally on your machine
- No data sent to external services  
- Respects macOS security permissions
- Configurable privacy filters for sensitive content
- Optional encryption for exported data

## Integration

Compatible with:
- Obsidian (direct vault export)
- Logseq (Markdown export)
- Notion (JSON import)
- Custom workflows (JSON/CSV output)
- AI processing pipelines
- Search engines (full-text indexing)

## Troubleshooting

Common issues:
- **Permission denied**: Grant Notes access in System Preferences → Security & Privacy
- **Import errors**: Ensure Python 3.8+ and required packages installed
- **AppleScript errors**: Check if Notes app is running and accessible
- **Empty output**: Verify folder names and note permissions

See README.md for detailed troubleshooting guide.