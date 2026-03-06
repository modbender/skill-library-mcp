# Card generation SOP (optional)

Goal: After logging a pee/poop event, optionally generate a **consistent, cute, lighthearted** 3:4 vertical card image.

## Dependency

This skill **does not ship an image generator**.

If (and only if) the user has installed **`nano-banana-pro`**, use it to generate the card image. If it is not installed, **skip** card generation.

### How to detect `nano-banana-pro`

- Check if this path exists:
  - `/Users/herve.clawd/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py`

If missing: do nothing.

## Output constraints

- Output must be a PNG in a Telegram-allowed local directory:
  - `~/.openclaw/media/excretion-cards/`

## Card style (keep consistent)

- Ratio: **3:4** vertical
- Theme: **cute, playful, non-judgmental**, sticker-style icons
- Palette: pastel / soft
- Layout: consistent grid (title + 4–5 blocks)
- Text: large and readable, avoid long paragraphs
- Keep content minimal:
  - Type (Pee/Poop)
  - Date/time
  - Duration
  - Color
  - Pain (0–3)
  - If Poop: Bristol (1–7)
- Do **not** include medical advice on the image

## Prompt template

Use a prompt like this (fill placeholders):

```
Design a cute, lighthearted, playful vertical 3:4 card infographic, pastel colors, rounded corners, sticker-style icons.

Title: "Bathroom log" + Chinese subtitle "厕所记录"
Subheader: "{date} {time}".

Blocks (big text):
- Type: Pee / Poop（小便/大便）
- Duration: {minutes} min（持续时间）
- Color: {color_title_case}（颜色）
- Pain: {pain}/3（痛感）
- If poop: Bristol: {bristol}（形态）

Add a small cute mascot (droplet for pee / friendly poop icon for poop), but keep it tasteful.
No realistic photos. No medical advice.
Use a consistent grid layout.
```

## How to run Nano Banana Pro (example)

```bash
mkdir -p ~/.openclaw/media/excretion-cards
uv run /Users/herve.clawd/.openclaw/workspace/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "<PROMPT>" \
  --filename "$HOME/.openclaw/media/excretion-cards/excretion-card-YYYY-MM-DD-HH-MM-SS.png" \
  --resolution 1K
```

Note: `nano-banana-pro` handles its own API key configuration through OpenClaw.
