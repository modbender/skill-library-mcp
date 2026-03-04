---
name: video-production
description: Complete A/B video pipeline — storyboard, Veo 3 batch generation, browser preview with feedback loop, and ffmpeg assembly into final videos. Use when creating multi-scene videos, running A/B tests on hooks/CTAs, previewing clips before stitching, or assembling a final cut from approved clips.
---

# Video Production Skill

Generate cinematic video clips with Veo 3, review them in a browser preview, iterate with feedback, and assemble final A/B test videos — all with minimal token spend.

## Quick Start

```bash
cd ~/.openclaw/workspace/skills/video-production

# 1. Generate all clips from storyboard
.venv/bin/python3 scripts/batch_generate.py --storyboard /path/to/storyboard.json

# 2. Open browser preview
.venv/bin/python3 scripts/generate_preview.py --storyboard /path/to/storyboard.json

# 3. (After feedback) Re-generate only revised scenes
.venv/bin/python3 scripts/apply_feedback.py --storyboard storyboard.json --feedback feedback.json

# 4. Assemble final video
.venv/bin/python3 scripts/ffmpeg_assembler.py --storyboard storyboard.json
```

## A/B Video Architecture

**Target: 15-second videos, 3 clips × 5s each**

```
[HOOK: 5s] → [CORE: 5s] → [CTA/PAYOFF: 5s]
     ↑                           ↑
 swap for A/B               swap for A/B
```

**Economics:**
- 5 Veo prompts → 4 unique A/B videos (2 hooks × 1 core × 2 CTAs)
- 7 prompts → 9 videos | 9 prompts → 16+ videos
- Transitions at 5s and 10s marks — clean for analytics

## Pipeline Overview

```
storyboard.json
      ↓
batch_generate.py     → clips/scene_01.mp4 ... scene_05.mp4
      ↓
generate_preview.py   → preview.html (opens in browser, zero tokens)
      ↓
[review + paste feedback JSON to Muffin]
      ↓
[Muffin suggests revised prompts, updates storyboard.json]
      ↓
apply_feedback.py     → re-generates only 'revise' scenes
      ↓
ffmpeg_assembler.py   → final_AA.mp4, final_BA.mp4, final_AB.mp4, final_BB.mp4
```

**Token cost:** Only when writing storyboard + interpreting feedback. Preview, generation, and assembly are all zero tokens.

## Storyboard Format

```json
{
  "project": "my-video",
  "output_dir": "clips",
  "final_output": "final.mp4",
  "scenes": [
    {
      "id": "scene_01",
      "role": "hook_a",
      "label": "Hook A",
      "order": 1,
      "duration": 5,
      "aspect_ratio": "16:9",
      "prompt": "..."
    }
  ],
  "_ab_combinations": {
    "video_1_AA": ["scene_01", "scene_03", "scene_04"],
    "video_2_BA": ["scene_02", "scene_03", "scene_04"],
    "video_3_AB": ["scene_01", "scene_03", "scene_05"],
    "video_4_BB": ["scene_02", "scene_03", "scene_05"]
  }
}
```

See `scripts/storyboard_template.json` for full template.

## Feedback Format

Paste this JSON to Muffin after reviewing preview.html:

```json
{
  "scenes": [
    { "id": "scene_01", "action": "approve", "notes": "" },
    { "id": "scene_02", "action": "revise", "notes": "slower camera, warmer light" }
  ]
}
```

## Veo 3 API — Current Limits (Gemini API, verified 2026-02-23)

| Parameter | Supported |
|---|---|
| `aspect_ratio` | ✅ |
| `number_of_videos` | ✅ |
| `negative_prompt` | ✅ |
| `duration_seconds` | ❌ Broken (throws 400 even with valid values) |
| `fps` | ❌ Vertex AI only |
| `compression_quality` | ❌ Vertex AI only |
| `enhance_prompt` | ❌ Vertex AI only |

**Models:** `veo-3.1-generate-preview` (best) | `veo-3.1-fast-generate-preview` | `veo-3.0-generate-001`

**SDK:** `google-genai` (NOT `google-generativeai`)

## Prompting Techniques

**Motion in every sentence** — Veo produces laggy output from static prompts. Every sentence should describe camera OR subject movement.

**Character continuity** — Veo can't maintain exact characters across clips. Describe physical details explicitly in every scene that includes the same character.
> ✅ "The same client character from the opening — dark jacket, professional bearing, 30s-40s"

**Stitch continuity** — For seamless cuts, open each prompt with the color/light state the previous clip ends on.
> ✅ "Warm amber light, a direct visual continuation from the post-production suite..."

**Single continuous shot** — Each prompt is one continuous clip. Design it as one camera move that reveals multiple elements — not a montage description.

**Content policy** — Environmental/prop-only scenes generate reliably. Stressed people on phones can silently return no video. Keep humans calm or describe the environment instead.

## Quota Management

When you hit the daily limit (429 RESOURCE_EXHAUSTED), use the quota watcher:

```bash
# Sets a cron that retries every 30 min, texts Master when done
chmod +x scripts/quota_watcher.sh

# Add to crontab:
(crontab -l 2>/dev/null | grep -v quota_watcher; \
 echo "*/30 * * * * /path/to/quota_watcher.sh >> /tmp/quota_watcher.log 2>&1") | crontab -
```

See `api-quota-watcher` skill for the generic pattern.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/batch_generate.py` | Generate all scenes from storyboard, skip existing |
| `scripts/generate_preview.py` | Build preview.html with video players + feedback form |
| `scripts/apply_feedback.py` | Re-generate only scenes marked 'revise' |
| `scripts/ffmpeg_assembler.py` | Stitch approved clips → final MP4 (cut or crossfade) |
| `scripts/quota_watcher.sh` | Retry + notify cron for quota recovery |
| `scripts/storyboard_template.json` | Starting storyboard template |

## Environment Setup

```bash
cd ~/.openclaw/workspace/skills/video-production
uv venv .venv
uv pip install google-genai Pillow requests

# API key must be in ~/.zshenv:
export GOOGLE_API_KEY="AIza..."
```

## Assembling A/B Combinations

After all scenes approved, run assembler for each combo:

```bash
# Assemble all 4 A/B videos
for combo in AA BA AB BB; do
  # Edit storyboard or pass scene list directly
  .venv/bin/python3 scripts/ffmpeg_assembler.py \
    --storyboard storyboard.json \
    --output "final_${combo}.mp4"
done
```

Or hardcode in `_ab_combinations` in storyboard.json — assembler reads it automatically.

## Format Adaptation

| Format | Notes |
|---|---|
| 16:9 (master) | Default — all scripts use this |
| 9:16 (vertical) | Change `aspect_ratio` to `"9:16"` in storyboard |
| 1:1 (square) | Change `aspect_ratio` to `"1:1"` |

Generate separate storyboards per format for best results. Don't crop 16:9 to 9:16 in post — re-generate with proper aspect.

## What Veo 3 Does Well

- Atmospheric/mood shots
- Smooth camera movements (push-in, crane, tracking)
- Lighting transitions within a single clip
- Office/studio/urban environments
- Abstract beauty (nature, space, product)

## What Veo 3 Struggles With

- Exact text on screen (add in post via After Effects/Resolve)
- Maintaining character consistency across clips
- Very fast montage within a single generation
- Complex multi-person scenes
- Specific prop/brand details

---

## Character Registry & Learning System

### Clean Slate Default
**Every new campaign starts fresh.** No inherited characters, no assumed cast, no prompt weights from previous runs. If you want continuity from a past campaign, explicitly say so:
> "Use HERO_01 from the MMM campaign"

### Character IDs (Bootstrap Defaults)
If no cast is defined, use these placeholders:
- `HERO_01` — Primary UGC creator
- `FRIEND_01` — Recurring side character
- `HAND_MODEL_01` — Hands-only product handler

First approved output becomes the canonical identity baseline for that campaign.

### Character Bible (Per Campaign)
When characters are defined, maintain a `character_registry.json` in the project folder:
```json
{
  "HERO_01": {
    "identity": {
      "age_range": "28-35",
      "gender": "male",
      "skin_tone": "...",
      "hair": "...",
      "build": "..."
    },
    "wardrobe": {
      "preferred": [],
      "avoid": [],
      "signature": ""
    },
    "camera_rules": {
      "preferred_framing": "medium close-up",
      "avoid": []
    },
    "negative_constraints": [],
    "reference_frames": [],
    "phrase_weights": {}
  }
}
```

### CAST Block Injection
When characters are defined, every prompt must include:
```
CAST:
- HERO: HERO_01 (identity locked; must match reference frames exactly)
Do not alter identity traits across frames or across future assets.
```

### Verification Thresholds
After generation, run vision model consistency check against reference frames:
- **>= 85** → auto-pass
- **75–84** → escalate to Master (Telegram), do not auto-regen
- **<= 74** → auto-fail, apply stabilize patch, retry once → then escalate if still failing

### Learning Loop
After every human review decision, update:
- **Approved** → increase weights for phrases that produced good consistency; add best frames to approved reference set
- **Rejected** → identify drift attributes; downweight or ban phrases causing drift; add negative constraints
- **Borderline** → apply stabilize patch for that engine+character+scene combo

### Generation Log
Append every attempt to `generation_log.jsonl` (never deleted):
```json
{
  "timestamp": "...",
  "campaign": "...",
  "scene_id": "...",
  "engine": "veo-3.1-generate-preview",
  "attempt": 1,
  "characters": ["HERO_01"],
  "prompt": "...",
  "output": "clips/scene_01.mp4",
  "verification_score": 88,
  "drift_notes": "",
  "decision": "auto_pass",
  "human_outcome": "approved",
  "worked_phrases": [],
  "failed_phrases": []
}
```

### Escalation Policy — Ask Before Guessing
Escalate to Master via Telegram (never silently loop) when:
- Verification score is borderline (75–84)
- Character is on a new engine for the first time
- Scene type is new for that character+engine combo
- Same prompt has failed 2+ times in a row

Escalation message must include: scene ID, engine, score, drift notes, and 2–3 options.

### Archive (Persists Across Campaigns)
Even though each campaign starts clean, these persist in the skill folder:
- `generation_log.jsonl` — full audit trail
- `approved_references/` — canonical frames by campaign, available to load on request
- `campaign_phrase_weights/` — weight archives per campaign, loadable for continuity
