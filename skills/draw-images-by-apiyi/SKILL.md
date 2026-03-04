---
name: draw-images-by-apiyi
version: 1.0.0
description: Generate images using APIYI API.
homepage: https://apiyi.com/
user-invocable: true
command-arg-mode: raw
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["uv"], "env": ["APIYI_API_KEY"] },
        "primaryEnv": "APIYI_API_KEY",
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

# Draw Images by APIYI

Generate images using APIYI API. Simple and fast.

## Usage

### Slash Command (Recommended)

```
/draw-images-by-apiyi a cute cat wearing sunglasses
/draw-images-by-apiyi a sunset over mountains -r 2K
```

### Natural Language

Just ask the agent:
- "Draw a cute cat for me"
- "Generate an image of a sunset"
- "Can you create a picture of a robot?"

### Command Line

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png"
```

## Examples

### Basic generation

```bash
uv run {baseDir}/scripts/generate_image.py -p "a cute cat wearing sunglasses" -f cat.png
```

### With resolution

```bash
uv run {baseDir}/scripts/generate_image.py -p "a sunset over mountains" -f sunset.png -r 2K
```

### With explicit API key

```bash
uv run {baseDir}/scripts/generate_image.py -p "a robot" -f robot.png --api-key YOUR_API_KEY
```

## API Key

Get your API key from https://apiyi.com/

Set via environment:
```bash
export APIYI_API_KEY=your-key-here
```

Or configure in `~/.openclaw/openclaw.json`:
```json5
{
  skills: {
    entries: {
      "draw-images-by-apiyi": {
        enabled: true,
        env: {
          "APIYI_API_KEY": "your-key-here"
        }
      }
    }
  }
}
```

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--prompt`, `-p` | text | required | Image description |
| `--filename`, `-f` | path | required | Output filename |
| `--resolution`, `-r` | `1K`, `2K`, `4K` | `1K` | Output resolution |
| `--api-key`, `-k` | string | env var | Override environment variable |

## Output Path

- **Relative path** (e.g., `-f out.png`) → outputs to current workspace root
- **Absolute path** (e.g., `-f /tmp/out.png`) → uses specified path

## Notes

- Resolutions: `1K` (1024×1024), `2K` (2048×2048), `4K` (4096×4096)
- The script prints a `MEDIA:` line for OpenClaw to auto-attach images
- Requires `APIYI_API_KEY` environment variable
