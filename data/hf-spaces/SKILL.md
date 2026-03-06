---
name: hf-spaces
description: |
  Generate images, videos, audio, and more using HuggingFace Spaces and Inference Providers directly. Supports batch generation (e.g. "generate 10 images"), chaining multiple Spaces, and finding the right Space for any task. Use when asked to: generate images, create videos, text-to-speech, batch generate content, use a Gradio Space, call HF models, or any AI generation task that doesn't involve building a daggr pipeline. Triggers on: "generate images", "create a video", "text to speech", "use this Space", "batch generate", "generate 10 images", "image generation", "video generation".
---

# hf-spaces

Generate AI content (images, video, audio, text) using HuggingFace Spaces and Inference Providers directly via `gradio_client` or MCP tools.

## When MCP Tools Are Available

Check if relevant MCP tools exist (e.g. `mcp__claude_ai_HF__gr1_z_image_turbo_generate` for images, `mcp__claude_ai_HF__gr2_ltx_2_turbo_generate_video` for video). If so, use them directly — no script needed.

**Batch with MCP tools:** Call the tool multiple times (sequentially or in parallel tool calls) to generate multiple outputs.

## When Writing Scripts

Use `gradio_client` for Spaces and `huggingface_hub` for Inference Providers.

### Setup

```bash
uv init && uv add gradio_client huggingface_hub
```

### Gradio Space Call

```python
from gradio_client import Client

client = Client("owner/space-name")
result = client.predict(param1="value", param2="value", api_name="/endpoint")
```

### HF Inference Provider Call

```python
from huggingface_hub import InferenceClient

client = InferenceClient(provider="fal-ai")  # or replicate, together, etc.
image = client.text_to_image("a cat in space", model="black-forest-labs/FLUX.1-schnell")
image.save("output.png")
```

### Batch Generation

```python
from gradio_client import Client

client = Client("Tongyi-MAI/Z-Image-Turbo")
prompts = [f"A cute cat in style {i}" for i in range(10)]

for i, prompt in enumerate(prompts):
    result = client.predict(
        prompt=prompt,
        resolution="1024x1024 ( 1:1 )",
        random_seed=True,
        api_name="/generate",
    )
    images, seed_str, seed_int = result
    print(f"Generated image {i}: {images[0]['image']}")
```

### Chaining Spaces

```python
from gradio_client import Client

img_client = Client("Tongyi-MAI/Z-Image-Turbo")
vid_client = Client("alexnasa/ltx-2-TURBO")

result = img_client.predict(prompt="a sunset", resolution="1024x1024 ( 1:1 )", random_seed=True, api_name="/generate")
image_path = result[0][0]["image"]

video = vid_client.predict(first_frame=image_path, prompt="cinematic motion", duration=5, api_name="/generate_video")
print(f"Video: {video[0]}")
```

## Finding Spaces

Semantic search (describe what you need):
`https://huggingface.co/api/spaces/semantic-search?q=generate+music+for+a+video&sdk=gradio&includeNonRunning=false`

By category:
`https://huggingface.co/api/spaces/semantic-search?category=image-generation&sdk=gradio&includeNonRunning=false`

Categories: image-generation | video-generation | text-generation | speech-synthesis | music-generation | voice-cloning | image-editing | background-removal | image-upscaling | ocr | style-transfer | image-captioning

Also use the `mcp__claude_ai_HF__space_search` tool if available.

## Finding Models (Inference Providers)

`https://huggingface.co/api/models?inference_provider=all&pipeline_tag=text-to-image`

Pipeline tags: text-to-image | image-to-image | image-to-text | image-to-video | text-to-video | text-to-speech | automatic-speech-recognition

VLM/LLM models: https://router.huggingface.co/v1/models

## Checking a Space's API

```bash
curl -s "https://<space-subdomain>.hf.space/gradio_api/openapi.json"
```

Replace `<space-subdomain>` with hyphenated lowercase (e.g., `Tongyi-MAI/Z-Image-Turbo` -> `tongyi-mai-z-image-turbo`). Spaces also have a "Use via API" link in the footer.

## Handling Files

Gradio returns file dicts:
```python
path = file.get("path") if isinstance(file, dict) else file
```

## Authentication

Required for ZeroGPU Spaces and Inference Providers. Before making any authenticated call, check if a token is available:

```bash
python3 -c "from huggingface_hub import get_token; t = get_token(); print('HF token found' if t else 'NO TOKEN')"
```

If no token is found, ask the user to create one at:
`https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained`

Then have them run `hf auth login` or set `HF_TOKEN` in their environment.

## Common Spaces

```python
# Image Generation
Client("Tongyi-MAI/Z-Image-Turbo").predict(prompt="...", resolution="1024x1024 ( 1:1 )", random_seed=True, api_name="/generate")

# Text-to-Speech
Client("Qwen/Qwen3-TTS").predict(text="...", language="English", voice_description="...", api_name="/generate_voice_design")

# Image-to-Video
Client("alexnasa/ltx-2-TURBO").predict(first_frame="path.png", prompt="...", duration=5, api_name="/generate_video")
```
