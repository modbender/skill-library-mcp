---
name: anime-meme-collector
description: Daily collection and management of anime/ACG memes and trending phrases from Chinese internet. Automatically fetches from Bilibili and other platforms to build a meme database for enhancing AI's understanding of otaku culture. Use when user wants to stay updated with anime community trends or improve AI's anime/meme knowledge.
---

# Anime Meme Collector

Automated daily collection of anime/ACG memes from Chinese internet platforms.

## Overview

Maintains an up-to-date database of:
- Bilibili trending video memes
- Bilibili hot search keywords
- Galgame terminology (Yuzusoft, Key, Type-Moon, etc.)
- Streamer/gaming culture (电棍, 山泥若, 炫狗, etc.)
- 346+ curated memes

## Quick Start

### Manual Collection

```bash
python scripts/collect_memes.py
```

### Automated Daily Updates

Set up cron job for midnight (Asia/Shanghai):

```bash
0 0 * * * cd /path/to/skill && python scripts/collect_memes.py
```

Or use OpenClaw cron:
```json
{
  "action": "add",
  "job": {
    "name": "daily-anime-meme-collect",
    "schedule": { "kind": "cron", "expr": "0 0 * * *", "tz": "Asia/Shanghai" },
    "payload": {
      "kind": "systemEvent",
      "command": "python scripts/collect_memes.py"
    }
  }
}
```

## Using the Database

When responding with anime/meme context:
1. Check `references/anime_memes_db.json` for recent trends
2. Reference `references/anime_memes_manual.md` for classics
3. Incorporate memes naturally into responses

## Data Sources

- **Bilibili API**: Trending videos and hot search
- **Manual curation**: Classic and timeless memes
- **Galgame terms**: Yuzusoft, Key, Type-Moon, etc.
- **Streamer culture**: 电棍, 山泥若, 炫狗, etc.

## Reference Files

- [anime_memes_db.json](references/anime_memes_db.json) - Auto-generated database (300+ entries)
- [anime_memes_manual.md](references/anime_memes_manual.md) - Curated classic memes

## Notes

- Script respects rate limits with timeouts
- Failed requests are logged but don't stop collection
- Database limited to 300 entries to prevent bloat
- Each entry includes source tracking
