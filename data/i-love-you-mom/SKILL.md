---
name: mixtiles-monthly
description: Automated monthly photo-to-Mixtiles pipeline. Collects photos from a WhatsApp group, curates the best ones using vision, builds a multi-photo Mixtiles cart link, and sends it. Use when it's time for the monthly Mixtiles order, when asked to "run the monthly tiles", "collect family photos for tiles", or on the monthly cron trigger.
metadata: {"openclaw": {"emoji": "🖼️", "requires": {"bins": ["wacli", "jq", "python3"]}}}
---

# Mixtiles Monthly Pipeline

Automatically collect the best family photos from a WhatsApp group each month, curate them, and generate a ready-to-order Mixtiles cart link.

## Configuration

These environment variables control the pipeline. Set them before running:

| Variable | Description | Default |
|----------|-------------|---------|
| `MIXTILES_GROUP_JID` | WhatsApp group JID to collect photos from | *(required)* |
| `MIXTILES_SEND_TO` | Where to send the cart link (group JID or phone number) | Same as `MIXTILES_GROUP_JID` |
| `MIXTILES_PHOTO_COUNT` | How many photos to select | `4` |
| `MIXTILES_TILE_SIZE` | Tile size for the order | `RECTANGLE_12X16` |

## Pipeline Steps

### Step 1: Collect Photos

Calculate the date range for last month and download all photos from the group:

```bash
# Calculate first day of last month
YEAR_MONTH=$(date -v-1m +%Y-%m)  # macOS
AFTER_DATE="${YEAR_MONTH}-01"
OUTPUT_DIR=~/mixtiles-queue/${YEAR_MONTH}

# Run the collection script
bash <skill-dir>/scripts/collect-photos.sh "$MIXTILES_GROUP_JID" "$AFTER_DATE" "$OUTPUT_DIR"
```

The script outputs a JSON manifest on stdout with `{id, sender, timestamp, filepath}` for each downloaded photo.

### Step 2: Curate with Vision

Read each downloaded photo using your vision capability. For each photo, evaluate:

**Include if:**
- Real family/life moment (people, gatherings, milestones, kids, travel, pets)
- Good image quality (clear, well-lit, in focus)
- Unique scene (not a near-duplicate of another photo)

**Exclude if:**
- Screenshot, meme, forwarded image, or link preview
- Blurry, too dark, or very low quality
- Near-duplicate of a better version already selected
- Text-heavy image (WhatsApp forwards, news articles)
- Promotional content or ads

### Step 3: Select Top Photos

From the curated set, pick the top `$MIXTILES_PHOTO_COUNT` photos (default: 4). Prioritize:
1. People and faces (especially kids, family gatherings)
2. Milestone moments (birthdays, first steps, graduations)
3. Travel and experiences
4. Variety — don't pick 4 photos from the same event if there are others

If fewer than `$MIXTILES_PHOTO_COUNT` good photos exist, use whatever passes curation.

### Step 4: Build Multi-Photo Cart

Use the mixtiles-it skill's script with the `--batch` flag:

```bash
MIXTILES_CART_SCRIPT="$(find ~/.openclaw/workspace/skills/mixtiles-it/scripts -name 'mixtiles-cart.py')"

python3 "$MIXTILES_CART_SCRIPT" \
  --batch <photo1> <photo2> <photo3> <photo4> \
  --size "${MIXTILES_TILE_SIZE:-RECTANGLE_12X16}"
```

This uploads each photo to Cloudinary and outputs a single Mixtiles cart URL with all photos.

### Step 5: Send the Link

Send the cart link to the target chat:

```bash
SEND_TO="${MIXTILES_SEND_TO:-$MIXTILES_GROUP_JID}"

wacli send text \
  --to "$SEND_TO" \
  --message "Your monthly tiles are ready! Here are the best ${MIXTILES_PHOTO_COUNT:-4} photos from last month. Tap to customize and order: $CART_URL"
```

## Error Handling

- If `collect-photos.sh` finds 0 photos: report that no images were found for the period and skip the pipeline.
- If fewer photos pass curation than `MIXTILES_PHOTO_COUNT`: use all that passed — even 1 photo is worth sending.
- If Cloudinary upload fails for a photo: skip that photo, continue with the rest.
- If `wacli send` fails: print the cart URL so the user can send it manually.

## Manual Trigger

To run the pipeline outside the monthly schedule:

> Run the mixtiles-monthly skill: collect photos from the family group for the past month, curate the best ones, build a multi-photo cart link, and send it.
