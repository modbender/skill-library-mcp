# Pack Commands

Packs are collections of background images used in slideshows.

## list-packs
List available image packs.

```bash
genviral.sh list-packs
genviral.sh list-packs --search motivation --include-public false
genviral.sh list-packs --limit 20 --offset 0 --json
```

**`--search` is metadata-aware:** Matches across pack names AND AI image metadata (descriptions + keywords).

Returns pack summaries: `id`, `name`, `image_count`, `preview_image_url`, `is_public`, `created_at`.

---

## get-pack
Get a single pack with the full ordered image list.

```bash
genviral.sh get-pack --id PACK_ID
```

Returns top-level fields: `id`, `name`, `image_count`, `is_public`, `created_at`.

Returns `images[]` ordered by creation time, each with:
- `id`, `url`
- `metadata` — AI-generated enrichment:
  - `status`: `pending` | `processing` | `completed` | `failed`
  - `description`: One-sentence description of the image content
  - `keywords`: Array of lowercase search-friendly keywords
  - `model`, `generated_at`, `error`

**Example image with metadata:**
```json
{
  "id": "22222222-2222-2222-2222-222222222222",
  "url": "https://cdn.example.com/packs/motivation/01.jpg",
  "metadata": {
    "status": "completed",
    "description": "Woman lifting dumbbells in a bright, minimal gym environment.",
    "keywords": ["fitness", "workout", "strength", "gym", "motivation"],
    "model": "gpt-4.1-nano",
    "generated_at": "2026-02-17T11:02:00.000Z",
    "error": null
  }
}
```

---

## Smart Image Selection (MANDATORY — DO NOT SKIP)

**If you pass `--pack-id` to `generate` without `pinned_images`, the server picks random images. That produces incoherent slideshows. You MUST select images deliberately and pin them.**

### Step-by-step (required every time a pack is used)

**1. Fetch pack images:**
```bash
genviral.sh get-pack --id PACK_ID
```

**2. Use metadata to shortlist images:**
- Read each image's `metadata.description` and `metadata.keywords`
- Match images to slide topics
- If metadata `status` is `pending` or `failed`, use vision tool for those images

**When to use the vision/image tool additionally:**
- When metadata is unavailable
- When assessing **readability** (clean space for text, contrast, visual complexity)
- For rendered slide review (always — see pipeline)

Example vision call:
```
image(image="https://...", prompt="Assess for slideshow text overlay: Where is clean space? How busy is the background? What text style would be most readable?")
```

**3. Plan your slides, then match images:**
- Slide 0: Hook text
- Slide 1: Problem/setup
- Slide 2: Discovery/shift
- Slide 3: Feature/proof
- Slide 4: CTA

For each slide, pick the best-matching image. Consider topic match, text readability, visual variety.

**4. Build `pinned_images` and pass to generate:**
```bash
genviral.sh generate \
  --prompt "Your prompt" \
  --pack-id PACK_ID \
  --slides 5 \
  --slide-config-json '{
    "total_slides": 5,
    "slide_types": ["image_pack","image_pack","image_pack","image_pack","image_pack"],
    "pinned_images": {
      "0": "https://...hook-bg...",
      "1": "https://...problem-bg...",
      "2": "https://...discovery-bg...",
      "3": "https://...feature-bg...",
      "4": "https://...cta-bg..."
    }
  }'
```

**Without `pinned_images`, your visual inspection is wasted.**

#### Quick reference: what NOT to do

```bash
# BAD: server picks random images, your image analysis was pointless
genviral.sh generate --prompt "..." --pack-id PACK_ID --slides 5

# GOOD: you control which image goes on which slide
genviral.sh generate --prompt "..." --pack-id PACK_ID --slides 5 \
  --slide-config-json '{"total_slides":5,"slide_types":["image_pack","image_pack","image_pack","image_pack","image_pack"],"pinned_images":{"0":"URL_0","1":"URL_1","2":"URL_2","3":"URL_3","4":"URL_4"}}'
```

#### Alternative: `custom_images` approach
Use `custom_image` type with `custom_images` for full manual control (images AND text):
```json
{
  "total_slides": 5,
  "slide_types": ["custom_image","custom_image","custom_image","custom_image","custom_image"],
  "custom_images": {
    "0": {"image_url": "https://...", "image_name": "hook-bg"},
    "1": {"image_url": "https://...", "image_name": "problem-bg"}
  },
  "slide_texts": {"0": "your hook text", "1": "your problem text"}
}
```

Use `custom_images + --skip-ai` for full manual control. Use `pinned_images` + AI for AI-written text with your image choices.

### Choosing text styles (THINK — don't follow a rigid table)

Different backgrounds call for different text styles. Do NOT use the same style on every slide, and do NOT follow rigid rules. Use your judgment based on what you see.

**Available styles and what they do:**
- `tiktok` — White text with strong black outline/stroke. The "default" TikTok look.
- `inverted` — Black text on a white box. High contrast, cuts through anything.
- `shadow` — White text with heavy drop shadow. Subtle separation from background.
- `white` — Plain white text, minimal styling.
- `black` — Plain black text, minimal styling.
- `snapchat` — White text on a translucent dark bar.

**What to consider when choosing:**
- How busy/detailed is the background? (metadata keywords hint at this; vision tool confirms)
- What's the dominant color/brightness of the area where text lands?
- Does the slide have a clear zone for text, or is the whole image complex?
- What's the overall aesthetic of the slideshow? Consistency matters, but readability matters more.

**You have full control per slide.** Set `style_preset` per text element using `slides[].text_elements[].style_preset` in the `update-slideshow` command. Mix styles across slides when it makes sense.

**You can also adjust the background itself** with `background_filters` via `update-slideshow`. Must include all 10 sub-fields:
- Darken a busy image: `{"brightness": 0.5, "contrast": 1, "saturation": 1, "hue": 0, "blur": 0, "grayscale": 0, "sepia": 0, "invert": 0, "drop_shadow": 0, "opacity": 1}`
- Blur: same object with `"blur": 2`

**The goal is readability.** If text is hard to read at a glance, fix it — change the style, adjust the background, or pick a different image. There's no single "correct" style; the correct one is whatever makes the slide look good and the text instantly readable.

---

## create-pack
Create a new pack.

```bash
genviral.sh create-pack --name "My Pack"
genviral.sh create-pack --name "Public Pack" --is-public
genviral.sh create-pack --name "Private Pack" --is-public false
```

---

## update-pack
Update pack name or visibility.

```bash
genviral.sh update-pack --id PACK_ID --name "New Name"
genviral.sh update-pack --id PACK_ID --is-public true
```

---

## delete-pack
```bash
genviral.sh delete-pack --id PACK_ID
```

---

## add-pack-image
Add an image to a pack. AI metadata generates asynchronously — re-fetch later to get completed metadata.

```bash
genviral.sh add-pack-image --pack-id PACK_ID --image-url "https://cdn.example.com/image.jpg"
genviral.sh add-pack-image --pack-id PACK_ID --image-url "https://..." --file-name "hero-1.jpg"
```

---

## delete-pack-image
Remove an image from a pack.

```bash
genviral.sh delete-pack-image --pack-id PACK_ID --image-id IMAGE_ID
```
