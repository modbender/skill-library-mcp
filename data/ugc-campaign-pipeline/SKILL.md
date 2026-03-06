---
name: ugc-campaign-pipeline
description: |
  Complete UGC video campaign pipeline: product → hero image → variations → videos → edited final.
  
  ✅ USE WHEN:
  - User says "crear campaña UGC" or "pipeline completo"
  - Need end-to-end UGC video production
  - Starting from product image/URL → final edited video
  - Want the full Doritos-style workflow
  
  ❌ DON'T USE WHEN:
  - Just need one step (use individual skills)
  - Already have final videos, just editing → use Remotion
  - Only need images, no video → use Morpheus only
  
  OUTPUT: Edited MP4 video with multiple scenes + subtitles + logo
---

# UGC Campaign Pipeline

Complete workflow for creating UGC-style promotional videos from a product.

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     UGC CAMPAIGN PIPELINE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STEP 1: HERO IMAGE                                                  │
│  ├─ Input: Product image + model selection                          │
│  ├─ Tool: morpheus-fashion-design                                    │
│  └─ Output: ~/clawd/outputs/{project}/morpheus/hero.png             │
│                                                                      │
│  STEP 2: VARIATIONS                                                  │
│  ├─ Input: Hero image                                                │
│  ├─ Tool: multishot-ugc                                              │
│  └─ Output: ~/clawd/outputs/{project}/multishot/*.png (10 images)   │
│                                                                      │
│  STEP 3: SELECTION                                                   │
│  ├─ Analyze all 11 images                                            │
│  ├─ Criteria: variety, no errors, lip-sync friendly                  │
│  └─ Output: 4 best images selected                                   │
│                                                                      │
│  STEP 4: SCRIPT                                                      │
│  ├─ Write 4-scene dialogue script                                    │
│  ├─ Format: PURE DIALOGUE (no annotations)                           │
│  └─ Output: 4 lines of dialogue                                      │
│                                                                      │
│  STEP 5: UGC VIDEOS                                                  │
│  ├─ Input: 4 images + 4 script lines                                 │
│  ├─ Tool: veed-ugc (run 4 times)                                     │
│  └─ Output: ~/clawd/outputs/{project}/ugc/*.mp4 (4 videos)          │
│                                                                      │
│  STEP 6: FINAL EDIT                                                  │
│  ├─ Input: 4 videos + logo                                           │
│  ├─ Tool: Remotion                                                   │
│  ├─ Add: subtitles, transitions, logo ending                         │
│  └─ Output: ~/clawd/outputs/{project}/final/video.mp4               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Execution Checklist

### Before Starting
- [ ] Product image received
- [ ] Brand/product name known
- [ ] Target audience understood
- [ ] Tone defined (casual, professional, energetic)

### Step 1: Hero Image (Morpheus)
```bash
# Select model from catalog
cat ~/clawd/models-catalog/catalog/catalog.json | jq '[.talents[] | select(.gender == "male/female") | {id, name, ethnicity}]'

# Generate hero image
COMFY_DEPLOY_API_KEY="..." uv run ~/.clawdbot/skills/morpheus-fashion-design/scripts/generate.py \
  --product "product.jpg" \
  --model "models-catalog/catalog/images/model_XX.jpg" \
  --brief "..." \
  --target "..." \
  --aspect-ratio "9:16" \
  --output "~/clawd/outputs/{project}/morpheus/hero.png"
```

### Step 2: Variations (Multishot)
```bash
COMFY_DEPLOY_API_KEY="..." uv run ~/.clawdbot/skills/multishot-ugc/scripts/generate.py \
  --image "~/clawd/outputs/{project}/morpheus/hero.png" \
  --output-dir "~/clawd/outputs/{project}/multishot" \
  --resolution "2K" \
  --aspect-ratio "9:16"
```

### Step 3: Selection Criteria
Analyze all 11 images for:
- ✅ Face clearly visible (frontal or 3/4)
- ✅ Mouth not obscured
- ✅ No distorted hands/fingers
- ✅ Product visible
- ✅ Different from other selected images

Select 4 images that are:
1. Different angles/perspectives
2. Suitable for lip-sync
3. Error-free

### Step 4: Script Writing
Write 4 lines of pure dialogue:
```
ESCENA 1: [Opening hook - grab attention]
ESCENA 2: [Problem/benefit - relate to audience]  
ESCENA 3: [Feature highlight - specific value]
ESCENA 4: [CTA/brand mention - close strong]
```

**Rules:**
- Pure dialogue only
- NO annotations: [excited], (pause), *smiles*
- NO stage directions
- NO tone indicators
- Just what the person says

### Step 5: Generate Videos (VEED)
```bash
for i in 1 2 3 4; do
  COMFY_DEPLOY_API_KEY="..." uv run ~/.clawdbot/skills/veed-ugc/scripts/generate.py \
    --image "selected_image_$i.png" \
    --script "Script line $i" \
    --output "~/clawd/outputs/{project}/ugc/escena$i.mp4"
done
```

### Step 6: Final Edit (Remotion)
Create Remotion project with:
- All 4 video clips sequenced
- Animated subtitles for each scene
- Logo animation at end
- Render to final MP4

---

## Script Templates by Industry

### Snacks/Food
```
Escena 1: Che, tenés que probar esto.
Escena 2: [Sabor/textura highlight]. Te pega de una.
Escena 3: Y mirá, no es solo [feature], tiene ese gustito que te deja queriendo más.
Escena 4: [Brand + Product]. Una vez que arrancás, no parás.
```

### Tech/Gadgets
```
Escena 1: Mirá lo que me llegó.
Escena 2: Esto cambia todo. [Key feature].
Escena 3: Y lo mejor? [Secondary benefit].
Escena 4: [Brand]. Ya no vuelvo atrás.
```

### Beauty/Skincare
```
Escena 1: Ok, necesito contarte algo.
Escena 2: Este [producto] es increíble. [Result].
Escena 3: Lo uso hace [tiempo] y mirá la diferencia.
Escena 4: [Brand]. Tu piel te lo va a agradecer.
```

### Fashion
```
Escena 1: Encontré mi nueva obsesión.
Escena 2: Mirá este [prenda]. [Quality/style].
Escena 3: Combina con todo y es súper [comfort/style].
Escena 4: [Brand]. Estilo sin esfuerzo.
```

---

## Output Structure

```
~/clawd/outputs/{project}/
├── morpheus/
│   └── hero.png              # Original hero image
├── multishot/
│   ├── 1_00001_.png          # 10 variations
│   ├── 2_00001_.png
│   └── ...
├── ugc/
│   ├── escena1.mp4           # Individual scene videos
│   ├── escena2.mp4
│   ├── escena3.mp4
│   └── escena4.mp4
├── assets/
│   └── logo.png              # Brand logo
└── final/
    └── video.mp4             # Final edited video
```

---

## Quality Checklist (Before Delivery)

- [ ] Hero image: product visible, model looks natural
- [ ] Variations: 4 selected are distinct and lip-sync ready
- [ ] Script: matches brand tone, pure dialogue format
- [ ] Videos: lip-sync quality is good, no artifacts
- [ ] Final: subtitles readable, transitions smooth, logo appears
- [ ] Audio: voice quality clear, timing natural
