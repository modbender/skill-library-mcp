# wecom-doc-fetcher

Use this skill when the user wants to save any page from the WeChat Work (企业微信) developer documentation site (`developer.work.weixin.qq.com/document/path/*`) as a clean Markdown file in their Obsidian vault.

## Files in this skill

```
wecom-doc-fetcher/
├── SKILL.md          # this file
└── wx_doc_fetch.py   # the fetch & convert script
```

---

## Setup (one-time)

Run these once before using the skill:

```bash
pip install requests playwright
playwright install chromium
```

> `playwright install chromium` downloads a ~150 MB headless Chromium binary. This is required for automatic `doc_id` detection.

Python 3.8+ is required.

---

## Usage

Place `wx_doc_fetch.py` anywhere convenient (e.g. your vault's scripts folder), then run:

```bash
# Basic: auto-detect doc_id, print to stdout
python wx_doc_fetch.py <URL>

# Save to file
python wx_doc_fetch.py <URL> output.md

# Skip Playwright, supply doc_id manually
python wx_doc_fetch.py <URL> output.md --doc-id <integer>

# Override cookies at runtime
python wx_doc_fetch.py <URL> output.md --cookies "wwapidoc.sid=xxx; ..."
```

### Example

```bash
python wx_doc_fetch.py https://developer.work.weixin.qq.com/document/path/94677 发送消息.md
# [info] path_id=94677  doc_id=31152
# [done] 已写入：发送消息.md
```

---

## How It Works

The WeChat Work docs site is a Vue SPA — the visible content is **not in the initial HTML**. It is loaded at runtime via a private POST API:

```
POST https://developer.work.weixin.qq.com/docFetch/fetchCnt?lang=zh_CN&ajax=1&f=json
Body: doc_id=<integer>   (application/x-www-form-urlencoded)
```

The response includes `data.content_md` — the page content as a Markdown string. The script fetches this field, cleans it, and writes the result.

### Why not WebFetch / defuddle?

The page renders client-side. `WebFetch` and `defuddle` only see the pre-JS HTML skeleton — no content. Scraping `innerText` via browser tools works but produces a very large accessibility tree with poor formatting. The `content_md` API field is the cleanest, most token-efficient source.

### URL path ID ≠ doc_id

The number in the browser URL (e.g. `94677`) is a routing slug — **not** the `doc_id` the API needs. The actual `doc_id` (e.g. `31152`) is determined at runtime by loading the page with Playwright and intercepting the `fetchCnt` XHR request.

---

## Manual doc_id Fallback

If Playwright is unavailable or times out:

1. Open the target URL in Chrome
2. DevTools → **Network** tab → filter by `fetchCnt`
3. Click the request → **Payload** tab
4. Read the `doc_id` value
5. Pass it with `--doc-id`:

```bash
python wx_doc_fetch.py https://developer.work.weixin.qq.com/document/path/94677 发送消息.md --doc-id 31152
```

---

## Cookie Configuration

The `fetchCnt` API requires an authenticated session. Playwright's headless browser obtains session cookies automatically when loading the page — **no manual cookie setup needed for normal use**.

If you see `errCode: -30001` in the output, the session is rejected. Fix:

1. Open the site in Chrome while logged in
2. DevTools → Network → any `fetchCnt` request → **Copy as cURL**
3. Find the `-b '...'` cookie string in the copied command
4. Either paste it into `COOKIES_RAW` at the top of `wx_doc_fetch.py`, or pass it via `--cookies "..."`

Key cookies and their lifetimes:

| Cookie | Purpose | Lifetime |
|--------|---------|---------|
| `wwapidoc.sid` | Session identifier | ~24 hours |
| `wwapidoc.token_wt` | JWT auth token | ~30 minutes |

---

## API Reference

| Item | Detail |
|------|--------|
| Endpoint | `POST /docFetch/fetchCnt?lang=zh_CN&ajax=1&f=json&random=<rand>` |
| Body | `doc_id=<integer>` (form-urlencoded) |
| Auth | Session cookies |
| Key response field | `data.content_md` |
| Other response fields | `data.content_html`, `data.content_html_v2`, `data.content_txt`, `data.title`, `data.time` |

---

## content_md Cleaning Rules

The `content_md` field is mostly valid CommonMark but has site-specific issues. The `clean_md()` function in `wx_doc_fetch.py` handles all of them:

| # | Problem | Raw example | After cleaning |
|---|---------|-------------|----------------|
| 1 | `[TOC]` marker at top | `[TOC]\n# 概述` | `# 概述` |
| 2 | Heading missing space after `#` | `##接口定义` | `## 接口定义` |
| 3 | Internal numeric anchor links | `[接收事件](#12977)` | `接收事件` |
| 3 | Anchors with sub-path | `[开启API](#31106/如何开启API)` | `开启API` |
| 4 | HTML line breaks inside table cells | `说明</br>补充` | `说明 补充` |
| 5 | `<b>` bold tags | `<b>注意</b>` | `**注意**` |
| 6 | `<code>` inline tags | `<code>open_kfid</code>` | `` `open_kfid` `` |
| 7 | `<font>` color tags | `<font color="red">警告</font>` | `警告` |
| 8 | `!!#rrggbb text!!` site-specific highlight | `!!#ff0000 重要!!` | `重要` |
| 9 | Leading spaces before table rows | `··\| 参数 \|` | `\| 参数 \|` |
| 10 | No blank line before table (Obsidian won't render) | `文字\n\| col \|` | `文字\n\n\| col \|` |
| 11 | Excess blank lines | 3+ `\n` in a row | 2 `\n` max |

### Rule 10 — critical regex note

The blank-line-before-table rule must match on **lines that don't start with `|`**, not just on the trailing character of the previous line:

```python
# CORRECT — matches on start of line, avoids breaking table rows apart
re.sub(r"^([^|\n][^\n]*)\n(\|)", r"\1\n\n\2", content, flags=re.MULTILINE)

# WRONG — table rows end with "| " (trailing space), so last char is space,
#          causing blank lines to be inserted between every table row
re.sub(r"([^\n])\n(\|)", r"\1\n\n\2", content)
```
