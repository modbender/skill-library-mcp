---
name: markdown-slides
description: Convert markdown into self-contained HTML slide presentations with
  keyboard navigation.
---


# Markdown Slides

Convert markdown into standalone HTML slide decks — zero dependencies, works offline.

**Use when** creating presentations from markdown, quick slide decks, or demo presentations.

## Requirements

- No external tools, build steps, or API keys
- Output: single HTML file, works in any browser

## Instructions

1. **Parse input** — Split markdown content on `---` (horizontal rule) to create individual slides.

2. **Convert markdown to HTML** for each slide:
   - `# heading` → `<h1>` (title slides)
   - `## heading` → `<h2>` (section headers)
   - `- item` → `<ul><li>` (bullet lists)
   - `**bold**` → `<strong>`, `*italic*` → `<em>`
   - `` `code` `` → `<code>`, code blocks → `<pre><code>`
   - `![alt](url)` → `<img>`
   - Paragraphs → `<p>`

3. **Wrap in HTML template** with embedded CSS and JavaScript:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PRESENTATION_TITLE</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }
  .slide { width: 100vw; height: 100vh; display: none; flex-direction: column; justify-content: center; align-items: center; padding: 8vh 10vw; text-align: center; }
  .slide.active { display: flex; }
  .slide h1 { font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .slide h2 { font-size: 2.5rem; margin-bottom: 1rem; color: #667eea; }
  .slide p { font-size: 1.5rem; line-height: 1.8; max-width: 800px; color: #ccc; }
  .slide ul, .slide ol { font-size: 1.4rem; text-align: left; line-height: 2; }
  .slide code { background: #16213e; padding: 2px 8px; border-radius: 4px; font-size: 1.2rem; }
  .slide pre { background: #16213e; padding: 1.5rem; border-radius: 8px; text-align: left; overflow-x: auto; max-width: 90%; }
  .slide pre code { background: none; padding: 0; }
  .slide img { max-width: 70%; max-height: 60vh; border-radius: 8px; }
  .progress { position: fixed; bottom: 0; left: 0; height: 4px; background: #667eea; transition: width 0.3s; z-index: 10; }
  .slide-num { position: fixed; bottom: 12px; right: 20px; font-size: 0.9rem; color: #555; }
</style>
</head>
<body>
<!-- SLIDES_HERE: <div class="slide">content</div> per slide -->
<div class="progress" id="progress"></div>
<div class="slide-num" id="slideNum"></div>
<script>
let current = 0;
const slides = document.querySelectorAll('.slide');
function show(n) {
  current = Math.max(0, Math.min(n, slides.length - 1));
  slides.forEach(s => s.classList.remove('active'));
  slides[current].classList.add('active');
  document.getElementById('progress').style.width = ((current + 1) / slides.length * 100) + '%';
  document.getElementById('slideNum').textContent = (current + 1) + ' / ' + slides.length;
}
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ') show(current + 1);
  if (e.key === 'ArrowLeft') show(current - 1);
  if (e.key === 'Home') show(0);
  if (e.key === 'End') show(slides.length - 1);
});
document.addEventListener('click', e => {
  if (e.clientX > window.innerWidth / 2) show(current + 1);
  else show(current - 1);
});
show(0);
</script>
</body>
</html>
```

4. **Save** as `slides.html` (or user-specified path).

5. **Tell the user**: Open in browser, use ←/→ arrows or click to navigate, F11 for fullscreen.

## Customization Options

| Option | Default | Alternatives |
|--------|---------|-------------|
| Theme | Dark (#1a1a2e) | Light (#fff), Solarized |
| Font | System UI | Monospace, Serif |
| Accent | #667eea | Any hex color |
| Ratio | 16:9 (viewport) | Can add letterboxing |

## Edge Cases

- **No `---` separators**: Treat each `# heading` as a slide break.
- **Very long slides**: Content may overflow. Suggest splitting into multiple slides.
- **Images**: Must be URLs or base64-encoded. Local file paths won't work in standalone HTML.
- **Code-heavy slides**: Reduce font size for `<pre>` blocks on those slides.
- **Speaker notes**: Can add `<!-- notes: ... -->` comments (hidden from view).
