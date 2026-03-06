---
name: anima
description: Anima Avatar - Interactive Video Generation Engine. Generates 16:9
  videos with dynamic character sprites (Shutiao), synced audio (Fish Audio),
  and text overlay.
---


# Anima Avatar (Project Anima)

Generates high-quality interactive videos where Shutiao speaks the text with appropriate expressions, gestures, and voice.

## Capabilities
- **True Voice**: Uses Fish Audio API for realistic speech synthesis.
- **Dynamic Sprites**: Auto-selects from a library of 30+ sprites (Happy, Angry, Shy, Think, Action) based on emotion tags.
- **Smart Director**: Handles parallel rendering, audio-sync, and video composition (FFmpeg).
- **Pro Delivery**: Uploads as native stream to Feishu for direct playback (with correct duration).

## Structure
- `src/director.js`: The core engine. Generates frames (sharp + SVG), audio (Fish Audio), and video (FFmpeg).
- `src/send_video_pro.js`: Delivery script. Handles transcoding, duration calculation, and Feishu upload.
- `src/batch_generator.js`: Batch sprite generator. Uses Gemini image generation to produce sprite variants.
- `assets/sprites/`: The sprite library (1920x1080 PNG files).
- `assets/production_plan.csv`: The asset registry (25 sprites).
- `assets/manifest.json`: Sprite metadata for reference.
- `output/`: Generated videos.

## IMPORTANT: Sprites Not Included

**ClawHub only distributes text files.** The sprite PNG images are **not included** in the published package.

After installing, follow the steps below **in order** to prepare your sprites before first use.

All image generation steps use **Gemini API (Nano Banana)** as the AI image generator. It works by "reference image + text prompt" — you give it an existing image and a text description of what to change, and it returns a new image with the changes applied. This is how both the base sprite (character + background fusion) and all expression variants are created.

### Step 1: Prepare your character image

You need a **standalone character illustration** (transparent background PNG recommended).

- This is your character's "identity" — it defines the look for all sprites.
- Resolution: at least 1920x1080. Full-body is best.
- Example: a full-body anime character PNG with transparent background.

Save it somewhere accessible (e.g. `avatars/my_character.png`).

### Step 2: Prepare your background image

You need a **background scene** for the character to stand in.

- This is the environment that appears behind the character in every video frame.
- Resolution: at least 1920x1080.
- Example: a cherry blossom garden, a classroom, a city street.

Save it at: `assets/backgrounds/` (e.g. `assets/backgrounds/cherry_blossom_bg.png`).

### Step 3: Fuse character + background into base sprite

This step uses **Gemini (Nano Banana) image generation** to merge your character onto the background. The AI sees both images and creates a natural-looking composite — this is NOT a simple overlay/paste, but an AI-generated fusion that handles lighting, shadows, and blending.

How to do it:

**Method A: Use Gemini directly (recommended)**
Use any Gemini-compatible image generation tool (like Nano Banana, Google AI Studio, or the Gemini API) with:
- **Input image**: Your background image
- **Reference/overlay**: Your character image
- **Prompt**: e.g. "Place this character naturally in the center of this background scene, full body visible, gentle smile"

Save the output as: `assets/sprites/shutiao_base.png`

**Method B: Use the built-in compose script (simple overlay)**
If you just want a quick mechanical overlay (no AI blending), `src/compose_base.js` can paste your character onto the background using sharp:
1. Edit `src/compose_base.js` — update `BG_PATH` and `AVATAR_PATH` to point to your files.
2. Run: `node src/compose_base.js`
3. Output: `assets/sprites/shutiao_base.png`

Note: Method B is a plain image composite. Method A (Gemini) produces much better results because it handles lighting and integration naturally.

### Step 4: Plan your sprite variants

Now that you have a base sprite, plan what expression/pose variants you want.

Open `assets/production_plan.csv` and customize it:

```
ID,Emotion,Variant,Description,Filename,Prompt,Status
001,Base,v1,Standard,shutiao_base.png,gentle smile looking at viewer,Done
003,Happy,v1,Smile,shutiao_happy.png,big happy smile eyes closed,Pending
007,Angry,v1,Pout,shutiao_angry.png,angry face pouting,Pending
...
```

Column meanings:
- **Emotion**: Category used by the video director to pick sprites (Happy, Angry, Shy, Think, Sad, Action, Base).
- **Filename**: Output filename. Must follow `shutiao_<emotion>_<variant>.png` format.
- **Prompt**: Describes how this variant differs from the base. The generator sends the base image + this prompt to Gemini, asking it to change only the expression/pose while keeping everything else the same.
- **Status**: `Pending` = will be generated. `Done` = already exists, skip.

The default CSV has 25 entries. You can add, remove, or modify rows freely.

### Step 5: Generate sprite variants

This step uses **Gemini (Nano Banana) image generation** again. For each `Pending` row, the batch generator sends your base sprite + the prompt to Gemini, asking: "Same image, change facial expression to [prompt]. Keep clothes and background exactly same."

1. Set your Gemini API key in `skills/anima/.env`:
```ini
GEMINI_API_KEY=your_key_here
```

2. Make sure `assets/sprites/shutiao_base.png` (or `shutiao_base_1k.png`) exists from Step 3.

3. Run the batch generator:
```bash
node skills/anima/src/batch_generator.js
```

What happens:
- Reads `production_plan.csv`
- Finds all rows with `Status=Pending`
- For each: sends the base sprite + prompt to Gemini API
- Saves the generated image as a PNG in `assets/sprites/`
- Updates the CSV row to `Status=Done`
- Waits 10 seconds between generations (API rate limit cooldown)

### Step 6: Verify

Check that `assets/sprites/` now has a PNG file for every row in `production_plan.csv`:
```bash
ls assets/sprites/*.png | wc -l
```

Then do a quick test run:
```bash
node skills/anima/run.js --preview --script '[{"text":"Test","emotion":"Happy"}]'
```

Check the generated frame at `temp/frame_0.png` — you should see your character with the text overlay.

If a sprite is missing at runtime, the director will fall back to a white background with a warning in the console.

## Setup & Requirements

### 1. System Dependencies
- **ffmpeg** (required for video processing):
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: Download/Install FFmpeg and add to PATH.

### 2. Node Dependencies
Install inside the skill folder:
```bash
cd skills/anima
npm install
```

The only native dependency is `sharp`, which ships prebuilt binaries for all major platforms via N-API. It does **not** need recompilation when Node versions change — install once, run everywhere.

### 3. External Services (API Keys Required)

This skill depends on two external services. You need to provide your own API keys.

#### Fish Audio (TTS - Text to Speech)
- **What**: Generates realistic voice audio from text.
- **Used by**: `src/director.js` (the `generateAudio()` function).
- **Get a key**: https://fish.audio/dashboard/api
- **Env vars needed**:
  - `FISH_AUDIO_KEY` — Your API key (starts with `sk-...` or a hex string).
  - `FISH_AUDIO_REF_ID` — The voice model reference ID. You can use Fish Audio's default models or clone your own voice.

#### Gemini API (Image Generation - Optional)
- **What**: Generates sprite variants using Google Gemini image generation.
- **Used by**: `src/batch_generator.js` (only needed if you want to create new sprite variants).
- **Self-contained**: No external skills needed. `batch_generator.js` calls the Gemini API directly via curl.
- **Get a key**: https://aistudio.google.com/apikey
- **Env var needed**: `GEMINI_API_KEY`
- **Not needed** for normal video generation — only for creating new character sprites.

#### Feishu / Lark (Delivery - Optional)
- **What**: Uploads videos to Feishu as native media messages.
- **Used by**: `src/send_video_pro.js`.
- **Env vars needed**:
  - `FEISHU_APP_ID` — Your Feishu app ID.
  - `FEISHU_APP_SECRET` — Your Feishu app secret.
- **Not needed** if you only use `--preview` mode.

### 4. Environment Configuration
Create a `.env` file **inside the skill folder** (`skills/anima/.env`):
```ini
# Fish Audio (Required for TTS)
FISH_AUDIO_KEY=your_key_here
FISH_AUDIO_REF_ID=your_model_ref_id_here

# Gemini (Optional, for sprite generation)
GEMINI_API_KEY=your_key_here

# Feishu/Lark (Optional, for delivery)
FEISHU_APP_ID=cli_...
FEISHU_APP_SECRET=...
```

**Important**: The `.env` file is loaded from the skill folder first (least-privilege). Never commit `.env` files — the `.clawignore` already excludes it.

## Usage

### Generate & Send
```bash
# Basic usage (Demo script)
node skills/anima/run.js --target "ou_..."

# With custom script (JSON string)
node skills/anima/run.js --target "ou_..." --script '[{"text":"Hello World","emotion":"Happy"}]'

# With custom script (File)
node skills/anima/run.js --target "ou_..." --script "path/to/script.json"

# Preview only (No upload)
node skills/anima/run.js --script '[{"text":"Test","emotion":"Happy"}]' --preview
```

### One-Liner (for agent use)
```bash
node skills/anima/run.js --target "<open_id>" --script '[{"text":"Hello","emotion":"Happy"}]'
```

## Script Format
Each scene in the script is a JSON object:
```json
[
  { "text": "Hello boss!", "emotion": "Happy" },
  { "text": "Let me think...", "emotion": "Think" },
  { "text": "I got it!", "emotion": "Action" }
]
```

**Available emotions**: `Base`, `Happy`, `Angry`, `Shy`, `Think`, `Sad`, `Action`.

## Extension: Custom TTS

To use a different TTS provider (e.g., OpenAI, ElevenLabs):

1. Open `src/director.js`.
2. Locate the `generateAudio(text, filename)` function.
3. Replace the Fish Audio API call with your provider's logic.
4. **Contract**: The function must return: `{ path: "/path/to/audio.wav", duration: 1.5 }` (duration in seconds).

## Advanced: Adding More Sprite Variants

To add new expressions or poses after the initial setup:

1. Add a new row to `assets/production_plan.csv` with `Status=Pending`.
2. Write a clear prompt describing the change from the base (e.g. `angry expression, arms crossed, looking away`).
3. Run `node src/batch_generator.js` — it will only process `Pending` rows.
4. The new sprite will auto-register in the director's emotion pool via `loadSprites()`.

See `ASSETS_PLAN.md` for the full production matrix and design philosophy.

## Troubleshooting
- **Duration 00:00**: Ensure `send_video_pro.js` calculates duration in **ms** and passes it to both upload and message payload.
- **Fish Audio 400**: Check that your Ref ID matches the API Key owner's model.
- **Video Black**: Check `ffmpeg` transcoding logs and verify source frame images in `temp/frame_*.png`.
- **SVG text not rendering**: Ensure the system has CJK fonts installed (macOS has them by default; on Linux: `sudo apt install fonts-noto-cjk`).
- **No audio fallback**: If `FISH_AUDIO_KEY` is missing, the skill falls back to macOS `say` command (English only).
