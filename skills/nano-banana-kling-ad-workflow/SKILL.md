---
name: nano-banana-kling-ad-workflow
description: Recreate low-budget AI video ad workflows using Nano Banana image generation plus Kling 3.0 video synthesis with dialogue, including prompt design, scene planning, cost control, and export handoff. Use when a user wants to produce a cinematic ad quickly (often in a few hours) with a small credit budget, or asks for a Deon-style Nano Banana + Kling pipeline.
---

# Nano Banana Kling Ad Workflow

## Overview
Build a short ad from scratch using a fast two-stage pipeline: generate stills in Nano Banana, animate them in Kling 3.0, then stitch a publishable cut. Optimize for speed, visual consistency, and low spend.

## Workflow

### 1) Define outcome before generating assets
Capture these constraints first:
- Product or story concept
- Audience and tone
- Target duration (15s, 30s, or 45s)
- Delivery format (X, TikTok, Reels, YouTube)
- Budget ceiling in credits

If missing, ask for only the minimum required details and proceed.

### 2) Build a shot list
Create 5-9 shots with:
- Shot number
- Scene goal
- Subject + environment
- Camera style
- On-screen line or dialogue intent

Keep each shot prompt short and concrete.

### 3) Generate base visuals in Nano Banana
For each shot:
- Prompt for one clear hero frame
- Keep recurring anchors stable (character traits, wardrobe, color palette, lens style)
- Generate 2-4 variations max, pick one

If consistency drifts, add explicit anchor text to the next prompt.

### 4) Animate in Kling 3.0
Import selected stills into Kling 3.0 and add:
- Motion direction (camera push, pan, dolly, parallax)
- Dialogue or narration intent
- Timing per clip (usually 2-5s)

Prefer subtle motion over aggressive movement unless the concept requires action-heavy pacing.

### 5) Assemble final cut
Sequence clips by narrative flow:
- Hook (first 1-2 shots)
- Value demonstration
- Clear CTA

Add captions if platform autoplay is likely muted.

### 6) Track cost and output quality
After generation, report:
- Total clips generated
- Credits used and estimated cost
- Final runtime
- Export ratio(s)
- What to improve in next iteration

## Prompt pattern
Use this compact prompt shape for each Nano Banana shot:

"[subject], [action], in [environment], [lighting], [camera framing], [style anchors], ultra-clean composition, ad-grade, no text overlays"

Use this compact Kling prompt shape:

"Animate this still with [motion], keep subject identity stable, cinematic realism, [timing], [dialogue/emotion cue], smooth transitions"

## Fast defaults
- Runtime target: 20-30 seconds
- Shot count: 6
- Variations per shot: 3
- Clip length: 3-4 seconds
- Revision passes: 1 content pass + 1 polish pass

## Failure handling
- If faces drift: repeat identity anchors and reduce motion complexity
- If scenes look noisy: simplify prompts and reduce style stacking
- If cost rises too fast: reduce variations and shorten shot list
- If timeline slips: ship a 15-second cut first, then extend

## Deliverable format
When executing this skill, output:
1. Final shot list
2. Prompt set used
3. Generation and edit log
4. Final export summary
5. Next-iteration recommendations
