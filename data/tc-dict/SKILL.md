---
name: openclaw-tc-dict-skill
description: Query Traditional Chinese dictionaries from Ministry of Education (MOE) Taiwan. Supports looking up word definitions from the "國語辭典簡編本" (Concised Mandarin Dictionary) with automatic version management and optional periodic updates. Use when you need to look up Chinese word meanings, check definitions, or ensure you have the latest dictionary data.
---

# OpenClaw Traditional Chinese Dictionary Skill

## Installation

This skill requires Python dependencies. Install them with `uv`:

```bash
# Install dependencies (recommended: use uv for faster installation)
uv pip install -r requirements.txt

# Alternative: use pip if uv is not available
pip install -r requirements.txt
```

**Required packages:**
- `pandas>=2.0.0` — Data processing
- `openpyxl>=3.1.0` — Excel file reading

## Security

This skill implements the following security measures:

✅ **TLS Certificate Verification** — All HTTPS connections to MOE servers use proper SSL/TLS certificate validation (no disabled verification)

✅ **Zip-Slip Protection** — Dictionary downloads validate all zip file paths before extraction to prevent directory traversal attacks (path validation applied)

✅ **Safe File Handling** — Extracted files are validated and stored in user-isolated directory (`~/.openclaw/dictionaries/`)

⚠️ **Cron/Automatic Updates** — If you enable automatic updates via cron, the skill will download dictionary files from MOE on your specified schedule. Consider the frequency and enable notifications to track changes.

## Overview

This skill enables you to query Traditional Chinese dictionaries published by Taiwan's Ministry of Education. It provides:

- **Word lookup** — Search for word definitions with automatic fuzzy matching
- **Dictionary management** — Download, extract, and version-control dictionary data
- **Update automation** — Automatic periodic checks (cron) + manual update requests
- **Extensible design** — Currently supports "國語辭典簡編本" (Concised Dictionary), with room for other MOE dictionaries in the future

## Core Capabilities

### 1. Query Words

Users can look up words using natural language like:
- "請告訴我『蒼鷺』的意思" (Tell me the meaning of '蒼鷺')
- "查『梅雨』" (Look up '梅雨')
- "『破曉』是什麼意思？" (What does '破曉' mean?)

The skill returns the primary definition first. If the user asks for details, provide:
- Full definition
- Examples/usage
- Related information from the dictionary

**Implementation**: See `query_dictionary.py` for the search logic.

### 2. Manage Dictionary Updates

Users can trigger updates in two ways:

**Manual update:**
- "更新字典" (Update dictionary)
- "重新下載國語辭典" (Re-download the dictionary)

**Automatic update (cron):**
- Set up a cron job to check for updates monthly
- Compare local version (stored in metadata.json) against MOE's latest version
- Download and extract only if a newer version exists

**Implementation**: See `download_dictionary.py` for download/extraction logic and `check_updates.py` for version management.

## Configuration

The skill respects a configuration file at `~/.openclaw/dictionaries/config.json`:

```json
{
  "storage_path": "~/.openclaw/dictionaries",
  "auto_update_interval_days": 30,
  "dictionaries": {
    "concised": {
      "enabled": true,
      "name": "國語辭典簡編本",
      "source": "https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html"
    }
  }
}
```

Users can customize `storage_path` to store dictionaries elsewhere. The default is `~/.openclaw/dictionaries/`.

## Usage Examples

### Example 1: Simple word lookup
```
User: "請告訴我『藍寶石』的意思"
Response: 藍寶石：寶石名。紅玉髓的一種。（如需詳細資料，請告訴我）
```

### Example 2: Request with details
```
User: "『藍寶石』是什麼意思？告訴我更多"
Response: 藍寶石：寶石名。紅玉髓的一種。
例句：...
相關詞語：...
```

### Example 3: Manual update
```
User: "更新字典"
Response: 正在檢查最新版本...
當前版本：2025-12-29
最新版本：[Latest from MOE]
[如果有更新] 已更新字典至最新版本 (2025-12-29)
[如果無更新] 字典已是最新版本
```

## Bundled Resources

### scripts/
- `download_dictionary.py` — Download zip from MOE, extract, parse xlsx, store locally
- `query_dictionary.py` — Search dictionary data, return definitions and optional details
- `check_updates.py` — Query MOE website for version info, compare with local metadata

See [DICTIONARY_SOURCES.md](references/DICTIONARY_SOURCES.md) for data source URLs and version tracking.

### references/
- `DICTIONARY_SOURCES.md` — All MOE dictionary sources, update URLs, version history
- `SCHEMA.md` — xlsx structure documentation (columns, formats, data layout)

For setting up cron jobs to monitor updates, reference the `scripts/check_updates.py` documentation.
