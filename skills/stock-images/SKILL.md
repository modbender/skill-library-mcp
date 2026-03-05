---
name: Stock Images
slug: stock-images
version: 1.0.0
homepage: https://clawic.com/skills/stock-images
description: Source free stock photos and placeholder images with direct URLs for Unsplash, Pexels, Pixabay, and Lorem Picsum.
metadata: {"clawdbot":{"emoji":"📸","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` silently. No setup needed for basic use.

## When to Use

User needs stock photos or placeholder images for mockups, prototypes, websites, or presentations. Agent provides direct URLs without API keys when possible.

## Architecture

No persistent storage needed. Reference files loaded on demand.

## Quick Reference

| Topic | File |
|-------|------|
| Setup | `setup.md` |
| Memory template | `memory-template.md` |
| All providers with examples | `providers.md` |
| Unsplash category URLs | `unsplash-categories.md` |

## Core Rules

### 1. Prefer Direct URL Services
For quick mockups and prototypes, use services that work without API keys:
- **Lorem Picsum** — random photos by size
- **Placehold.co** — colored placeholders with text
- **PlaceKeanu** — Keanu Reeves placeholder photos
- **Unsplash Source** — direct links to Unsplash photos

### 2. Match Content to Context
| Need | Best Source |
|------|-------------|
| Generic photo placeholders | Lorem Picsum, Unsplash Source |
| Specific subjects (business, nature) | Unsplash, Pexels, Pixabay |
| Colored boxes with dimensions | Placehold.co |
| Avatars/faces | UI Faces, This Person Does Not Exist |
| Icons | Iconify, Feather Icons |

### 3. Know the URL Patterns
Quick patterns that work immediately:

```
# Lorem Picsum - random photo at size
https://picsum.photos/800/600

# Lorem Picsum - specific image by ID
https://picsum.photos/id/237/800/600

# Lorem Picsum - grayscale
https://picsum.photos/800/600?grayscale

# Placehold.co - gray placeholder with text
https://placehold.co/800x600

# Placehold.co - custom colors
https://placehold.co/800x600/000/fff

# Unsplash Source - specific search
https://source.unsplash.com/800x600/?nature

# PlaceKeanu - with size
https://placekeanu.com/800/600
```

### 4. Use Cached URLs for Consistency
When building prototypes that need consistent images across sessions:
- Use `id` parameter in Lorem Picsum
- Save specific Unsplash photo URLs
- Use `?random=1` only when variety is needed

### 5. Respect Licensing
| Service | License | Attribution |
|---------|---------|-------------|
| Unsplash | Unsplash License | Not required but appreciated |
| Pexels | Pexels License | Not required |
| Pixabay | Pixabay License | Not required |
| Lorem Picsum | Various | Photos from Unsplash |

For commercial projects, verify license on original photo page.

### 6. Load Category Index for Specific Needs
When user needs specific subjects (business people, landscapes, food), load `unsplash-categories.md` for curated URLs by category.

### 7. Optimize for Performance
- Use WebP format when supported: `https://picsum.photos/800/600.webp`
- Use exact dimensions needed (no oversized images)
- For retina: Placehold.co supports `@2x` and `@3x`

## Common Traps

- Using random URLs in production without caching → inconsistent images
- Hotlinking without checking terms → service blocks requests
- Using placeholder services for final production → unprofessional
- Requesting too large images → slow load times

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| picsum.photos | Image dimensions | Random photo |
| placehold.co | Dimensions, colors, text | Placeholder image |
| source.unsplash.com | Search terms | Unsplash photos |
| placekeanu.com | Dimensions | Keanu placeholder |

No authentication required. No user data sent.

## Security & Privacy

**Data that leaves your machine:**
- HTTP requests with dimensions and optional search terms

**Data that stays local:**
- Cached images in browser
- No tracking, no API keys needed

**This skill does NOT:**
- Store credentials
- Track usage
- Require API registration

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `image` — image analysis and manipulation
- `image-generation` — AI image generation
- `frontend` — frontend development
- `design` — design principles
- `ui` — UI design patterns

## Feedback
- If useful: `clawhub star stock-images`
- Stay updated: `clawhub sync`
