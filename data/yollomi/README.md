# Yollomi AI Image Generator (All Models)

An AI image generator skill for OpenClaw. Image generation for text-to-image and image-to-image, across many AI image models via one unified Yollomi API.

Keywords: image, ai image, image generator, image generation, text-to-image, image-to-image, multimodel.

> Note: Video generation is temporarily disabled in this build.

## Install (ClawHub)

```bash
clawhub install yollomi
```

## Configuration

Set the following environment variable for OpenClaw:

- `YOLLOMI_API_KEY` (required)

## Usage

Ask the agent to generate an image. The skill uses the unified endpoint:

`POST /api/v1/generate` with `{ type: "image", modelId, ... }`

See [SKILL.md](SKILL.md) and [models-reference.md](models-reference.md) for modelIds and parameters.
