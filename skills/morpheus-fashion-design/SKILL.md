---
name: morpheus-fashion-design
version: 1.2.0
description: |
  Generate professional advertising images with AI models holding/wearing products.
  
  ✅ USE WHEN:
  - Need a person/model in the image WITH a product
  - Creating fashion ads, product campaigns, commercial photography
  - Want consistent model face across multiple shots
  - Need professional lighting/camera simulation
  - Input: product image + model reference (or catalog)
  
  ❌ DON'T USE WHEN:
  - Just editing/modifying an existing image → use nano-banana-pro
  - Product-only shot without a person → use nano-banana-pro
  - Already have the hero image, need variations → use multishot-ugc
  - Need video, not image → use veed-ugc after generating image
  - URL-based product fetch with brand profile → use ad-ready instead
  
  OUTPUT: Single high-quality PNG image (2K-4K resolution)
---

# Morpheus Fashion Design

Generate professional fashion/product advertising images using ComfyDeploy's Morpheus Fashion Design workflow.

## ⚠️ CRITICAL RULES

### 1. NO `logo` field — EVER
The `logo` input has been **removed from the API**. Do NOT pass it.
Only two image inputs exist:
- `product` → the product being advertised
- `model` → frontal face photo of the model

### 2. NEVER USE AUTO VALUES for packs
**Configuration packs MUST NEVER be left on `auto` or `AUTO`.**

`auto` = empty values = neutral, boring images with no creative direction.

Always select deliberately based on the brief. Custom string values are allowed and encouraged.

## Pack Selection Guidelines

| Pack | How to Choose |
|------|---------------|
| `style_pack` | Brand personality: luxury→`premium_restraint`, sports→`cinematic_realism`, street→`street_authentic` |
| `camera_pack` | Sports→`sony_a1`, editorial→`hasselblad_x2d`, street→`leica_m6` |
| `lens_pack` | Portrait compression? Wide? Match shot type and mood |
| `lighting_pack` | Golden hour? Studio? Natural window? Match brief |
| `pose_discipline_pack` | Sport action→`sport_in_motion`, commercial→`commercial_front_facing`, UGC→`street_style_candid_walk` |
| `film_texture_pack` | Warm editorial→`kodak_portra_400`, cinematic→`kodak_vision3_500t`, clean→`digital_clean_no_emulation` |
| `environment_pack` | `beach_minimal`, `urban_glass_steel`, `street_crosswalk` — or custom string |
| `color_science_pack` | `warm_golden_editorial`, `neutral_premium_clean`, `cinematic_low_contrast` |
| `time_weather_pack` | `golden_hour_clear`, `bright_midday_sun`, `overcast_winter_daylight` |

## API Details

**Endpoint:** `https://api.comfydeploy.com/api/run/deployment/queue`
**Deployment ID:** `1e16994d-da67-4f30-9ade-250f964b2abc`

## Canonical API Call

```javascript
const response = await fetch("https://api.comfydeploy.com/api/run/deployment/queue", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
  },
  body: JSON.stringify({
    "deployment_id": "1e16994d-da67-4f30-9ade-250f964b2abc",
    "inputs": {
      "product": "/* product image URL */",
      "model":   "/* model face URL */",
      "brief":   "Detailed scene, pose, lighting, mood, product placement...",
      "target":  "Target audience: demographics, psychographics, lifestyle...",
      "input_seed": -1,
      "branding_pack": "logo_none",
      "aspect_ratio": "9:16",
      "style_pack": "street_authentic",
      "camera_pack": "sony_a1",
      "lens_pack": "zeiss_otus_55",
      "film_texture_pack": "kodak_portra_400",
      "color_science_pack": "warm_golden_editorial",
      "shot_pack": "medium_shot",
      "pose_discipline_pack": "street_style_candid_walk",
      "lighting_pack": "natural_window",
      "time_weather_pack": "golden_hour_clear",
      "environment_pack": "urban_glass_steel",
      "intent": "awareness"
    }
  })
});
```

## 🎭 Model Catalog

**GitHub:** `https://github.com/PauldeLavallaz/model_management`
**Local path:** `~/clawd/models-catalog/catalog/images/`

### Priority order
1. User provides model image → use directly
2. User describes model → search catalog, select best match
3. No specification → choose based on brief context

### Searching
```bash
# By body type
cat models-catalog/catalog/catalog.json | python3 -c "
import json,sys; data=json.load(sys.stdin)
for t in data['talents']:
    if t.get('body_type') in ['curvy','plus_size']:
        print(t['id'], t['name'], t['ethnicity'])
"
# By ethnicity + gender
cat models-catalog/catalog/catalog.json | jq '[.talents[] | select(.ethnicity == "hispanic" and .gender == "female") | {id, name, body_type}]'
```

## Creative Brief — How to Write It

Write it as a **real photography director's brief** — specific, physical, cinematic:

### Example: CasanCrem Light (ironic/viral UGC angle)
```
Campaña UGC TikTok para CasanCrem Light La Serenísima.
Joven de contextura robusta sostiene el pote con sonrisa cómplice en cocina hogareña argentina.
Pose relajada, apoyada en la mesada, mirando directo a cámara con energía y complicidad.
El pote visible y protagonista en la mano. Luz de ventana natural, cálida de tarde.
Estilo UGC auténtico, no publicitario clásico. Cuerpo real, relatable, no atlético.
```

### Example: Oakley Snowboarding
```
Oakley snowboarding campaign. Rider on metal rail in snowpark, body slightly rotated,
arms open for balance, eyes on the line. Technical authentic freestyle pose.
Alpine snowpark, full midday daylight, compacted snow, metal structures.
Natural sun bouncing off snow — saturated colors, strong contrast.
Documentary approach — freeze rider on rail, sharp body and board.
Real session frame: balance, concentration, style merged.
```

## Configuration Packs Reference

| Pack | Options |
|------|---------|
| `style_pack` | `premium_restraint`, `editorial_precision`, `cinematic_realism`, `cinematic_memory`, `campaign_hero`, `product_truth`, `clean_commercial`, `street_authentic`, `archive_fashion`, `experimental_authorial` |
| `shot_pack` | `full_body_wide`, `medium_shot`, `close_up`, `low_angle_hero`, `three_quarter`, `waist_up` |
| `camera_pack` | `arri_alexa35`, `canon_r5`, `hasselblad_x2d`, `leica_m6`, `sony_a1` |
| `lens_pack` | `cooke_anamorphic_i_50`, `leica_noctilux_50`, `zeiss_otus_55`, `wide_distortion_controlled` |
| `lighting_pack` | `golden_hour_backlit`, `natural_window`, `studio_three_point`, `bright_midday_sun` |
| `pose_discipline_pack` | `commercial_front_facing`, `street_style_candid_walk`, `sport_in_motion` |
| `film_texture_pack` | `kodak_portra_400`, `fujifilm_velvia_50`, `kodak_vision3_500t`, `digital_clean_no_emulation` |
| `color_science_pack` | `neutral_premium_clean`, `warm_golden_editorial`, `cinematic_low_contrast` |
| `environment_pack` | `beach_minimal`, `urban_glass_steel`, `street_crosswalk` — or custom descriptive string |
| `time_weather_pack` | `golden_hour_clear`, `bright_midday_sun`, `overcast_winter_daylight` |
| `branding_pack` | `logo_none` ← always unless logo explicitly requested |
| `intent` | `awareness`, `consideration`, `conversion`, `retention` |
| `aspect_ratio` | `9:16`, `16:9`, `1:1`, `4:5`, `3:4` |

## Python Upload Helper

```python
def comfy_upload(filepath: str, api_key: str) -> str:
    from pathlib import Path
    import requests
    p = Path(filepath)
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    with open(p, "rb") as f:
        r = requests.post(
            "https://api.comfydeploy.com/api/file/upload",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (p.name, f, mime)},
            timeout=60
        )
    r.raise_for_status()
    return r.json()["file_url"]
```

## Priority Hierarchy

```
Talent (identity) > Product fidelity > Fit > Pose > Style > Location > Branding
```

## Troubleshooting

**Imagen negra/vacía** = filtro de moderación de Google/Gemini activado.
- No usar personas famosas o celebridades
- Modificar el brief eliminando referencias problemáticas

**API Key:** NO pasar como parámetro. Ya está configurado en ComfyDeploy.

## Integración con Portrait Generator

### Flujo de selección de modelo (actualizado)

El campo `model` puede venir de dos fuentes:

**Opción A — Catálogo (default):**
```
~/clawd/models-catalog/catalog/images/model_XX.jpg
```
Usar cuando el guión no requiere rasgos muy específicos.

**Opción B — Portrait Generator (cuando el guión lo requiere):**
```
portrait-generator → imagen_1 (vista frontal) → model en Morpheus
```
Usar cuando necesitás: etnia muy específica, edad exacta, rasgos únicos, personaje
que no existe en el catálogo de 114 modelos.

**Regla:** `imagen_1` del Portrait Generator = siempre la vista frontal = la correcta para `model`.

### Cuándo usar Portrait Generator
- Personaje mayor de 60 años
- Etnia muy específica no disponible en catálogo
- Rasgos físicos únicos (cicatrices, vitiligo, asimetría facial)
- Cualquier personaje que el guión describa con detalle

### Cuándo usar el catálogo
- Personaje genérico / sin especificaciones
- Cualquier modelo joven-adulto estándar
- Cuando la velocidad importa más que la precisión
