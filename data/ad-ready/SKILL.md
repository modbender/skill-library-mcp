---
name: ad-ready
description: |
  Generate advertising images automatically from a product URL + brand profile.
  
  ✅ USE WHEN:
  - User provides a product URL (e-commerce link)
  - Want automated product scraping + image generation
  - Have a brand profile to apply (70+ brands available)
  - Need funnel-stage targeting (awareness/consideration/conversion)
  - Want AI to auto-select model, scene, lighting based on brand
  
  ❌ DON'T USE WHEN:
  - User provides local product image file → use morpheus-fashion-design
  - Don't need a person in the image → use nano-banana-pro
  - Want manual control over model, scene, packs → use morpheus-fashion-design
  - Already have hero image, need variations → use multishot-ugc
  - Need video output → use veed-ugc after image generation
  
  INPUT: Product URL + brand name (optional) + funnel stage (optional)
  OUTPUT: PNG advertising image with product + model
---

# Ad-Ready: AI Advertising Image Generator

Generate professional advertising images from product URLs using a 4-phase AI pipeline on ComfyDeploy.

**Source:** [github.com/PauldeLavallaz/ads_SV](https://github.com/PauldeLavallaz/ads_SV)

---

## Pipeline Architecture

The pipeline runs as a ComfyUI custom node deployed on ComfyDeploy. A single `ProductToAds_Manual` node executes 4 phases internally:

```
┌─────────────────────────────────────────────────────────────┐
│                  ProductToAds_Manual Node                     │
│                                                             │
│  PHASE 1: Product Scraping (Gemini Flash)                   │
│  ─────────────────────────────────────────                   │
│  Scrapes product URL → extracts title, description,         │
│  features, price, materials, image URLs                      │
│  Also scrapes HTML for high-res product images (≥1000px)    │
│                                                             │
│  PHASE 2: Campaign Brief Generation (Gemini Flash)          │
│  ────────────────────────────────────────────────            │
│  Brand Identity + Product Data + References →                │
│  10-point Campaign Brief (creative direction)                │
│                                                             │
│  PHASE 3: Blueprint Generation (Gemini Flash)               │
│  ──────────────────────────────────────────────              │
│  Master Prompt (funnel stage) + Brief + Keywords →           │
│  Production-Ready JSON Blueprint                             │
│                                                             │
│  PHASE 4: Image Generation (Nano Banana Pro / Imagen 3)     │
│  ──────────────────────────────────────────────────          │
│  Blueprint + all reference images → final ad image           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Campaign Brief (The Creative Brain)

The Brief Generator is the most critical intermediate step. It acts as a "Senior Art Director" that translates raw data into actionable creative direction using a 10-point framework:

1. **Strategic Objective** — Why this campaign exists (awareness/positioning/launch)
2. **Central Message** — One idea perceivable without text
3. **Visual Tone of Voice** — Register: calm/energetic/intimate/monumental
4. **Product Role** — Hero vs co-protagonist vs implicit presence
5. **Visual Language & Brand Coherence** — Non-negotiable brand codes
6. **Photographer & Equipment** — Photography as concept, not execution
7. **Extended Art Direction** — Styling, casting, poses, hair/makeup, layout
8. **Environment & Context** — Where and why (conceptual, never decorative)
9. **Texture, Material & Product Render** — How surfaces are perceived
10. **Final Image Signature** — Finish, grain, temporal positioning

Without the brief, the Master Prompt must guess creative strategy. With it, the Master Prompt only executes.

The brief prompt template is included at `{baseDir}/configs/Brief_Generator/brief_prompt.json`.

### Phase 3: Master Prompts (8 Funnel Stages)

Each funnel stage has a specialized Master Prompt that generates a production-ready JSON Blueprint. All share the same internal simulation:

- **ROUND -1: Brand Identity Forensics** (stages 03+) — Unified Brand Style Manifest
- **ROUND 0: Fidelity Lock** — Product geometry & talent identity are IMMUTABLE
- **ROUND 1: Stage Strategy** — Strategic approach specific to funnel position
- **ROUND 2: Graphic Design** — UI, typography, CTA engineering

The Blueprint JSON covers: scene production, talent lock, camera perspective, subject action/pose/wardrobe, lighting, product constraints, layout architecture, typography, CTA engineering, and brand asset placement.

Master prompt files are included at `{baseDir}/configs/Product_to_Ads/`.

### Reference Analyzer

Reference images (`referencia`) are **optional** and **off by default**. The pipeline generates creative direction internally from Brand Identity + Campaign Brief. Only use a reference when the user explicitly asks to clone a specific ad's style.

When used, the reference is analyzed for pose, photographic style, and location cues.

---

## ⚠️ CRITICAL: Required Inputs Checklist

Before running ANY ad generation, ensure these are provided:

| Input | Required? | How to Get It |
|-------|-----------|---------------|
| `--product-url` | ✅ ALWAYS | User provides the product page URL |
| `--product-image` | ✅ ALWAYS | Download from the product page, or user provides |
| `--brand-profile` | ✅ NEVER EMPTY | Pick from catalog or run brand-analyzer first. NEVER leave as "No Brand" if a brand is known |
| `--prompt-profile` | ✅ ALWAYS | Choose based on campaign objective |
| `--aspect-ratio` | Default: 4:5 | Change if needed for platform |
| `--model` | 🔶 OPTIONAL | Model/talent face. Ads with talent perform much better. Empty = product-only ad (no person). When used, pick from `~/clawd/models-catalog/catalog/images/` (114 models available) |
| `--logo` | 🔶 OPTIONAL | Try to find it. Use if good quality & easy to get. Skip if low-res or hard to find. Empty = bypassed |
| `--reference` | 🔶 OPTIONAL (off) | Only when user explicitly asks to clone a reference ad. Empty = bypassed |
| `--creative-brief` | 🔶 ON-DEMAND | Only when user gives explicit creative direction. Omit to let pipeline auto-generate from brand profile |
| `--language` | 🔶 ON-DEMAND | Only when user requests a specific language. Omit to use default (es) |

### 🚨 NEVER Skip These Steps:

1. **Product image** — Download the main product photo from the product URL. The scraper is fragile; always provide a product image explicitly.
2. **Brand profile** — If the brand doesn't exist in the catalog, run `brand-analyzer` skill FIRST to generate one. Never submit with "No Brand" when a brand is known.
3. **Brand logo** — TRY to find it (Clearbit, logo.dev, brand website). Use if good quality. If not found or low-res, skip it — the variable accepts empty string (bypassed server-side).
4. **Reference** — Do NOT search for references by default. Only provide when the user explicitly asks to clone a specific ad or says "find a good ad to clone".

---

## Auto-Preparation Workflow

When the user asks to generate an ad:

```
1. User provides: product URL + brand name + objective

2. CHECK brand profile exists:
   → ls ~/clawd/ad-ready/configs/Brands/ | grep -i "{brand}"
   → If not found: run brand-analyzer skill first

3. DOWNLOAD product image:
   → Visit the product URL or fetch the page
   → Find and download the main product image
   → Save to /tmp/ad-ready-product.jpg

4. DOWNLOAD brand logo:
   → Search "{brand name} logo PNG" or fetch from brand website
   → Download clean logo image
   → Save to /tmp/ad-ready-logo.png

5. SELECT prompt profile based on objective:
   → 🎨 Morfeo_Creative: DEFAULT — cinematic, narrative-rich, slightly surreal. Best visuals.
   → Awareness: brand discovery, dynamic scenes, world-building, scroll-stoppers
   → Interest: sustained attention, micro-world hinting at use-case
   → Consideration: feature communication, proof cues, informative
   → Evaluation: trust, authority, reviews, certifications
   → Conversion: ⚠️ MINIMAL by design — clean, CTA-dominant, white backgrounds
   → Retention: post-purchase confidence, onboarding
   → Loyalty: editorial, lifestyle, emotional bond
   → Advocacy: share-worthy, community, belonging

   DEFAULT SELECTION LOGIC:
   - Generic "generate an ad" → Morfeo_Creative (09)
   - "awareness" / "brand discovery" → Awareness (01)
   - "conversion" / "buy now" / CTA-focused → Conversion (05)
   - "creative" / "original" / "surreal" → Morfeo_Creative (09)
   - "lifestyle" / "editorial" → Loyalty (07)
   - When in doubt → Morfeo_Creative (09), NOT Conversion

5b. SELECT MODEL (optional):
   → If user wants a person in the ad: pick from ~/clawd/models-catalog/catalog/images/model_XX.jpg (114 available)
   → If user wants product-only ad (no person): leave --model empty
   → If user doesn't specify: ASK if they want a model or product-only
   → Catalog preview: catalog.json at ~/clawd/models-catalog/catalog/catalog.json

6. RUN the generation with ALL inputs filled
```

---

## Usage

### Full command (recommended):
```bash
COMFY_DEPLOY_API_KEY="$KEY" uv run {baseDir}/scripts/generate.py \
  --product-url "https://shop.example.com/product" \
  --product-image "/tmp/product-photo.jpg" \
  --logo "/tmp/brand-logo.png" \
  --model "models-catalog/catalog/images/model_15.jpg" \
  --brand-profile "Nike" \
  --prompt-profile "Master_prompt_05_Conversion" \
  --aspect-ratio "4:5" \
  --output "ad-output.png"
```

### With reference (only when explicitly requested):
```bash
COMFY_DEPLOY_API_KEY="$KEY" uv run {baseDir}/scripts/generate.py \
  --product-url "https://shop.example.com/product" \
  --product-image "/tmp/product-photo.jpg" \
  --reference "/tmp/reference-ad.jpg" \
  --brand-profile "Nike" \
  --prompt-profile "Master_prompt_01_Awareness" \
  --output "ad-output.png"
```

### Auto-fetch mode (downloads product image and logo automatically):
```bash
COMFY_DEPLOY_API_KEY="$KEY" uv run {baseDir}/scripts/generate.py \
  --product-url "https://shop.example.com/product" \
  --brand-profile "Nike" \
  --prompt-profile "Master_prompt_05_Conversion" \
  --auto-fetch \
  --output "ad-output.png"
```

### List available brands:
```bash
uv run {baseDir}/scripts/generate.py --list-brands
```

---

## API Details

**Endpoint:** `https://api.comfydeploy.com/api/run/deployment/queue`
**Deployment ID:** `e37318e6-ef21-4aab-bc90-8fb29624cd15`

### ComfyDeploy Input Variables

| Variable | Type | Description |
|----------|------|-------------|
| `product_url` | string | Product page URL to scrape |
| `producto` | image URL | Product image (uploaded to ComfyDeploy) |
| `model` | image URL | Model/talent face reference. **OPTIONAL** — empty = product-only ad without a person. When used, select from models catalog (`~/clawd/models-catalog/catalog/images/model_XX.jpg`, 114 available) |
| `referencia` | image URL | Style reference ad — OPTIONAL, empty = bypassed. Only when user asks to clone a reference |
| `marca` | image URL | Brand logo — OPTIONAL, empty = bypassed. Use if found easily in good quality |
| `brand_profile` | enum | Brand name from catalog (70+ brands) |
| `prompt_profile` | enum | Funnel stage master prompt |
| `aspect_ratio` | enum | Output format (1:1, 4:5, 5:4, 9:16, etc.) |
| `language` | string | **ON-DEMAND ONLY.** Output language for ad copy/CTA. Default: `es`. Only send when the user explicitly requests a different language. Otherwise, DO NOT include this parameter — let the pipeline use its default. |
| `creative_brief` | string | **ON-DEMAND ONLY.** Free-text creative direction override. Only use when the user explicitly asks for a specific creative direction, scene, mood, or concept. Otherwise, DO NOT include this parameter — let the pipeline generate its own brief from the Brand Identity profile automatically. |

---

## Funnel Stages — Strategic Detail

### 01 — Awareness
**Goal:** Scroll-stop, curiosity, brand introduction
**Reject:** Generic "product on table" concepts
**Strategy:** Dynamic camera angles, world-building environments, high-concept creativity
**CTA:** Soft or optional
**Visual Hierarchy:** Talent → Product → Optional CTA

### 02 — Interest
**Goal:** Sustained attention, introduce value proposition
**Reject:** Abstract visuals that hide the product
**Strategy:** One clear visual idea, believable micro-world hinting at use-case
**CTA:** Learn More, Discover, See Details
**Visual Hierarchy:** Talent → Product → Headline → CTA

### 03 — Consideration
**Goal:** Informed evaluation, reduce uncertainty
**Reject:** Pure mood storytelling, vague emotional content
**Strategy:** Communicate WHAT product does, ONE primary differentiator, ONE proof cue
**CTA:** Compare, See Details, Explore
**Visual Hierarchy:** Talent → Product → Key Benefit → Proof Cue → CTA
**New:** Adds Brand Identity Manifest to Blueprint JSON

### 04 — Evaluation
**Goal:** Validate purchase decision, proof & trust
**Reject:** Pure mood, unsupportable claims, visual clutter
**Strategy:** One trust anchor (quality/legitimacy/authority), one proof cue (reviews/certification)
**CTA:** See Reviews, Verified Quality, Learn More
**Visual Hierarchy:** Trust Anchor → Proof Cue → Product → Talent → CTA

### 05 — Conversion
**Goal:** Trigger decisive action, remove friction
**Reject:** New hesitation-inducing info, complex compositions
**Strategy:** One hero (product), one action, optional micro-reassurance
**CTA:** Buy Now, Get Yours, Complete Order (PRIMARY visual element)
**Visual Hierarchy:** Product → CTA → Optional Reassurance → Brand → Talent

### 06 — Retention
**Goal:** Post-purchase confidence, reduce churn
**Reject:** Hard-sell, urgency, price talk
**Strategy:** "You made the right choice" + "Here is the next step"
**CTA:** Start, Set Up, Learn, Track (guidance, not purchase)
**Visual Hierarchy:** Confirmation → Next Step → Product → Talent

### 07 — Loyalty
**Goal:** Strengthen emotional bond over time
**Reject:** Sales layouts, instructional tone, aggressive CTAs
**Strategy:** "This brand is part of who you are" — habitual engagement
**CTA:** Optional: Explore, Be Part Of, Continue
**Visual Hierarchy:** Brand World/Mood → Talent (identity mirror) → Product → Brand

### 08 — Advocacy
**Goal:** Turn customers into voluntary brand ambassadors
**Reject:** Sales language, instructional tone, forced testimonials
**Strategy:** Signal belonging, create share-worthy imagery, enable organic sharing
**CTA:** Optional or absent: Join the Movement, Part of Us
**Visual Hierarchy:** Mood → Talent (identity proxy) → Product (symbol) → Brand

### 09 — Morfeo Creative 🎨 (DEFAULT)
**Goal:** Maximum visual impact, narrative-rich, cinematic quality
**Reject:** White backgrounds, studio shots, "product on table", generic poses, sterile compositions
**Strategy:** Build immersive WORLDS, not backgrounds. Talent is a CHARACTER with emotion and action. Subtle surreal/magical elements elevate the mundane. Think movie stills + magical realism + high fashion.
**CTA:** Present but integrated into scene aesthetics
**Visual Hierarchy:** Scene → Talent (as character) → Product (organic in scene) → CTA
**Creative Philosophy:**
- NEVER a white background or studio
- Every image has depth (foreground/midground/background layers)
- Lighting is narrative (golden hour, practicals, colored atmosphere)
- One subtle surreal element per scene (impossible beauty, dream-logic detail)
- Wardrobe is costume design, not "simple clothes"
- Camera has personality (specific film stocks, intentional imperfections)

---

## Creating New Ad Types

To create a new funnel stage or specialized ad type:

1. **Copy** the closest existing Master Prompt from `{baseDir}/configs/Product_to_Ads/`
2. **Redefine ROUND 1** with the new strategic objective
3. **Adjust ROUND 2** UI hierarchy accordingly
4. **Shift** talent/product narrative roles
5. **Modify** CTA philosophy and copy voice
6. **Keep** the JSON output structure identical for pipeline compatibility
7. **Maintain** the Fidelity Lock (ROUND 0) — product and talent are always immutable
8. **Save** as `Master_prompt_XX_NewStage.json` — the node auto-discovers new profiles

### Key Evolution Pattern Across Stages:

| Aspect | Early (01-02) | Mid (03-05) | Late (06-08) | Morfeo (09) |
|--------|--------------|-------------|--------------|-------------|
| Talent role | Attention anchor | Credibility anchor | Identity mirror | Character in story |
| Product role | Secondary hero | Evaluation hero | Familiar symbol | Organic in world |
| CTA | Soft/exploratory | Proof-led → Decisive | Guidance → Optional | Integrated/aesthetic |
| Copy voice | Intriguing | Clarity, proof, action | Supportive → Proud | Evocative/poetic |
| Visual density | High-concept | Structured, scannable | Editorial, spacious | Cinematic/layered |
| Environment | World-building | Context-rich | Lifestyle | Immersive + surreal |
| Environment | World-building | Context-rich | Lifestyle, intimate |

---

## Image Input Types

### Binding Images (strict fidelity — immutable)
- **talent**: Face/body locked, no deviation in facial structure, ethnicity, proportions
- **product_1-4**: Shape, label text, material, proportions preserved 1:1
- **brand_logo**: UI/button style derived from logo geometry

### Soft References (optional, off by default)
Reference image input (`referencia`) is optional. When provided, it's analyzed for:
- **POSE_REF** → Body position, limbs, weight, gaze, micro-gestures
- **PHOTO_STYLE_REF** → Camera, lens, lighting, grading, grain
- **LOCATION_REF** → Setting, materials, colors, mood

When empty (default), creative direction comes from Brand Identity + Campaign Brief alone.

---

## Brand Profiles

### Catalog (70+ brands):
```bash
ls ~/clawd/ad-ready/configs/Brands/*.json | sed 's/.*\///' | sed 's/\.json//'
```

### Creating new brand profiles:
Use the `brand-analyzer` skill:
```bash
GEMINI_API_KEY="$KEY" uv run ~/.clawdbot/skills/brand-analyzer/scripts/analyze.py \
  --brand "Brand Name" --auto-save
```

The Brand Analyzer uses a 3-phase methodology:
1. **Phase 1:** Official research via Google Search (canonical data: name, founding, positioning, vision, mission, tagline)
2. **Phase 1.1:** Independent campaign research (10+ distinct campaigns via Google Images/Pinterest)
3. **Phase 2-3:** Visual analysis → JSON profile following the standard template

Output covers: brand_info, brand_values, target_audience, tone_of_voice, visual_identity, photography, campaign_guidelines, brand_behavior, channel_expression, compliance.

---

## Aspect Ratios

| Ratio | Use Case |
|-------|----------|
| `4:5` | **Default.** Instagram feed, Facebook |
| `9:16` | Stories, Reels, TikTok |
| `1:1` | Square posts |
| `16:9` | YouTube, landscape banners |
| `5:4` | Alternative landscape |
| `2:3` | Pinterest |
| `3:4` | Portrait |

---

## Config Files Reference

The skill includes reference copies of all pipeline configuration files:

```
{baseDir}/configs/
├── Brief_Generator/
│   └── brief_prompt.json              # 10-point campaign brief framework
├── Product_to_Ads/
│   ├── Master_prompt_01_Awareness.json
│   ├── Master_prompt_02_Interest.json
│   ├── Master_prompt_03_Consideration.json
│   ├── Master_prompt_04_Evaluation.json
│   ├── Master_prompt_05_Conversion.json
│   ├── Master_prompt_06_Retention.json
│   ├── Master_prompt_07_Loyalty.json
│   ├── Master_prompt_08_Advocacy.json
│   └── Master_prompt_09_Morfeo_Creative.json  # 🎨 DEFAULT — cinematic, surreal, narrative
└── Reference_Analyzer/
    └── reference_analysis_prompt.txt   # Pose/style/location analysis prompt
```

These configs are the canonical reference for the pipeline's behavior. The actual live configs are stored in the ComfyUI deployment at `ads_SV/configs/`.

---

## Known Limitations

1. **Product image scraping is fragile** — always provide product images manually
2. **Some websites block scraping** — provide product data manually when scraping fails
3. **Gemini hallucinations** — occasional issues in complex reasoning steps
4. **No brief editing** — brief is generated automatically; manual override not yet supported
5. **Logo & reference are optional** — both use server-side bypass; empty string = not used. Logo: use if good quality. Reference: only on explicit request

---

## Ad-Ready vs Morpheus

| Feature | Ad-Ready | Morpheus |
|---------|----------|----------|
| Input | Product URL (auto-scrapes) | Manual product image |
| Brand intelligence | 70+ brand profiles | None |
| Funnel targeting | 8 funnel stages | None |
| Brief generation | Auto (10-point creative direction) | None |
| Creative direction | Objective-driven (brief → blueprint) | Pack-based (camera, lens, lighting) |
| Best for | Product advertising campaigns | Fashion/lifestyle editorial photography |
| Control level | High-level (strategy-first) | Granular (every visual parameter) |

---

## API Key

Uses ComfyDeploy API key. Set via `COMFY_DEPLOY_API_KEY` environment variable.

## Source Repository

- GitHub: [PauldeLavallaz/ads_SV](https://github.com/PauldeLavallaz/ads_SV)
- Architecture: ComfyUI custom node package with 3 nodes:
  - `ProductToAds_Manual` — Full manual control, single format
  - `ProductToAds_Auto` — Auto-downloads images, generates 4 formats
  - `BrandIdentityAnalyzer` — Analyzes brands via Gemini + Google Search
