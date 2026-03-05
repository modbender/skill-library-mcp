---
name: venice-models
description: Explore Venice AI's available models - LLMs, image generators, video, TTS, ASR, and embeddings. View capabilities, pricing, and constraints.
homepage: https://venice.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["uv"] },
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Venice Models

Explore Venice AI's available models - discover capabilities, pricing, and find the right model for your use case.

**API Base URL:** `https://api.venice.ai/api/v1`
**No API key required** - the models endpoint is public.

---

## List Models

```bash
uv run {baseDir}/scripts/models.py
```

**Options:**

- `--type`: Filter by model type (default: `all`)
  - `all` - All models
  - `text` - LLMs for chat/completions
  - `image` - Image generation
  - `video` - Video generation
  - `tts` - Text-to-speech
  - `asr` - Speech recognition
  - `embedding` - Text embeddings
  - `code` - Code-optimized LLMs
- `--format`: Output format: `table`, `json`, `names` (default: `table`)
- `--output`: Save to file

---

## Examples

**List all models:**
```bash
uv run {baseDir}/scripts/models.py
```

**Image generation models only:**
```bash
uv run {baseDir}/scripts/models.py --type image
```

**Video models:**
```bash
uv run {baseDir}/scripts/models.py --type video
```

**Just model names (for scripting):**
```bash
uv run {baseDir}/scripts/models.py --type text --format names
```

**Export to JSON:**
```bash
uv run {baseDir}/scripts/models.py --format json --output models.json
```

---

## Model Types

| Type | Description |
|------|-------------|
| `text` | LLMs for chat, completions, reasoning |
| `image` | Image generation (Flux, SDXL, etc.) |
| `video` | Video generation |
| `tts` | Text-to-speech voices |
| `asr` | Automatic speech recognition (Whisper) |
| `embedding` | Text embeddings for RAG |
| `code` | Code-optimized LLMs |
| `upscale` | Image upscaling |

---

## Output Formats

**Table (default):**
```
MODEL ID                    TYPE    CONTEXT  PRICING
llama-3.3-70b              text    128K     $0.35/M in, $0.40/M out
flux-2-max                 image   -        $0.03/image
openai/whisper-large-v3    asr     -        $0.006/minute
```

**Names only:**
```
llama-3.3-70b
flux-2-max
openai/whisper-large-v3
```

---

## Runtime Note

This skill uses `uv run` which automatically installs Python dependencies (httpx) via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata. No manual Python package installation required - `uv` handles everything.

---

## API Reference

| Endpoint | Description | Auth |
|----------|-------------|------|
| `GET /models` | List all models | None (public) |
| `GET /models?type=image` | Filter by type | None |
| `GET /models/traits` | Model capabilities | None |

Full API docs: [docs.venice.ai](https://docs.venice.ai)

