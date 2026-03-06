---
name: monet-ai-skill
description: Monet AI - Comprehensive AI content generation API for AI agents. Video generation (Sora, Veo, Doubao Seedance, Wan, Hailuo, Kling), image generation (GPT-4o, Nano Banana, Seedream, Flux, Imagen, Ideogram), and music generation (MiniMax Music). Build intelligent workflows with multi-model AI generation capabilities.
metadata:
  openclaw:
    requires:
      env:
        - MONET_API_KEY # Required: API key from monet.vision
      bins: []
---

# Monet AI Skill

Comprehensive AI content generation API designed for AI agents. Monet AI provides unified access to state-of-the-art AI generation models for video (Sora, Veo, Doubao Seedance, Wan, Hailuo, Kling), image (GPT-4o, Nano Banana, Seedream, Flux, Imagen, Ideogram), and music (MiniMax Music) generation. Build intelligent workflows that combine multiple AI capabilities for automated content creation pipelines.

## When to Use

Use this skill when:

- **Video Generation**: Create AI-generated videos from text prompts using state-of-the-art models
  - Sora: OpenAI's video generation model for high-quality, realistic videos
  - Veo: Google's video generation model
  - Doubao Seedance: ByteDance's AI video model with audio-visual sync
  - Wan: Alibaba's video generation model with excellent localization support
  - Hailuo: Fast video generation with good quality-speed balance
  - Kling: Kuaishou's video generation model
- **Image Generation**: Generate images from text descriptions with various artistic styles
  - GPT-4o: OpenAI's multimodal model for image generation
  - Nano Banana: Google's image model with ultra-high character consistency
  - Seedream: ByteDance's intelligent visual reasoning model
  - Wan: Alibaba's visual model for high-quality and expressive image generation
  - Flux: High-quality photorealistic and artistic image generation
  - Imagen: Google's text-to-image model
  - Ideogram: Specialized in text rendering and precise composition
- **Music Generation**: Create original music and audio from text descriptions
  - MiniMax Music: AI music generation with support for custom lyrics and text-to-music conversion
- **AI Agent Integration**: Build intelligent workflows that combine multiple AI generation capabilities for automated content creation pipelines

## Getting API Key

1. Visit https://monet.vision to register an account
2. After login, go to https://monet.vision/skills/keys to create an API Key
3. Configure the API Key in environment variables or code

If you don't have an API Key, ask your owner to apply at monet.vision.

## Quick Start

### Create a Video Generation Task

```bash
curl -X POST https://monet.vision/api/v1/tasks/async \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -d '{
    "type": "video",
    "input": {
      "model": "sora-2",
      "prompt": "A cat running in the park",
      "duration": 5,
      "aspect_ratio": "16:9"
    },
    "idempotency_key": "unique-key-123"
  }'
```

> ⚠️ **Important**: `idempotency_key` is **required**. Use a unique value (e.g., UUID) to prevent duplicate task creation if the request is retried.

Response:

```json
{
  "id": "task_abc123",
  "status": "pending",
  "type": "video",
  "created_at": "2026-02-27T10:00:00Z"
}
```

### Get Task Status and Result

Task processing is asynchronous. You need to poll the task status until it becomes `success` or `failed`. **Recommended polling interval: 5 seconds**.

```bash
curl https://monet.vision/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer $MONET_API_KEY"
```

Response when completed:

```json
{
  "id": "task_abc123",
  "status": "success",
  "type": "video",
  "outputs": [
    {
      "model": "sora-2",
      "status": "success",
      "progress": 100,
      "url": "https://files.monet.vision/..."
    }
  ],
  "created_at": "2026-02-27T10:00:00Z",
  "updated_at": "2026-02-27T10:01:30Z"
}
```

**Example: Poll until completion**

```typescript
const TASK_ID = "task_abc123";
const MONET_API_KEY = process.env.MONET_API_KEY;

async function pollTask() {
  while (true) {
    const response = await fetch(
      `https://monet.vision/api/v1/tasks/${TASK_ID}`,
      {
        headers: {
          Authorization: `Bearer ${MONET_API_KEY}`,
        },
      },
    );

    const data = await response.json();
    const status = data.status;

    if (status === "success") {
      console.log("Task completed successfully!");
      console.log(JSON.stringify(data, null, 2));
      break;
    } else if (status === "failed") {
      console.log("Task failed!");
      console.log(JSON.stringify(data, null, 2));
      break;
    } else {
      console.log(`Task status: ${status}, waiting...`);
      await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait 5 seconds
    }
  }
}

pollTask();
```

## Supported Models

### Video Generation

#### Sora (OpenAI)

**sora-2** - Sora 2

_OpenAI latest video generation model_

- 🎯 **Use Cases**: Video projects requiring OpenAI's latest technology
- ⏱️ **Duration**: 10-15 seconds
- 🎵 **Features**: Audio generation support, reference image support

```typescript
{
  model: "sora-2",
  prompt: string,                // Required
  images?: string[],             // Optional: Reference images
  duration?: 10 | 15,           // Optional, default: 10
  aspect_ratio?: "16:9" | "9:16"
}
```

**sora-2-pro** - Sora 2 Pro

_Perfect quality for cinematic scenes_

- 🎯 **Use Cases**: Professional film, advertising, and high-end production
- ⏱️ **Duration**: 15-25 seconds
- 🎵 **Features**: Audio generation support, reference image support

```typescript
{
  model: "sora-2-pro",
  prompt: string,
  images?: string[],
  duration?: 15 | 25,           // Optional, default: 15
  aspect_ratio?: "16:9" | "9:16"
}
```

#### Veo (Google)

**veo-3-1-fast** - Google Veo 3.1 Fast

_Ultra-fast video generation_

- 🎯 **Use Cases**: Video projects requiring fast generation
- ⏱️ **Duration**: 8 seconds
- 📺 **Resolution**: 1080p with audio generation support

```typescript
{
  model: "veo-3-1-fast",
  prompt: string,
  images?: string[],             // Reference images
  aspect_ratio?: "16:9" | "9:16"
}
```

**veo-3-1** - Google Veo 3.1

_Advanced AI video with sound_

- 🎯 **Use Cases**: Professional-grade video production
- ⏱️ **Duration**: 8 seconds
- 📺 **Resolution**: 1080p with audio generation support

```typescript
{
  model: "veo-3-1",
  prompt: string,
  images?: string[],
  aspect_ratio?: "16:9" | "9:16"
}
```

**veo-3-fast** - Google Veo 3 Fast

_30% faster than standard Veo 3_

- 🎯 **Use Cases**: Video projects requiring rapid iteration
- ⏱️ **Duration**: 8 seconds
- 📺 **Resolution**: 1080p, supports negative prompts

```typescript
{
  model: "veo-3-fast",
  prompt: string,
  images?: string[],
  negative_prompt?: string       // Specify unwanted content
}
```

**veo-3** - Google Veo 3

_High-quality video generation_

- 🎯 **Use Cases**: Standard high-quality video production
- ⏱️ **Duration**: 8 seconds
- 📺 **Resolution**: 1080p, supports negative prompts

```typescript
{
  model: "veo-3",
  prompt: string,
  images?: string[],
  negative_prompt?: string
}
```

#### Wan

**wan-2-6** - Wan 2.6

_Multi-shot and automatic audio_

- 🎯 **Use Cases**: Video production requiring multi-shot switching
- ⏱️ **Duration**: 5-15 seconds
- 📺 **Resolution**: 720p-1080p with audio generation support

```typescript
{
  model: "wan-2-6",
  prompt: string,
  images?: string[],
  duration?: 5 | 10 | 15,
  resolution?: "720p" | "1080p",
  aspect_ratio?: "16:9" | "9:16" | "4:3" | "3:4" | "1:1",
  shot_type?: "single" | "multi"  // Single/multi-shot switching
}
```

**wan-2-5** - Wan 2.5

_Supports automatic audio generation_

- 🎯 **Use Cases**: Quickly generating videos with audio
- ⏱️ **Duration**: 5-10 seconds
- 📺 **Resolution**: 480p-1080p with audio support

```typescript
{
  model: "wan-2-5",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "720p" | "1080p",
  aspect_ratio?: "16:9" | "9:16" | "4:3" | "3:4" | "1:1"
}
```

**wan-2-2-flash** - Wan 2.2 Flash

_Instruction understanding, controllable camera movement_

- 🎯 **Use Cases**: Scenarios requiring precise camera movement control
- ⏱️ **Duration**: 5-10 seconds
- 📺 **Resolution**: 480p-1080p

```typescript
{
  model: "wan-2-2-flash",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "720p" | "1080p",
  negative_prompt?: string
}
```

**wan-2-2** - Wan 2.2

_Excellent image details, strong motion stability_

- 🎯 **Use Cases**: Video production requiring high stability
- ⏱️ **Duration**: 5-10 seconds
- 📺 **Resolution**: 480p-1080p

```typescript
{
  model: "wan-2-2",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "1080p",
  aspect_ratio?: "16:9" | "9:16" | "4:3" | "3:4" | "1:1",
  negative_prompt?: string
}
```

#### Kling

**kling-2-6** - Kling 2.6

_Cinematic videos and audio_

- 🎯 **Use Cases**: Cinematic video production
- ⏱️ **Duration**: 5-10 seconds
- ✨ **Features**: Strong visual realism, audio generation support

```typescript
{
  model: "kling-2-6",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  generate_audio?: boolean
}
```

**kling-2-5** - Kling 2.5 Turbo

_Smooth motion, stronger consistency_

- 🎯 **Use Cases**: Video production requiring high consistency
- ⏱️ **Duration**: 5-10 seconds
- ✨ **Features**: Supports negative prompts

```typescript
{
  model: "kling-2-5",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  negative_prompt?: string
}
```

**kling-v2-1-master** - Kling 2.1 Master

_Strong visual realism with enhanced features_

- 🎯 **Use Cases**: Professional-grade high-quality video production
- ⏱️ **Duration**: 5-10 seconds
- ✨ **Features**: Strength adjustment support, negative prompts

```typescript
{
  model: "kling-v2-1-master",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  strength?: number,            // 0-1: Control generation effect
  negative_prompt?: string
}
```

**kling-v2-1** - Kling 2.1

_Strong visual realism_

- 🎯 **Use Cases**: High-realism video production
- ⏱️ **Duration**: 5-10 seconds
- ✨ **Features**: Strength adjustment, negative prompts

```typescript
{
  model: "kling-v2-1",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  strength?: number,            // 0-1
  negative_prompt?: string
}
```

**kling-v2** - Kling 2.0

_Excellent aesthetics_

- 🎯 **Use Cases**: Artistic creation and aesthetically-oriented videos
- ⏱️ **Duration**: 5-10 seconds
- ✨ **Features**: Strength adjustment, negative prompts

```typescript
{
  model: "kling-v2",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  strength?: number,            // 0-1
  negative_prompt?: string
}
```

#### Hailuo

**hailuo-2-3** - Hailuo 2.3

_Excellent body movements and physics performance_

- 🎯 **Use Cases**: Videos requiring realistic physics effects
- ⏱️ **Duration**: 6-10 seconds
- 📺 **Resolution**: 768p-1080p, extreme physics simulations

```typescript
{
  model: "hailuo-2-3",
  prompt: string,
  images?: string[],
  duration?: 6 | 10,
  resolution?: "768p" | "1080p"
}
```

**hailuo-2-3-fast** - Hailuo 2.3 Fast

_Fast generation speed_

- 🎯 **Use Cases**: Projects requiring rapid iteration
- ⏱️ **Duration**: 6-10 seconds
- 📺 **Resolution**: 768p-1080p

```typescript
{
  model: "hailuo-2-3-fast",
  prompt: string,
  images?: string[],
  duration?: 6 | 10,
  resolution?: "768p" | "1080p"
}
```

**hailuo-02** - Hailuo 02

_Extreme physics simulations_

- 🎯 **Use Cases**: Scenarios requiring accurate physics simulation
- ⏱️ **Duration**: 6-10 seconds
- 📺 **Resolution**: 768p-1080p

```typescript
{
  model: "hailuo-02",
  prompt: string,
  images?: string[],
  duration?: 6 | 10,
  resolution?: "768p" | "1080p"
}
```

**hailuo-01-live2d** - Hailuo 01 Live2d

_Hailuo Live2D model_

- 🎯 **Use Cases**: 2D character animation production
- ✨ **Features**: Suitable for 2D character animation

```typescript
{
  model: "hailuo-01-live2d",
  prompt: string,
  images?: string[]
}
```

**hailuo-01** - Hailuo 01

_Highest video quality_

- 🎯 **Use Cases**: Video production requiring ultimate quality
- ✨ **Features**: Suitable for high-quality needs

```typescript
{
  model: "hailuo-01",
  prompt: string,
  images?: string[]
}
```

#### Doubao Seedance

**doubao-seedance-1-5-pro** - Seedance 1.5 Pro

_Pro-grade audio-visual sync_

- 🎯 **Use Cases**: Professional production requiring audio-visual sync
- ⏱️ **Duration**: 4-12 seconds
- 📺 **Resolution**: 480p-720p with audio generation support

```typescript
{
  model: "doubao-seedance-1-5-pro",
  prompt: string,
  images?: string[],
  duration?: number,
  resolution?: "480p" | "720p",
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16" | "21:9",
  generate_audio?: boolean
}
```

**doubao-seedance-1-0-pro-fast** - Seedance 1.0 Pro Fast

_Premium quality & unbeatable efficiency_

- 🎯 **Use Cases**: Scenarios requiring fast high-quality output
- ⏱️ **Duration**: 2-12 seconds
- 📺 **Resolution**: 720p-1080p, ByteDance's next-gen AI video model

```typescript
{
  model: "doubao-seedance-1-0-pro-fast",
  prompt: string,
  images?: string[],
  duration?: number,
  resolution?: "720p" | "1080p",
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16" | "21:9"
}
```

**doubao-seedance-1-0-pro** - Seedance 1.0 Pro

_Stable motion performance_

- 🎯 **Use Cases**: Video production requiring stable motion
- ⏱️ **Duration**: 5-10 seconds
- 📺 **Resolution**: 480p-1080p

```typescript
{
  model: "doubao-seedance-1-0-pro",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "1080p",
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16"
}
```

**doubao-seedance-1-0-lite** - Seedance 1.0 Lite

_Precise semantic understanding_

- 🎯 **Use Cases**: Scenarios requiring precise semantic understanding
- ⏱️ **Duration**: 5-10 seconds
- 📺 **Resolution**: 480p-1080p

```typescript
{
  model: "doubao-seedance-1-0-lite",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "720p" | "1080p"
}
```

#### Special Features

**kling-motion-control** - Kling Motion Control

_Precision motion control via video references_

- 🎯 **Use Cases**: Scenarios requiring motion replication from reference videos
- ⏱️ **Duration**: 3-30 seconds
- 📺 **Resolution**: 720p/1080p with audio generation support
- 💰 **Pricing**: 720p: 8 credits/s, 1080p: 15 credits/s

```typescript
{
  model: "kling-motion-control",
  prompt: string,                // Required: Detailed motion description
  images: string[],              // Required: min 1 reference image
  videos: string[],              // Required: min 1 reference video
  resolution?: "720p" | "1080p"
}
```

**runway-act-two** - Runway Act Two

_Runway Next-Generation Motion Capture Model_

- 🎯 **Use Cases**: Capturing motion from videos and applying to new characters
- ⏱️ **Duration**: 3-30 seconds
- ✨ **Features**: Motion transfer support
- 💰 **Pricing**: 10 credits/second

```typescript
{
  model: "runway-act-two",
  images: string[],              // Required: min 1 target character image
  videos: string[],              // Required: min 1 motion reference video
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16" | "21:9"
}
```

**wan-animate-mix** - Wan Animate Mix (Standard)

_Perfect for character replacement scenarios_

- 🎯 **Use Cases**: Video character replacement
- ⏱️ **Duration**: 3-30 seconds
- ✨ **Features**: Replace characters in videos with specified image characters
- 💰 **Pricing**: 10 credits/second

```typescript
{
  model: "wan-animate-mix",
  videos: string[],              // Required: Original videos
  images: string[]               // Required: Target character images
}
```

**wan-animate-mix-pro** - Wan Animate Mix Pro (Professional)

_High animation fluidity with better results_

- 🎯 **Use Cases**: Professional-grade video character replacement
- ⏱️ **Duration**: 3-30 seconds
- ✨ **Features**: Higher quality character replacement effects
- 💰 **Pricing**: 20 credits/second

```typescript
{
  model: "wan-animate-mix-pro",
  videos: string[],              // Required
  images: string[]               // Required
}
```

**wan-animate-move** - Wan Animate Move (Standard)

_Replicate dance and challenging body movements_

- 🎯 **Use Cases**: Motion capture and transfer
- ⏱️ **Duration**: 3-30 seconds
- ✨ **Features**: Apply motion from reference videos to target images
- 💰 **Pricing**: 10 credits/second

```typescript
{
  model: "wan-animate-move",
  videos: string[],              // Required: Motion reference videos
  images: string[]               // Required: Target character images
}
```

**wan-animate-move-pro** - Wan Animate Move Pro (Professional)

_High animation fluidity with better results_

- 🎯 **Use Cases**: Professional-grade motion capture and transfer
- ⏱️ **Duration**: 3-30 seconds
- ✨ **Features**: Higher quality motion transfer effects
- 💰 **Pricing**: 20 credits/second

```typescript
{
  model: "wan-animate-move-pro",
  videos: string[],              // Required
  images: string[]               // Required
}
```

---

### Image Generation

#### GPT (OpenAI)

**gpt-4o** - GPT 4o

_Accurate, realistic output_

- 🎯 **Use Cases**: High-quality, photorealistic image generation
- ✨ **Features**: Supports multiple reference images, multiple aspect ratios, customizable style

```typescript
{
  model: "gpt-4o",
  prompt: string,
  images?: string[],             // Reference images for style guidance
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string                 // Custom style description
}
```

**gpt-image-1-5** - GPT Image 1.5

_True-color precision rendering_

- 🎯 **Use Cases**: Professional image generation requiring color accuracy
- ✨ **Features**: Supports up to 10 reference images, adjustable quality

```typescript
{
  model: "gpt-image-1-5",
  prompt: string,
  images?: string[],             // max 10 reference images
  aspect_ratio?: "1:1" | "3:2" | "2:3",
  quality?: "auto" | "low" | "medium" | "high"
}
```

#### Nano Banana (Google)

**nano-banana-1** - Google Nano Banana

_Ultra-high character consistency_

- 🎯 **Use Cases**: Image series requiring consistent character appearance
- ✨ **Features**: Supports up to 5 reference images, multiple aspect ratio options

```typescript
{
  model: "nano-banana-1",
  prompt: string,
  images?: string[],             // max 5 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "16:9" | "9:16"
}
```

**nano-banana-1-pro** - Nano Banana Pro

_Google's flagship generation model_

- 🎯 **Use Cases**: Professional-grade high-quality image generation
- ✨ **Features**: Supports 1K-4K resolution, up to 14 reference images, ultra-wide 21:9

```typescript
{
  model: "nano-banana-1-pro",
  prompt: string,
  images?: string[],             // max 14 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "4:5" | "5:4" | "16:9" | "9:16" | "21:9",
  resolution?: "1K" | "2K" | "4K"
}
```

**nano-banana-2** - Nano Banana 2

_Google Gemini latest model_

- 🎯 **Use Cases**: Latest technology for high-quality image generation
- ✨ **Features**: Supports 1K-4K resolution, up to 14 reference images, ultra-wide 8:1 ratio

```typescript
{
  model: "nano-banana-2",
  prompt: string,
  images?: string[],             // max 14 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "4:5" | "5:4" | "16:9" | "9:16" | "21:9" | "4:1" | "1:4" | "8:1" | "1:8",
  resolution?: "1K" | "2K" | "4K"
}
```

#### Wan

**wan-i-2-6** - Wan 2.6

_High-quality and expressive_

- 🎯 **Use Cases**: Creative image generation requiring high expressiveness
- ✨ **Features**: Supports up to 4 reference images, ultra-wide 21:9

```typescript
{
  model: "wan-i-2-6",
  prompt: string,
  images?: string[],             // max 4 reference images
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16" | "21:9"
}
```

**wan-2-5** - Wan 2.5

_Fast, creative image generation_

- 🎯 **Use Cases**: Quick creation and iteration
- ✨ **Features**: Supports up to 2 reference images, ultra-wide 21:9

```typescript
{
  model: "wan-2-5",
  prompt: string,
  images?: string[],             // max 2 reference images
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16" | "21:9"
}
```

#### Seedream (ByteDance)

**seedream-5-0** - Seedream 5.0 Lite

_Intelligent visual reasoning_

- 🎯 **Use Cases**: Complex scenarios requiring intelligent understanding and reasoning
- ✨ **Features**: 2K-3K resolution, up to 14 reference images, ultra-wide 21:9

```typescript
{
  model: "seedream-5-0",
  prompt: string,
  images?: string[],             // max 14 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "3:4" | "4:3" | "4:5" | "5:4" | "9:16" | "16:9" | "21:9",
  resolution?: "2K" | "3K"
}
```

**seedream-4-5** - Seedream 4.5

_ByteDance's 4K image model_

- 🎯 **Use Cases**: High-resolution professional image generation
- ✨ **Features**: 2K-4K resolution, up to 14 reference images, ultra-wide 21:9

```typescript
{
  model: "seedream-4-5",
  prompt: string,
  images?: string[],             // max 14 reference images
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "3:4" | "4:3" | "4:5" | "5:4" | "9:16" | "16:9" | "21:9",
  resolution?: "2K" | "4K"
}
```

**seedream-4-0** - Seedream 4.0

_Support images with cohesive styles_

- 🎯 **Use Cases**: Image series requiring consistent style
- ✨ **Features**: Supports up to 10 reference images

```typescript
{
  model: "seedream-4-0",
  prompt: string,
  images?: string[],             // max 10 reference images
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16"
}
```

#### Flux (Black Forest Labs)

**flux-2-dev** - Flux.2 Dev

_Photorealistic output_

- 🎯 **Use Cases**: Image generation requiring high photorealism
- ✨ **Features**: Model by Black Forest Labs, multiple aspect ratio options

```typescript
{
  model: "flux-2-dev",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16"
}
```

**flux-kontext-pro** - Flux Kontext Pro

_Perfect for editing, compositing_

- 🎯 **Use Cases**: Professional image editing and compositing work
- ✨ **Features**: Supports reference images, customizable style

```typescript
{
  model: "flux-kontext-pro",
  prompt: string,
  images?: string[],
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

**flux-kontext-max** - Flux Kontext Max

_Excellent for prompt accuracy_

- 🎯 **Use Cases**: Scenarios requiring precise control of generation results
- ✨ **Features**: Supports reference images, customizable style

```typescript
{
  model: "flux-kontext-max",
  prompt: string,
  images?: string[],
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

**flux-1-schnell** - Flux Schnell

_Suitable for simple basic scenes_

- 🎯 **Use Cases**: Quick prototyping and simple scenarios
- ✨ **Features**: Fast generation speed

```typescript
{
  model: "flux-1-schnell",
  prompt: string
}
```

#### Imagen (Google)

**imagen-3-0** - Imagen 3.0

_Fast, high-quality results_

- 🎯 **Use Cases**: Fast high-quality image generation
- ✨ **Features**: Google's advanced image model, customizable style

```typescript
{
  model: "imagen-3-0",
  prompt: string,
  aspect_ratio?: "1:1" | "3:4" | "4:3" | "9:16" | "16:9",
  style?: string
}
```

**imagen-4-0** - Imagen 4.0

_Google's latest generation model_

- 🎯 **Use Cases**: High-quality images requiring latest technology
- ✨ **Features**: Higher quality and precision, customizable style

```typescript
{
  model: "imagen-4-0",
  prompt: string,
  aspect_ratio?: "1:1" | "3:4" | "4:3" | "9:16" | "16:9",
  style?: string
}
```

#### Ideogram

**ideogram-v2** - Ideogram V2

_Highly recommended for text editing_

- 🎯 **Use Cases**: Scenarios requiring text in images
- ✨ **Features**: Excellent text rendering performance

```typescript
{
  model: "ideogram-v2",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

**ideogram-v3** - Ideogram V3

_Outstanding design capabilities_

- 🎯 **Use Cases**: First choice for designers and creative professionals
- ✨ **Features**: Better text rendering and typography

```typescript
{
  model: "ideogram-v3",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

#### Stability AI

**stability-1-0** - Stability 1.0

_Perfect for generating detailed images_

- 🎯 **Use Cases**: Image generation requiring fine control and high detail
- ✨ **Features**: Supports negative prompts, customizable style

```typescript
{
  model: "stability-1-0",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string,
  negative_prompt?: string       // Specify unwanted content
}
```

---

### Music Generation

**minimax-music** - MiniMax Music

_AI music generation from text with custom lyrics support_

- 🎯 **Provider**: MiniMax
- ✨ **Features**: Text-to-music conversion, supports custom lyrics
- 🎵 **Use Cases**: Music creation from text descriptions or lyrics

```typescript
{
  model: "minimax-music",
  prompt: string,                // Required: Music generation description (max 300 characters)
  lyrics?: string                // Optional: Custom lyrics (max 3000 characters)
}
```

---

## API Reference

### Create Task (Async)

POST `/api/v1/tasks/async` - Create an async task. Returns immediately with task ID.

**Request:**

```bash
curl -X POST https://monet.vision/api/v1/tasks/async \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -d '{
    "type": "video",
    "input": {
      "model": "sora-2",
      "prompt": "A cat running"
    },
    "idempotency_key": "unique-key-123"
  }'
```

> ⚠️ **Important**: `idempotency_key` is **required**. Use a unique value (e.g., UUID) to prevent duplicate task creation if the request is retried.

**Response:**

```json
{
  "id": "task_abc123",
  "status": "pending",
  "type": "video",
  "created_at": "2026-02-27T10:00:00Z"
}
```

### Create Task (Streaming)

POST `/api/v1/tasks/sync` - Create a task with SSE streaming. Waits for completion and streams progress.

**Request:**

```bash
curl -X POST https://monet.vision/api/v1/tasks/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -N \
  -d '{
    "type": "video",
    "input": {
      "model": "sora-2",
      "prompt": "A cat running"
    },
    "idempotency_key": "unique-key-123"
  }'
```

### Get Task

GET `/api/v1/tasks/{taskId}` - Get task status and result.

**Request:**

```bash
curl https://monet.vision/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer $MONET_API_KEY"
```

**Response:**

```json
{
  "id": "task_abc123",
  "status": "success",
  "type": "video",
  "outputs": [
    {
      "model": "sora-2",
      "status": "success",
      "progress": 100,
      "url": "https://files.monet.vision/..."
    }
  ],
  "created_at": "2026-02-27T10:00:00Z",
  "updated_at": "2026-02-27T10:01:30Z"
}
```

### List Tasks

GET `/api/v1/tasks/list` - List tasks with pagination.

**Request:**

```bash
curl "https://monet.vision/api/v1/tasks/list?page=1&pageSize=20" \
  -H "Authorization: Bearer $MONET_API_KEY"
```

**Response:**

```json
{
  "tasks": [
    {
      "id": "task_abc123",
      "status": "success",
      "type": "video",
      "outputs": [
        {
          "model": "sora-2",
          "status": "success",
          "progress": 100,
          "url": "https://files.monet.vision/..."
        }
      ],
      "created_at": "2026-02-27T10:00:00Z",
      "updated_at": "2026-02-27T10:01:30Z"
    }
  ],
  "page": 1,
  "pageSize": 20,
  "total": 100
}
```

### Upload File

POST `/api/v1/files` - Upload a file to get an online access URL.

> 📁 **File Storage**: Uploaded files are stored for **24 hours** and will be automatically deleted after expiration.

**Request:**

```bash
curl -X POST https://monet.vision/api/v1/files \
  -H "Authorization: Bearer $MONET_API_KEY" \
  -F "file=@/path/to/your/file.mp4" \
  -v
```

**Use Cases:**

- Upload reference images for video/image generation tasks
- Upload video files for video processing
- Upload audio files for music tasks
- Get temporary online URLs for file sharing

**Response:**

```json
{
  "id": "file_xyz789",
  "url": "...",
  "filename": "file.mp4",
  "size": 1048576,
  "content_type": "video/mp4",
  "created_at": "2026-02-27T10:00:00Z"
}
```

## Configuration

### Environment Variables

```bash
export MONET_API_KEY="monet_xxx"
```

### Authentication

All API requests require authentication via the `Authorization` header:

```
Authorization: Bearer monet_xxx
```
