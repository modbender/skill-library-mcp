# Content Creation Pipeline

All post tracking goes to `workspace/performance/log.json` — this is the single source of truth.

---

## Slideshow Workflow

### 1. Hook Selection
Read `workspace/hooks/library.json` and pick a hook. Rotate through categories.

### 2. Pack Discovery
```bash
genviral.sh list-packs
genviral.sh get-pack --id PACK_ID  # get full image list with metadata
```

### 3. Analyze Pack Images (MANDATORY — DO NOT SKIP)
Read each image's AI metadata (`description`, `keywords`) from the `get-pack` response. Use the vision/image tool for readability assessment (clean space for text, contrast, complexity) or when metadata is unavailable. See `docs/api/packs.md` for full details.

### 4. Map Images to Slides
- Slide 0: Hook text
- Slide 1: Problem/setup
- Slide 2: Discovery/shift
- Slide 3: Feature/proof
- Slide 4: CTA

Assign best-matching image to each slide. Build a `pinned_images` map.

### 5. Prompt Assembly
Use the selected hook and visual direction to build a slideshow prompt. Reference `workspace/content/scratchpad.md` and `docs/prompts/slideshow.md`.

### 6. Generate WITH Pinned Images
```bash
genviral.sh generate \
  --prompt "Your prompt" \
  --pack-id PACK_ID \
  --slides 5 \
  --slide-config-json '{"total_slides":5,"slide_types":["image_pack","image_pack","image_pack","image_pack","image_pack"],"pinned_images":{"0":"URL_0","1":"URL_1","2":"URL_2","3":"URL_3","4":"URL_4"}}'
```
**Never call generate with just `--pack-id` and no `pinned_images`.** See `docs/api/packs.md`.

### 7. Review Slide Text
Check each slide for clarity, readability, and flow. Update or regenerate weak slides.

### 8. Render
```bash
genviral.sh render --id SLIDESHOW_ID
```

### 9. Visual Review + Fix Loop (MANDATORY — HARD GATE)
Visually inspect EVERY rendered slide. For each slide check:
- (a) Is text readable at a glance? Can you read it in under 2 seconds?
- (b) Does the background match your intent?
- (c) Any text overflow or clipping?

**If ANY slide fails readability: fix it before moving on.** Do not just report "needs fixing."
```bash
genviral.sh update --id SLIDESHOW_ID --slides '[...slides with adjusted style_preset, filters, etc...]'
genviral.sh render --id SLIDESHOW_ID
```
Fix options: change `style_preset`, add `background_filters` (darken/blur), swap image, adjust text position.
Re-review after each fix. **You cannot proceed to step 10 until all slides pass.**

### 10. Post
```bash
genviral.sh create-post \
  --caption "Caption with #hashtags" \
  --media-type slideshow \
  --media-urls "url1,url2,url3,url4,url5" \
  --accounts "account_id"
```

Or for TikTok drafts (add music before publishing):
```bash
genviral.sh post-draft --id SLIDESHOW_ID --caption "Caption" --account-ids "account_id"
```

### 11. Log the Post (MANDATORY)
Immediately after posting, append to `workspace/performance/log.json`:
```json
{
  "id": "post-id",
  "date": "2026-01-01",
  "time_utc": "14:32:00",
  "type": "slideshow",
  "hook": "hook text snippet",
  "caption_snippet": "first 80 chars of caption",
  "status": "posted",
  "pack_id": "...",
  "slideshow_id": "...",
  "account_id": "...",
  "platform": "tiktok",
  "metrics": {"views": null, "likes": null, "comments": null, "shares": null, "saves": null}
}
```

### 12. Tag in Hook Tracker (MANDATORY)
Add an entry to `workspace/performance/hook-tracker.json`:
```json
{
  "post_id": "...",
  "slideshow_id": "...",
  "hook_text": "...",
  "hook_category": "person-conflict|relatable-pain|educational|pov|before-after|feature-spotlight",
  "cta_text": "...",
  "cta_type": "link-in-bio|search-app-store|app-name-only|soft-cta|no-cta",
  "pack_id": "...",
  "template_id": null,
  "posted_at": "2026-02-17T10:00:00Z",
  "platform": "tiktok|instagram",
  "account_id": "...",
  "metrics": {
    "views": null, "likes": null, "comments": null,
    "shares": null, "saves": null, "last_checked": null
  },
  "status": "posted"
}
```

### 13. Performance Check (48h and 7d after posting)
```bash
genviral.sh analytics-posts --range 7d --sort-by views --sort-order desc --json
```
Match posts to hook-tracker entries by `post_id`. Update metrics, set `last_checked` to now, set `status` to `tracking`.

### 14. Weekly Review (every Monday)
Pull analytics, apply diagnostic framework, categorize hooks, write summary in `workspace/performance/weekly-review.md`. See `docs/references/analytics-loop.md`.

---

## Video Post Workflow

1. Upload via `upload` or reference existing CDN URL
2. Write caption (brand voice, hashtags)
3. `create-post --media-type video`
4. Log to `workspace/performance/log.json`

---

## Performance Feedback Loop

### Core Files
- `workspace/performance/log.json` - canonical post record
- `workspace/performance/hook-tracker.json` - hook/CTA tracking with metrics
- `workspace/performance/insights.md` - agent learnings
- `workspace/performance/weekly-review.md` - weekly review notes
- `docs/references/analytics-loop.md` - full analytics reference

### The Diagnostic Framework

Once you have views and engagement rate (likes + comments + shares + saves / views):

**High views + High engagement:** Hook and content both work. SCALE — make 3 variations now. → `double_down`

**High views + Low engagement:** Hook stops scroll, content/CTA fails. Keep hook, fix content arc or swap CTA type. → investigate

**Low views + High engagement:** Content resonates but hook doesn't stop scroll. Rework hook — more direct, more charged, more pattern-interrupting. Keep content structure.

**Low views + Low engagement:** Nothing works. Drop this angle, try something radically different.

### Decision Rules

| Views | Action |
|-------|--------|
| 50K+ | Double down. 3 variations now. → `rules.double_down` |
| 10K–50K | Keep in rotation. → `rules.keep_rotating` |
| 1K–10K | Test one more variation. → `rules.testing` |
| Under 1K, twice | Drop it. → `rules.dropped` |

"Twice" = two posts with same hook category both failed. One bad post can be distribution. Two is a pattern.

### Weekly Review (every Monday)

1. `analytics-summary --range 7d`
2. `analytics-posts --range 7d --sort-by views --sort-order desc`
3. Update hook-tracker with fresh metrics
4. Categorize each recent post
5. Check `hook_categories` aggregates: which has highest `avg_views`?
6. Check `cta_performance`: which CTA type has best `avg_engagement_rate`?
7. Decide next week's focus from data, not intuition
8. Write brief summary in `workspace/performance/weekly-review.md`

After 4+ weeks of data, patterns become clear. Before that, keep posting a variety of hook categories to build the sample size.

See `docs/references/analytics-loop.md` for the full weekly review process and template.

---

## CTA Testing Framework

### CTA Types

| Type | Example | When to Use |
|------|---------|-------------|
| `link-in-bio` | "Link in bio to try for free" | Traffic to URL |
| `search-app-store` | "Search [App Name] on the App Store" | App is the product |
| `app-name-only` | Just say the app name | Soft brand awareness |
| `soft-cta` | "Worth checking out" | When hard CTAs feel off |
| `no-cta` | Nothing | Brand-building or when CTA kills the vibe |

### How to Rotate Systematically

1. Try each CTA type 2-3 times across different posts
2. Track in hook-tracker under `cta_type`
3. After 10+ posts, check which type has highest `avg_engagement_rate`
4. Shift weight toward the winner, keep testing others occasionally

### Pairing CTAs with Hook Categories

Not all CTAs work equally well with all hook types. Track these combinations in hook-tracker.

As you accumulate data, look for patterns like:
- "Relatable-pain hooks with soft CTAs get higher engagement than relatable-pain hooks with link-in-bio"
- "Feature-spotlight hooks with search-app-store CTAs convert better than with no-cta"

After 20+ posts across categories, you will have enough data to make these calls with confidence. Until then, vary and track.

### The Goal

Identify the CTA type that converts best for each hook category. This maximizes the value of every piece of content you produce.

---

## Platform Best Practices

### TikTok
- **Slide Count:** 5-6 slides is the sweet spot
- **Aspect Ratio:** `9:16` for fullscreen, `4:5` for feed
- **Text Readability:** One idea per slide. 8-16 words max. Avoid text in bottom 20% (UI overlap)
- **Narrative Structure (5-slide arc):**
  1. Hook (stop the scroll)
  2. Problem detail
  3. Shift (introduce the solution)
  4. Feature/proof
  5. CTA

### Instagram
- **Slide Count:** 5-10 slides for carousel
- **Aspect Ratio:** Reels: `9:16` / Feed: `4:5` or `1:1`

---

## Legacy Pipeline Commands

### post-draft
Post a rendered slideshow as a TikTok draft (forces `privacy_level=SELF_ONLY`, `post_mode=MEDIA_UPLOAD`).

```bash
genviral.sh post-draft \
  --id SLIDESHOW_ID \
  --caption "Caption with #hashtags" \
  --account-ids "account_id"
```

Guardrail: the CLI warns near TikTok's pending-share cap and blocks at 5+ MEDIA_UPLOAD drafts in a rolling 24h window. Use `--force-media-upload-cap` only for intentional testing.

### full-pipeline
End-to-end: generate -> render -> review -> post draft.

```bash
genviral.sh full-pipeline \
  --prompt "Your hook and content prompt" \
  --caption "Caption with #hashtags" \
  --pack-id PACK_ID \
  --slides 5 \
  --type educational \
  --style tiktok \
  --account-ids ACC_ID
```

Use `--skip-post` to stop after rendering.
