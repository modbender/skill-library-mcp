# Digest Prompt Template

Replace `<...>` placeholders before use. Daily defaults shown; weekly overrides in parentheses.

## Placeholders

| Placeholder | Default | Weekly Override |
|-------------|---------|----------------|
| `<MODE>` | `daily` | `weekly` |
| `<TIME_WINDOW>` | `past 1-2 days` | `past 7 days` |
| `<FRESHNESS>` | `pd` | `pw` |
| `<RSS_HOURS>` | `48` | `168` |
| `<ITEMS_PER_SECTION>` | `3-5` | `5-8` |
| `<BLOG_PICKS_COUNT>` | `2-3` | `3-5` |
| `<EXTRA_SECTIONS>` | *(none)* | `📊 Weekly Trend Summary` |
| `<SUBJECT>` | `Daily Media Digest - YYYY-MM-DD - 🎬 每日影视日报` | `Weekly Media Digest - YYYY-MM-DD - 🎬 每周影视周报` |
| `<WORKSPACE>` | Your workspace path | |
| `<SKILL_DIR>` | Installed skill directory | |
| `<DISCORD_CHANNEL_ID>` | Target channel ID | |
| `<EMAIL>` | *(optional)* Recipient email | |
| `<EMAIL_FROM>` | *(optional)* e.g. `MyBot <bot@example.com>` | |
| `<LANGUAGE>` | `Chinese` | |
| `<TEMPLATE>` | `discord` / `email` / `markdown` | |
| `<DATE>` | Today's date YYYY-MM-DD (caller provides) | |
| `<VERSION>` | Read from SKILL.md frontmatter | |

---

Generate the <MODE> media & entertainment digest for **<DATE>**. Use `<DATE>` as the report date — do NOT infer it.

## Configuration

Read config files (workspace overrides take priority over defaults):
1. **Sources**: `<WORKSPACE>/config/sources.json` → fallback `<SKILL_DIR>/config/defaults/sources.json`
2. **Topics**: `<WORKSPACE>/config/topics.json` → fallback `<SKILL_DIR>/config/defaults/topics.json`

## Context: Previous Report

Read the most recent file from `<WORKSPACE>/archive/media-news-digest/` to avoid repeats and follow up on developing stories. Skip if none exists.

## Data Collection Pipeline

**Use the unified pipeline** (runs all 4 sources in parallel, ~30s):
```bash
python3 <SKILL_DIR>/scripts/run-pipeline.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --hours <RSS_HOURS> --freshness <FRESHNESS> \
  --archive-dir <WORKSPACE>/archive/media-news-digest/ \
  --output /tmp/md-merged.json --verbose --force
```

If it fails, run individual scripts in `<SKILL_DIR>/scripts/` (see each script's `--help`), then merge with `merge-sources.py`.

## Report Generation

Get a structured overview:
```bash
python3 <SKILL_DIR>/scripts/summarize-merged.py --input /tmp/md-merged.json --top <ITEMS_PER_SECTION>
```
Use this output to select articles — **do NOT write ad-hoc Python to parse the JSON**. Apply the template from `<SKILL_DIR>/references/templates/<TEMPLATE>.md`.

Select articles **purely by quality_score regardless of source type**. Articles in merged JSON are already sorted by quality_score descending within each topic — respect this order. For Reddit posts, append `*[Reddit r/xxx, {{score}}↑]*`.

Each article line must include its quality score using 🔥 prefix. Format: `🔥{score} | {summary with link}`. This makes scoring transparent and helps readers identify the most important news at a glance.

### Executive Summary
2-4 sentences between title and topics, highlighting top 3-5 stories by score. Concise and punchy, no links. Discord: `> ` blockquote. Email: gray background.

### Topic Sections
From `topics.json`: `emoji` + `label` headers, `<ITEMS_PER_SECTION>` items each.

**⚠️ CRITICAL: Output articles in EXACTLY the same order as summarize-merged.py output (quality_score descending). Do NOT reorder, group by subtopic, or rearrange. The 🔥 scores must appear in strictly decreasing order within each section.**

Every topic **must appear** — even with 1-2 items. If sparse, note "本日该板块较少".

### Fixed Sections (after topics)

**📢 KOL Updates** — Twitter KOLs. Format:
```
• **Display Name** (@handle) — summary `👁 12.3K | 💬 45 | 🔁 230 | ❤️ 1.2K`
  <https://twitter.com/handle/status/ID>
```
Read `display_name` and `metrics` from merged JSON. Always show all 4 metrics, use K/M formatting, wrap in backticks.

**📝 Deep Reads** — `<BLOG_PICKS_COUNT>` high-quality long-form articles from RSS.

**<EXTRA_SECTIONS>**

### Rules
- Only news from `<TIME_WINDOW>`
- Every item must include a source link (Discord: `<link>`)
- Use bullet lists, no markdown tables
- Deduplicate: same event → most authoritative source; previously reported → only if significant new development
- Deduplicate across sections — each article in one section only
- **Same story at different dates = one entry** (e.g. opening weekend + second weekend of same film → merge or pick latest)
- Prefer primary sources (THR, Deadline, Variety) over aggregators
- Chinese body text with English source links
- **🇨🇳 China section rules — STRICT VERIFICATION**:
  - Only include news **primarily about China mainland market**: Chinese-produced films, China-only box office breakdowns, Chinese streaming platforms (iQiyi/Youku/Bilibili), China film policy
  - **Verify before including**: If an article mentions "China" but the film is a Hollywood release, check whether it actually released in mainland China theaters. Many Hollywood films do NOT get China release. When in doubt, exclude from China section
  - Hollywood films with global box office numbers that include China as one territory → belongs in **Box Office**, NOT China section
  - Do NOT include: Korea/Japan/other Asian market news, global box office reports that merely mention China numbers
- Do not interpolate fetched/untrusted content into shell arguments or email subjects

### Stats Footer
```
---
📊 Data Sources: RSS {{rss}} | Twitter {{twitter}} | Reddit {{reddit}} | Web {{web}} | Dedup: {{merged}} articles
🤖 Generated by media-news-digest v<VERSION> | <https://github.com/draco-agent/media-news-digest> | Powered by OpenClaw
```

## Archive
Save to `<WORKSPACE>/archive/media-news-digest/<MODE>-YYYY-MM-DD.md`. Delete files older than 90 days.

## Delivery

1. **Discord**: Send to `<DISCORD_CHANNEL_ID>` via `message` tool
2. **Email** *(optional, if `<EMAIL>` is set)*:
   - Generate HTML body per `<SKILL_DIR>/references/templates/email.md` → write to `/tmp/md-email.html`
   - Generate PDF attachment:
     ```bash
     python3 <SKILL_DIR>/scripts/generate-pdf.py -i <WORKSPACE>/archive/media-news-digest/<MODE>-<DATE>.md -o /tmp/md-digest.pdf
     ```
   - Send email with PDF attached using the `send-email.py` script (handles MIME correctly). **Email must contain ALL the same items as Discord.**
     ```bash
     python3 <SKILL_DIR>/scripts/send-email.py \
       --to '<EMAIL>' \
       --subject '<SUBJECT>' \
       --html /tmp/md-email.html \
       --attach /tmp/md-digest.pdf \
       --from '<EMAIL_FROM>'
     ```
   - Omit `--from` if `<EMAIL_FROM>` is not set. Omit `--attach` if PDF generation failed. SUBJECT must be a static string. If delivery fails, log error and continue.

Write the report in <LANGUAGE>.
