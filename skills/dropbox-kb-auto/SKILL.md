# Dropbox KB Auto

## What problem does this solve?

Your AI agent can't search your Dropbox. Documents, receipts, research papers, and notes sit in folders your agent doesn't know about — so you end up searching manually.

This skill bridges that gap: it syncs files from Dropbox, extracts text (PDF, Office, OCR for scans), and indexes everything into your agent's knowledge base. Changed files are detected via content hashing and automatically re-indexed. Unchanged files are never re-processed.

One-command installer configures folders, exclusions, file types, cron scheduling, and OpenClaw memory integration.

## What This Skill Does

```
    ┌───────────────────┐
    │  Dropbox Account  │
    └────────┬──────────┘
             │ Delta API (only changes)
             ▼
    ┌───────────────────┐
    │  Text Extraction  │
    │  PDF, Office, OCR │
    └────────┬──────────┘
             │ Markdown files
             ▼
    ┌───────────────────┐
    │  OpenClaw Memory  │
    │  Embed + Search   │
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────┐
    │  Agent answers    │
    │  your questions   │
    └───────────────────┘
```

Supported formats: PDF (with OCR fallback), Word, Excel, PowerPoint, images (Tesseract OCR), plain text.

## Prerequisites

### System Dependencies
```bash
# Debian/Ubuntu
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils

# macOS
brew install tesseract poppler
```

### Python Dependencies
```bash
pip3 install pypdf openpyxl python-pptx python-docx
```

Or run: `bash setup.sh`

### Dropbox App Setup

1. Create app at https://www.dropbox.com/developers/apps
2. Choose **Scoped access** → **Full Dropbox**
3. Enable: `files.metadata.read`, `files.content.read`
4. Generate refresh token via OAuth 2 flow
5. Add to `~/.openclaw/.env`:
   ```bash
   DROPBOX_FULL_APP_KEY=your_app_key
   DROPBOX_FULL_APP_SECRET=your_app_secret
   DROPBOX_FULL_REFRESH_TOKEN=your_refresh_token
   ```

## Installation

### Via ClawHub
```bash
clawhub install dropbox-kb-auto
```

### Manual
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/ferreirafabio/dropbox-kb-auto.git
```

## Configuration

Edit `config.json`:
```json
{
  "folders": ["/Documents", "/Work"],
  "skip_paths": ["/Archive", "/Backups"],
  "file_types": ["pdf", "docx", "xlsx", "pptx", "jpg", "png", "txt"],
  "max_file_size_mb": 20
}
```

## Usage

### Interactive Setup (recommended)
```bash
./install.sh
```

### Manual Sync
```bash
python3 dropbox-sync.py
```
First run: 5-10 min. Incremental runs: <10 sec.

### Automated via Cron
```bash
openclaw cron create \
  --name "Dropbox KB Sync" \
  --cron "0 */6 * * *" \
  --timeout-seconds 14400 \
  --session isolated \
  --message "cd ~/.openclaw/workspace/skills/dropbox-kb-auto && python3 dropbox-sync.py"
```

### Query Examples
Once indexed, ask your agent:
- "Find presentations about machine learning"
- "Search for expense receipts from Q1 2025"
- "What do my project notes say about deployment?"

## Performance

Tested on 650K files (1,840 indexable): first sync ~15 min, incremental <30 sec.

## Security

- Read-only Dropbox access recommended
- All extraction runs locally
- Credentials stored in `~/.openclaw/.env` (gitignored)

## License

MIT

## Author

Fabio Ferreira ([@ferreirafabio](https://github.com/ferreirafabio))
