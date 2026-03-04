---
name: sentiment-radar
description: "Multi-platform sentiment monitoring and analysis for products/brands/topics. Collect public opinions from Chinese platforms (小红书/XHS via MediaCrawler) and English platforms (Twitter/Reddit via Xpoz MCP). Generate structured sentiment reports with product mention tracking, pricing complaints, comparison analysis, and actionable insights. Use when: (1) monitoring competitor sentiment, (2) tracking product launch reception, (3) analyzing user pain points across social media, (4) building market intelligence reports."
---

# Sentiment Radar

Multi-platform social media sentiment collection and analysis.

## Supported Platforms

| Platform | Method | Auth Required |
|---|---|---|
| 小红书 (XHS) | MediaCrawler (CDP browser) | QR code login |
| Twitter | Xpoz MCP (`xpoz.getTwitterPostsByKeywords`) | OAuth token |
| Reddit | Xpoz MCP (`xpoz.getRedditPostsByKeywords`) | OAuth token |

## Prerequisites

### MediaCrawler (for 小红书)
If not installed:
```bash
git clone https://github.com/NanmiCoder/MediaCrawler ~/.openclaw/workspace/skills/media-crawler
cd ~/.openclaw/workspace/skills/media-crawler
uv sync
playwright install chromium
```
Config: `config/base_config.py` — set `ENABLE_CDP_MODE = True`, `SAVE_DATA_OPTION = "json"`

### Xpoz MCP (for Twitter/Reddit)
Requires mcporter with Xpoz OAuth configured. Token at `~/.mcporter/xpoz/tokens.json`.

## Workflow

### Step 1: Define targets

Identify products/brands and search keywords. Example:
```
Products: Plaud录音笔, 钉钉闪记, 飞书录音豆
Keywords (XHS): Plaud录音笔,钉钉闪记,飞书妙记,AI录音笔评测,录音豆
Keywords (Twitter): Plaud NotePin, DingTalk recorder, Lark voice
```

### Step 2: Collect data

#### XHS collection
Run MediaCrawler with keywords. Use CDP mode (user's Chrome browser) for anti-detection.
The crawler needs QR code scan for login — run in background with `exec(background=true)`.

```bash
cd skills/media-crawler
# Update keywords in config/base_config.py, then:
.venv/bin/python main.py --platform xhs --lt qrcode
```

Environment fixes for macOS:
```bash
export MPLBACKEND=Agg
export PATH="/usr/sbin:$PATH"
```

Data output: `data/xhs/json/search_contents_YYYY-MM-DD.json` and `search_comments_YYYY-MM-DD.json`

#### Twitter/Reddit collection
Use Xpoz MCP tools directly:
- `xpoz.getTwitterPostsByKeywords` — returns posts with engagement metrics
- `xpoz.getRedditPostsByKeywords` — returns posts with comments

### Step 3: Analyze

Run the analysis script on collected data:
```bash
python3 scripts/analyze.py \
  --data ./data \
  --products '{"Plaud": ["plaud","notepin"], "钉钉": ["钉钉","dingtalk","闪记"]}' \
  --output report.md
```

The script performs:
- Keyword distribution analysis (notes per keyword, total likes/collects)
- Product mention frequency in comments
- Sentiment classification (positive/negative/concern/neutral)
- Top notes ranking by engagement
- Price/subscription complaint extraction
- Product comparison comment extraction

### Step 4: Report

The analysis outputs:
1. JSON results to stdout (for programmatic use)
2. Markdown report to `--output` path

Combine XHS + Twitter data into a comprehensive report. See `references/report-template.md` for structure.

## Key Analysis Dimensions

1. **Sentiment split** — positive vs negative vs concern ratio
2. **Product mentions** — which products get discussed most
3. **Pricing complaints** — subscription fatigue, value perception
4. **Comparison comments** — head-to-head user opinions
5. **User pain points** — feature requests, complaints, unmet needs
6. **Engagement metrics** — likes, collects, shares as popularity signals

## Notes

- XHS data uses Chinese number format (e.g., "1.1万") — `parse_count()` in analyze.py handles this
- MediaCrawler has 2s sleep between requests to avoid rate limiting
- Each keyword returns ~20 notes per page (configurable in MediaCrawler config)
- Comments are fetched per note automatically
- For recurring monitoring, schedule via cron and compare against previous reports
