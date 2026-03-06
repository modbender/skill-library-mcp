---
name: article-illustrator
description: Insert scrapbook-style illustrations into articles using image generation (GLM or OpenRouter). Use when the user wants to add images to an article, create illustrated content, or requests "illustrate this article", "add images to this article", "generate pictures for this post", "insert illustrations".
---

# Scrapbook-Style Illustration Inserter

Transform articles into illustrated markdown by generating hand-crafted scrapbook-style images and inserting them at logical break points.

> **Attribution:** Based on [glm-image](https://github.com/ViffyGwaanl/glm-image) by ViffyGwaanl (MIT License).

## Setup

The bundled `scripts/generate.py` supports two providers. You need at least one:

### Option A: GLM (BigModel / Zhipu AI) — preferred for Chinese text

1. Register at https://bigmodel.cn
2. Set your key via any of:
   - `export GLM_API_KEY="your-key"`
   - Add `"glm_api_key": "your-key"` to `~/.openclaw/config.json`
   - Add `GLM_API_KEY=your-key` to `.env` in the skill directory

### Option B: OpenRouter — broader model selection, best for English

1. Register at https://openrouter.ai
2. Set your key via any of:
   - `export OPENROUTER_API_KEY="your-key"`
   - Add `"openrouter_api_key": "your-key"` to `~/.openclaw/config.json`
   - Add `OPENROUTER_API_KEY=your-key` to `.env` in the skill directory

Default OpenRouter model: `openai/gpt-5-image-mini` (strong text rendering for scrapbook prompts).

**Auto-detection:** If both keys are present, GLM is preferred. Use `--provider openrouter` or `--provider glm` to override.

## Inputs

- **article**: The full article text (markdown or plain text)
- **image_count** (optional): Number of images to generate, 2–5 (default: 3)
- **orientation** (optional): `portrait` (1088x1920, default) or `landscape` (1920x1088)
- **language** (required): Language for text in generated images — `zh`, `en`, `ja`, `ko`, `fr`, `de`, `es`. Always ask the user; never default or infer.

## Workflow

### Step 0: Check API Key

Run a quick check — if neither `GLM_API_KEY` nor `OPENROUTER_API_KEY` is found, stop and tell the user how to configure (see Setup above). Do not proceed without a valid key.

### Step 1: Validate Input

Before generating any images:
- Confirm article is at least 200 words. If shorter, warn user: "Article may be too short for meaningful illustration — proceed anyway?"
- Count major sections or topic transitions (H2 headings, paragraph breaks). This determines insertion points.
- Ask the user which language to use for image text. Never infer from the article language.

### Step 2: Generate Image Prompts

Read the scrapbook system prompt from `references/scrapbook-prompt.md`.

**Language handling:**
- Default (`zh`): generate image descriptions in Chinese as the scrapbook prompt produces
- If `language=en` or other: after generating the JSON plan, translate all `title` and `description` fields to the target language before passing to generate.py. Keep the JSON structure identical.

Using that prompt, analyze the article and output a JSON plan:

```json
{
  "project_title": "Article title — Scrapbook Style",
  "style": "Physical Mixed-Media Scrapbook",
  "total_images": 3,
  "images": [
    {
      "image_id": 1,
      "title": "Image caption",
      "description": "300-500 character visual description in scrapbook style...",
      "insert_after": "Exact sentence or heading after which to insert the image"
    }
  ]
}
```

Target 1 image per 300–400 words of article content.

### Step 3: Generate All Images in Parallel

**CRITICAL: Launch all image generations simultaneously.** Each generation takes 20–40 seconds. Sequential generation wastes the user's time. Use background processes or concurrent exec calls to run all images at once.

For each image in the JSON plan, run the bundled script (all at the same time):
```bash
# Launch ALL images concurrently — do NOT wait for one to finish before starting the next
python3 scripts/generate.py "<description_1>" --language <lang> --size 1088x1920 &
python3 scripts/generate.py "<description_2>" --language <lang> --size 1088x1920 &
python3 scripts/generate.py "<description_3>" --language <lang> --size 1088x1920 &
wait  # Wait for all to complete
```

In an OpenClaw agent context, use concurrent `exec` tool calls (one per image) rather than sequential calls. The agent MUST issue all exec calls in a single tool-use turn so they run in parallel.

Additional flags:
- `--provider glm|openrouter` — override auto-detection
- `--model <model>` — override OpenRouter model (default: `openai/gpt-5-image-mini`)

The script automatically:
- Appends a margin guard instruction (OpenRouter only) to prevent edge clipping
- Displays cost per image at the end of each run

**On failure:** If generation fails for one image, log the error and continue with remaining images. Do not abort the entire run. Note failed images in the output with `[Image generation failed: <error>]`.

Collect: image URL/local path and cost for each successful image.

### Step 4: Compose Final Markdown

Insert each image after its designated `insert_after` anchor:

```markdown
![Image caption](image_url)
```

If the `insert_after` anchor is not found verbatim, insert at the nearest paragraph break.

## Output Format

Return the complete markdown article with:
1. All original article text preserved exactly
2. Generated images inserted at logical break points
3. Captions from the JSON plan
4. A summary line at the end: `<!-- Illustrated: N images generated, M failed, total cost: $X.XX -->`

## Agent Owner

Executed by the main OpenClaw agent session. No sub-agents spawned. The agent reads the article, generates prompts, invokes generate.py for each, and composes output in a single session.

## Success Criteria

Succeeds when:
1. Article validated (length check passed or user confirmed)
2. Image prompt JSON generated with 2–5 entries
3. At least one image successfully generated
4. Final markdown returned with images inserted

## Edge Cases

- **Short article (<200 words)**: Warn and confirm before proceeding
- **Generation failure**: Log error inline, continue with other images — do not abort
- **Anchor not found**: Insert at nearest paragraph break instead
- **No API key**: Surface error immediately with setup instructions
- **All images fail**: Return original article unchanged with error summary

## Tips

- Generate 2–5 images depending on article length
- Insert images after major topic transitions (not mid-paragraph)
- Keep descriptions faithful to the scrapbook style in `references/scrapbook-prompt.md`
- Portrait orientation (1088x1920) works best for inline article images
- OpenRouter with gpt-5-image-mini costs ~$0.045–0.050 per image
- GLM costs ~¥0.10 (~$0.014) per standard image
