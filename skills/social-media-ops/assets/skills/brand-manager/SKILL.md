---
name: brand-manager
description: >
  Manage brands in the social-media-ops system. Add new brands, edit existing
  brand profiles, or archive brands. Each brand gets its own profile, content
  guidelines, domain knowledge file, asset directory, and channel topic.
  Use when the owner wants to add a new brand, modify brand settings,
  or deactivate a brand.
---

# Brand Manager

## Overview

Manages the brand lifecycle: creation, configuration, and archival. Each brand is an isolated unit with its own profile, content guidelines, industry knowledge file, and communication channel.

## Commands

### `add` — Add a New Brand

Creates all files and directories for a new brand.

**Collects from owner:**
1. **Brand ID** — Short lowercase identifier (e.g., "skincare", "cafe", "fitness")
2. **Display Name** — Human-readable name (e.g., "Glow Skincare")
3. **Local Name** — Name in local language (optional)
4. **Domain** — What the brand does (e.g., "Premium skincare products")
5. **Target Market** — Geographic/demographic target (e.g., "Thailand", "US millennials")
6. **Content Language** — Language for this brand's content (defaults to instance default)
7. **Channel Thread ID** — Telegram topic thread ID for this brand (if using topics mode)

**Creates:**
- `shared/brands/{id}/profile.md` — from template, pre-filled with collected info
- `shared/brands/{id}/content-guidelines.md` — from template
- `shared/domain/{id}-industry.md` — from template
- `assets/{id}/generated/` — directory for AI-generated assets
- `assets/{id}/received/` — directory for owner-provided assets
- Adds entry to `shared/brand-registry.md`
- Adds section to `shared/operations/posting-schedule.md`
- Adds entry to `shared/operations/channel-map.md`

**Example:**
```
Owner: Add a new brand
Bot: Let's set up a new brand.

1. Brand ID (short, lowercase)?
> bakery

2. Display name?
> Sweet Sunrise Bakery

3. Local name (optional)?
> 甜蜜日出

4. What does this brand do?
> Artisan bakery and pastry shop

5. Target market?
> Taiwan, young professionals

6. Content language?
> 繁體中文

7. Telegram topic thread ID?
> 8

Brand "bakery" created! Next: fill in shared/brands/bakery/profile.md with brand details.
```

### `edit` — Edit Brand Settings

Modify an existing brand's registry entry (display name, content language, channel, status).

**Usage:** `edit {brand_id}`

### `archive` — Archive a Brand

Moves a brand to the archived section of brand-registry.md. Does NOT delete files — they remain for reference.

**Usage:** `archive {brand_id}`

### `list` — List All Brands

Shows all active and archived brands from brand-registry.md.

## File Relationships

```
brand-manager add "mybrand"
  │
  ├── shared/brands/mybrand/profile.md        (from _template)
  ├── shared/brands/mybrand/content-guidelines.md  (from _template)
  ├── shared/domain/mybrand-industry.md        (from _template)
  ├── assets/mybrand/generated/               (empty dir)
  ├── assets/mybrand/received/                (empty dir)
  ├── shared/brand-registry.md                (new row added)
  ├── shared/operations/posting-schedule.md   (new section added)
  └── shared/operations/channel-map.md        (new row added)
```
