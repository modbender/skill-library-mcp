# Gemini API Reference

## Authentication

Gemini API uses API keys. Get yours at:
https://aistudio.google.com/app/apikey

Set as environment variable:
```bash
export GEMINI_API_KEY="your-key"
```

## Python SDK

Install:
```bash
pip install google-genai
```

## Image Generation

Gemini 2.0 Flash Experimental supports native image generation.

### Basic Example

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="your-key")

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Generate an image of a cozy living room",
    config=types.GenerateContentConfig(
        response_modalities=["Text", "Image"]
    ),
)

# Extract image
for part in response.candidates[0].content.parts:
    if hasattr(part, 'inline_data') and part.inline_data:
        image_data = part.inline_data.data
```

### Model Parameters

| Parameter | Description |
|-----------|-------------|
| `model` | Use `gemini-2.0-flash-exp` for image generation |
| `response_modalities` | Must include `"Image"` for image output |
| `contents` | Text prompt describing desired image |

### Prompting Tips

For best results with photorealistic images:

1. **Be specific about lighting**: "golden hour", "soft natural light", "studio lighting"
2. **Specify camera style**: "professional photography", "8K quality", "cinematic"
3. **Mention composition**: "rule of thirds", "centered subject", "wide angle"
4. **Avoid**: Text generation requests (model struggles with text in images)

### Rate Limits

Free tier:
- 15 requests per minute
- 1,500 requests per day

Paid tier available for higher limits.

## Output Format

Images are returned as inline data:
- Format: PNG or JPEG (varies)
- Resolution: ~1024x1024
- Encoding: Base64 in binary data

## Error Handling

Common errors:
- `429`: Rate limit exceeded - wait and retry
- `400`: Invalid request - check prompt content
- No image in response: Model may decline certain requests

## Links

- API Console: https://aistudio.google.com/app/apikey
- Documentation: https://ai.google.dev/gemini-api/docs
- Pricing: https://ai.google.dev/pricing
