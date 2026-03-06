# Draw Images by APIYI

Simple image generation skill using APIYI API.

## Usage

### Slash Command
```
/draw-images-by-apiyi a cute cat wearing sunglasses
/draw-images-by-apiyi a sunset over mountains -r 2K
```

### Natural Language
Just ask:
- "Draw a cute cat for me"
- "Generate an image of a sunset"
- "Can you create a picture of a robot?"

### Command Line
```bash
# Basic
uv run generate_image.py "a cute cat" -f cat.png

# With resolution
uv run generate_image.py "a sunset" -f sunset.png -r 2K

# With API key
uv run generate_image.py "a robot" -f robot.png --api-key YOUR_KEY
```

## Setup

1. Get API key from https://apiyi.com/
2. Set environment variable:
   ```bash
   export APIYI_API_KEY=your-key-here
   ```

## Output

Images are saved to the current workspace directory.

---

**Skill location:** `~/.openclaw/skills/draw-images-by-apiyi/`
