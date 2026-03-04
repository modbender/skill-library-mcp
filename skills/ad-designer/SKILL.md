---
name: ad-designer
description: Generate marketing ad images using Nano Banana Pro (Gemini 3 Pro Image). Accepts campaign-planner creative briefs, reads brand bible for visual style, constructs marketing-optimized prompts, and produces platform-ready images at correct aspect ratios. Supports 1:1, 9:16, 16:9, 4:5 formats. Includes self-review loop to catch hallucinated logos, wrong text, and quality issues. Draft-first workflow (1K fast iteration, 4K final). Outputs to /tmp/marketing/assets/images/.
---

# Ad Designer

Generate marketing ad images from campaign-planner creative briefs. Wrap nano-banana-pro with brand-aware prompt construction, aspect ratio handling, and a self-review loop that catches quality issues before marking images final.

## Roles

- **Ad Designer** (this skill) — sole executor
- **nano-banana-pro** — image generation engine (upstream dependency)
- **campaign-planner** — upstream source of creative briefs
- **brand-bible-builder** — upstream source of brand visual identity

---

## Prerequisites

Verify before starting:

```bash
command -v uv
test -n "$GEMINI_API_KEY"
test -f ~/.codex/skills/nano-banana-pro/scripts/generate_image.py
```

If `uv` is missing: tell the user to install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`.
If `GEMINI_API_KEY` is unset: tell the user to export it from Google AI Studio.
If the script is missing: tell the user the nano-banana-pro skill must be installed first.

---

## Step 1: Collect Inputs

Identify which inputs are present in the conversation or filesystem:

| Input | Source | Where to find it |
|-------|--------|-----------------|
| Creative brief(s) | campaign-planner skill | `/tmp/marketing/campaigns/<brand>-campaign-plan.json` → `ad_creatives[]` array, or inline in conversation |
| Brand bible | brand-bible-builder skill | `/tmp/marketing/brands/<brand>/brand-bible.md` or inline |
| Aspect ratio | User or brief | Defaults to 1:1 if not specified |
| Resolution mode | User | Defaults to draft (1K) unless user says "final" or "4K" |

If the creative brief is missing, ask:

> "I need a creative brief to generate the ad. Run `/campaign-planner` first, or paste the brief details: headline, visual direction, CTA, and target audience."

If the brand bible is missing, proceed with neutral visual defaults — note this in the output and recommend running `/brand-bible-builder` for on-brand results.

---

## Step 2: Read Brand Bible Visual Identity

Open the brand bible and extract these fields into a working reference:

- **Primary colors** — hex codes or descriptors (e.g. `#1A2E5A deep navy`, `#F5A623 amber`)
- **Secondary / accent colors** — supporting palette
- **Font style** — serif vs sans-serif, weight, mood descriptor (e.g. "bold geometric sans", "light editorial serif")
- **Imagery style** — photography vs illustration, lifestyle vs product-only, color grading mood (warm/cool/muted/vibrant)
- **Layout pattern** — minimal and clean vs content-dense, whitespace-heavy vs layered
- **Tone** — formal, casual, bold, playful, premium, approachable

Keep this as a 6-field internal reference. Do not show it to the user. Use it when constructing prompts in Step 3.

---

## Step 3: Construct Image Generation Prompt

Apply these rules every time. They are non-negotiable.

### Core Rules (from best-practice image generation)

**Rule 1 — Less is more.** Short, focused prompts outperform long descriptive ones. Target 15–30 words for the visual description. Cut adjectives that repeat the same idea.

**Rule 2 — No logos, brand names, or company names.** Never include the brand name, product name, logo description, or any trademark in the prompt. The generation engine hallucinates these badly and they must be added in post-production.

**Rule 3 — Only include text that is explicitly specified.** If the brief specifies a headline to appear in the image, include it exactly as written — no paraphrasing. If no text is specified, do not add any text to the prompt. Do not include CTAs, taglines, or copy unless the brief explicitly says to render text.

**Rule 4 — Describe emotion and composition, not data.** Instead of "a woman saving money on her bills," write "confident woman, bright home office, warm morning light, relaxed expression." The emotion communicates the message; the model handles the rest.

**Rule 5 — Translate brand colors without naming the brand.** Convert hex codes to descriptors: `#1A2E5A` → "deep navy", `#F5A623` → "warm amber". Use these color words in the prompt naturally.

### Prompt Construction Formula

Assemble the prompt in this order:

```
[SUBJECT] — who or what is the focal element
[SETTING] — environment or background context
[MOOD / EMOTION] — feeling the image should evoke
[COMPOSITION] — framing, shot type, perspective
[LIGHTING] — quality and direction of light
[COLOR PALETTE] — 2–3 colors derived from brand bible
[STYLE] — photography/illustration style from brand bible
[AVOID] — explicit exclusions (text, logos, clutter, etc.)
```

Do not use all 8 fields every time. Use only those relevant to the brief. A 5-field prompt is often stronger than an 8-field one.

### Example Construction

Brief input:
```
headline: "Finally, sleep that works"
visual_direction: "Woman waking up refreshed, natural light bedroom"
cta: "Try free tonight"
target_persona: "Aisha, 28, KL, stressed professional"
```

Brand bible: warm coral `#E8735A`, off-white `#FAF7F2`, editorial sans-serif, warm and minimal photography style.

Constructed prompt:
```
Young woman waking up peacefully, sunlit minimalist bedroom, linen textures,
warm coral and off-white tones, soft morning light through sheer curtains,
close-up on relaxed expression, warm editorial photography style
```

What was excluded: brand name, CTA text, product name, headline text (no text was specified for visual rendering).

---

## Step 4: Select Aspect Ratio

Map the brief's platform or format to the correct ratio flag and pixel dimensions:

| Platform / Format | Ratio | Pixel Dimensions | Use Case |
|-------------------|-------|-----------------|----------|
| Instagram / Facebook Feed | 1:1 | 1080 × 1080 | Square feed post |
| Instagram Story / Reel | 9:16 | 1080 × 1920 | Full-screen vertical |
| Facebook Feed (portrait) | 4:5 | 1080 × 1350 | Taller feed post, more screen area |
| YouTube / LinkedIn Cover | 16:9 | 1920 × 1080 | Landscape / banner |

If the brief does not specify a platform, default to 1:1.

For carousel ads: generate all cards at the same ratio. Use 1:1 unless the brief specifies otherwise.

Pass the ratio to the script via `--resolution`. The nano-banana-pro script handles internal sizing. Generate at 1K for drafts, 4K for finals.

---

## Step 5: Generate Images

Create the output directory:

```bash
mkdir -p /tmp/marketing/assets/images
```

### Single image generation

Use this command pattern. Always use absolute path for the script.

```bash
uv run ~/.codex/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "<constructed prompt>" \
  --filename "/tmp/marketing/assets/images/<timestamp>-<brief-id>-draft.png" \
  --resolution 1K
```

Filename format: `yyyy-mm-dd-hh-mm-ss-<brief-id>-draft.png`
- `brief-id`: lowercase kebab-case derived from the brief headline (e.g. `finally-sleep-works`)
- Use current date/time for timestamp

### Draft-first workflow

Always follow this sequence:

1. **Draft at 1K** — generate first at 1K for fast feedback. Present to user.
2. **Iterate** — if issues found in self-review (Step 6), adjust prompt and regenerate at 1K. Max 3 attempts.
3. **Final at 4K** — only after user approves the draft or after self-review passes. Change filename suffix from `-draft` to `-final`, set `--resolution 4K`.

### Carousel ads

Generate each card as a separate image. Naming convention:
```
yyyy-mm-dd-hh-mm-ss-<brief-id>-card-01-draft.png
yyyy-mm-dd-hh-mm-ss-<brief-id>-card-02-draft.png
```

Ensure visual consistency across cards:
- Use the same color palette descriptor in every card's prompt
- Use the same style descriptor in every card's prompt
- Use the same lighting descriptor in every card's prompt
- Vary only the subject and composition per card

---

## Step 6: Self-Review Loop (CRITICAL)

After generating each image, perform a structured self-review before presenting to the user. Do not skip this step.

Run through this checklist for every generated image:

| Check | Pass Condition | Fail Action |
|-------|---------------|-------------|
| Text accuracy | Any specified text appears correctly and is readable | Simplify prompt; add explicit text instruction |
| No hallucinated logos | No brand marks, wordmarks, icons, or watermarks visible | Add "no logos, no text, no watermarks" to avoid clause |
| No hallucinated brand names | No company names or product names rendered as text | Add "no brand names, no product names" to avoid clause |
| Aspect ratio | Matches requested format | Re-run with correct ratio flag |
| Color alignment | Dominant colors match brand palette intent | Strengthen color descriptors in prompt |
| Overall quality | Image is coherent, professional, on-brief | Rebuild prompt from scratch using simpler structure |

### Fail response

If any check fails:

1. Identify the specific failure from the table above.
2. Apply the corresponding fail action to the prompt.
3. Regenerate at 1K.
4. Re-run the self-review checklist on the new image.
5. Stop after 3 total attempts. If still failing on attempt 3, present the best result to the user with a note explaining what the issue is and what was tried.

Do not present a failing image silently. Always tell the user what was wrong and what fix was applied.

---

## Step 7: HITL — Present for User Review

After self-review passes (or after 3 attempts), present the results:

```
Ad image(s) generated for: [brief headline]

Draft(s) saved to /tmp/marketing/assets/images/:
  [timestamp]-[brief-id]-draft.png   ← [ratio] | 1K

Self-review: [PASS / notes on any issues found and fixed]

Review the image and reply with one of:
  A) Approve → I'll upscale to 4K final
  B) Adjust → describe what to change
  C) Skip → move to next brief
```

Wait for the user's response before generating the 4K final or moving to the next brief.

If the user says "adjust" or describes changes:
- Apply the change to the prompt (keep changes minimal — one diff at a time)
- Regenerate at 1K
- Re-run self-review
- Present again

If the user approves:
- Regenerate at 4K with `-final` filename suffix
- Confirm: "Final saved: `/tmp/marketing/assets/images/[filename]-final.png`"

---

## Step 8: Process Multiple Briefs

If the input contains multiple briefs (e.g. from a campaign-planner JSON with 3–5 image ad entries), process them sequentially. Complete the full cycle (generate → self-review → HITL approval → final) for each brief before moving to the next.

After all briefs are processed, present a summary:

```
All ad images complete.

Generated:
  /tmp/marketing/assets/images/[file-1]-final.png   [ratio]
  /tmp/marketing/assets/images/[file-2]-final.png   [ratio]
  /tmp/marketing/assets/images/[file-3]-final.png   [ratio]

Next step: run /meta-ads-publisher to upload these to your ad account,
or /campaign-planner to review the full campaign.
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `Error: No API key provided.` | Tell user to run `export GEMINI_API_KEY=<key>` and retry |
| `Error loading input image:` | Verify the `--input-image` path exists; fix path and retry |
| `quota / 403 / permission` API error | Wrong key or quota exceeded; ask user to check Google AI Studio quota |
| Script not found at `~/.codex/skills/...` | nano-banana-pro skill is not installed; tell user to install it from ClawHub |
| `uv: command not found` | Run `curl -LsSf https://astral.sh/uv/install.sh | sh` then retry |
| Image generation returns blank/empty | Prompt may be too restrictive; remove avoid clauses and simplify to subject + style only |

---

## File Paths Reference

```
/tmp/marketing/
├── assets/
│   └── images/
│       ├── yyyy-mm-dd-hh-mm-ss-<brief-id>-draft.png    ← draft outputs
│       └── yyyy-mm-dd-hh-mm-ss-<brief-id>-final.png    ← approved 4K finals
├── brands/<brand>/
│   └── brand-bible.md                                   ← brand visual reference
└── campaigns/
    └── <brand>-campaign-plan.json                       ← input brief source
```
