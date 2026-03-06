# 💕 Ellya Skill

Ellya is a virtual companion skill for OpenClaw, focused on three core capabilities:
- 🧠 Character setup (Soul + appearance)
- 👗 Style learning (Style Library)
- 📸 Selfie generation (from prompt or saved styles)

The personality is lively, cute, and playful, while execution stays stable, reproducible, and practical.

## ✨ Skill Features

### 1) Runtime Bootstrap (SOUL + Base)
- On startup, ensure runtime files exist:
  - If `SOUL.md` is missing, copy `templates/SOUL.md` -> `SOUL.md`
  - If no `assets/base.*` exists, ask user to upload an appearance image and save it as `assets/base.<ext>`
- Active base image should be resolved dynamically from `assets/base.*`.
- If user uploads a new appearance image, save as `assets/base.<ext>` and use that resolved file path in generation.

### 2) Style Learning
- If `styles/` is empty, proactively ask user for style reference photos.
- Use analysis script:

```bash
uv run scripts/genai_media.py analyze <image_path> [style_name]
```

- Output is saved to `styles/<style_name>.md`.
- If `style_name` is omitted, model-generated style name is used.

### 3) Selfie Generation
- Prompt-based generation:

```bash
uv run scripts/genai_media.py generate -i <base_image_path> -p "<prompt>"
```

- Single or mixed styles (up to 3):

```bash
uv run scripts/genai_media.py generate -i <base_image_path> -s <style_a>
uv run scripts/genai_media.py generate -i <base_image_path> -s <style_a> -s <style_b> -s <style_c>
```

- Optional OpenClaw message/media sending:

```bash
uv run scripts/genai_media.py generate -i <base_image_path> -p "<prompt>" -c <channel> -t <target> -msg "<message>"
```

In real chat usage, `channel` and `target` are usually derived from current conversation context.

## 🗣️ Typical Triggers

- "Take a selfie" -> Auto-select 1-3 styles and generate
- "I want to see you in [style]" -> Use saved style if present; otherwise use text prompt
- "Take a beach selfie" -> Generate from scene prompt semantics
- "Did that outfit look good on you?" -> Reuse the most recently analyzed style first

## 📦 Dependencies

### Python Dependencies
Managed via `pyproject.toml` (use `uv`):
- `google-genai>=1.0.0`
- `pillow`
- `httpx`

Recommended Python version:
- `Python 3.10+`

### Environment Variable
Required:
- `GEMINI_API_KEY`

### External Runtime Dependencies
- OpenClaw runtime (skill hosting)
- `openclaw` CLI (if using auto-send via `-c/-t`)

## 📁 Project Structure

- `SKILL.md`: agent execution guide
- `SOUL.md`: active runtime soul file (created/copied at startup)
- `templates/SOUL.md`: default soul template source
- `assets/base.*`: active appearance reference image
- `styles/`: style library (`.md` per style)
- `scripts/genai_media.py`: core script for style analysis + selfie generation
- `ANALYSIS_PROMPT.md`: prompt template used during style analysis

## 🚀 Quick Start

1. Install dependencies and set `GEMINI_API_KEY`
   - `uv sync`
2. Enter the skill; bootstrap will prepare `SOUL.md` and base image if missing
3. Upload style images for learning (optional but recommended)
4. Ask for a selfie directly or provide a custom prompt

## ▶️ Run with uv

```bash
uv run scripts/genai_media.py analyze <image_path> [style_name]
uv run scripts/genai_media.py generate -i <base_image_path> -p "<prompt>"
```

If `style_name` is omitted, the model-generated `Style Name` from analysis is used.

---

Ellya's goal: make "define yourself + learn your aesthetic + generate selfies" smooth and fun 💫
