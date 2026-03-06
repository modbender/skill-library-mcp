---
name: ak-rss-24h-brief
description: "Read RSS/Atom feeds from an OPML list, fetch articles from the
  last N hours, and generate a Chinese categorized brief. Use for requests like
  “generate a 24-hour brief from this RSS list” or “summarize recent posts from
  an OPML feed bundle”. Output must keep original titles + links, group by
  category, and avoid fabricated facts. The RSS subscription list is shared by
  Andrej Karpathy (source post:
  https://x.com/karpathy/status/2018043254986703167)."
---


# AK RSS 24h Brief

## Command

```bash
python3 scripts/generate_brief.py \
  --opml-url "https://gist.githubusercontent.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b/raw/426957f043dc0054f95aae6c19de1d0b4ecc2bb2/hn-popular-blogs-2025.opml" \
  --hours 24 \
  --min-items 5 \
  --max-items 10
```

## Parameters

- `--opml-url` / `--opml-file`: OPML source (choose one)
- `--hours`: time window (default `24`)
- `--min-items`: minimum output items (default `5`)
- `--max-items`: maximum output items (default `10`)
- `--timeout`: network timeout in seconds (default `15`)
- `--max-feeds`: max feeds to fetch (default `200`)
- `--workers`: concurrent workers (default `10`)

## Output Format (fixed)

- Header line:
  - `- [RSS Source](https://gist.githubusercontent.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b/raw/426957f043dc0054f95aae6c19de1d0b4ecc2bb2/hn-popular-blogs-2025.opml)`
- Category heading: `## **Category Name**`
- Article item:
  - `- [Original Title](URL)`
  - Next line: Chinese content summary (concise, content-based)
- Footer line: `Overall Summary: ...`

### Example Snippet

```markdown
# 技术资讯简报（最近 24 小时）

- [RSS Source](https://gist.githubusercontent.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b/raw/426957f043dc0054f95aae6c19de1d0b4ecc2bb2/hn-popular-blogs-2025.opml)

## **AI工程**
- [How I think about Codex](https://simonwillison.net/2026/Feb/22/how-i-think-about-codex/#atom-everything)
  重点澄清 Codex 相关概念与使用语境，帮助开发者在工具选择和工作流设计上减少认知偏差。

---
Overall Summary: 本期重点聚焦 AI 工程实践与开发效率优化。
```

## Constraints

- Keep original article titles and links
- Do not output source domain, published time, or fetch stats
- Each item must be a Chinese content summary (no boilerplate phrasing, no raw truncation, no embedded English sentences)
- Never fabricate facts
