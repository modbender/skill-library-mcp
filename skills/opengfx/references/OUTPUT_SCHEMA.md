# Logo System Output Schema

Defines the JSON contract for machine-readable logo system output.

---

## logo-system.json

Every generated logo system includes a JSON metadata file that enables downstream automation and tool integration.

```json
{
  "$schema": "https://opengfx.aklo.io/schemas/logo-system.v1.json",
  "version": "1.0.0",
  "generatedAt": "2026-02-16T12:00:00Z",
  
  "brand": {
    "name": "OpenGFX",
    "slug": "opengfx"
  },
  
  "concept": {
    "summary": "Paint palette abstracted to geometric form",
    "oneMemorableThing": "Three colored dots representing creativity",
    "baseShapes": ["circle"],
    "gridSystem": "golden",
    "approach": "Logo Modernism / Geometric"
  },
  
  "icon": {
    "file": "opengfx-icon.svg",
    "minSize": 16,
    "optimalSizes": [16, 32, 64, 128, 256, 512],
    "container": "1:1 square (NEVER stretch, use negative space)",
    "construction": {
      "primaryShape": "circle",
      "secondaryElements": ["dots"],
      "gridDivisions": 8
    },
    "useCase": ["favicon", "app-icon", "profile", "watermark"]
  },
  
  "wordmark": {
    "file": "opengfx-wordmark.svg",
    "typeface": {
      "family": "SF Pro Display",
      "fallback": "Helvetica Neue, system-ui, sans-serif",
      "weight": 500,
      "tracking": -10,
      "case": "titlecase"
    },
    "minWidth": 80
  },
  
  "lockups": {
    "stacked": {
      "file": "opengfx-stacked.svg",
      "aspectRatio": "1:1",
      "spacing": "4U",
      "useCase": ["social", "business-card", "centered-layout"]
    },
    "horizontal": {
      "file": "opengfx-horizontal.svg",
      "aspectRatio": "4:1",
      "spacing": "2U",
      "useCase": ["header", "navigation", "letterhead"]
    }
  },
  
  "colors": {
    "primary": {
      "hex": "#000000",
      "name": "Black"
    },
    "accent": {
      "hex": "#FF6B6B",
      "name": "Coral"
    },
    "background": {
      "light": "#FFFFFF",
      "dark": "#0A0A0F"
    }
  },
  
  "clearSpace": {
    "unit": "iconWidth / 8",
    "minimum": "2U"
  },
  
  "files": [
    "opengfx-icon.svg",
    "opengfx-wordmark.svg",
    "opengfx-stacked.svg",
    "opengfx-horizontal.svg",
    "logo-system.json"
  ],
  
  "exports": {
    "figma": "opengfx-figma-tokens.json",
    "tokensStudio": "opengfx-tokens-studio.json",
    "css": "opengfx-tokens.css",
    "openvid": "opengfx-openvid-style.json"
  }
}
```

---

## Field Definitions

### brand
| Field | Type | Description |
|-------|------|-------------|
| name | string | Display name of the brand |
| slug | string | URL-safe lowercase identifier |

### concept
| Field | Type | Description |
|-------|------|-------------|
| summary | string | One-sentence concept description |
| oneMemorableThing | string | The single distinctive feature |
| baseShapes | array | Geometric shapes used in construction |
| gridSystem | string | "golden" or "modular" |
| approach | string | Design philosophy applied |

### icon
| Field | Type | Description |
|-------|------|-------------|
| file | string | SVG filename |
| minSize | number | Minimum pixel size (usually 16) |
| optimalSizes | array | Recommended export sizes |
| aspectRatio | string | Width:Height ratio |
| construction | object | How icon was built |

### wordmark
| Field | Type | Description |
|-------|------|-------------|
| file | string | SVG filename |
| typeface.family | string | Font family used |
| typeface.fallback | string | CSS fallback stack |
| typeface.weight | number | Font weight (300-700) |
| typeface.tracking | number | Letter-spacing adjustment |
| typeface.case | string | "lowercase", "uppercase", or "titlecase" |
| minWidth | number | Minimum readable width in pixels |

### lockups
Each lockup contains:
| Field | Type | Description |
|-------|------|-------------|
| file | string | SVG filename |
| aspectRatio | string | Width:Height ratio |
| spacing | string | Internal spacing in units |
| useCase | array | Recommended applications |

### colors
| Field | Type | Description |
|-------|------|-------------|
| primary.hex | string | Primary brand color (usually black) |
| accent.hex | string | Optional accent color |
| background.light | string | Light mode background |
| background.dark | string | Dark mode background |

### exports
Paths to generated export files for various tools:
| Field | Description |
|-------|-------------|
| figma | Figma-compatible tokens JSON |
| tokensStudio | Tokens Studio format |
| css | CSS custom properties |
| openvid | OpenVid style pack for video generation |

---

## Interoperability

This schema enables:

1. **Figma Integration** — Import tokens directly
2. **Tokens Studio** — Sync with design system
3. **Web Export** — CSS variables for implementation
4. **OpenVid** — Consistent video branding
5. **Automation** — Programmatic logo manipulation

---

## Validation

Schema validation endpoint (planned):
```
POST https://opengfx.aklo.io/validate/logo-system
Content-Type: application/json

{body: logo-system.json contents}
```

Returns validation errors or success confirmation.
