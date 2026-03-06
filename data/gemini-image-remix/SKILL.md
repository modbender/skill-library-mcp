---
name: gemini-image-remix
description: Advanced image generation and remixing using Gemini. Supports Gemini 2.5 Flash Image (default) and models like Gemini 3.0 Pro (Nano Banana Pro).
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
        "primaryEnv": "GEMINI_API_KEY",
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

# Gemini Image Remix

A versatile tool for text-to-image generation and complex image-to-image remixing. By default, it uses **Gemini 2.5 Flash Image** for fast, high-quality results. It also supports flagship models like **Gemini 3.0 Pro (Nano Banana Pro)** for advanced artistic tasks.

## Generate Image

Create stunning visuals from a text prompt.

```bash
uv run {baseDir}/scripts/remix.py --prompt "a cybernetic owl in a neon forest" --filename "owl.png"
```

## Remix/Modify Image

Use one or more reference images to guide the generation. Perfect for style transfers, background changes, or character modifications.

```bash
uv run {baseDir}/scripts/remix.py --prompt "change the art style to a pencil sketch" --filename "sketch.png" -i "original.png"
```

## Multi-image Composition

Combine elements from up to 14 different images into a single cohesive scene.

```bash
uv run {baseDir}/scripts/remix.py --prompt "place the character from image 1 into the environment of image 2" --filename "result.png" -i "character.png" -i "env.png"
```

## Advanced Model Selection

Switch to advanced models like **Nano Banana Pro** for high-fidelity work.

```bash
uv run {baseDir}/scripts/remix.py --model "gemini-3-pro-image-preview" --prompt "highly detailed oil painting of a dragon" --filename "dragon.png"
```

## Options

- `--prompt`, `-p`: Image description or specific edit instructions.
- `--filename`, `-f`: The output path for the generated PNG.
- `--input-image`, `-i`: Path to an input image (repeatable up to 14 times).
- `--resolution`, `-r`: `1K` (default), `2K`, or `4K`.
- `--aspect-ratio`, `-a`: Output aspect ratio (e.g., `1:1`, `16:9`, `9:16`, `4:3`, `3:4`).
- `--model`, `-m`: Model to use (defaults to `gemini-2.5-flash-image`). Supported: `gemini-2.5-flash-image`, `gemini-3-pro-image-preview`.
- `--api-key`, `-k`: Gemini API key (defaults to `GEMINI_API_KEY` env var).
