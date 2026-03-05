# Image card without Python (HTML/SVG → screenshot)

Goal: generate a clean, readable image to attach to an X post without relying on Pillow.

Approach:
1) Write a small standalone HTML file with embedded CSS + text (or SVG).
2) Open it in the browser.
3) Take a screenshot at a fixed viewport (e.g., 1200×675) so it becomes a shareable card.

Minimal HTML snippet:

```html
<!doctype html>
<meta charset="utf-8" />
<style>
  body { margin:0; font-family: ui-sans-serif, system-ui; }
  .card { width:1200px; height:675px; padding:64px; background:#0b0f14; color:#e8eef6; box-sizing:border-box; }
  .title { font-size:54px; font-weight:800; line-height:1.1; }
  .sub { margin-top:24px; font-size:30px; opacity:.9; }
  .foot { position:absolute; bottom:48px; left:64px; font-size:22px; opacity:.7; }
</style>
<div class="card">
  <div class="title">Elon Musk on Moon vs Mars: iteration speed</div>
  <div class="sub">Moon cadence ~10 days vs Mars windows ~26 months → faster learning loops</div>
  <div class="foot">Source: public X posts • Not exhaustive</div>
</div>
```

Then screenshot:
- Set viewport to 1200×675
- Capture full viewport (not full page)

Use this when:
- a tweet screenshot is still hard to read, or
- you want a clean summary image.
