# Index

| API | Line |
|-----|------|
| Anthropic | 2 |
| OpenAI | 119 |
| Cohere | 232 |
| Groq | 327 |
| Mistral AI | 400 |
| Perplexity AI | 488 |
| Hugging Face | 578 |
| Replicate | 666 |
| Stability AI | 767 |
| ElevenLabs | 860 |
| Deepgram | 957 |
| AssemblyAI | 1040 |
| Together AI | 1129 |
| Anyscale | 1235 |

---

# Anthropic

## Base URL
```
https://api.anthropic.com/v1
```

## Authentication
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /messages | POST | Create message (Claude) |

## Quick Examples

### Basic Message
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello, Claude!"}
    ]
  }'
```

### With System Prompt
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "system": "You are a helpful assistant.",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### Streaming
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "stream": true,
    "messages": [{"role": "user", "content": "Tell me a story"}]
  }'
```

### With Image (Vision)
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [{
      "role": "user",
      "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "BASE64_DATA"}},
        {"type": "text", "text": "What is in this image?"}
      ]
    }]
  }'
```

## Models

| Model | Use Case |
|-------|----------|
| claude-sonnet-4-20250514 | Best balance |
| claude-3-5-haiku-20241022 | Fast, cheap |
| claude-3-opus-20240229 | Most capable |

## Common Traps

- Header is `x-api-key`, not Authorization
- `anthropic-version` header is required
- max_tokens is required (no default)
- System prompt is separate field, not a message
- Streaming uses SSE format

## Rate Limits

Varies by tier. Check console for your limits.

Headers:
```
anthropic-ratelimit-requests-limit
anthropic-ratelimit-requests-remaining
anthropic-ratelimit-tokens-limit
anthropic-ratelimit-tokens-remaining
```

## Official Docs
https://docs.anthropic.com/en/api/messages
# OpenAI

## Base URL
```
https://api.openai.com/v1
```

## Authentication
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /chat/completions | POST | Chat/GPT models |
| /embeddings | POST | Text embeddings |
| /images/generations | POST | DALL-E images |
| /audio/transcriptions | POST | Whisper STT |
| /audio/speech | POST | TTS |
| /models | GET | List models |

## Quick Examples

### Chat Completion
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Streaming Chat
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

### Create Embedding
```bash
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "Your text here"
  }'
```

### Generate Image
```bash
curl https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "A white cat",
    "size": "1024x1024"
  }'
```

### Transcribe Audio
```bash
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file=@audio.mp3 \
  -F model=whisper-1
```

## Models

| Model | Use Case |
|-------|----------|
| gpt-4o | Best overall |
| gpt-4o-mini | Fast, cheap |
| gpt-4-turbo | Previous best |
| text-embedding-3-small | Embeddings (cheap) |
| text-embedding-3-large | Embeddings (better) |
| dall-e-3 | Image generation |
| whisper-1 | Speech to text |
| tts-1 | Text to speech |

## Common Traps

- Max tokens includes input + output
- Streaming responses are SSE format
- Image URLs expire after 1 hour
- Whisper max file size: 25MB
- Rate limits vary by model and tier

## Rate Limits

Varies by tier and model. Check:
```bash
# Response headers include:
x-ratelimit-limit-requests
x-ratelimit-remaining-requests
x-ratelimit-reset-requests
```

## Official Docs
https://platform.openai.com/docs/api-reference
# Cohere

LLM API specialized in embeddings, reranking, and RAG applications.

## Base URL
`https://api.cohere.com/v2`

## Authentication
API key in Authorization header as Bearer token.

```bash
curl https://api.cohere.com/v2/chat \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "command-r-plus",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Core Endpoints

### Embed (Embeddings)
```bash
curl https://api.cohere.com/v2/embed \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "embed-v4.0",
    "texts": ["Hello world", "How are you?"],
    "input_type": "search_document",
    "embedding_types": ["float"]
  }'
```

### Rerank
```bash
curl https://api.cohere.com/v2/rerank \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rerank-v4.0-pro",
    "query": "What is the capital of USA?",
    "documents": [
      "Washington D.C. is the capital of the United States.",
      "Paris is the capital of France.",
      "The US has 50 states."
    ],
    "top_n": 2
  }'
```

### Chat
```bash
curl https://api.cohere.com/v2/chat \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "command-r-plus",
    "messages": [
      {"role": "user", "content": "Explain RAG in simple terms"}
    ]
  }'
```

## Models
- `embed-v4.0` - Latest embeddings (multimodal)
- `embed-english-v3.0` - English embeddings
- `embed-multilingual-v3.0` - 100+ languages
- `rerank-v4.0-pro` - Best reranking
- `command-r-plus` - Most capable chat

## Embedding Input Types
- `search_document` - For documents to be searched
- `search_query` - For search queries
- `classification` - For classification tasks
- `clustering` - For clustering tasks

## Rate Limits
- Free tier: 1000 API calls/month
- Production: Based on plan
- Trial keys have stricter limits

## Gotchas
- Embeddings require `input_type` parameter
- Max 96 texts per embed call
- Rerank max 1000 documents per call
- Long docs auto-truncated to `max_tokens_per_doc`
- Use v2 API (v1 is deprecated)

## Links
- [Docs](https://docs.cohere.com/)
- [API Reference](https://docs.cohere.com/reference/about)
- [Embed Guide](https://docs.cohere.com/docs/embeddings)
- [Rerank Guide](https://docs.cohere.com/docs/reranking)
# Groq

Blazing-fast LLM inference with custom LPU hardware. OpenAI-compatible API.

## Base URL
`https://api.groq.com/openai/v1`

## Authentication
API key in Authorization header as Bearer token.

```bash
curl https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Core Endpoints

### Chat Completions
```bash
curl https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "What is 2+2?"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Audio Transcription (Whisper)
```bash
curl https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F file=@audio.mp3 \
  -F model=whisper-large-v3
```

### List Models
```bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

## Models
- `llama-3.3-70b-versatile` - Best quality
- `llama-3.1-8b-instant` - Fastest
- `mixtral-8x7b-32768` - 32k context
- `whisper-large-v3` - Audio transcription

## Rate Limits
- Free tier: 30 RPM, 14,400 RPD
- Paid: Higher limits based on plan
- Varies by model (check console)

## Gotchas
- OpenAI SDK compatible but base URL must be changed
- Context length varies by model (check docs)
- Whisper has 25MB file limit
- Some models may be deprecated — check /models endpoint

## Links
- [Docs](https://console.groq.com/docs)
- [API Reference](https://console.groq.com/docs/api-reference)
- [Models](https://console.groq.com/docs/models)
# Mistral AI

European LLM provider with efficient, high-quality models. OpenAI-compatible API.

## Base URL
`https://api.mistral.ai/v1`

## Authentication
API key in Authorization header as Bearer token.

```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Core Endpoints

### Chat Completions
```bash
curl https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-large-latest",
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Embeddings
```bash
curl https://api.mistral.ai/v1/embeddings \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-embed",
    "input": ["Hello world", "Bonjour le monde"]
  }'
```

### FIM (Fill-in-the-Middle)
```bash
curl https://api.mistral.ai/v1/fim/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "codestral-latest",
    "prompt": "def fibonacci(",
    "suffix": "    return result"
  }'
```

### List Models
```bash
curl https://api.mistral.ai/v1/models \
  -H "Authorization: Bearer $MISTRAL_API_KEY"
```

## Models
- `mistral-large-latest` - Most capable
- `mistral-small-latest` - Fast and efficient
- `codestral-latest` - Code generation
- `mistral-embed` - Embeddings (1024 dims)

## Rate Limits
- Varies by subscription tier
- Check console for current limits
- Retry-After header on 429 responses

## Gotchas
- Model names use `-latest` suffix for auto-updates
- JSON mode requires explicit instruction in prompt
- `safe_prompt` parameter adds safety guidelines
- FIM only available for code models

## Links
- [Docs](https://docs.mistral.ai/)
- [API Reference](https://docs.mistral.ai/api/)
- [Models](https://docs.mistral.ai/getting-started/models/)
# Perplexity AI

Search-augmented LLM API with real-time web access and citations.

## Base URL
`https://api.perplexity.ai`

## Authentication
API key in Authorization header as Bearer token.

```bash
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "What happened in tech news today?"}]
  }'
```

## Core Endpoints

### Chat Completions (with Search)
```bash
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [
      {"role": "system", "content": "Be precise and cite sources."},
      {"role": "user", "content": "Latest developments in AI regulation?"}
    ],
    "temperature": 0.2,
    "max_tokens": 1024
  }'
```

### With Domain Filtering
```bash
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "Recent ML papers on transformers"}],
    "search_domain_filter": ["arxiv.org", "openreview.net"],
    "search_recency_filter": "month"
  }'
```

### Streaming
```bash
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "Explain quantum computing"}],
    "stream": true
  }'
```

## Models
- `sonar` - Default search model (online)
- `sonar-pro` - Enhanced reasoning + search
- `sonar-reasoning` - Deep reasoning with search

## Search Parameters
- `search_domain_filter` - Limit to specific domains
- `search_recency_filter` - `day`, `week`, `month`, `year`
- `return_citations` - Include source URLs
- `return_images` - Include relevant images

## Rate Limits
- Varies by subscription tier
- Free tier available with limits
- Check dashboard for current usage

## Gotchas
- Models do web search by default — can't disable
- Citations in response need parsing from `citations` field
- `sonar` models only — no offline models available
- OpenAI SDK compatible with base URL change
- Streaming recommended for long responses

## Links
- [Docs](https://docs.perplexity.ai/)
- [API Reference](https://docs.perplexity.ai/api-reference)
- [Models](https://docs.perplexity.ai/docs/model-cards)
# Hugging Face

Model hub API for running inference on 200k+ ML models.

## Base URL
`https://api-inference.huggingface.co/models`

## Authentication
API token in Authorization header as Bearer token.

```bash
curl https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Hello, who are you?"}'
```

## Core Endpoints

### Text Generation
```bash
curl https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1 \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "Explain machine learning in simple terms",
    "parameters": {
      "max_new_tokens": 250,
      "temperature": 0.7,
      "return_full_text": false
    }
  }'
```

### Embeddings
```bash
curl https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2 \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["Hello world", "How are you?"]}'
```

### Image Classification
```bash
curl https://api-inference.huggingface.co/models/google/vit-base-patch16-224 \
  -H "Authorization: Bearer $HF_TOKEN" \
  --data-binary @image.jpg
```

### Text-to-Image
```bash
curl https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0 \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "A cat wearing sunglasses"}' \
  --output image.png
```

### Speech-to-Text
```bash
curl https://api-inference.huggingface.co/models/openai/whisper-large-v3 \
  -H "Authorization: Bearer $HF_TOKEN" \
  --data-binary @audio.mp3
```

## Parameters (vary by model)
- `max_new_tokens` - Max tokens to generate
- `temperature` - Randomness (0-1)
- `top_p` - Nucleus sampling
- `return_full_text` - Include prompt in response
- `wait_for_model` - Wait if model loading

## Rate Limits
- Free tier: Rate limited, model may need loading
- Pro: Higher limits, faster inference
- Enterprise: Dedicated endpoints

## Gotchas
- Models may need "cold start" time (use `wait_for_model`)
- Response format varies by model type
- Not all models available for inference
- Some models require Pro subscription
- Use `x-wait-for-model: true` header for loading models

## Links
- [Docs](https://huggingface.co/docs/api-inference)
- [Model Hub](https://huggingface.co/models)
- [Inference Endpoints](https://huggingface.co/inference-endpoints)
# Replicate

ML model hosting platform for running open-source models via API.

## Base URL
`https://api.replicate.com/v1`

## Authentication
API token in Authorization header as Bearer token.

```bash
curl https://api.replicate.com/v1/predictions \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "MODEL_VERSION_ID",
    "input": {"prompt": "A photo of a cat"}
  }'
```

## Core Endpoints

### Create Prediction (Async)
```bash
curl https://api.replicate.com/v1/predictions \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "stability-ai/sdxl:VERSION_HASH",
    "input": {
      "prompt": "A serene mountain landscape",
      "negative_prompt": "blurry, low quality",
      "width": 1024,
      "height": 1024
    }
  }'
# Returns prediction ID, poll for result
```

### Create Prediction (Sync)
```bash
curl https://api.replicate.com/v1/predictions \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait" \
  -d '{
    "version": "meta/llama-2-70b-chat:VERSION",
    "input": {"prompt": "Hello, who are you?"}
  }'
```

### Get Prediction Status
```bash
curl https://api.replicate.com/v1/predictions/PREDICTION_ID \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN"
```

### Run Official Model
```bash
curl https://api.replicate.com/v1/models/stability-ai/sdxl/predictions \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "A happy robot"}}'
```

### List Models
```bash
curl https://api.replicate.com/v1/models \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN"
```

## Prediction Status Values
- `starting` - Model booting up
- `processing` - Running
- `succeeded` - Complete, output available
- `failed` - Error occurred
- `canceled` - User canceled

## Popular Models
- `stability-ai/sdxl` - Image generation
- `meta/llama-2-70b-chat` - LLM chat
- `lucataco/sdxl-lightning-4step` - Fast images
- `openai/whisper` - Transcription

## Rate Limits
- Pay per second of compute
- Cold start time varies by model
- Concurrent prediction limits by plan

## Gotchas
- Async by default: poll for completion
- Use `Prefer: wait` header for sync mode (60s timeout)
- Version hash required for community models
- Model cold starts can take 10-30 seconds
- Webhook callback available for async
- Output URLs expire after 1 hour

## Links
- [Docs](https://replicate.com/docs)
- [API Reference](https://replicate.com/docs/reference/http)
- [Model Explorer](https://replicate.com/explore)
# Stability AI

Image generation API powered by Stable Diffusion models.

## Base URL
`https://api.stability.ai/v1`

## Authentication
API key in Authorization header.

```bash
curl https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image \
  -H "Authorization: Bearer $STABILITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text_prompts": [{"text": "A lighthouse on a cliff"}],
    "height": 1024,
    "width": 1024
  }'
```

## Core Endpoints

### Text-to-Image
```bash
curl https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image \
  -H "Authorization: Bearer $STABILITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text_prompts": [
      {"text": "A serene lake at sunset, photorealistic", "weight": 1},
      {"text": "blurry, low quality", "weight": -1}
    ],
    "cfg_scale": 7,
    "height": 1024,
    "width": 1024,
    "samples": 1,
    "steps": 30
  }'
```

### Image-to-Image
```bash
curl https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image \
  -H "Authorization: Bearer $STABILITY_API_KEY" \
  -F init_image=@input.png \
  -F 'text_prompts[0][text]=A painting in impressionist style' \
  -F 'text_prompts[0][weight]=1' \
  -F image_strength=0.35
```

### Upscale
```bash
curl https://api.stability.ai/v1/generation/esrgan-v1-x2plus/image-to-image/upscale \
  -H "Authorization: Bearer $STABILITY_API_KEY" \
  -F image=@input.png \
  -F width=2048
```

### List Engines
```bash
curl https://api.stability.ai/v1/engines/list \
  -H "Authorization: Bearer $STABILITY_API_KEY"
```

## Models (Engines)
- `stable-diffusion-xl-1024-v1-0` - SDXL 1.0
- `stable-diffusion-v1-6` - SD 1.6
- `esrgan-v1-x2plus` - Upscaling

## Parameters
- `text_prompts` - Array with text and weight
- `cfg_scale` - Prompt adherence (0-35, default 7)
- `steps` - Diffusion steps (10-50)
- `samples` - Number of images (1-10)
- `style_preset` - Optional style hint

## Rate Limits
- Based on credits system
- Check account balance via API
- Different models cost different credits

## Gotchas
- Response is base64 encoded image by default
- Use `accept: image/png` header for raw image
- Negative prompts use negative weight values
- SDXL requires specific dimensions (1024x1024, etc.)
- Some features require specific engine versions

## Links
- [Docs](https://platform.stability.ai/docs)
- [API Reference](https://platform.stability.ai/docs/api-reference)
- [Pricing](https://platform.stability.ai/pricing)
# ElevenLabs

High-quality text-to-speech API with voice cloning capabilities.

## Base URL
`https://api.elevenlabs.io/v1`

## Authentication
API key in `xi-api-key` header.

```bash
curl https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "model_id": "eleven_multilingual_v2"}' \
  --output speech.mp3
```

## Core Endpoints

### Text-to-Speech
```bash
curl "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75
    }
  }' \
  --output speech.mp3
```

### Streaming TTS
```bash
curl "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM/stream" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "model_id": "eleven_multilingual_v2"}' \
  --output stream.mp3
```

### List Voices
```bash
curl https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### Get Voice Settings
```bash
curl https://api.elevenlabs.io/v1/voices/21m00Tcm4TlvDq8ikWAM/settings \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### List Models
```bash
curl https://api.elevenlabs.io/v1/models \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

## Models
- `eleven_multilingual_v2` - Best quality, 29 languages
- `eleven_turbo_v2_5` - Low latency, multilingual
- `eleven_turbo_v2` - Fast English
- `eleven_monolingual_v1` - English only, legacy

## Voice Settings
- `stability` (0-1) - Higher = more consistent
- `similarity_boost` (0-1) - Higher = closer to original
- `style` (0-1) - Style exaggeration
- `speed` (0.25-4.0) - Speech speed multiplier

## Output Formats
- `mp3_44100_128` - MP3, 44.1kHz, 128kbps (default)
- `mp3_22050_32` - Smaller MP3
- `pcm_16000` - Raw PCM
- `ulaw_8000` - μ-law (Twilio compatible)

## Rate Limits
- Based on character quota per month
- Varies by subscription tier
- Check usage via API or dashboard

## Gotchas
- Auth header is `xi-api-key`, not Bearer
- Voice ID required in URL path
- Output is binary audio, not JSON
- Character limits per request (5000 chars)
- Some voices require Pro subscription

## Links
- [Docs](https://elevenlabs.io/docs)
- [API Reference](https://elevenlabs.io/docs/api-reference)
- [Voice Library](https://elevenlabs.io/voice-library)
# Deepgram

Speech-to-text API with real-time and batch transcription.

## Base URL
`https://api.deepgram.com/v1`

## Authentication
API key in Authorization header.

```bash
curl https://api.deepgram.com/v1/listen?model=nova-2 \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary @audio.wav
```

## Core Endpoints

### Transcribe File (Pre-recorded)
```bash
curl https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/mp3" \
  --data-binary @audio.mp3
```

### Transcribe URL
```bash
curl https://api.deepgram.com/v1/listen?model=nova-2&punctuate=true \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/audio.mp3"}'
```

### With Diarization (Speaker Labels)
```bash
curl "https://api.deepgram.com/v1/listen?model=nova-2&diarize=true&punctuate=true" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: audio/wav" \
  --data-binary @meeting.wav
```

### Text-to-Speech
```bash
curl "https://api.deepgram.com/v1/speak?model=aura-asteria-en" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you today?"}' \
  --output speech.mp3
```

## Models
- `nova-2` - Latest, most accurate
- `nova` - Fast, accurate
- `enhanced` - Better accuracy
- `base` - Fastest, basic

## Query Parameters
- `model` - Model to use
- `language` - Language code (e.g., `en`, `es`)
- `punctuate` - Add punctuation
- `diarize` - Speaker detection
- `smart_format` - Numbers, dates formatting
- `utterances` - Segment by utterance
- `paragraphs` - Add paragraph breaks

## Rate Limits
- Pay-as-you-go pricing
- Based on audio minutes
- Concurrent request limits by plan

## Gotchas
- Auth header is `Token`, not `Bearer`
- Audio sent as binary, not base64
- Real-time requires WebSocket connection
- Diarization adds latency
- Some features (like summarization) are add-ons

## Links
- [Docs](https://developers.deepgram.com/docs)
- [API Reference](https://developers.deepgram.com/reference)
- [Models](https://developers.deepgram.com/docs/models-languages-overview)
# AssemblyAI

Speech-to-text API with advanced analysis features (summarization, sentiment, etc.).

## Base URL
`https://api.assemblyai.com/v2`

## Authentication
API key in Authorization header.

```bash
curl https://api.assemblyai.com/v2/transcript \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "https://example.com/audio.mp3"}'
```

## Core Endpoints

### Submit Transcription
```bash
curl https://api.assemblyai.com/v2/transcript \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.mp3",
    "speaker_labels": true,
    "auto_chapters": true
  }'
# Returns transcript ID
```

### Get Transcript Status/Result
```bash
curl https://api.assemblyai.com/v2/transcript/TRANSCRIPT_ID \
  -H "Authorization: $ASSEMBLYAI_API_KEY"
```

### Upload Local File
```bash
# First upload
curl https://api.assemblyai.com/v2/upload \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  --data-binary @audio.mp3
# Returns {"upload_url": "..."}

# Then transcribe
curl https://api.assemblyai.com/v2/transcript \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "UPLOAD_URL_FROM_ABOVE"}'
```

### LeMUR (LLM Analysis)
```bash
curl https://api.assemblyai.com/lemur/v3/generate/task \
  -H "Authorization: $ASSEMBLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_ids": ["TRANSCRIPT_ID"],
    "prompt": "Summarize the key points discussed"
  }'
```

## Features (via request body)
- `speaker_labels` - Diarization
- `auto_chapters` - Auto-generated chapters
- `sentiment_analysis` - Sentiment per sentence
- `entity_detection` - Named entities
- `auto_highlights` - Key phrases
- `summarization` - Auto summary
- `content_safety` - Detect sensitive content

## Rate Limits
- Based on concurrent transcription limit
- Pay per audio hour
- LeMUR has separate pricing

## Gotchas
- Async API: Submit → Poll for status → Get result
- Status values: `queued`, `processing`, `completed`, `error`
- Must upload file first for local audio
- EU endpoint available: `api.eu.assemblyai.com`
- Webhook available instead of polling

## Links
- [Docs](https://www.assemblyai.com/docs)
- [API Reference](https://www.assemblyai.com/docs/api-reference)
- [LeMUR](https://www.assemblyai.com/docs/lemur)
# Together AI

LLM inference platform with serverless and dedicated endpoints. OpenAI-compatible.

## Base URL
`https://api.together.xyz/v1`

## Authentication
API key in Authorization header as Bearer token.

```bash
curl https://api.together.xyz/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Core Endpoints

### Chat Completions
```bash
curl https://api.together.xyz/v1/chat/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain neural networks"}
    ],
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

### Completions (Legacy)
```bash
curl https://api.together.xyz/v1/completions \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "prompt": "The capital of France is",
    "max_tokens": 50
  }'
```

### Embeddings
```bash
curl https://api.together.xyz/v1/embeddings \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "togethercomputer/m2-bert-80M-8k-retrieval",
    "input": ["Hello world", "How are you?"]
  }'
```

### Image Generation
```bash
curl https://api.together.xyz/v1/images/generations \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "stabilityai/stable-diffusion-xl-base-1.0",
    "prompt": "A futuristic city at night",
    "width": 1024,
    "height": 1024,
    "n": 1
  }'
```

## Models (Turbo = Optimized)
- `meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo`
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`
- `Qwen/Qwen2.5-72B-Instruct-Turbo`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`

## Parameters
- `max_tokens` - Max output tokens
- `temperature` - Randomness (0-2)
- `top_p` / `top_k` - Sampling parameters
- `repetition_penalty` - Reduce repetition
- `stop` - Stop sequences
- `stream` - Enable streaming

## Rate Limits
- Pay per token
- Rate limits vary by plan
- Check dashboard for usage

## Gotchas
- OpenAI SDK compatible
- Model names are full paths (org/model)
- `-Turbo` suffix = optimized versions
- Some models support JSON mode
- Function calling supported on select models

## Links
- [Docs](https://docs.together.ai/)
- [API Reference](https://docs.together.ai/reference)
- [Models](https://docs.together.ai/docs/serverless-models)
# Anyscale

LLM inference endpoints with focus on fine-tuning. OpenAI-compatible API. (Now part of Databricks)

## Base URL
`https://api.endpoints.anyscale.com/v1`

## Authentication
API key in Authorization header as Bearer token.

```bash
curl https://api.endpoints.anyscale.com/v1/chat/completions \
  -H "Authorization: Bearer $ANYSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-70b-chat-hf",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Core Endpoints

### Chat Completions
```bash
curl https://api.endpoints.anyscale.com/v1/chat/completions \
  -H "Authorization: Bearer $ANYSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-70b-chat-hf",
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "What is machine learning?"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Completions
```bash
curl https://api.endpoints.anyscale.com/v1/completions \
  -H "Authorization: Bearer $ANYSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-70b-chat-hf",
    "prompt": "The meaning of life is",
    "max_tokens": 100
  }'
```

### Embeddings
```bash
curl https://api.endpoints.anyscale.com/v1/embeddings \
  -H "Authorization: Bearer $ANYSCALE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thenlper/gte-large",
    "input": ["Hello world", "How are you?"]
  }'
```

### List Models
```bash
curl https://api.endpoints.anyscale.com/v1/models \
  -H "Authorization: Bearer $ANYSCALE_API_KEY"
```

## Models
- `meta-llama/Llama-2-70b-chat-hf`
- `meta-llama/Llama-2-13b-chat-hf`
- `mistralai/Mistral-7B-Instruct-v0.1`
- `codellama/CodeLlama-34b-Instruct-hf`
- `thenlper/gte-large` (embeddings)

## Parameters
- `max_tokens` - Maximum output tokens
- `temperature` - Randomness (0-2)
- `top_p` - Nucleus sampling
- `stream` - Enable SSE streaming
- `stop` - Stop sequences

## Rate Limits
- Based on subscription tier
- Per-minute and per-day limits
- Check dashboard for current usage

## Gotchas
- Now part of Databricks (service may change)
- OpenAI SDK compatible with base URL change
- Model availability may vary
- Fine-tuned models use different naming
- Check current model list via /models endpoint

## Links
- [Docs](https://docs.endpoints.anyscale.com/)
- [Anyscale](https://www.anyscale.com/)
- [Databricks](https://www.databricks.com/)

---

**Note:** Anyscale Endpoints has been acquired by Databricks. Check current documentation for the latest API details and model availability.
