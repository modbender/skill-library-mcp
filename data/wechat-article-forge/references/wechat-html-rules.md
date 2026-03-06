# WeChat HTML/CSS Rendering Rules

WeChat's article renderer (微信公众号文章渲染器) is not a standard browser. It is an embedded WebView that strips or ignores many common HTML and CSS features. This document describes what works, what doesn't, and the safe alternatives.

These rules apply to content created with `wenyan-cli`. If you write custom HTML fragments, follow this guide.

---

## The Golden Rule

**WeChat renders inline styles only.**

External stylesheets, `<link>` tags, and `<style>` blocks in `<head>` are stripped at upload time. All styling must be in `style=""` attributes on individual elements.

`wenyan-cli` handles this automatically by inlining styles during conversion. If you edit HTML manually, always use inline styles.

---

## Supported HTML Elements

### ✅ Fully Supported

| Element | Notes |
|---------|-------|
| `<p>` | Primary text container. Use for all paragraphs. |
| `<h1>` `<h2>` `<h3>` | Rendered. H1 is typically the title (auto-generated). Use H2 for sections, H3 for subsections. |
| `<strong>` `<b>` | Bold — works reliably. |
| `<em>` `<i>` | Italic — works. Use sparingly; light on mobile screens. |
| `<u>` | Underline — works, but looks like a hyperlink. Avoid. |
| `<br>` | Line break — works. Prefer `<p>` over multiple `<br>`. |
| `<blockquote>` | Renders with indent. Use for quotes and callout boxes (apply colored border via inline style). |
| `<ul>` `<ol>` `<li>` | Lists — work. |
| `<img>` | Works. Must be absolute HTTPS URL or WeChat CDN URL. Local paths fail silently. |
| `<a>` | Works for display only. **Links are not clickable in articles.** WeChat converts URLs to non-clickable text. Only internal WeChat links (via 公众号 link mechanism) work. |
| `<table>` `<tr>` `<td>` `<th>` | Basic tables work on mobile. Avoid complex tables — prefer lists or split into multiple paragraphs. |
| `<code>` `<pre>` | Renders with monospace font. `wenyan-cli` applies syntax highlighting as inline `<span>` elements — safe. |
| `<hr>` | Horizontal rule — works. |
| `<section>` | Acts like `<div>`. |

### ⚠️ Partially Supported / Use with Caution

| Element | Status | Notes |
|---------|--------|-------|
| `<div>` | Partially | Works as a block container. Don't nest more than 3 levels deep. |
| `<span>` | Partially | Inline container — works for colored text. |
| `<figure>` `<figcaption>` | Partially | Renders, but `figcaption` may not display below image on all devices. Use `<p style="text-align:center; color:#999; font-size:14px;">` instead. |
| `<details>` `<summary>` | No | Stripped. |
| `<video>` | Partially | WeChat converts to a WeChat video embed only if uploaded via the WeChat backend. Raw `<video>` tags are stripped. |
| `<audio>` | No | Stripped. |

### ❌ Stripped / Not Supported

| Element | What Happens |
|---------|-------------|
| `<script>` | Completely stripped |
| `<iframe>` | Completely stripped |
| `<form>` `<input>` `<button>` | Stripped |
| `<link>` (stylesheets) | Stripped |
| `<style>` in `<head>` | Stripped on upload |
| `<svg>` (inline) | Stripped. Use `<img src="...svg">` with CDN URL instead, or convert to PNG. |

---

## CSS Properties

### ✅ Reliable Inline CSS

These properties work reliably in WeChat's WebView when applied as inline styles:

```css
/* Typography */
font-size: 16px;          /* Use px, not rem/em */
font-weight: bold;
font-style: italic;
color: #333333;           /* Hex values preferred over named colors */
line-height: 1.8;
text-align: left | center | right;
text-decoration: underline | none;
letter-spacing: 1px;
word-break: break-all;    /* Prevents overflow on long URLs/code */

/* Box model */
margin: 0 auto;
padding: 10px 15px;
border: 1px solid #e0e0e0;
border-left: 4px solid #1AAD19;  /* Classic callout box */
border-radius: 4px;
width: 100%;
max-width: 100%;

/* Background */
background-color: #f5f5f5;
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Works */

/* Display */
display: block;
display: inline;
display: inline-block;

/* Images */
max-width: 100%;          /* ALWAYS set on images */
height: auto;
vertical-align: middle;
```

### ❌ Unreliable / Stripped CSS

```css
/* Layout — don't use for structural layout */
display: flex;            /* Stripped on some older WebView versions */
display: grid;            /* Not supported */
position: fixed;          /* Stripped */
position: sticky;         /* Stripped */
z-index: 999;             /* Irrelevant — no stacking context */
float: left | right;      /* Works but causes layout issues; avoid */

/* Media queries — ignored */
@media (max-width: 768px) { ... }  /* Ignored in article renderer */

/* External fonts */
font-family: 'Inter', sans-serif;   /* External fonts stripped; only system fonts load */
@font-face { ... }                  /* Stripped */

/* Transitions & animations */
transition: all 0.3s ease;   /* Stripped */
animation: ...;              /* Stripped */
transform: rotate(45deg);    /* Partially; avoid for layout */

/* CSS variables */
--my-color: red;             /* Not supported */
color: var(--my-color);      /* Not supported */

/* calc() */
width: calc(100% - 40px);   /* Unreliable; use fixed values or 100% */
```

---

## Safe Font Stack

External fonts are stripped. Use only system fonts:

```css
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB",
             "Microsoft YaHei", "微软雅黑", sans-serif;
```

For monospace (code):
```css
font-family: "SF Mono", Monaco, Consolas, "Courier New", monospace;
```

---

## Images

### Required Rules

1. **Always use absolute HTTPS URLs** — no local paths, no relative paths.
2. **Upload to WeChat CDN first** using `wenyan-cli --upload-media <file>` or via the WeChat management backend.
3. **Set `max-width: 100%`** on every image to prevent overflow on narrow screens.
4. **Cover image**: 900×383px. WeChat will crop/distort if wrong size.
5. **In-article images**: Any aspect ratio. WeChat does not auto-resize beyond 100% max-width.

### Image Template

```html
<img
  src="https://mmbiz.qpic.cn/your_image_path/0"
  style="max-width:100%; height:auto; display:block; margin:0 auto;"
  alt="图片描述"
/>
<p style="text-align:center; color:#999999; font-size:13px; margin-top:6px;">
  图注：这里写图片说明文字
</p>
```

### SVG

Do not embed SVG inline — it is stripped. Convert to PNG first:

```bash
# Using ImageMagick
convert diagram.svg diagram.png

# Using mmdc (mermaid skill — preferred for diagrams)
mmdc -i diagram.mmd -o diagram.png -w 800
```

---

## Tables

Tables render but are not responsive. Follow these rules:

- Max 4 columns on mobile
- Keep cell content short (< 20 characters)
- Use `width:100%` on `<table>` and `border-collapse:collapse`
- Use `padding:8px` on `<td>` and `<th>`
- Use alternating row colors via inline style (WeChat strips CSS classes)

**Safe table template:**

```html
<table style="width:100%; border-collapse:collapse; font-size:14px;">
  <thead>
    <tr style="background-color:#f0f0f0;">
      <th style="padding:8px 12px; text-align:left; border:1px solid #ddd;">列一</th>
      <th style="padding:8px 12px; text-align:left; border:1px solid #ddd;">列二</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color:#ffffff;">
      <td style="padding:8px 12px; border:1px solid #ddd;">数据</td>
      <td style="padding:8px 12px; border:1px solid #ddd;">数据</td>
    </tr>
    <tr style="background-color:#fafafa;">
      <td style="padding:8px 12px; border:1px solid #ddd;">数据</td>
      <td style="padding:8px 12px; border:1px solid #ddd;">数据</td>
    </tr>
  </tbody>
</table>
```

---

## Callout / Highlight Boxes

Use `<blockquote>` or `<section>` with inline border styling:

**Tip / Info box (green left border):**
```html
<blockquote style="border-left:4px solid #1AAD19; padding:10px 16px; background:#f0fff0; margin:16px 0; border-radius:0 4px 4px 0;">
  <p style="margin:0; color:#333; font-size:15px;">💡 <strong>提示：</strong>这里写要强调的内容。</p>
</blockquote>
```

**Warning box (orange left border):**
```html
<blockquote style="border-left:4px solid #F5A623; padding:10px 16px; background:#fffbf0; margin:16px 0; border-radius:0 4px 4px 0;">
  <p style="margin:0; color:#333; font-size:15px;">⚠️ <strong>注意：</strong>这里写警告内容。</p>
</blockquote>
```

**Summary box (blue left border):**
```html
<blockquote style="border-left:4px solid #1989FA; padding:10px 16px; background:#f0f7ff; margin:16px 0; border-radius:0 4px 4px 0;">
  <p style="margin:0; color:#333; font-size:15px;">📌 <strong>核心观点：</strong>这里写关键摘要。</p>
</blockquote>
```

---

## Code Blocks

`wenyan-cli` handles code block conversion with syntax highlighting. The output is `<pre>` with inline `<span>` color styles — safe for WeChat.

If writing manually:

```html
<pre style="background:#1e1e1e; color:#d4d4d4; padding:16px; border-radius:4px; overflow-x:auto; font-size:13px; line-height:1.6; word-break:break-all;">
<code><span style="color:#569cd6;">const</span> <span style="color:#9cdcfe;">greeting</span> = <span style="color:#ce9178;">"你好，世界"</span>;</code>
</pre>
```

---

## Links

**Links are not clickable in WeChat articles for external URLs.** WeChat converts `<a href="...">` to plain text for external links.

Options:
- For important URLs: display the full URL as text so readers can copy it
- For WeChat-internal links: use the `公众号文章` link type via the WeChat editor or API
- For sponsored content: use WeChat's official link card format

Do not rely on `<a>` for navigation.

---

## Article Size Limits

| Item | Limit |
|------|-------|
| HTML content size | ~64KB after upload (API limit is higher but renderer may truncate) |
| Number of images | No hard limit; recommend ≤ 20 |
| Title length (feed) | 26 characters visible; 64 max stored |
| Total article characters | No hard limit; practical max ~10,000 characters for readability |
| Cover image file size | ~2MB |
| In-article image file size | ~10MB per image (via API upload) |

---

## Emoji

Emoji render correctly in WeChat on both iOS and Android (using the device's native emoji font).

Unicode emoji are safe. WeChat's custom emoji (the animated ones in chat) cannot be embedded in articles.

---

## WeChat-Specific Meta Tags

When using the WeChat API to create a draft, these fields are separate from the HTML body:

| API field | Description |
|-----------|-------------|
| `title` | Article title (separate from HTML `<title>`) |
| `thumb_media_id` | Cover image (uploaded separately to WeChat CDN) |
| `author` | Author name displayed below title |
| `digest` | Auto-generated excerpt shown in feed (first 120 chars of body, or custom) |
| `content_source_url` | "阅读原文" link at bottom (optional) |
| `show_cover_pic` | 0 or 1 — whether cover image appears inside article body |

`wenyan-cli` handles populating these from Markdown frontmatter.

---

## Testing Your HTML

Before publishing, test render in WeChat DevTools or view via:

```bash
# Quick sanity check — open in a standard browser first
xdg-open formatted.html

# Check for forbidden patterns
grep -E 'position:\s*fixed|display:\s*(flex|grid)|@media' formatted.html

# Check for local image paths
grep -oE 'src="[^h][^t][^t][^p][^"]*"' formatted.html
```

---

## Sources

- **WeChat Official Account API Documentation:** https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
- **WeChat Draft Article API (图文消息):** https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html
- **WeChat Publish API:** https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html
- **Cover image dimensions (900×383px):** https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html
- **Article content size limits:** https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html (content field docs)
- **Reading speed estimate (500 chars/min):** Based on average Chinese reading speed research; commonly cited in Chinese content strategy guides.
