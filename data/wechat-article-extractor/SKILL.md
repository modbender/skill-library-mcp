---
name: wechat-article-extractor
description: >
  Extract full text and figures from a WeChat public account (微信公众号) article URL
  and save as a clean Markdown file. Handles WeChat's bot-detection by finding mirror
  sites automatically. Use when the user shares an mp.weixin.qq.com URL and asks to
  save, archive, extract, or read the article.
triggers:
  - mp.weixin.qq.com
  - wechat article
  - 微信公众号
  - extract wechat
  - save wechat article
  - archive wechat
  - 提取公众号文章
  - 保存公众号文章
---

# WeChat Article Extractor

Extract WeChat public account articles to clean Markdown. WeChat blocks headless browsers (环境异常 CAPTCHA) and `web_fetch` gets empty JS-rendered pages, so the reliable approach is: find a mirror on aggregator sites, then extract content.

## Scope & Boundaries

**This skill handles:**
- Extracting article text, images, and metadata from WeChat article URLs
- Finding mirror copies when direct access is blocked
- Converting HTML to clean Markdown
- Saving output as `.md` files

**This skill does NOT handle:**
- Publishing or syncing to note-taking apps (that's the user's workflow)
- Batch extraction of multiple articles (handle one at a time)
- WeChat login, authentication, or account management
- Translating article content

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| WeChat URL | Yes | An `mp.weixin.qq.com` link |
| Output filename | No | Defaults to kebab-case of article title |
| Save location | No | Defaults to `/tmp/` |

## Outputs

- A Markdown file with full article content, images, and metadata header
- Console confirmation with file path and character count

## Workflow

### Step 1 — Try direct fetch (fast path)

```
web_fetch(url, extractMode="markdown", maxChars=50000)
```

**Success check:** If result `rawLength > 500` AND content has real paragraphs (not just nav/footer text) → skip to Step 4 Option B.

**Failure indicators:** `rawLength < 500`, content is navigation/boilerplate only, or contains "环境异常" → go to Step 2.

### Step 2 — Extract article metadata

From the URL or any partial content, identify:
- Article title (from `<title>` or og:title)
- Author / account name (from og:description or page content)

If metadata is unavailable from the URL, ask the user for the article title.

### Step 3 — Search for mirrors

```
web_search("<article title> <author/account name>")
```

**Mirror site priority** (ranked by content quality and reliability):
1. **53ai.com** — full content, reliable formatting
2. **mp.ofweek.com** — tech articles
3. **juejin.cn** — developer content
4. **woshipm.com** — product/business content
5. **36kr.com** — tech/business news

If title is unknown, try: `web_search("site:53ai.com <keywords from URL path>")`

**If no mirrors found:** Try the Chrome Extension Relay fallback (see Fallback section).

### Step 4 — Download and extract

**Option A — Mirror found:**
```bash
curl -s -L "<mirror_url>" -o /tmp/wechat-article.html
```
Verify file size > 10KB (smaller usually means redirect/error page).

Run the extraction script:
```bash
python3 <skill_dir>/scripts/extract_wechat.py /tmp/wechat-article.html /tmp/<output-filename>.md
```

Replace `<skill_dir>` with the directory containing this SKILL.md.

**Option B — Direct fetch succeeded (Step 1):**
Format the fetched markdown with the header template below.

### Step 5 — Verify output quality

Check the output file:
- Has a title (not "WeChat Article")
- Has multiple paragraphs of real content
- Images have valid URLs (not broken/placeholder)
- No excessive HTML artifacts remaining

If output looks truncated or garbled, try a different mirror site (return to Step 3).

### Step 6 — Deliver to user

Report:
- File saved at: `<path>`
- Title: `<title>`
- Size: `<char count>` characters
- Image count: `<N>` images

If the user wants it saved to a specific location (e.g., Obsidian), follow their instructions for the final copy.

## Markdown Header Template

Every extracted article must include this header:

```markdown
# <title>

**作者：** <author>
**来源：** 微信公众号「<account_name>」
**日期：** <date>
**原文：** <original_wechat_url>

---

> **摘要：** <1-2 sentence summary generated from content>

---
```

Fields that cannot be determined should be omitted (don't write "Unknown").

## Fallback: Chrome Extension Relay

If no mirror exists (very new or niche article):

Tell the user (in Chinese if they wrote in Chinese):
> "没有找到镜像。请在 Chrome 中打开这篇文章，然后点击 OpenClaw Browser Relay 扩展图标（badge 亮起），我就能直接读取内容。"

Then use:
```
browser(action="snapshot", profile="chrome")
```
Extract content from the snapshot and format with the header template.

## Error Handling

| Problem | Detection | Action |
|---------|-----------|--------|
| WeChat blocks access | rawLength < 500 or "环境异常" | Search for mirrors (Step 3) |
| No mirrors found | Search returns 0 relevant results | Try Chrome Relay fallback |
| Mirror content truncated | Output < 1000 chars when original is long | Try next mirror site |
| Script extraction fails | Python error or empty output | Fall back to `web_fetch` on mirror URL |
| Images broken | Image URLs return 404 | Note in output; images may expire |

## Success Criteria

- Output Markdown contains the full article text (not truncated)
- Title and metadata are correctly extracted
- Images are preserved with working URLs
- No HTML artifacts or navigation junk in output
- File is saved at the specified location

## Notes

- WeChat image URLs from mirrors (e.g., api.ibos.cn proxy) are generally valid and render in most Markdown viewers
- Mirror sites typically publish within minutes of the original
- The `· · ·` section dividers are WeChat style — preserve them
- For very long articles (>50K chars), the script handles them fine but `web_fetch` may truncate

## Configuration

No persistent configuration required. The skill uses standard OpenClaw tools (`web_fetch`, `web_search`, `exec`) and optionally `browser` for the Chrome Relay fallback.

**Required tools:**

| Tool | Purpose |
|------|---------|
| `web_fetch` | Direct article fetch attempt |
| `web_search` | Mirror site discovery |
| `exec` | Run curl and Python extraction script |

**Optional tools:**

| Tool | Purpose |
|------|---------|
| `browser` | Chrome Extension Relay fallback |

**System dependencies:**

| Dependency | Purpose |
|------------|---------|
| Python 3.8+ | Extraction script |
| curl | Mirror page download |
