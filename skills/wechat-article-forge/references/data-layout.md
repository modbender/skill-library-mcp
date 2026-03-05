# Data Layout & Schemas

## Directory Structure

```
~/.wechat-article-writer/
├── config.json              # User configuration
├── voice-profile.json       # Writing style profile (from forge voice train)
├── session.json             # Current active session (topic handoff)
└── drafts/
    └── <slug-YYYYMMDD>/
        ├── meta.json        # Status, title, type, timestamps
        ├── pipeline-state.json  # Compaction-safe state machine
        ├── outline.md       # Section outline
        ├── sources.json     # Verified source bank from research (Step 1)
        ├── draft.md         # Raw Markdown draft (+ draft-v2.md, v3, ...)
        ├── review-v1.json   # Reviewer scores (+ v2, v3, ...)
        ├── fact-check.json  # Claim verification results (Step 7)
        ├── formatted.html   # WeChat HTML (from wenyan-cli)
        ├── cover.png        # 900×383px cover image
        └── images/          # Inline illustrations
            ├── illustration-plan.json  # Scrapbook JSON plan
            ├── fig1.png
            └── fig2.png
```

## Slug Generation

1. Convert Chinese title to pinyin (first 6 syllables, hyphen-separated, lowercase).
2. Keep ASCII portions as-is (e.g., `AI`, `Rust`).
3. Append `-YYYYMMDD`.
4. Replace non-`[a-z0-9-]` with hyphen. Collapse consecutive hyphens.

**Examples:**
- `本周技术周报` → `ben-zhou-ji-shu-zhou-bao-20260217`
- `AI编程工具深度评测` → `ai-bian-cheng-gong-ju-shen-20260217`

## session.json Schema

```json
{
  "topic": {
    "title": "本周AI工具精选",
    "angle": "news_hook",
    "type": "资讯",
    "hook": "上周有三个AI产品同时发布……",
    "subject": "AI工具"
  },
  "selected_at": "2026-02-17T21:00:00Z",
  "slug": "ben-zhou-ai-gong-ju-20260217"
}
```

Handoff: `forge topic` writes → `forge write`/`forge draft` reads (expires after 24h).

## config.json

```json
{
  "default_theme": "condensed",
  "default_article_type": "教程",
  "auto_publish_types": ["资讯", "周报"],
  "cover_style": "ai_generate",
  "word_count_targets": {
    "资讯": [800, 1500],
    "周报": [1000, 2000],
    "教程": [1500, 3000],
    "观点": [1200, 2500],
    "科普": [1500, 3000]
  },
  "chrome_debug_port": 18800,
  "chrome_display": ":1",
  "chrome_user_data_dir": "/tmp/openclaw-browser2",
  "wechat_author": "你的公众号名称"
}
```
