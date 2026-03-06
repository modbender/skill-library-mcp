---
name: nano-banana-image-gen
description: AI image generation using Google Gemini API. Create thumbnails,
  banners, and graphics with Japanese text support.
---


# Nano Banana Image Gen

AI-powered image generation using Google Gemini 2.0 Flash.

**Use when** generating images, thumbnails, banners, or graphics. Supports Japanese text in images.

**Triggers**: "generate image", "create thumbnail", "make banner", "画像生成", "Nano Banana"

## Requirements

- Python 3.10+
- `google-genai` Python package
- `GOOGLE_AI_API_KEY` environment variable (Google AI Studio API key)

## Instructions

1. **Set up API key**:
   ```bash
   export GOOGLE_AI_API_KEY=$(grep GOOGLE_AI_API_KEY ~/.openclaw/secrets.env | cut -d= -f2)
   ```

2. **Generate an image**:
   ```bash
   python3 {skill_dir}/generate.py \
     --prompt "Description of the image you want" \
     --output "./output.png" \
     --aspect 16:9
   ```

3. **Prompt engineering tips**:
   - Be specific: "A futuristic Tokyo skyline at sunset with neon lights" > "Tokyo"
   - Include style: "in watercolor style", "photorealistic", "flat illustration"
   - For text in images: Include exact text in prompt: `"Blog banner with text: AIの未来"`
   - Specify mood: "warm tones", "minimalist", "vibrant and colorful"

4. **Save output** to organized directory:
   ```bash
   # Default output location
   --output /mnt/hdd/rey/images/YYYY-MM-DD_description.png
   ```

## Aspect Ratios

| Ratio | Use Case | Resolution |
|-------|----------|------------|
| 16:9 | YouTube thumbnails, blog headers | 1792×1024 |
| 1:1 | Instagram, profile pics | 1024×1024 |
| 9:16 | Stories, vertical content | 1024×1792 |

## Use Cases

- **SNS Thumbnails** — Eye-catching images for Twitter/note.com posts
- **Article Covers** — Professional headers for blog posts
- **Banners** — Promotional graphics
- **Presentation Assets** — Visual slides for decks

## Edge Cases

- **API key not set**: Error will mention authentication. Check `~/.openclaw/secrets.env`.
- **Rate limiting**: Google AI API has per-minute limits. Wait and retry.
- **Japanese text rendering**: Works natively but complex layouts may need iteration.
- **NSFW content**: API will reject inappropriate prompts. Rephrase if blocked.
- **Large batch generation**: Add delays between requests to avoid rate limits.

## Security Considerations

- Never log or display the API key in output.
- Store API key in `~/.openclaw/secrets.env` with `chmod 600`, never in code or git.
- Generated images may contain artifacts — always review before publishing.
