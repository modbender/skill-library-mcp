---
name: best-image
description: Best quality AI image generation (~$0.12-0.20/image). Text-to-image, image-to-image, and image editing via the EvoLink API.
homepage: https://evolink.ai
metadata: {"openclaw": {"emoji": "🎨", "requires": {"env": ["EVOLINK_API_KEY"]}, "primaryEnv": "EVOLINK_API_KEY"}}
---

# EvoLink Best Image

Generate and edit images via the EvoLink Nano Banana Pro (gemini-3-pro-image-preview) API.

## Run

Try Python first (zero dependencies, all platforms):

```bash
python3 {baseDir}/scripts/generate.py --prompt "a cute cat" --size "auto"
```

Options: `--size` (auto, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9), `--quality` (1K, 2K, 4K), `--image-urls URL1 URL2 ...`

If Python is unavailable:

- **Windows**: see PowerShell fallback in `{baseDir}/references/powershell.md`
- **Unix/macOS**: use the curl fallback in `{baseDir}/references/curl_heredoc.md`

## API key

- `EVOLINK_API_KEY` env var (required)
- Get key: https://evolink.ai

## Triggers

- Chinese: "高质量生图：xxx" / "编辑图片：xxx"
- English: "best image: xxx" / "edit image: xxx"

Treat the text after the colon as `prompt`, use default size `auto` and quality `2K`, generate immediately.

For image-to-image or editing, the user provides image URLs alongside the prompt.

## Notes

- Script prints `MEDIA:<path>` for OC auto-attach — no extra delivery logic needed.
- Image saved locally (format auto-detected from URL: png/jpg/webp). URL expires ~24h but local file persists.
- `--quality 4K` incurs additional charges.
- `--image-urls` accepts up to 10 URLs (each image ≤10MB, formats: jpeg/jpg/png/webp).
