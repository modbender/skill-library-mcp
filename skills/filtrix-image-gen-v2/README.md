# filtrix-image-gen

Generate and edit images using multiple AI providers — zero dependencies, pure Python.

## Supported Providers & Models

| Provider | Model | Type | Best For |
|----------|-------|------|----------|
| Google Gemini | `gemini-2.5-flash-image` | Generate + Edit | Fast, cheap — **recommended default** |
| Google Gemini | `gemini-3-pro-image-preview` | Generate + Edit | Premium quality, up to 4K resolution |
| OpenAI | `gpt-image-1` | Generate + Edit | Photorealistic, artistic, mask-based inpainting |
| fal.ai | `seedream45` | Generate + Edit | Asian aesthetics, anime |
| fal.ai | `seedream4` | Generate + Edit | General purpose |
| fal.ai | `flux-pro` | Generate | Photorealism |
| fal.ai | `flux-dev` | Generate | Open weights |
| fal.ai | `recraft-v3` | Generate | Design, illustration, logos |

## Setup

Set API key(s) as environment variables (you only need keys for providers you'll use):

```bash
export GOOGLE_API_KEY=your-key    # https://aistudio.google.com
export OPENAI_API_KEY=your-key    # https://platform.openai.com
export FAL_KEY=your-key           # https://fal.ai/dashboard
```

## Usage Examples

### Generate Images (Text → Image)

```bash
# Basic generation (Gemini Flash — fast and cheap)
python scripts/generate.py --provider gemini --prompt "a fox in a forest, watercolor style"

# High quality with Gemini Pro, 2K resolution, landscape
python scripts/generate.py --provider gemini \
  --model gemini-3-pro-image-preview \
  --prompt "cinematic sunset over mountains" \
  --size 16:9 --resolution 2K

# Using OpenAI
python scripts/generate.py --provider openai --prompt "a cat wearing sunglasses" --size 1024x1024

# Using fal.ai with specific model
python scripts/generate.py --provider fal --model flux-pro --prompt "professional headshot photo"
```

### Edit Images (Image → Image)

```bash
# Style transfer with Gemini
python scripts/edit.py --provider gemini \
  --image input.png \
  --prompt "transform into cyberpunk style with neon lights"

# High-res edit with Gemini Pro
python scripts/edit.py --provider gemini \
  --model gemini-3-pro-image-preview \
  --image photo.png \
  --prompt "change background to a beach sunset" \
  --resolution 2K

# Inpainting with OpenAI (mask-based)
python scripts/edit.py --provider openai \
  --image photo.png --mask mask.png \
  --prompt "replace the sky with aurora borealis"

# Edit with fal.ai SeedReam
python scripts/edit.py --provider fal \
  --image portrait.png \
  --prompt "change hair color to blue"
```

### Output

Both scripts print the result path on success:
```
OK: /tmp/filtrix_gemini_20260213_120000.png (1820826 bytes)
```

## Prompt Tips

Need help writing prompts? Check out:
- **[filtrix.ai/prompts](https://www.filtrix.ai/prompts)** — 100+ production-tested prompts you can copy directly
- **references/prompts.md** — Built-in prompt writing guide with tips by category

## File Structure

```
filtrix-image-gen/
├── SKILL.md              # Agent instructions (auto-loaded by compatible agents)
├── scripts/
│   ├── generate.py       # Text-to-image generation
│   └── edit.py           # Image-to-image editing
└── references/
    ├── openai.md         # OpenAI-specific parameters and tips
    ├── gemini.md         # Gemini-specific parameters and tips
    ├── fal.md            # fal.ai-specific parameters and tips
    └── prompts.md        # Prompt writing guide
```

## License

MIT
