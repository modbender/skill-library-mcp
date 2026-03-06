---
name: kb-collector
description: Knowledge Base Collector - save YouTube, URLs, text to Obsidian with AI summarization. Auto-transcribes videos, fetches pages, supports weekly/monthly digest emails.
---

# KB Collector

Knowledge Base Collector - Save YouTube, URLs, and text to Obsidian with automatic transcription and summarization.

## Features

- **YouTube Collection** - Download audio, transcribe with Whisper, auto-summarize
- **URL Collection** - Fetch and summarize web pages
- **Plain Text** - Direct save with tags
- **Digest** - Weekly/Monthly/Yearly review emails

## Installation

```bash
# Install dependencies
pip install yt-dlp faster-whisper requests beautifulsoup4

# For AI summarization (optional)
pip install openai anthropic
```

## Usage (Python Version - Recommended)

```bash
# Collect YouTube video
python3 scripts/collect.py youtube "https://youtu.be/xxxxx" "stock,investing"

# Collect URL
python3 scripts/collect.py url "https://example.com/article" "python,api"

# Collect plain text
python3 scripts/collect.py text "My note content" "tag1,tag2"
```

## Usage (Bash Version - Legacy)

```bash
# Collect YouTube
./scripts/collect.sh "https://youtu.be/xxxxx" "stock,investing" youtube

# Collect URL
./scripts/collect.sh "https://example.com/article" "python,api" url

# Collect text
./scripts/collect.sh "My note" "tag1,tag2" text
```

## Configuration

Edit the script to customize:

```python
VAULT_PATH = os.path.expanduser("~/Documents/YourVault")
NOTE_AUTHOR = "YourName"
```

## Output Format

Notes saved to: `{VAULT_PATH}/yyyy-mm-dd-title.md`

```markdown
---
created: 2026-03-03T12:00:00
source: https://...
tags: [stock, investing]
author: George
---

# Title

> **TLDR:** Summary here...

---

Content...

---
*Saved: 2026-03-03*
```

## Dependencies

- yt-dlp
- faster-whisper (for transcription)
- requests + beautifulsoup4 (for URL fetching)
- Optional: openai/anthropic (for AI summarization)

## Credits

Automated note-taking workflow for Obsidian.
