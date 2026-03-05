# Slideshow Commands

## generate | generate-slideshow
Generate a slideshow from a prompt (AI mode), or build it manually with explicit slide config (`--skip-ai`).

```bash
# AI mode (default)
genviral.sh generate \
  --prompt "Your hook and content prompt" \
  --pack-id PACK_ID \
  --slides 5 \
  --type educational \
  --aspect-ratio 4:5 \
  --style tiktok \
  --language en \
  --font-size small \
  --text-width narrow \
  --product-id PRODUCT_ID

# Manual/mixed mode with slide_config
genviral.sh generate \
  --skip-ai \
  --slide-config-file slide-config.json

# Pass slide_config inline
genviral.sh generate \
  --skip-ai \
  --slide-config-json '{"total_slides":2,"slide_types":["image_pack","custom_image"],...}'
```

Options:
- `--prompt` -> `prompt` (required unless `--skip-ai true` or `--product-id` is provided)
- `--product-id` -> `product_id` (UUID, optional)
- `--pack-id` -> `pack_id` (UUID, optional global image pack)
- `--slides` -> `slide_count` (`1-10`, default `5`)
- `--type` -> `slideshow_type` (`educational` or `personal`)
- `--aspect-ratio` -> `aspect_ratio` (`9:16`, `4:5`, `1:1`)
- `--language` -> `language` (2-32 chars, e.g. `en`, `es`, `fr`)
- `--style` / `--text-preset` -> `advanced_settings.text_preset`
- `--font-size` -> `advanced_settings.font_size` (`default`, `small`, or numeric `8-200`)
- `--text-width` -> `advanced_settings.text_width` (`default` or `narrow`)
- `--skip-ai` -> `skip_ai` (bool)
- `--slide-config-json` / `--slide-config` -> `slide_config` (inline JSON)
- `--slide-config-file` -> `slide_config` (JSON file)

`slide_config` supports:
- `total_slides` (1-10)
- `slide_types` (exact length = `total_slides`, each `image_pack` or `custom_image`)
- `custom_images` map: `{"index": {"image_url", "image_id", "image_name?"}}` (required for each `custom_image` slide)
- `pinned_images` map: `{"index": "https://..."}`
- `slide_texts` map: `{"index": "text"}`
- `slide_text_elements` map: `{"index": [{"content", "x", "y", "id?", "font_size?", "width?"}]}`
- `pack_assignments` map: `{"index": "pack_uuid"}` (only for `image_pack` slides)

Validation rules:
- All slide-config map keys must be numeric 0-based indices in range.
- `slide_types.length` must equal `total_slides`.
- Every `image_pack` slide must resolve a pack via global `pack_id` or per-slide `pack_assignments[index]`.
- Every `custom_image` slide must have `custom_images[index]`.

---

## render | render-slideshow
Render a slideshow to images via Remotion.

```bash
genviral.sh render --id SLIDESHOW_ID
```

Returns:
- Updated slideshow with rendered image URLs
- Status: `rendered`

---

## review | get-slideshow
Get full slideshow details for review. Shows slide text, status, rendered URLs.

```bash
genviral.sh review --id SLIDESHOW_ID
genviral.sh review --id SLIDESHOW_ID --json
genviral.sh get-slideshow --id SLIDESHOW_ID  # alias
```

---

## update | update-slideshow
Update slideshow fields, settings, or slides. Re-render after updating slides.

```bash
# Update title
genviral.sh update --id SLIDESHOW_ID --title "New Title"

# Update status
genviral.sh update --id SLIDESHOW_ID --status draft

# Update settings
genviral.sh update --id SLIDESHOW_ID --settings-json '{"aspect_ratio":"9:16","advanced_settings":{"text_width":"narrow"}}'

# Update slides (full replacement)
genviral.sh update --id SLIDESHOW_ID --slides '[{"image_url":"...","text_elements":[{"content":"..."}]}]'

# Load slides from file
genviral.sh update --id SLIDESHOW_ID --slides-file slides.json

# Update product_id or clear it
genviral.sh update --id SLIDESHOW_ID --product-id NEW_PRODUCT_ID
genviral.sh update --id SLIDESHOW_ID --clear-product-id
```

Options:
- `--title` - Update title
- `--status` - `draft` or `rendered`
- `--slideshow-type` - `educational` or `personal`
- `--product-id` / `--clear-product-id` - Link or detach product
- `--settings-json` / `--settings-file` - Partial settings patch
- `--slides` / `--slides-file` - Full slides array replacement

**Critical: `--slides` payload rules (the API is strict about these):**

1. **No `null` values.** Omit any field you don't want to set.
2. **No `index` field.** Slide order is determined by array position (0-based).
3. **`background_filters` requires ALL 10 sub-fields** when present:
   ```json
   "background_filters": {
     "brightness": 0.5, "contrast": 1, "saturation": 1, "hue": 0,
     "blur": 0, "grayscale": 0, "sepia": 0, "invert": 0,
     "drop_shadow": 0, "opacity": 1
   }
   ```
   Defaults: brightness=1, contrast=1, saturation=1, hue=0, blur=0, grayscale=0, sepia=0, invert=0, drop_shadow=0, opacity=1.
4. **Each slide needs at minimum:** `image_url` and `text_elements` array (can be empty `[]`).
5. **Preserve existing fields** — `--slides` fully replaces all slides.

**Example: darken slide 0's background:**
```json
[
  {
    "image_url": "https://cdn.example.com/slide-0-bg.jpg",
    "text_elements": [{"content": "Your hook text", "x": 50, "y": 50, "font_size": 48, "width": 80, "style_preset": "tiktok"}],
    "background_filters": {"brightness": 0.5, "contrast": 1, "saturation": 1, "hue": 0, "blur": 0, "grayscale": 0, "sepia": 0, "invert": 0, "drop_shadow": 0, "opacity": 1}
  }
]
```

---

## Text Styles, Fonts, and Formatting

### Global generation controls (`advanced_settings`)
- `font_size`: `default`, `small`, or numeric `8-200`
- `text_width`: `default` (wide) or `narrow`
- `text_preset`: style preset string

`font_size` preset mapping:
- `default`: title/single `48px`, body `40px`
- `small`: title/single `40px`, body `33px`
- If user says "bigger than small" without a number, use a midpoint like `44`.

### Text presets
- `tiktok` - White text with strong black outline/stroke
- `inverted` - Black text on a white text box
- `shadow` - White text with heavy shadow
- `white` - Plain white text
- `black` - Plain black text
- `snapchat` - White text on translucent black bar

**Partner API note:** `PATCH /slideshows/{id}` `slides[].text_elements[].style_preset` validates: `tiktok`, `inverted`, `shadow`, `white`, `black`.

### Available fonts
Anton, Arial, Bebas Neue, Bitcount, Cinzel, Della, Eagle Lake, Georgia, Helvetica, Inter, Open Sans, Oswald, Playwrite, Poppins, Roboto, Russo One, TikTok Display (default), TikTok Sans, Times New Roman

Apply font per text element using `slides[].text_elements[].font_family`.

### Per-text-element formatting fields
- `content`, `x`, `y`, `font_size`, `width`, `height`
- `style_preset`, `font_family`
- `background_color`, `text_color`, `border_radius`
- `editable`

### Other slide-level visual controls
- `grid_images` + `grid_type` (`2x2`, `1+2`, `vertical`, `horizontal`)
- `background_filters` (brightness, contrast, saturation, hue, blur, grayscale, sepia, invert, drop_shadow, opacity)
- `image_overlays` (id, image_url, x, y, width, height, rotation, opacity)

---

## regenerate-slide
Regenerate AI text for a single slide (0-indexed).

```bash
genviral.sh regenerate-slide --id SLIDESHOW_ID --index 2
genviral.sh regenerate-slide --id SLIDESHOW_ID --index 2 --instruction "Make this shorter and more punchy"
```

Constraints:
- `--index` must be a non-negative integer
- `--instruction` max length: 500 characters

---

## duplicate | duplicate-slideshow
Clone an existing slideshow as a new draft.

```bash
genviral.sh duplicate --id SLIDESHOW_ID
```

---

## delete | delete-slideshow
Delete a slideshow.

```bash
genviral.sh delete --id SLIDESHOW_ID
```

---

## list-slideshows
List slideshows with filtering and pagination.

```bash
genviral.sh list-slideshows
genviral.sh list-slideshows --status rendered --search "hook" --limit 20 --offset 0
genviral.sh list-slideshows --json
```
