# Quality Checks Reference

These are the quality gates applied during the `forge write`, `forge draft`, and `forge preview` pipelines. Every check is listed with its failure criteria and the automatic fix (if any) or the human action required.

Checks are organized into two gates:
- **Gate 1: Content** — run after draft writing, before formatting
- **Gate 2: Format** — run after wenyan-cli conversion, before publishing

A gate failure blocks the pipeline. Up to 2 automatic fix cycles are attempted before the user is notified.

---

## Gate 1: Content Quality

### CQ-01 — Hook Strength

**What it checks:** Does the opening paragraph (first 150 characters) contain a compelling hook?

**Failure criteria (any one):**
- Opens with "本文将介绍…" / "今天我们来聊…" / "随着…的发展" pattern
- First sentence is a definition ("X是一种…")
- No tension, question, surprising fact, or narrative by end of paragraph 1

**Automatic fix:** Prepend a generated hook paragraph that creates tension or poses a question. Original para 1 becomes para 2.

**Prompt injection for fix:**
> 请为以下文章写一个开篇钩子（2-3句话）。钩子必须：提出一个让读者想继续读的问题、揭示一个反直觉的事实、或者讲述一个3秒场景。不要用定义开头，不要用"本文将介绍"。原文：[ARTICLE_EXCERPT]

**Severity:** HIGH — fix before proceeding.

---

### CQ-02 — Word Count

**What it checks:** Article length matches the target range for the declared article type.

**Targets:**
| Type | Min | Max |
|------|-----|-----|
| 资讯 | 800 | 1500 |
| 周报 | 1000 | 2000 |
| 教程 | 1500 | 3000 |
| 观点 | 1200 | 2500 |
| 科普 | 1500 | 3000 |

**Failure criteria:**
- Word count < min → **too short**
- Word count > max → **too long**

**Automatic fix (too short):** Identify the 2 shortest sections. Expand each with a concrete example, data point, or elaboration. Re-check length.

**Automatic fix (too long):** Identify the 2 longest sections. Trim redundant sentences and restate denser. Re-check length.

**Severity:** MEDIUM — attempt fix. If still out of range after 2 cycles, warn user and continue.

---

### CQ-03 — Voice Match Score

**What it checks:** The article's style matches the author's voice profile (if `~/.wechat-article-writer/voice-profile.json` exists).

**How it's scored (0–100):**
- Sentence length within ±30% of profile average: +20 pts
- Opening style matches `structure.opening_style`: +15 pts
- Closing style matches `structure.closing_style`: +15 pts
- At least 2 of the author's `dominant_devices` present: +20 pts
- Formality level consistent with profile: +15 pts
- Emoji usage consistent with profile: +15 pts

**Failure threshold:** Score < 60

**Automatic fix:** Rephrase 3–5 representative paragraphs to match the voice profile. Inject `writing_prompt_injection` from profile and regenerate those paragraphs.

**Severity:** MEDIUM — fix if profile exists. Skip check if no profile found (warn user to run `forge voice train`).

---

### CQ-04 — Section Balance

**What it checks:** No single section is disproportionately long or short relative to others.

**Failure criteria:**
- Any section < 100 characters (stub section)
- Any section > 50% of total article word count
- Standard deviation of section word counts > 2.5× the mean (extreme imbalance)

**Automatic fix:**
- Stub section: expand with 1–2 concrete examples
- Bloated section: split into two sections with a new H2, or trim to key points

**Severity:** MEDIUM

---

### CQ-05 — Chinese-First Rule

**What it checks:** No untranslated English passages longer than a phrase.

**Failure criteria:**
- Any consecutive run of 5+ English words that is not:
  - A proper noun (product name, person name)
  - A code snippet inside backticks
  - A quoted external source

**Automatic fix:** Translate offending passages into Chinese. Keep technical terms in parenthetical form: `术语（Technical Term）`.

**Severity:** HIGH — must fix.

---

### CQ-06 — Link Quality

**What it checks:** Any links included in the article are valid and accessible.

**How it checks:** `curl -s -o /dev/null -w "%{http_code}" <url>` for each link. Expected: 2xx or 3xx.

**Failure criteria:** HTTP 4xx or 5xx response, or timeout after 5 seconds.

**Automatic fix:** None — notify user with list of broken links. User must replace or remove.

**Severity:** HIGH (for 4xx/5xx). LOW (for timeout — may be transient; warn and continue).

---

### CQ-07 — 标题 (Title) Quality

**What it checks:** The article title follows 公众号 best practices.

**Failure criteria (any):**
- Title > 26 characters (WeChat truncates beyond this in feed)
- Title is all lowercase English
- Title contains no noun or active verb (too abstract)
- Title begins with a number that is spelled out (e.g., "三个理由" is fine; "三" alone is too vague)

**Automatic fix:** Generate 3 alternative titles within constraints. Ask user to confirm one.

**Severity:** HIGH — do not publish without confirming title.

---

### CQ-08 — Duplicate Content Check

**What it checks:** The draft is not too similar to an already-published article in `~/.wechat-article-writer/drafts/`.

**How it checks:** Simple trigram overlap against all published `draft.md` files. Similarity threshold: 40%.

**Failure criteria:** Trigram similarity > 40% with any published article.

**Automatic fix:** None — notify user with the similar article slug. User decides whether to proceed or differentiate.

**Severity:** MEDIUM — warn and pause. User must explicitly confirm to proceed.

---

## Gate 2: Format Quality

### FQ-01 — Broken Image References

**What it checks:** All `<img src="...">` tags in the formatted HTML point to valid URLs (WeChat CDN or absolute HTTPS).

**How it checks:** HEAD request to each image URL. Also checks that no `src` value starts with `./`, `../`, or `/` (local paths not supported by WeChat).

**Failure criteria:**
- Any `src` is a local file path
- Any `src` returns non-2xx HTTP response

**Automatic fix:**
- Local images: upload to WeChat CDN using `wenyan-cli --upload-media` and replace src with CDN URL.
- Broken remote URLs: flag to user.

**Severity:** HIGH — WeChat will silently drop broken images.

---

### FQ-02 — HTML File Size

**What it checks:** The formatted HTML file is within WeChat's limits.

**Failure criteria:**
- HTML file > 200KB — WeChat API may reject or truncate

**Automatic fix:** Identify embedded base64 images (if any) and replace with CDN URLs. Remove redundant inline styles. Trim whitespace.

**Severity:** HIGH

---

### FQ-03 — Encoding Check

**What it checks:** The HTML file is valid UTF-8 with correct meta charset declaration.

**How it checks:**
```bash
file --mime-encoding formatted.html   # must be utf-8
grep -c 'charset=utf-8' formatted.html  # must be >= 1
```

**Failure criteria:**
- Encoding is not UTF-8
- No `charset=utf-8` meta tag

**Automatic fix:** Re-save with explicit UTF-8 encoding. Insert `<meta charset="utf-8">` in `<head>`.

**Severity:** HIGH

---

### FQ-04 — Forbidden CSS Properties

**What it checks:** No CSS properties are used that WeChat's renderer strips or breaks.

**Forbidden properties (WeChat strips these):**
```
position: fixed
position: sticky
display: flex          (partially supported — avoid for layout)
display: grid          (not supported)
@media queries         (ignored in article renderer)
JavaScript in <script> (stripped)
<iframe>               (stripped)
external font-family   (only system fonts work)
```

**How it checks:** Grep the formatted HTML for each forbidden pattern.

**Failure criteria:** Any match found outside a `<code>` block.

**Automatic fix:** Remove or replace with WeChat-safe equivalents (see `wechat-html-rules.md`).

**Severity:** HIGH

---

### FQ-05 — Cover Image Dimensions

**What it checks:** The cover image is exactly 900×383px (WeChat official account recommended dimensions).

**How it checks:**
```bash
identify -format "%wx%h" cover.png
```
(requires ImageMagick)

**Failure criteria:** Dimensions ≠ 900×383

**Automatic fix:**
```bash
convert cover.png -resize 900x383^ -gravity center -extent 900x383 cover-fixed.png
```

**Severity:** HIGH — incorrect dimensions cause distorted display in feed.

---

### FQ-06 — Reading Time Estimate

**What it checks:** Estimated reading time is communicated so the user can adjust length if needed.

**How it calculates:** Chinese reading speed ≈ 500 characters/minute.
`reading_time_min = total_chars / 500`

**Failure criteria:** None — this is informational only.

**Output example:**
```
📖 预计阅读时间：4分钟（2,100字）
```

**Severity:** INFO

---

### FQ-07 — Title Tag in HTML

**What it checks:** The formatted HTML contains a correct `<title>` tag matching the article title.

**Failure criteria:** `<title>` tag is missing or contains placeholder text.

**Automatic fix:** Insert/replace `<title>` with article title from `meta.json`.

**Severity:** MEDIUM

---

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| HIGH | Blocks publish. Auto-fix attempted; if fix fails, pause and notify user. | Must resolve |
| MEDIUM | Should fix; attempt auto-fix. If fix fails after 2 cycles, warn and continue. | Strongly recommended |
| LOW | Informational. | Optional |
| INFO | Always shown; no action required. | Informational |

---

---

## Gate 3: Figure Quality

Checked after step 6 (figure generation), before cover image and formatting.

### FIG-01 — Minimum Figure Count

**What it checks:** Article contains at least 2 inline figure references (`![图`).

**Severity:** HIGH — articles without figures have significantly lower engagement on WeChat.

**Automatic fix:** Re-run figure generation step. If mermaid-cli fails, use ImageMagick fallback.

### FIG-02 — Figure Files Exist

**What it checks:** Every `![...](<path>)` in draft.md points to a file that exists and is ≥10KB.

**Severity:** HIGH — missing or corrupt figures will show as broken images.

### FIG-03 — Figure File Size

**What it checks:** No figure PNG exceeds 2MB (WeChat CDN upload limit).

**Severity:** MEDIUM — large images may fail upload or slow mobile loading.

**Automatic fix:** Compress with `pngquant` or re-generate at lower resolution.

### FIG-04 — Chinese Figure Captions

**What it checks:** All image references use Chinese captions: `![图N：<description>]`.

**Severity:** MEDIUM — uncaptioned figures look unprofessional.

### FIG-05 — Prompt Files Preserved

**What it checks:** Each `.png` in `images/` has a corresponding `.prompt.txt` file (for article-illustrator images) or `.mmd` file (for Mermaid fallback).

**Severity:** LOW — source files enable future edits and reproducibility.

### FIG-06 — Even Distribution

**What it checks:** No two figures appear within 200 characters of each other in `draft.md`.

**Severity:** LOW — clustering figures disrupts reading flow.

### FIG-07 — CDN URLs After Upload

**What it checks:** After the publish step, all `<img src="...">` in the editor point to `mmbiz.qpic.cn` CDN URLs, not local file paths.

**Severity:** HIGH — local paths will show as broken images in published articles.

---

## Running Checks Manually

You can invoke individual checks via shell during development:

```bash
# Word count
wc -m draft.md

# Chinese encoding
file --mime-encoding formatted.html

# Image size check
identify -format "%wx%h\n" cover.png

# Find potential English passages
grep -oE '[A-Za-z ]{20,}' draft.md | grep -v '`'

# HTML file size
du -k formatted.html | awk '{print $1 " KB"}'
```
