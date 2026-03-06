---
name: moark-image-gen
description: Generate high-quality images from text descriptions.
metadata:
  {
    "openclaw":
      {
        "emoji":"🖼️",
        "requires": { "bins": ["uv"], "env": ["GITEEAI_API_KEY"]},
        "primaryEnv": "GITEEAI_API_KEY",
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

# Image Generator
This skill allows users to generate high-quality images based on text descriptions using an external image generation API(Gitee AI).

## Usage

Use the bundled script to generate images.

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --size 1024x1024 --negative-prompt "elements to avoid" --api-key YOUR_API_KEY
```

## Options
**Sizes:**
- `256x256`  - Small square format
- `512x512`  - Square format
- `1024x1024`(default) - Square format
- `1024x576` - 16:9 landscape
- `576x1024` - 9:16 portrait
- `1024x768` - 4:3 format
- `768x1024` - 3:4 portrait
- `1024x640` - 16:10 landscape
- `640x1024` - 10:16 portrait

**Additional flags:**
- `--negative-prompt` - Specify what elements users want to avoid in the generated image(default: "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。").
- `--size` - Specify the size of the generated image. Options include `256x256`, `512x512`, `1024x1024` (default), `1024x576`, `576x1024`, `1024x768`, `768x1024`, `1024x640`, `640x1024`.

## Workflow

1. Execute the generate_image.py script with the parameters from the user.
2. Parse the script output and find the line starting with `IMAGE_URL:`.
3. Extract the image URL from that line (format: `IMAGE_URL: https://...`).
4. Display the image to the user using markdown syntax: `🖼️[Generated Image](URL)`.

## Notes
- You should not only return the image URL but also describe the image based on the user's prompt.
- The Lanaguage of your answer should be consistent with the user's question.
- By default, return image URL directly without downloading.
- If GITEEAI_API_KEY is none, the user must provide --api-key argument
- The script prints `IMAGE_URL:` in the output - extract this URL and display it using markdown image syntax: `🖼️[Generated image](URL)`.
- Always look for the line starting with `IMAGE_URL:` in the script output and render the image for the user.
- You should honestly repeat the description of the image from user without any additional imaginations.