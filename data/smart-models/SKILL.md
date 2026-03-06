---
name: Smart Router
description: >
  Intelligent multi-model router — automatically selects the best AI model based on task type
  (vision, image generation, video generation, audio, reasoning, code, general chat) via any
  OpenAI-compatible API endpoint. Supports 35+ models across 7 categories with @alias shortcuts.
  Use when: user sends an image for analysis, requests image/video/audio generation, needs deep
  reasoning or math proofs, wants to use a specific model, or prefixes message with @alias
  (e.g. @gpt52, @o3, @sora, @imagen).
author: whatevername2023@proton.me
read_when:
  - User sends an image for analysis or understanding
  - Requests to generate images, draw, paint, design
  - Requests to generate video
  - Requests for music generation, TTS, sound effects
  - Needs deep reasoning, math proofs, complex logic
  - Needs code generation, debugging, review (via external model)
  - Wants to use a specific AI model
  - User explicitly requests a particular model
  - Message starts with @alias (e.g. @gpt52, @o3, @sora)
metadata: {"clawdbot":{"emoji":"🧭"}}
allowed-tools: Bash(smart-router:*)
---

# Smart Router — Intelligent Model Router

Route tasks to the best model automatically, via any OpenAI-compatible API.

Author: whatevername2023@proton.me

## Setup

Models and provider are configured in `models.json`. Set two environment variables:

- `SMART_ROUTER_BASE_URL` — OpenAI-compatible API base URL (e.g. `https://api.openai.com/v1`)
- `SMART_ROUTER_API_KEY` — API key for the provider

Edit `models.json` to customize categories, models, and defaults for your provider.

## @ Alias Shortcuts

Prefix a message with `@alias` to skip auto-classification and call a specific model directly.

Format: `@alias your question or prompt here`

### Alias Table

| Alias | Model ID | Category |
|-------|----------|----------|
| **Vision** | | |
| `@gpt4o` | chatgpt-4o-latest | vision |
| `@qwen-vl` | qwen3-vl-235b-a22b-instruct | vision |
| `@qwen-vl-max` | qwen-vl-max-2025-08-13 | vision |
| `@llama-vl` | llama-3.2-90b-vision-instruct | vision |
| `@qwen-vl-32b` | qwen3-vl-32b-instruct | vision |
| **Image Gen** | | |
| `@imagen` | google/imagen-4-ultra | image_gen |
| `@flux` | black-forest-labs/flux-1.1-pro-ultra | image_gen |
| `@flux-kontext` | black-forest-labs/flux-kontext-max | image_gen |
| `@dalle` | dall-e-3 | image_gen |
| `@flux2` | flux-2-pro | image_gen |
| **Video Gen** | | |
| `@sora` | sora-2-pro-all | video_gen |
| `@veo` | veo3.1-pro-4k | video_gen |
| `@vidu` | viduq3-pro | video_gen |
| `@kling` | kling-video | video_gen |
| `@runway` | runwayml-gen4_turbo-10 | video_gen |
| **Audio** | | |
| `@suno` | suno_music | audio |
| `@tts` | gemini-2.5-pro-preview-tts | audio |
| `@tts-hd` | tts-1-hd | audio |
| `@kling-audio` | kling-audio | audio |
| `@vidu-tts` | vidu-tts | audio |
| **Reasoning** | | |
| `@o3` | o3 | reasoning |
| `@o3-pro` | o3-pro | reasoning |
| `@o4-mini` | o4-mini | reasoning |
| `@deepseek` | deepseek-r1 | reasoning |
| `@gemini-think` | gemini-2.5-pro-thinking | reasoning |
| `@claude-think` | claude-sonnet-4-5-20250929-thinking | reasoning |
| **Code** | | |
| `@claude` | claude-opus-4-6 | code |
| `@codex` | gpt-5.1-codex-max | code |
| `@claude-sonnet` | claude-sonnet-4-6 | code |
| `@qwen-coder` | qwen3-coder-480b-a35b-instruct | code |
| `@qwen-coder-plus` | qwen3-coder-plus | code |
| `@gpt4t` | gpt-4-turbo | code |
| **General** | | |
| `@gpt52` / `@gpt5` | gpt-5.2-chat-latest | general |
| `@gemini` | gemini-2.5-pro | general |
| `@deepseekv3` | deepseek-v3.2 | general |
| `@qwen` | qwen3-max | general |
| `@claude-chat` | claude-opus-4-6 | general |

Aliases are case-insensitive. If no alias matches, attempt fuzzy match on model name/ID. If still no match, prompt the user.

## Auto-Classification Rules

When no `@alias` is specified, classify the task automatically:

| Category | Trigger |
|----------|---------|
| `vision` | User sends image/URL, asks to analyze, describe, OCR, understand image content |
| `image_gen` | Requests to draw, generate image, design poster, create illustration |
| `video_gen` | Requests to generate video, animation, text-to-video, image-to-video |
| `audio` | Requests for music generation, TTS, sound effects |
| `reasoning` | Complex math, logic puzzles, proofs, deep analysis, long-chain reasoning |
| `code` | Code generation, debugging, refactoring, review (when external model needed) |
| `general` | Everyday chat, translation, summarization, writing, Q&A |

## Usage

### 1. Read Model Config

```bash
cat "$(dirname "$0")/../models.json"
```

### 2. Select Model

- Determine `category` based on classification rules above
- Use the first model with `"default": true` in each category
- If user specifies a model via `@alias`, use that model directly
- For cost-sensitive tasks, pick a smaller model in the same category

### 3. Call Model

#### Chat (vision / reasoning / code / general)

```bash
scripts/call-model.sh --model "MODEL_ID" --prompt "user request" --type chat
```

With image (vision):

```bash
scripts/call-model.sh --model "MODEL_ID" --prompt "request" --type chat --image "IMAGE_URL"
```

#### Image Generation

```bash
scripts/call-model.sh --model "MODEL_ID" --prompt "image description" --type image
```

#### Async Tasks (video / audio)

```bash
scripts/call-model.sh --model "MODEL_ID" --prompt "task description" --type async
```

#### TTS

```bash
scripts/call-model.sh --model "MODEL_ID" --prompt "text to speak" --type tts --voice alloy
```

### 4. Return Results

- Chat: return the model's text reply directly
- Image: return the generated image URL in markdown format
- Video/Audio: return task status and result URL

## Model Recommendations

- Vision: `qwen3-vl-235b-a22b-instruct` (strongest visual understanding)
- Image gen: `google/imagen-4-ultra` (highest quality)
- Video: `sora-2-pro-all` (best results)
- Music: `suno_music` / TTS: `tts-1-hd` or `gemini-2.5-pro-preview-tts`
- Reasoning: `o3` (strongest reasoning)
- Code: `gpt-5.1-codex-max`
- General: `claude-opus-4-6`

## Fallback

If a model call fails, automatically fall back to the next model in the same category.

## Customization

Edit `models.json` to:
- Add/remove models in any category
- Change default models
- Add new categories
- Update aliases in SKILL.md to match

The `scripts/sync-models.sh` script lists all available models from your provider to help discover new ones.
