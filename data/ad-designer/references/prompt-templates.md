---
name: ad-designer-prompt-templates
description: Proven prompt templates, anti-patterns, aspect ratio guide, and brand-aware prompt construction rules for generating marketing ad images with Nano Banana Pro.
---

# Ad Designer — Prompt Templates & Reference

---

## Core Principle: Less Is More

Short prompts consistently outperform long ones. Each word you add competes for the model's attention. A 20-word prompt with the right words beats a 60-word prompt with redundant ones.

Target range: **15–30 words** for the visual description. The avoid clause adds 5–10 more.

---

## Prompt Templates by Ad Type

Use these as starting points. Swap bracketed placeholders for brief-specific content. Cut any field that does not add meaning.

---

### 1. Lifestyle — Aspirational (TOF Awareness)

Use when: the goal is to make the audience see themselves living a better life with the product or service.

```
[aspirational activity], [setting that signals the life upgrade],
[emotion on subject's face or body language],
[time of day + lighting quality],
[2–3 brand colors], [photography style],
no text, no logos
```

Example:
```
Woman working from a sun-filled cafe, laptop open, relaxed confident posture,
golden hour window light, warm terracotta and cream tones,
candid lifestyle photography, no text, no logos
```

---

### 2. Product Showcase — Clean Hero Shot (MOF Consideration)

Use when: the product needs to be the undeniable focal point with no distraction.

```
[product type] on [surface/background], [angle: overhead/45-degree/straight-on],
[surface texture], [lighting: studio/natural/dramatic],
[2 brand colors as background and accent], minimal composition,
product photography style, no text, no logos
```

Example:
```
Skincare serum bottle on white marble surface, 45-degree angle,
soft diffused studio light, clean white background with dusty rose accent,
high-end product photography, no text, no logos
```

---

### 3. Testimonial / Social Proof (MOF–BOF)

Use when: the ad needs to signal trust through a real person's experience.

```
[gender/age group] [candid action that shows the result],
[setting relevant to the result],
[genuine emotion — not posed smiling],
[warm or neutral lighting], [brand color palette],
authentic documentary photography style, no text, no logos
```

Example:
```
Young professional woman reviewing documents at her desk, satisfied expression,
organized modern home office, warm afternoon light,
navy and soft gold tones, authentic candid photography, no text, no logos
```

---

### 4. Before / After — Transformation (BOF Conversion)

Use when: the ad shows contrast between the problem state and the desired outcome.

For split-screen carousel, generate two separate images:

**Card 1 — Before (problem state):**
```
[subject] showing [visible sign of the problem],
[environment that amplifies the problem],
[muted, desaturated, or cool color grading],
[tired or frustrated expression], no text, no logos
```

**Card 2 — After (outcome state):**
```
[same subject type] showing [visible sign of the improvement],
[environment that signals success or relief],
[warm, vibrant, or bright color grading],
[confident or relieved expression], no text, no logos
```

Example pair:
```
// Card 1
Person hunched at cluttered desk, stressed expression,
dim blue-grey office light, muted desaturated tones, no text, no logos

// Card 2
Same person upright at clean organized desk, calm confident expression,
bright warm light, soft amber and white tones, no text, no logos
```

---

### 5. Stat / Number Ad (TOF–MOF)

Use when: the creative leads with a bold statistic or claim (e.g. "10x faster", "87% of users"). The number is the hero.

For text in image: specify the exact text string. Do not paraphrase.

```
[minimalist background — solid color or subtle texture],
[large centered text area, clean layout],
[brand primary color as background],
[brand accent color as text highlight],
typographic layout, flat design, no photography, no illustrations,
text: "[exact headline from brief]"
```

Example:
```
Deep navy solid background, generous whitespace, centered typographic layout,
warm amber accent highlight, modern sans-serif layout feel,
flat minimal design, text: "87% sleep better in 7 days"
```

Note: Only include `text:` when the brief explicitly specifies text to render in the image. Omit otherwise.

---

### 6. Emotional / Storytelling (TOF Brand Awareness)

Use when: the ad prioritizes feeling over information — it sells a state of being, not a feature.

```
[cinematic scene that encapsulates the core emotion],
[environmental storytelling details],
[lighting that reinforces the mood],
[color palette that matches the emotion],
[wide or medium shot to show full scene],
cinematic photography, [mood adjective] atmosphere, no text, no logos
```

Example:
```
Parent and child sharing a quiet morning ritual at a kitchen table,
warm steam rising from mugs, soft filtered light through curtains,
honey and cream tones, wide shot showing full domestic scene,
cinematic documentary photography, tender intimate atmosphere,
no text, no logos
```

---

### 7. Problem Agitation (TOF–MOF Pain Point)

Use when: the ad opens with the audience's frustration to create recognition and engagement.

```
[subject visibly experiencing the problem],
[setting where the problem typically occurs],
[body language or expression that communicates the frustration],
[lighting: harsh, flat, or unflattering to amplify tension],
[muted or cold tones], no text, no logos
```

Example:
```
Person staring at a pile of unopened bills, overwhelmed expression,
small apartment kitchen table, harsh overhead fluorescent light,
desaturated blue-grey tones, no text, no logos
```

---

### 8. Comparison / Competitor Contrast (MOF)

Use when: the creative is a side-by-side or sequential contrast that implies superiority.

Generate two images (carousel cards 1 and 2):

**Card 1 — Competitor / Old Way:**
```
[object or scene representing the old/worse option],
cluttered or outdated appearance, [cold or flat lighting],
[muted palette], no text, no logos
```

**Card 2 — Your Product / New Way:**
```
[same object type representing the better option],
clean modern polished appearance, [warm or crisp lighting],
[brand color palette], no text, no logos
```

---

### 9. Countdown / Urgency (BOF Retargeting)

Use when: the creative communicates scarcity or a time-limited offer.

Background-only approach (text overlaid in post-production):

```
[abstract or symbolic image suggesting time or urgency],
[clock, hourglass, or countdown-adjacent visual metaphor],
[brand primary color dominant], dramatic lighting,
minimal composition, no text, no logos
```

Example:
```
Hourglass with fine sand streaming, dramatic side lighting,
deep navy background, warm amber sand glow,
close-up macro shot, minimal composition, no text, no logos
```

---

### 10. Influencer / UGC Style (TOF–MOF Trust)

Use when: the creative needs to look authentic, not polished — phone camera aesthetic, real-life context.

```
[subject using or holding the product type in a casual real setting],
slightly imperfect composition, natural available light,
[candid framing — off-center is fine],
warm everyday tones, authentic handheld photography aesthetic,
no professional studio lighting, no text, no logos
```

Example:
```
Young woman holding a green smoothie at a farmers market,
casual off-center framing, soft natural daylight,
warm earthy greens and ochre tones,
authentic handheld photography feel, no text, no logos
```

---

### 11. Premium / Luxury (BOF High-Ticket)

Use when: the product or service is priced at the high end and the creative must signal exclusivity.

```
[subject or product in a high-end context],
[luxury setting: hotel suite, private terrace, curated interior],
[deep shadows with selective highlights],
[rich dark palette — navy, charcoal, deep emerald, or black + gold],
[low angle or perspective that implies grandeur],
editorial fashion or luxury brand photography, no text, no logos
```

Example:
```
Minimalist watch on a dark slate surface beside a folded linen cloth,
selective overhead spotlight creating sharp shadow,
deep charcoal and brushed gold tones,
luxury product editorial photography, no text, no logos
```

---

### 12. Seasonal / Event Contextual (TOF)

Use when: the ad aligns to a cultural moment, holiday, or seasonal context.

```
[seasonal visual element as background or accent],
[subject or product integrated naturally],
[seasonal lighting quality — e.g. golden autumn, bright summer, soft winter],
[seasonal color palette], [festive or cozy atmosphere as appropriate],
lifestyle photography style, no text, no logos
```

Example (Hari Raya / festive season):
```
Warm lanterns hanging in a decorated interior, soft bokeh background,
family gathering scene in the distance, rich gold and emerald tones,
warm candlelight quality, festive celebratory atmosphere,
lifestyle photography, no text, no logos
```

---

## Anti-Patterns: What NOT to Include

These prompt elements consistently produce bad results. Remove them if found.

| Anti-Pattern | Why It Fails | What to Do Instead |
|---|---|---|
| Brand name in prompt | Model hallucinates the text incorrectly | Never include; add in post-production |
| Logo description | Generated logos are unreadable blobs | Never include; composite separately |
| Product name as text | Renders distorted or misspelled | Specify as `text: "exact string"` only if it must appear |
| "Photorealistic" | Overused, often makes output look synthetic | Use specific style: "candid documentary", "editorial" |
| "Professional" | Meaningless to the model | Describe the actual look: "studio lighting, clean background" |
| "High quality" | Meaningless to the model | Describe what quality looks like: "sharp focus, detailed texture" |
| Lists of features | Model treats them as visual items to include | Use one focal subject, not a product features list |
| Negative instructions alone | "No people" gets ignored | Pair with a positive: "empty clean surface, no people" |
| More than 3 colors | Palette becomes muddy | Pick 2 dominant + 1 accent maximum |
| Sentences over 15 words | Creates conflicting instructions | Break into short descriptive phrases with commas |
| Adjective stacking | "beautiful amazing stunning gorgeous" | Use one strong adjective per concept |

---

## Aspect Ratio Guide

| Ratio | Pixel Size at 1K | Pixel Size at 4K | Platform | Notes |
|-------|-----------------|-----------------|----------|-------|
| 1:1 | 1024 × 1024 | 4096 × 4096 | Instagram Feed, Facebook Feed | Universal fallback; works everywhere |
| 9:16 | 576 × 1024 | 2304 × 4096 | Instagram Story, Instagram Reel, Facebook Story | Full-screen vertical; max visual impact on mobile |
| 16:9 | 1024 × 576 | 4096 × 2304 | YouTube pre-roll, LinkedIn banner, website hero | Landscape; rarely used for feed ads |
| 4:5 | 819 × 1024 | 3277 × 4096 | Facebook Feed, Instagram Feed (portrait) | Takes up more feed screen than 1:1; higher CTR on mobile |

Default to **1:1** when the brief or user does not specify a platform.
Default to **4:5** when the goal is maximum mobile feed engagement.
Use **9:16** for Story and Reel placements only.

---

## Brand-Aware Prompt Construction: Inject Style Without Naming the Brand

The model cannot accurately reproduce a specific brand's visual identity by name. Translate brand bible fields into prompt-safe descriptors.

### Color Translation

Convert hex codes to natural language color descriptors before inserting into prompts.

| Hex Range | Descriptor to Use |
|-----------|------------------|
| `#1A2E5A` – `#0D1F4A` | deep navy, midnight blue, dark ink blue |
| `#E8735A` – `#D95F47` | warm coral, terracotta, burnt orange |
| `#F5A623` – `#FBBC2A` | warm amber, golden yellow, honey |
| `#2ECC71` – `#27AE60` | fresh green, emerald, leafy green |
| `#FAF7F2` – `#F5F0E8` | off-white, warm cream, linen white |
| `#333333` – `#1A1A1A` | charcoal, deep graphite, near-black |
| `#E91E8C` – `#C2185B` | hot pink, vibrant magenta, bold fuchsia |
| `#00BCD4` – `#0097A7` | teal, bright cyan, cool aqua |

### Font Style to Visual Mood

Font characteristics inform the overall visual composition style, not just text.

| Brand Font Type | Visual Style to Request |
|-----------------|------------------------|
| Bold geometric sans (Futura, Montserrat) | clean minimal layout, strong geometric shapes |
| Light editorial serif (Garamond, Playfair) | editorial luxury photography, refined composition |
| Rounded friendly sans (Nunito, Poppins) | warm lifestyle photography, approachable framing |
| Slab serif (Rockwell, Clarendon) | bold graphic composition, high contrast |
| Monospace / tech (JetBrains, Courier) | flat UI-style visuals, tech editorial aesthetic |

### Imagery Style to Photography Descriptor

| Brand Imagery Style | Prompt Descriptor |
|--------------------|------------------|
| Lifestyle, aspirational | candid lifestyle photography, natural available light |
| Clean product-only | product photography, studio light, minimal background |
| People + product | editorial documentary photography, real-world setting |
| Abstract / conceptual | fine art photography, symbolic composition |
| Illustration / flat | flat vector illustration style, bold color fills |
| Warm and organic | warm grain film photography, earthy tones |

### Construction Workflow

1. Open brand bible.
2. Extract: primary hex, secondary hex, font style, imagery style, layout pattern.
3. Convert hex → color descriptor using table above.
4. Convert font → visual mood descriptor using table above.
5. Convert imagery style → photography descriptor using table above.
6. Insert all three into the prompt in the COLOR PALETTE, STYLE, and COMPOSITION fields.
7. Never write the brand name anywhere in the prompt.

### Example: Full Brand → Prompt Translation

Brand bible fields:
```
Primary: #1A2E5A (deep navy)
Accent: #F5A623 (amber)
Background: #FAF7F2 (warm cream)
Font: Montserrat Bold (geometric sans)
Imagery: clean lifestyle with real people, warm natural light
Layout: minimal whitespace-heavy
```

Translated prompt (for a financial services lifestyle ad):
```
Young couple reviewing documents together at a bright dining table,
relaxed satisfied expressions, minimal clean home interior,
warm afternoon light, deep navy and warm amber accents on cream background,
geometric clean composition, candid lifestyle photography, no text, no logos
```

---

## Iteration Strategy

When a draft is not quite right, change one thing at a time. Do not rebuild the entire prompt.

| Issue | Single Change to Apply |
|-------|----------------------|
| Colors look off | Strengthen or replace the color descriptor — be more specific |
| Subject looks posed or unnatural | Add "candid" or "documentary" to style; remove "professional" |
| Background is too busy | Add "clean simple background" or "solid [color] background" |
| Image feels generic | Add a specific environmental detail (location, texture, object) |
| Wrong mood | Replace lighting descriptor — lighting drives mood more than any other field |
| Too much in the frame | Remove one subject or detail from the prompt |
| Text rendered wrong | Remove text from prompt; specify with `text:` prefix followed by exact string |
| Aspect ratio wrong | Rerun with correct resolution flag — do not adjust prompt for this |
