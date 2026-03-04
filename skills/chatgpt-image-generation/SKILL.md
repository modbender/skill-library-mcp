---
name: chatgpt-image-generation
description: Generate and download images from chatgpt.com using Playwright automation. Opens chatgpt.com in a new chat, types prompts, waits for bulletproof generation completion detection, downloads via hover+download button, then processes next or stops.
---

# ChatGPT Image Generation Skill

Use Playwright to automate ChatGPT web UI for free image generation (no API costs).

## Prerequisites

```bash
# Install Playwright
npm install playwright

# Install Chromium browser
npx playwright install chromium
```

## Usage

```bash
# Generate images from prompts file
node skills/chatgpt-image-generation/scripts/generate.js --prompts prompts.json --output ./images

# Resume from a specific index
node skills/chatgpt-image-generation/scripts/generate.js --prompts prompts.json --output ./images --start 5

# Use a specific Chrome profile
node skills/chatgpt-image-generation/scripts/generate.js --prompts prompts.json --output ./images --profile "~/Library/Application Support/Google/Chrome/YourProfile"

# Run in headless mode (no browser window)
node skills/chatgpt-image-generation/scripts/generate.js --prompts prompts.json --output ./images --headless
```

## Prompt File Format

```json
["prompt 1", "prompt 2"]
```

or

```json
{ "prompts": ["prompt 1", "prompt 2"] }
```

## Bulletproof Completion Detection

The detection method checks ALL of the following (must pass):

1. **Send button re-enabled** — `button[data-testid="send-button"]` is no longer disabled
2. **Image exists** — `img[alt="Generated image"]` present with `naturalWidth >= 1024` AND `naturalHeight >= 1024`
3. **Download button visible** — Download button appears on hover and is enabled
4. **Image src stable** — Same src URL detected across 2+ consecutive checks (ensures generation fully done)
5. **No progress spinner** — No visible `[role="progressbar"]` or spinner elements

This multi-signal approach prevents:
- Downloading before generation finishes
- Downloading placeholder/thumbnail images
- Missing the download button
- Downloading mid-generation

## Download Method

1. Hover over the generated image to reveal the download button
2. Click the download button (uses Playwright `expect_download()`)
3. Save directly to numbered output file

## Output

- Numbered image files: `001.png`, `002.png`, etc.
- `results.jsonl` — log of success/failure per prompt

## Login (One-Time)

If not logged in:
1. Run script once (it will open browser visible)
2. Sign into ChatGPT
3. Session persists for future runs (uses persistent profile)

## Platform Support

- **macOS**: `~/Library/Application Support/Google/Chrome/`
- **Windows**: `%LOCALAPPDATA%\Google\Chrome\User Data\`
- **Linux**: `~/.config/google-ch script autorome/`

The-detects your OS and uses the appropriate default profile path.

---

## 💡 Optional Enhancements

### Use a Dedicated Chrome Profile

**Benefit:** Keep your image generation sessions separate from your normal Chrome browsing. Creates a clean, dedicated environment.

**How:** Pass `--profile` with a custom profile path:
```bash
--profile ~/Library/Application\ Support/Google/Chrome/ImageGenProfile
```

Create a new profile in Chrome first, then use its path.

### Organize Images in a ChatGPT Project

**Benefit:** Keep all auto-generated images organized in one project folder in ChatGPT, making it easy to find and review them later.

**How:** Modify the script to add project selection (see free-image-generation skill as reference). The free-image-generation skill includes this feature by default.

---

## Differences from free-image-generation

This skill:
- ✅ Opens a new chat window (no project selection)
- ✅ Uses default Chrome profile (can specify custom with --profile)

The [free-image-generation](/skills/free-image-generation) skill:
- ✅ Automatically selects "Auto Image Generation" project
- ✅ Uses dedicated ImageGenProfile by default
