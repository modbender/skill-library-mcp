---
name: clawpet
description: "OpenClaw pet companion skill. Manage adopted pets, run interactions, and produce pet image prompts."
metadata:
  openclaw:
    requires:
      anyBins: [clawpet, uv, uvx]
    install:
      - id: clawpet-git
        kind: pip
        package: "git+https://github.com/yazelin/clawpet.git"
        bins: [clawpet]
        label: "Install clawpet from GitHub"
---

# clawpet — OpenClaw Pet Companion 🐾

Use this skill when the user wants to adopt a pet, check pet status, interact with the pet, or send a pet image.
Pet status includes passive time-based updates, so each check-in can reflect elapsed time.

## Typical triggers
- "我想養一隻貓"
- "我的寵物今天狀態如何？"
- "幫我餵牠"
- "讓牠拍一張照"

## Command reference

### 1) List pets
```bash
bash {baseDir}/scripts/clawpet.sh pets
```

### 2) Adopt a pet
```bash
bash {baseDir}/scripts/clawpet.sh adopt momo
```

### 3) Check current status
```bash
bash {baseDir}/scripts/clawpet.sh status
```

### 4) Interact with pet
```bash
bash {baseDir}/scripts/clawpet.sh interact feed
bash {baseDir}/scripts/clawpet.sh interact play
bash {baseDir}/scripts/clawpet.sh interact rest
```

### 5) Generate image prompt
```bash
bash {baseDir}/scripts/clawpet.sh prompt
bash {baseDir}/scripts/clawpet.sh prompt --place "sunny window" --style "photorealistic, professional pet photography"
```
Outputs the full image generation prompt text. Default style is photorealistic.

### 6) Auto care
```bash
bash {baseDir}/scripts/clawpet.sh care
bash {baseDir}/scripts/clawpet.sh care --action feed
```

## Agent behavior guidance

### Basic interactions
1. Always call `bash {baseDir}/scripts/clawpet.sh ...` to avoid missing executable issues.
2. When user says they want a pet, first run `bash {baseDir}/scripts/clawpet.sh pets`, then ask which one they want.
3. For regular check-ins, run `bash {baseDir}/scripts/clawpet.sh status`.
4. For daily care, prefer `bash {baseDir}/scripts/clawpet.sh care`; for explicit requests, run `... interact <action>`.

### Image generation workflow (IMPORTANT)
When the user requests a pet image:

1. **Generate the prompt:**
   ```bash
   bash {baseDir}/scripts/clawpet.sh prompt --place "cozy afternoon window"
   ```
   This outputs the full prompt text. Default style is photorealistic pet photography.

2. **Generate the image with nano-banana-pro:**
   ```bash
   uv run /home/yaze/.npm-global/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
     --prompt "<prompt from step 1>" \
     --filename "YYYY-MM-DD-HH-MM-pet-name.png" \
     --resolution 1K
   ```
   This saves the image to `/home/yaze/.openclaw/workspace/YYYY-MM-DD-HH-MM-pet-name.png`

3. **Send the image with message tool:**
   ```
   message(action="send", channel="telegram", media="/home/yaze/.openclaw/workspace/YYYY-MM-DD-HH-MM-pet-name.png", message="🐾 <pet_name> 的即時快照")
   ```

**Why this workflow:**
- Uses Gemini (nano-banana-pro) for high-quality watercolor-style images
- Local file path works with message tool's media parameter
- Consistent with other OpenClaw image generation patterns

## Troubleshooting
- If `clawpet` command is not found, this skill wrapper auto-falls back to:
  - `uvx --from git+https://github.com/yazelin/clawpet.git clawpet ...`
  - `uv tool run --from git+https://github.com/yazelin/clawpet.git clawpet ...`
