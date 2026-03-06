---
name: html2md
description: Convert HTML pages to clean, agent-friendly markdown using Readability + Turndown. Strips navigation, ads, footers, cookie banners, social CTAs. Supports URL fetch, local files, stdin, token budgeting, and output flags. Ideal for research tasks, content extraction, and web scraping in agent workflows.
---

# html2md

Aggressive HTML-to-markdown converter for AI agents. Mozilla Readability isolates main content, Turndown converts to markdown, then heavy post-processing strips remaining noise.

> Full flag reference and advanced examples: `references/usage.md`

## Setup

```bash
cd <skill-dir>/scripts
npm install
npm link        # makes `html2md` globally available
```

Requires Node.js 22+.

## Quick Start

```bash
html2md https://example.com                    # fetch + convert
html2md --file page.html                       # local HTML file
cat page.html | html2md --stdin                # pipe from stdin
html2md --max-tokens 2000 https://example.com  # budget-aware truncation
html2md --no-links https://example.com         # strip hrefs, keep text
html2md --json https://example.com             # JSON: {title, url, markdown, tokens}
```

## Key Features

- **Readability extraction** — kills navbars, sidebars, ads, cookie banners. Falls back to cleaned `<body>` when Readability returns too little (e.g. HN's table layout).
- **Token budgeting** — `--max-tokens N` keeps all headings, fills remaining budget in document order, appends `[truncated — N more tokens]`. Uses 1 token ≈ 4 chars heuristic.
- **Post-processing** — strips HTML comments, zero-width chars, social CTAs, breadcrumbs, empty headings, collapses excess blank lines.
- **Error handling** — bad URLs, timeouts (15s), non-HTML content, missing files all exit code 1 with descriptive stderr.
- **Output modes** — plain markdown or `--json` for programmatic use.

## When to Use vs `web_fetch`

| Use `html2md` when | Use `web_fetch` when |
|-------------------|---------------------|
| Reading pages in cron jobs / sub-agents | Quick one-off fetch in main session |
| Token budget matters (`--max-tokens`) | Page is a JSON/XML API endpoint |
| Heavy nav/ads/footers to strip | JS rendering not needed |
| Need JSON output | Simple pages |

## Security Considerations

html2md fetches URLs and reads local files — that's its job. If you're passing untrusted input:

- **URL fetching**: the tool will fetch whatever URL it's given. Don't pass user-controlled URLs without validation if your threat model includes SSRF.
- **File reading**: `--file` reads any path the process can access. In agent workflows, the agent controls the path — this is equivalent to the agent using `cat`.
- **No shell execution**: the tool itself never spawns shells or runs commands. When calling from scripts, use `execFileSync` (not `execSync`) to avoid shell injection.
- **No data exfiltration**: output goes to stdout only. No network requests beyond the single URL fetch. No telemetry, no analytics, no phone-home.
- **Dependencies**: jsdom (Mozilla DOM implementation), Readability (Mozilla content extractor), Turndown (HTML→markdown). All widely audited, open source libraries.

## Examples

```bash
# Read a Paul Graham essay within 2000 tokens
html2md --max-tokens 2000 https://paulgraham.com/greatwork.html

# HN front page as clean text, no link noise
html2md --no-links --no-images https://news.ycombinator.com

# Get token count before committing
html2md --json https://example.com | jq .tokens

# Pipe to file
html2md https://docs.example.com/api > api-docs.md
```
