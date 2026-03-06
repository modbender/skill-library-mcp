# wechat-article-extractor

Extract WeChat public account (微信公众号) articles to clean Markdown files with images and metadata.

## Problem

WeChat articles are notoriously difficult to archive:
- Direct scraping is blocked by bot detection (环境异常 CAPTCHA)
- `web_fetch` gets empty JavaScript-rendered shells
- Headless browsers trigger anti-bot measures

This skill works around these limitations by automatically finding mirror copies on aggregator sites, then extracting clean content.

## How It Works

1. Attempts direct fetch (works ~10% of the time)
2. If blocked, searches for mirror copies on aggregator sites (53ai.com, ofweek.com, juejin.cn, etc.)
3. Downloads mirror HTML and extracts article content, images, and metadata
4. Outputs clean Markdown with proper formatting

Falls back to Chrome Extension Relay for very new or niche articles with no mirrors.

## Installation

Copy the skill directory to your OpenClaw skills folder:

```bash
cp -r wechat-article-extractor ~/.openclaw/<workspace>/skills/
```

### Requirements

- Python 3.8+
- `curl` (for downloading mirror pages)
- OpenClaw tools: `web_fetch`, `web_search`, `exec`
- Optional: `browser` tool (for Chrome Relay fallback)

## Usage

Share a WeChat article URL with your agent:

> "Save this article: https://mp.weixin.qq.com/s/example123"

The skill triggers automatically on `mp.weixin.qq.com` URLs.

### Trigger Phrases

- Any `mp.weixin.qq.com` URL
- "extract wechat article"
- "save wechat article"
- "archive wechat"
- "提取公众号文章"
- "保存公众号文章"

## Output Format

```markdown
# Article Title

**作者：** Author Name
**来源：** 微信公众号「Account Name」
**日期：** 2024-01-15
**原文：** https://mp.weixin.qq.com/s/...

---

Full article content with images preserved...
```

## Extraction Script

The included Python script handles HTML-to-Markdown conversion:

```bash
# Extract from downloaded HTML
python3 scripts/extract_wechat.py article.html output.md

# With source URL for metadata
python3 scripts/extract_wechat.py article.html output.md --source "https://mp.weixin.qq.com/s/..."

# Run self-tests
python3 scripts/extract_wechat.py --test
```

## Quality Scorecard

| Category | Score | Details |
|----------|-------|---------|
| Completeness (SQ-A) | 8/8 | All checks pass |
| Clarity (SQ-B) | 5/5 | Clear workflow, edge cases covered |
| Balance (SQ-C) | 5/5 | Script/AI split appropriate |
| Integration (SQ-D) | 5/5 | Standard Markdown output |
| Scope (SCOPE) | 3/3 | Clean boundaries |
| OPSEC | 2/2 | No violations |
| References (REF) | 3/3 | N/A (no external methodology claims) |
| Architecture (ARCH) | 2/2 | Deterministic extraction in script |
| **Total** | **33/33** | |

*Scored by skill-engineer Reviewer (iteration 1)*

## Limitations

- Mirror sites may not have very new articles (< 1 hour old)
- Some niche/low-traffic articles may not be mirrored at all
- Image URLs from mirrors may expire over time
- Formatting of complex layouts (tables, nested lists) may be imperfect
