---
name: wechat-pack
description: Convert local .docx or Markdown files into WeChat-ready HTML and generate a publish folder (source/assets/cover/wechat). Use when packaging documents for WeChat public account publishing with local assets and copy-paste HTML output. 当用户要求打包微信文章、转换文章为微信格式、微信公众号排版、生成微信推文 HTML、或将 Markdown/Word 转成微信可粘贴的格式时触发。
---

# WeChat Pack

## Quick start

Run from the skill root:

```bash
./wechat_pack path/to/article.docx
./wechat_pack path/to/article.md
```

Outputs a publish folder with:

- `source/` original input file
- `assets/` downloaded or extracted images
- `cover/` optional cover image
- `wechat/` `article.html` ready to paste into WeChat editor
- `meta.json` metadata (title, paths, asset count, cover variants)

## Supported inputs

- `.docx` (requires `pandoc` installed)
- `.md` / `.markdown`
- `.html` / `.htm` (treated as already-converted HTML)

## Recommended workflow

1. Export the document from your editor to `.docx` or `.md`.
2. Run `./wechat_pack <file>`.
3. Open `wechat/article.html` and paste into the WeChat editor.

## Options

- `--out <dir>`: output directory (default: `<basename>-wechat`)
- `--title <title>`: insert a top-level title if missing
- `--cover <path-or-url>`: download or copy a cover image into `cover/`

## Notes

- For `.docx` conversion, `pandoc` must be available in `PATH`.
- The script downloads external images and rewrites `<img>` to local `assets/` paths.
- Output HTML is styled with inline CSS to be friendly to the WeChat editor.
- If Pillow is available, cover variants are generated in `cover/`: `cover-wide-2.35x1.jpg` and `cover-square-1x1.jpg`.
