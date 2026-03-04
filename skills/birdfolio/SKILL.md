---
name: birdfolio
description: >
  Bird identification, life list tracking, and trading card generation.
  Use this skill when the user: sends a bird photo to identify, says "set up
  my Birdfolio" or "set my region", asks "how's my checklist", asks "Birdfolio
  progress", asks "how many birds have I found", asks "show my Birdfolio" or
  "show my life list", asks "what's my rarest bird", or asks "tell me about
  [bird species]". Handles everything from first-time setup through ongoing
  life list tracking and visual trading card generation.
---

# Birdfolio

Birdfolio turns bird photos into a personal life list. Users photograph birds in the wild, send the photo to you, and you identify the species with Vision. You.com provides real-time rarity and regional data. Each sighting is logged to a life list with a Pokémon-inspired rarity tier (Common / Rare / Super Rare) and gets a visual trading card sent back via Telegram.

**Data lives in:** Railway PostgreSQL (via API) + local `birdfolio/` folder (cards, birds, config)
**Scripts live in:** `{baseDir}/scripts/`
**API:** `https://api-production-d0e2.up.railway.app` (also saved to `birdfolio/config.json` after init)
**Schema reference:** `{baseDir}/references/data-schema.md`
**Search queries:** `{baseDir}/references/you-search-queries.md`

> **Note on --workspace & --api-url:** Every data script accepts `--workspace` (absolute path to `birdfolio/`) and `--api-url` (API base URL). After `init_birdfolio.py` runs, both the API URL and Telegram ID are saved to `birdfolio/config.json` and read automatically — subsequent scripts only need `--workspace`.
>
> **Telegram ID:** Read from the inbound message metadata (`sender_id`). Pass as `--telegram-id` to `init_birdfolio.py` on first setup.

---

## 1. Setup Flow

**Trigger:** User says "Set up my Birdfolio", "set my region", or sends a photo before setup exists.

**Check first:** If `birdfolio/config.json` exists in your workspace, setup is already done — skip to the relevant flow.

**Steps:**

1. Ask: *"What's your home region? (e.g. California, Texas, United Kingdom)"*

2. Run to create the workspace folder structure and register the user in the API:
   ```
   exec: python {baseDir}/scripts/init_birdfolio.py \
     --telegram-id {senderTelegramId} \
     --region "{region}" \
     --api-url "https://api-production-d0e2.up.railway.app" \
     --workspace <absolute path to birdfolio/ in your workspace>
   ```

3. Search You.com (run all three):
   ```
   "{region} most common backyard birds eBird species list"
   "{region} uncommon seasonal rare birds eBird checklist"
   "{region} rare vagrant endangered birds eBird"
   ```

4. From results, build a checklist with **10 common, 5 rare, 1 super rare** species. Use classification signals from `{baseDir}/references/you-search-queries.md`.

5. Write the populated checklist to `birdfolio/checklist.json` in your workspace:
   ```json
   {
     "{region}": {
       "common": [
         { "species": "American Robin", "slug": "american-robin", "found": false, "dateFound": null }
       ],
       "rare": [...],
       "superRare": [...]
     }
   }
   ```

6. Reply with a welcome message and checklist preview:
   ```
   🦅 Birdfolio is set up for {region}!

   Your checklist:
   Common (10):  American Robin, House Sparrow, ...
   Rare (5):     Great Blue Heron, ...
   Super Rare:   California Condor

   Send me a bird photo to start collecting!
   ```

---

## 2. Bird Identification Flow

**Trigger:** User sends a photo.

> **Getting the photo file path:** When a user sends a photo via Telegram, OpenClaw downloads it and makes the local file path available in the message attachment metadata. Capture this path — you'll need it for card generation in Step 5. If OpenClaw provides the image inline without a path, use `exec` to find the most recently downloaded file in OpenClaw's temp/media folder, or check `%APPDATA%\openclaw\media\` on Windows. Save the photo to `birdfolio/birds/{slug}-{timestamp}.jpg` for permanent storage:
> ```
> exec: copy "<attachment path>" "birdfolio/birds/<slug>-<timestamp>.jpg"
> ```

### Step 1 — Identify with Vision

The submitted photo is directly visible in your context. Analyze it (or use the `image` tool if it's not inline):
```
Identify the bird species in this photo. Return JSON only:
{
  "commonName": "...",
  "scientificName": "...",
  "confidence": "high|medium|low",
  "features": ["visible feature 1", "visible feature 2"]
}
```

**Rarity rules:**
- Bird IS on the checklist → use its tier: `common`, `rare`, or `superRare`
- Bird is NOT on the checklist → use `bonus` (shows a neutral "Bonus Find" badge, no rarity assigned)

**Confidence rules:**
- `"high"` → proceed automatically, no confirmation needed
- `"medium"` → ask: *"I think this might be a [species] — based on [features]. Does that look right to you?"* → wait for confirmation before continuing
- `"low"` → reply: *"This photo isn't clear enough for me to be confident. Could you send a clearer shot?"* → stop, do not log anything

### Step 2 — Rarity lookup

Search You.com:
```
"{commonName} {homeRegion} eBird frequency how common rare"
```

Classify using these signals:
| Tier | Script value | Signals |
|------|-------------|---------|
| Common 🟢 | `common` | "abundant", "widespread", "year-round resident", >50% of checklists |
| Rare 🟡 | `rare` | "uncommon", "seasonal", "migratory", "occasional", 5–50% of checklists |
| Super Rare 🔴 | `superRare` | "rare", "vagrant", "accidental", "endangered", <5% of checklists |

When unsure → default to **`rare`**. Always use the script value (e.g. `superRare`, not `Super Rare`) when passing `--rarity` to any script.

### Step 3 — Get a fun fact

Search You.com:
```
"{commonName} bird interesting facts habitat behavior"
```

Extract one punchy fact (1–2 sentences).

### Step 4 — Log the sighting

Save the sighting to `birdfolio/lifeList.json` in your workspace:
```
exec: python {baseDir}/scripts/log_sighting.py \
  --species "{commonName}" \
  --scientific-name "{scientificName}" \
  --rarity "{rarity}" \
  --region "{homeRegion}" \
  --notes "" \
  --workspace <absolute path to birdfolio/ in your workspace>
```

Capture from output: `isLifer`, `totalSightings`, `totalSpecies`.

### Step 5 — Update checklist

Mark the species as found in `birdfolio/checklist.json`:
```
exec: python {baseDir}/scripts/update_checklist.py \
  --species "{commonName}" \
  --region "{homeRegion}" \
  --workspace <absolute path to birdfolio/ in your workspace>
```

### Step 6 — Generate trading card

The card is a two-column design: the user's photo fills the left panel (280px), a solid dark info panel sits on the right. **Always use the user's actual submitted photo** — not a stock image.

**Step 6a — Detect bird position with Vision:**
Use the `image` tool on the submitted photo:
> "Where is the bird positioned horizontally in this photo? Give me approximately what percentage from the left edge the bird's center is (0–100)."

Convert the answer to a CSS value: `"40% center"`, `"60% center"`, `"center center"`, etc. Use this as `--object-position`.

**Step 6b — Generate the card HTML with the embedded photo:**
```
exec: python {baseDir}/scripts/generate_card.py \
  --species "{commonName}" \
  --scientific-name "{scientificName}" \
  --rarity "{rarity}" \
  --region "{homeRegion}" \
  --date "{YYYY-MM-DD}" \
  --fun-fact "{funFact}" \
  --image-path "<absolute path to submitted photo>" \
  --object-position "{objectPosition}" \
  --life-count {totalSpecies} \
  --workspace <absolute path to birdfolio/ in your workspace>
```

`--image-path` embeds the user's actual photo as base64 directly into the HTML. No separate embed step needed.

**Fallback if photo path is unavailable:** omit `--image-path` and pass `--image-url "<stock photo URL>"` instead (find a URL via You.com: `"{commonName} bird photo wildlife"`).

Capture `cardPath` from output.

**Step 6c — Screenshot, save, upload, and send:**
Run the screenshot script to render the card at 600×400 and save a PNG:
```
exec: node {baseDir}/scripts/screenshot_card.js "<cardPath>"
```
Capture `pngPath` from output.

Upload to Cloudflare R2 and get a public URL:
```
exec: python {baseDir}/scripts/upload_card.py "<pngPath>"
```
Capture `url` from output.

Update the sighting's card URL in the API (use the `id` from the log_sighting output):
```
PATCH /users/{telegram_id}/sightings/{sighting_id}/card
Body: {"card_png_url": "<url>"}
```

Send the PNG via Telegram:
```
message(action="send", media="<pngPath>")
```

### Step 7 — Reply

- If `isLifer` is true:
  *"🎉 New lifer! That's your first ever [commonName]! Bird #[totalSpecies] in your Birdfolio."*

  **If `totalSpecies == 1` (this is their very first bird ever):** also send their personal PWA link:
  *"🦅 Your Birdfolio is live! Bookmark this link to see your life list:
  https://birdfolio.tonbistudio.com/app/[telegram_id]"*

  The `telegram_id` is the sender's Telegram ID from the inbound message metadata (`sender_id`). This is also stored in `birdfolio/config.json` after init.

- Otherwise:
  *"[commonName] spotted! You've now seen [N] species in your Birdfolio."*

Include: rarity badge emoji, the fun fact, checklist status (if species was on checklist, mention it).

**Fallback if screenshot fails:** Send a formatted text card:
```
🦅 [RARITY_EMOJI] [Common Name]
Scientific: [Scientific Name]
Region: [Region] | Spotted: [Date]
Rarity: [Rarity]
💡 [Fun Fact]
Bird #[N] in your Birdfolio
```

---

## 3. Checklist & Stats

**Trigger:** "How's my checklist?", "Birdfolio progress", "How many birds have I found?"

```
exec: python {baseDir}/scripts/get_stats.py \
  --workspace <absolute path to birdfolio/ in your workspace>
```

Format response using `checklistProgress` from output:

```
📋 {region} Checklist

Common     ✅✅✅⬜⬜⬜⬜⬜⬜⬜  3/10
Rare       ✅⬜⬜⬜⬜              1/5
Super Rare ⬜                      0/1

🐦 {totalSpecies} species | {totalSightings} total sightings
📍 Last spotted: {mostRecentSighting.commonName} on {date}
🏆 Rarest find: {rarestBird.commonName} ({rarity})
```

Use ✅ for found, ⬜ for not found. One box per species.

**Optional visual checklist card:** Generate a visual HTML checklist card and screenshot it:
```
exec: python {baseDir}/scripts/generate_checklist_card.py \
  --workspace <absolute path to birdfolio/ in your workspace>
```
Then screenshot with `screenshot_card.js` and send the PNG.

---

## 4. Life List View

**Trigger:** "Show my Birdfolio", "Show my life list"

Read `birdfolio/lifeList.json` from your workspace.

Group lifers by rarity (Super Rare first, then Rare, then Common). Format as a text list or generate an HTML gallery, save it to `birdfolio/my-birdfolio.html` in your workspace, and screenshot it.

---

## 5. Species Lookup (no logging)

**Trigger:** "Tell me about [species]"

Search You.com:
```
"{species} bird facts habitat range behavior diet"
"{species} bird {homeRegion} eBird frequency resident or migratory"
```

Return a conversational summary. Do **not** log a sighting or generate a card.

---

## 6. Rarest Bird

**Trigger:** "What's my rarest bird?", "Show my best find"

```
exec: python {baseDir}/scripts/get_stats.py \
  --workspace <absolute path to birdfolio/ in your workspace>
```

Read `rarestBird` from output and reply with species name, rarity, date spotted, and region.

---

## Quick Reference

| Script | Key args | Returns |
|--------|----------|---------|
| `init_birdfolio.py` | `--telegram-id`, `--region`, `--api-url`, `--workspace` | `{status, workspace, files_created, next}` |
| `log_sighting.py` | `--species`, `--scientific-name`, `--rarity`, `--region`, `--date`, `--workspace` | `{status, sighting, isLifer, totalSightings, totalSpecies}` |
| `update_checklist.py` | `--species`, `--region`, `--workspace` | `{status, tier, dateFound}` or `{status: not_on_checklist}` |
| `get_stats.py` | `--workspace` | `{totalSightings, totalSpecies, checklistProgress, mostRecentSighting, rarestBird}` |
| `generate_card.py` | `--species`, `--scientific-name`, `--rarity`, `--region`, `--date`, `--fun-fact`, `--image-path` (preferred) OR `--image-url`, `--object-position`, `--life-count`, `--workspace` | `{status, cardPath, filename}` |
| `generate_checklist_card.py` | `--workspace` | `{status, cardPath}` — visual HTML checklist card |
| `screenshot_card.js` | `<cardPath>` `[outputPath]` | `{status, pngPath}` — saves PNG to `birdfolio/cards/` |
| `upload_card.py` | `<pngPath>` `[--secrets path]` | `{status, url}` — uploads to R2, returns public URL |

All Python scripts output JSON to stdout. Always pass absolute `--workspace` path.
`screenshot_card.js` uses OpenClaw's bundled `playwright-core` + system Chrome/Edge (no separate install needed).

