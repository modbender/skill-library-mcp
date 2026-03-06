# Style Card Schema

A style card captures the visual DNA of a design reference. Each field provides specific, actionable information for prompt generation.

## Schema (JSON)

```json
{
  "id": "sc_0001",
  "title": "Design title from source",
  "source_url": "https://dribbble.com/shots/...",
  "image_url": "https://cdn.dribbble.com/...",
  "palette": ["#1A1A2E", "#16213E", "#0F3460", "#E94560"],
  "composition": "asymmetric",
  "typography": "bold geometric sans",
  "mood": ["bold", "energetic"],
  "textures": ["glassmorphism", "grain"],
  "lighting": "neon rim light with dark ambient",
  "depth": "layered with parallax",
  "contrast": "high",
  "style_tags": ["futuristic", "dark-mode", "ui-design"],
  "description": "Brief description of the design",
  "created_at": "2026-01-15T10:30:00Z",
  "analyzed": true
}
```

## Field Descriptions

### id (string, required)
Unique identifier. Format: `sc_NNNN` (zero-padded).

### title (string, required)
Original title from the source platform.

### source_url (string, required)
Link back to the original design on Dribbble or other platform.

### image_url (string)
Direct link to the design image. Used for AI visual analysis.

### palette (array of strings)
3-6 dominant hex colors extracted from the design. Order by visual prominence.

### composition (string)
Layout structure. Values: `centered`, `asymmetric`, `grid`, `split`, `diagonal`, `layered`, `radial`, `scattered`, `stacked`, `bleeding-edge`, `z-pattern`, `f-pattern`, `rule-of-thirds`, `golden-ratio`, `unknown`.

### typography (string)
Font characteristics as a brief description. Examples: "bold geometric sans", "thin serif with wide tracking", "handwritten script", "condensed slab serif".

### mood (array of strings)
2-3 precise emotional descriptors. Use terms from visual-vocabulary.md mood section. Avoid generic words like "beautiful" or "nice".

### textures (array of strings)
Surface qualities present in the design. Values from visual-vocabulary.md texture section.

### lighting (string)
Description of light sources and quality. Combine terms: "[type] from [direction] with [quality]". Example: "soft diffused overhead with warm rim accent".

### depth (string)
Spatial quality. Values: `flat`, `layered`, `isometric`, `parallax`, `deep-field`, `shallow-field`, `atmospheric`, `overlapping`, `unknown`.

### contrast (string)
Tonal range. Values: `high`, `medium`, `low`.

### style_tags (array of strings)
Design style categories. Extracted automatically from title/description, refined by visual analysis.

### description (string)
Brief text description of the design content and notable elements.

### created_at (string, ISO 8601)
Timestamp when the style card was created.

### analyzed (boolean)
Whether an AI agent has visually analyzed the design image and filled in detailed fields. Cards start as `false` and become `true` after visual analysis.

## Analysis Workflow

1. `scrape_dribbble.py` creates raw references
2. `style_card.py build` creates skeleton cards (`analyzed: false`)
3. AI agent views each card's `image_url` and fills in visual fields
4. Agent sets `analyzed: true` after completing analysis
5. Only analyzed cards are used for high-quality prompt generation
