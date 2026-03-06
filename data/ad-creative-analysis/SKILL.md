---
name: ad-creative-analysis
description: Analyze ad creatives (images and videos) extracted from competitor research. Use when given a directory of ad images, video files, or transcripts to evaluate ad quality, score visual and messaging effectiveness, assign a scale score for viral/engagement potential, and generate a cross-creative pattern summary. Triggered by requests like "analyze these ads", "score these creatives", "what hooks are competitors using", "evaluate the ad library", "give me a scale score", "analyze the ad folder", or "what's working in these ads".
---

# Ad Creative Analysis

Analyze a directory of competitor or reference ad creatives. Produce a per-creative JSON analysis and a cross-creative pattern summary.

## Step 1 — Accept Inputs

Expect one of:
- A directory path containing image files (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`) and/or video files (`.mp4`, `.mov`, `.avi`, `.webm`)
- An optional `metadata.json` file in that directory with fields per filename: `platform`, `spend`, `duration_days`, `impressions`, `format`

If no path is given, ask the user: "Please provide the directory path containing the ad creatives."

List all files in the directory. Separate into image ads and video ads. Log the count of each before proceeding.

## Step 2 — Analyze Image Ads

For each image file, use vision/image analysis to evaluate the following.

### Design Evaluation

Assess these five dimensions:

1. **Visual hierarchy** — Is the eye drawn to the right element first? Is there a clear focal point?
2. **Color usage** — Does the palette create contrast, evoke emotion, and maintain brand coherence?
3. **Text overlay readability** — Is copy legible at a glance? Font size, contrast, placement?
4. **CTA prominence** — Is the call-to-action visually distinct, clearly placed, and easy to act on?
5. **Brand consistency** — Logo placement, color adherence, font alignment with brand identity.

### Image Scores (1-10 each)

- `attention_grab` — How fast and strongly does the creative stop a scroll?
- `message_clarity` — How clearly is the core message communicated without needing context?
- `cta_strength` — How compelling and action-oriented is the CTA?

### Image Extraction

Extract:
- `primary_message` — The single core thing this ad is communicating (one sentence)
- `emotion_appeal` — One of: fear, aspiration, social_proof, urgency, curiosity, humor, trust, belonging, exclusivity
- `target_audience` — Inferred from visuals, copy, and context (e.g., "women 25-35 interested in fitness")
- `hook_text` — The first piece of copy the eye lands on (headline or main text)

## Step 3 — Analyze Video Ads

For each video file, analyze the video directly using vision. If a transcript file exists alongside the video (same filename, `.txt` or `.srt` extension), read and use it.

### Video Evaluation

Assess these four dimensions:

1. **Hook quality (first 3 seconds)** — Does it immediately create curiosity, shock, or recognition? Would someone stop scrolling?
2. **Script structure** — Does it follow a logical persuasion arc (problem, solution, proof, CTA)?
3. **Pacing** — Is the editing rhythm appropriate for platform and audience? Not too slow or rushed?
4. **CTA placement** — Is the call-to-action clear, timed well, and repeated if needed?

### Video Scale Score (1-10)

Assign a single `scale_score` representing the ad's viral and engagement potential at scale:

- **9-10**: Exceptional hook, tight script, clear CTA. Likely to perform well at high spend.
- **7-8**: Strong fundamentals, minor weaknesses. Good candidate for testing.
- **5-6**: Average execution. Needs a stronger hook or clearer CTA before scaling.
- **3-4**: Core idea present but poor execution. Requires significant rework.
- **1-2**: Unlikely to perform. Fundamental issues with hook, message, or CTA.

See `references/analysis-framework.md` for detailed scale score rubric.

### Video Extraction

Extract:
- `hook_text` — Exact words spoken or shown in the first 3 seconds
- `hook_type` — One of: question, bold_claim, pain_point, curiosity_gap, social_proof, before_after, demonstration
- `main_message` — The core value proposition stated in the ad
- `emotion_appeal` — One of: fear, aspiration, social_proof, urgency, curiosity, humor, trust, belonging, exclusivity
- `cta_text` — The exact CTA spoken or shown
- `cta_timing` — When the CTA appears (e.g., "end", "middle", "repeated throughout")

## Step 4 — Universal Metadata (All Ad Types)

For every creative, regardless of type, record:

- `filename` — The file name
- `ad_format` — One of: single_image, carousel, video, story, reel
- `aspect_ratio` — Detected or inferred (e.g., `1:1`, `9:16`, `16:9`, `4:5`)
- `dimensions` — Width x height in pixels if detectable
- `ad_objective` — Inferred from content and CTA: `awareness`, `consideration`, or `conversion`
- `platform_fit` — Which platforms this format and ratio suits best (e.g., `["Instagram Feed", "Facebook Feed"]`)

## Step 5 — Output Per-Creative JSON

Output one JSON object per creative. Print all results together in a single JSON array.

### Image ad example structure

```json
{
  "filename": "ad_001.jpg",
  "type": "image",
  "ad_format": "single_image",
  "aspect_ratio": "1:1",
  "dimensions": "1080x1080",
  "ad_objective": "conversion",
  "platform_fit": ["Instagram Feed", "Facebook Feed"],
  "scores": {
    "attention_grab": 8,
    "message_clarity": 7,
    "cta_strength": 9
  },
  "primary_message": "Lose 10kg in 30 days without giving up your favourite food",
  "emotion_appeal": "aspiration",
  "target_audience": "Women 28-45 who have tried dieting before",
  "hook_text": "Still counting calories? There's a better way."
}
```

### Video ad example structure

```json
{
  "filename": "ad_002.mp4",
  "type": "video",
  "ad_format": "video",
  "aspect_ratio": "9:16",
  "dimensions": "1080x1920",
  "ad_objective": "consideration",
  "platform_fit": ["TikTok", "Instagram Reels", "Facebook Reels"],
  "scale_score": 8,
  "hook_text": "I was $40,000 in debt until I found this",
  "hook_type": "before_after",
  "main_message": "This budgeting app helped me pay off debt in 18 months",
  "emotion_appeal": "fear",
  "cta_text": "Download free — link in bio",
  "cta_timing": "end"
}
```

## Step 6 — Generate Cross-Creative Summary

After analyzing all creatives, produce a `summary` object appended to the output. Include:

- `total_analyzed` — Count of creatives analyzed (split by type)
- `top_performers` — Filenames of the top 3 creatives by score (images by average score, videos by scale score)
- `dominant_emotion` — Most frequently detected emotion appeal across all ads
- `common_hooks` — List of recurring hook patterns or phrases observed
- `cta_patterns` — Most common CTA structures seen (e.g., "verb + free + urgency")
- `dominant_objective` — Most common inferred ad objective
- `format_breakdown` — Count per ad format
- `recommendations` — 3-5 actionable observations for improving or scaling these creatives

### Summary example structure

```json
{
  "summary": {
    "total_analyzed": { "images": 5, "videos": 3 },
    "top_performers": ["ad_004.jpg", "ad_002.mp4", "ad_007.jpg"],
    "dominant_emotion": "aspiration",
    "common_hooks": [
      "Question-based hook challenging a common belief",
      "Before/after framing in first sentence"
    ],
    "cta_patterns": [
      "Shop now + scarcity signal",
      "Free trial + no credit card"
    ],
    "dominant_objective": "conversion",
    "format_breakdown": { "single_image": 4, "video": 3, "carousel": 1 },
    "recommendations": [
      "Hooks are strong but CTAs lack urgency — test adding 'today only' or limited quantity",
      "All videos open with talking head — test a demonstration hook for variety",
      "Aspiration dominates — test a fear/pain angle to broaden audience response"
    ]
  }
}
```

## Step 7 — Handle Missing or Unreadable Files

If a file cannot be analyzed (corrupted, unsupported format, too dark/blurry for vision):
- Include the filename in the output with `"status": "unreadable"` and a brief `"reason"` field
- Continue analyzing remaining files, do not stop

## Reference Material

Consult `skills/ad-creative-analysis/references/analysis-framework.md` for:
- Detailed scoring rubrics per metric
- Ad psychology pattern definitions
- Hook formula templates
- Extended example output
