# Gemini Image Generation

## Models

| Model | Cost | Best For |
|-------|------|----------|
| `gemini-2.5-flash-image` | Low | Default choice. Fast, good for iterative work |
| `gemini-3-pro-image-preview` | High | Premium quality, use when user requests best results |

Always default to Flash. Only use Pro when explicitly requested or when quality is critical.

- Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- API key passed as query parameter `?key=`
- Returns inline base64 image data in response candidates
- Aspect ratios: `1:1`, `16:9`, `9:16`

## Response Structure

The response contains `candidates[0].content.parts[]`. Each part may have:
- `inlineData.data` — base64 image bytes
- `text` — text response (sometimes returned alongside or instead of image)

## Safety Filters

- `finishReason: "IMAGE_SAFETY"` means the prompt was blocked
- Text-only response with refusal keywords (e.g., "cannot create", "inappropriate") indicates a content policy block
- Retry with a modified prompt

## Tips

- Gemini is fast and good for iterative prompt refinement
- Supports mixed text+image responses — the script extracts only the image
- For best results, be descriptive but concise
