# Dropbox KB Auto

## What problem does this solve?

You have years of documents, receipts, research papers, and notes in Dropbox — but your AI agent can't search any of them. Finding a specific file means opening Dropbox and digging through folders manually.

This skill connects Dropbox to your agent's knowledge base. It syncs your files, extracts text (including OCR for scans and photos), and indexes everything so you can ask natural-language questions like *"Find my Q1 2025 expense receipts"* and get answers instantly.

## How It Works

```
        ┌─────────────────────┐
        │   Dropbox (files)   │
        │  PDFs, Office, Imgs │
        └────────┬────────────┘
                 │  Delta API (only changes)
                 ▼
        ┌─────────────────────┐
        │   Text Extraction   │
        │                     │
        │  PDF → pypdf / OCR  │
        │  DOCX → python-docx │
        │  XLSX → openpyxl    │
        │  PPTX → python-pptx │
        │  IMG → Tesseract    │
        │  TXT → UTF-8 read   │
        └────────┬────────────┘
                 │  Saves as .md files
                 ▼
        ┌─────────────────────┐
        │  OpenClaw Memory    │
        │                     │
        │  Embeddings + Index │
        │  Semantic + keyword │
        │  hybrid search      │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  Ask your agent:    │
        │  "Find my Q1 2025   │
        │   expense receipts" │
        └─────────────────────┘
```

## Features

- **Delta sync with content hashing** - Only processes new/changed files via Dropbox cursor API and content hashes (unchanged files are never re-downloaded or re-processed)
- **Multi-format extraction** - PDF, Word, Excel, PowerPoint, images, plain text
- **OCR** - Reads scanned documents and photos via Tesseract
- **Interactive installer** - Configures folders, exclusions, cron schedule in one command
- **Production-tested** - Handles 650K+ file Dropboxes with rate limiting and retries

## Requirements

- OpenClaw installed and running
- Dropbox account with API access ([create app](https://www.dropbox.com/developers/apps))
- Linux or macOS (tested on Ubuntu 24.04, macOS 14+)

## Installation

```bash
# Via ClawHub (recommended)
clawhub install dropbox-kb-auto

# Or manually
cd ~/.openclaw/workspace/skills
git clone https://github.com/ferreirafabio/dropbox-kb-auto.git
```

Then run the interactive setup:
```bash
cd ~/.openclaw/workspace/skills/dropbox-kb-auto
./install.sh
```

The installer walks you through folder selection, exclusion patterns, file types, Dropbox API credentials, and cron scheduling.

## Manual Setup

### 1. Dropbox App

1. Go to https://www.dropbox.com/developers/apps
2. Create app → **Scoped access** → **Full Dropbox**
3. Enable permissions: `files.metadata.read`, `files.content.read`
4. Generate a refresh token via OAuth 2 flow

### 2. Credentials

Add to `~/.openclaw/.env`:
```bash
DROPBOX_FULL_APP_KEY=your_app_key
DROPBOX_FULL_APP_SECRET=your_app_secret
DROPBOX_FULL_REFRESH_TOKEN=your_refresh_token
```

### 3. Config

Edit `config.json`:
```json
{
  "folders": ["/Documents", "/Work"],
  "skip_paths": ["/Archive", "/Backups"],
  "file_types": ["pdf", "docx", "xlsx", "pptx", "jpg", "png", "txt"],
  "max_file_size_mb": 20
}
```

### 4. Run

```bash
python3 dropbox-sync.py
```

First run: 5-10 min (builds delta cursors). Subsequent runs: <10 seconds.

### 5. Schedule (optional)

```bash
openclaw cron create \
  --name "Dropbox KB Sync" \
  --cron "0 */6 * * *" \
  --tz "America/New_York" \
  --timeout-seconds 14400 \
  --session isolated \
  --message "cd ~/.openclaw/workspace/skills/dropbox-kb-auto && python3 dropbox-sync.py"
```

## Performance

Tested on 650,000 files (1,840 indexable):

| Metric | First Run | Incremental |
|--------|-----------|-------------|
| Time | ~15 min | <30 sec |
| Files processed | 1,840 | 5-20 (avg) |
| Disk usage | ~45 MB | +100 KB |

## Supported File Types

| Type | Extensions | Method |
|------|-----------|--------|
| PDF | `.pdf` | pypdf + OCR fallback |
| Word | `.docx`, `.doc` | python-docx |
| Excel | `.xlsx`, `.xls` | openpyxl (5 sheets, 100 rows) |
| PowerPoint | `.pptx`, `.ppt` | python-pptx (30 slides) |
| Images | `.jpg`, `.png` | Tesseract OCR |
| Text | `.txt`, `.md`, `.csv`, `.json` | UTF-8 |

## Troubleshooting

**Missing Python packages:**
```bash
pip3 install pypdf openpyxl python-pptx python-docx
```

**Tesseract not found:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng  # add language packs as needed
```

**Timeout on large Dropboxes (500K+ files):**
```bash
openclaw cron edit <job-id> --timeout-seconds 28800
```

## Security

- Read-only Dropbox access recommended
- All extraction runs locally on your machine
- No data leaves your Dropbox / local knowledge base
- Credentials stored in `~/.openclaw/.env` (gitignored)

## File Structure

```
dropbox-kb-auto/
├── dropbox-sync.py    # Delta-based indexer
├── config.json        # Folder/type configuration
├── install.sh         # Interactive setup
├── setup.sh           # Dependency installer
├── SKILL.md           # OpenClaw skill manifest
├── .env.example       # Credential template
└── LICENSE            # MIT
```

## Contributing

Issues and PRs welcome: https://github.com/ferreirafabio/dropbox-kb-auto

## License

MIT
