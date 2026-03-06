# Apple Notes Automatic Extraction System

A comprehensive system for extracting and processing Apple Notes content for workflow integration.

## Overview

This system provides multiple extraction methods to handle different types of Apple Notes content:

1. **AppleScript/JXA Method** - Fast extraction for simple text notes
2. **Apple Cloud Notes Parser** - Complete extraction including attachments, tables, and embedded media
3. **Hybrid Approach** - Intelligent selection based on note complexity
4. **Real-time Monitoring** - Automated extraction of new/modified notes

## Features

- ✅ Extract text content from all notes
- ✅ Handle embedded images and attachments
- ✅ Process note metadata (creation date, modification date, folders)
- ✅ Support for different output formats (JSON, Markdown, SQLite)
- ✅ Integration with existing workflows
- ✅ Automatic deduplication and incremental updates
- ✅ Privacy-first design with local processing

## System Architecture

```
apple-notes-extractor/
├── scripts/           # Core extraction scripts
├── tools/            # External tools and dependencies
├── output/           # Extracted content storage
├── configs/          # Configuration files
└── workflows/        # Integration workflows
```

## Quick Start

1. **Initial Setup**: `./scripts/setup.sh`
2. **Basic Extraction**: `./scripts/extract-notes.py --method simple`
3. **Full Extraction**: `./scripts/extract-notes.py --method full`
4. **Monitor Mode**: `./scripts/monitor-notes.py --daemon`

## Security & Privacy

- All processing happens locally on your machine
- No data is sent to external services
- Respects macOS security permissions
- Optional encryption for sensitive notes

## Integration

The system integrates with:
- File-based workflows (Markdown, JSON output)
- Database systems (SQLite export)
- Search engines (full-text indexing)
- Note-taking apps (import/sync)
- AI processing pipelines

## Dependencies

- macOS with Apple Notes app
- Python 3.8+ (for coordination scripts)
- Ruby 3.0+ (for complex extraction)
- osascript (built-in macOS)

## Configuration

See `configs/` directory for:
- Extraction preferences
- Output formats
- Workflow integrations
- Privacy settings