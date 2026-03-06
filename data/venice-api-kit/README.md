# Venice AI Skill for OpenClaw

A comprehensive skill that adds Venice.ai's extended API capabilities to OpenClaw:

- **Image Generation** - Generate images with multiple models and styles
- **Image Upscaling** - 2x or 4x image upscaling
- **Image Editing** - AI-powered image editing with text prompts
- **Background Removal** - Remove backgrounds from images
- **Text-to-Speech** - 60+ voices for speech synthesis  
- **Embeddings** - Vector embeddings for RAG applications
- **Video Generation** - Text-to-video generation

All with Venice.ai's privacy-focused inference (no logging, no data retention).

## Publishing to ClawHub

### Prerequisites

1. A GitHub account (at least 1 week old)
2. Venice AI API key from [venice.ai](https://venice.ai)

### Steps

1. **Install the ClawHub CLI:**

```bash
npm i -g clawhub
```

2. **Login to ClawHub:**

```bash
clawhub login
```

This opens a browser for GitHub OAuth.

3. **Publish the skill:**

```bash
cd "C:\Users\sabri\OneDrive\Trabalho\venice\interface-outerface\venice-aiskill"

clawhub publish . \
  --slug venice-ai-extended \
  --name "Venice AI Extended" \
  --version 1.0.0 \
  --changelog "Initial release: image generation/editing/upscaling, background removal, TTS, embeddings, video generation" \
  --tags latest
```

4. **Verify on ClawHub:**

Visit [clawhub.ai](https://clawhub.ai) to see your published skill.

## Local Testing

To test the skill locally with OpenClaw before publishing:

1. Copy the `venice-aiskill` folder to `~/.openclaw/skills/venice-ai/` or your workspace `skills/` folder:

```bash
# On macOS/Linux
cp -r venice-aiskill ~/.openclaw/skills/venice-ai

# On Windows (PowerShell)
Copy-Item -Recurse venice-aiskill $env:USERPROFILE\.openclaw\skills\venice-ai
```

2. Set your API key:

```bash
export VENICE_API_KEY="your_api_key_here"
```

3. Start a new OpenClaw session - the skill will be automatically loaded

## Files

```
venice-aiskill/
├── SKILL.md                           # Main skill definition
├── README.md                          # This file
└── scripts/
    ├── image_generate.py              # Image generation
    ├── image_upscale.py               # Image upscaling (2x/4x)
    ├── image_edit.py                  # AI image editing
    ├── image_background_remove.py     # Background removal
    ├── audio_speech.py                # Text-to-speech
    ├── embeddings.py                  # Vector embeddings
    └── video_generate.py              # Video generation
```

## API Endpoints Used

All scripts use the official Venice.ai API (`https://api.venice.ai/api/v1`):

| Script | Endpoint | Description |
|--------|----------|-------------|
| `image_generate.py` | `/image/generate` | Full image generation |
| `image_upscale.py` | `/image/upscale` | Image upscaling |
| `image_edit.py` | `/image/edit` | AI image editing |
| `image_background_remove.py` | `/image/background-remove` | Background removal |
| `audio_speech.py` | `/audio/speech` | Text-to-speech |
| `embeddings.py` | `/embeddings` | Vector embeddings |
| `video_generate.py` | `/video/queue`, `/video/retrieve` | Video generation |

## Security Notes

- **API Key**: Store securely in environment variables, never commit to version control
- **Privacy**: Venice.ai does not log or retain request/response data
- **Trust**: Verify you trust Venice.ai before sending sensitive data
- **Scope**: This skill only requests `VENICE_API_KEY` - no additional permissions

## Comparison to Existing ClawHub Skills

This skill is designed to complement the existing `venice-ai` skill at [clawhub.ai/jonisjongithub/venice-ai](https://clawhub.ai/jonisjongithub/venice-ai) by providing:

1. **Updated endpoints** matching Venice.ai's current API (as of Feb 2026)
2. **Additional capabilities** (video generation, background removal, image editing)
3. **Cleaner script organization** with consistent naming conventions
4. **Better error handling** and status reporting

## License

MIT
