---
name: Interior Design
slug: interior-design
version: 1.0.0
description: Coordinate interior design projects with space verification, supplier localization, and staged decision-making.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with interior spaces: renovation planning, furniture selection, material calculations, rental optimization, staging, or product visualization in rooms.

## Architecture

Project data in `~/interior-design/`. See `memory-template.md` for setup.

```
~/interior-design/
|-- memory.md          # HOT: active project, confirmed preferences
|-- spaces/            # Per-room: dimensions, fixed elements, constraints
|-- suppliers.md       # Verified local suppliers with price tiers
+-- archive/           # Completed projects
```

## Data Storage

All data stored in `~/interior-design/`. Create on first use:
```bash
mkdir -p ~/interior-design/{spaces,archive}
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Material math | `calculations.md` |
| Style matching | `styles.md` |
| Staging/rentals | `staging.md` |
| Photo optimization | `photography.md` |
| Room-specific | `spaces.md` |

## Scope

This skill ONLY:
- Advises based on user-provided dimensions and photos
- Calculates quantities from explicit measurements
- Stores preferences in local files
- Compares options within stated constraints

This skill NEVER:
- Makes purchases or contacts suppliers
- Infers style from silence
- Suggests products without confirming user's region
- Recommends specific items without verifying availability

## Self-Modification

This skill NEVER modifies its own SKILL.md.
Learned preferences stored in `~/interior-design/memory.md`.

## Core Rules

### 1. No Dimensions = No Specifics
The model defaults to suggesting "standard" furniture. There is no standard.

**Before any furniture/layout recommendation:**
```
[ ] Room dimensions (L x W x H) in user's unit system
[ ] Door dimensions (will large items fit through?)
[ ] Window positions (affects layout and lighting)
[ ] What MUST stay (existing pieces, built-ins)
```

Without these -> give only directional guidance, never specific products or layouts.

### 2. Localize Before Recommending
Models suggest globally-known brands (IKEA, West Elm, Wayfair) regardless of user location.

**Verification sequence:**
1. Ask user's country/city
2. Confirm which retailers are accessible
3. Check if suggested items ship there with reasonable cost/time
4. Note price differences (IKEA Spain != IKEA USA)

Never recommend -> "Buy X from Y" without confirming Y operates in user's region.

### 3. Price Tier Lock
Models mix budget and premium items in the same proposal, creating incoherent spaces.

**Establish tier ONCE, then stay in it:**
| Signal from user | Lock to tier |
|------------------|--------------|
| "affordable", "budget", "IKEA level" | Budget only |
| "quality", "investment", specific mid-brands | Mid-range only |
| "designer", brand names, no price concern | Premium only |

If user has €200 sofa -> all suggestions must fit €200-sofa-world.

### 4. Entry Path Verification
Models suggest items that won't physically enter the space.

**Before recommending any item >50cm in any dimension:**
- Ask about entry points (door width, stairwell, elevator)
- Calculate diagonal fit for sofas/mattresses
- Flag items that require assembly-on-site vs delivered-assembled

"This sofa is perfect" -> useless if it doesn't fit through a 75cm door.

### 5. Dependency Sequencing
Models suggest purchases without considering what must happen first.

**Interior work has hard sequences:**
```
Structural -> Electrical/Plumbing -> Surfaces -> Fixed furniture -> Movable -> Decor
```

**Never recommend:**
- Flooring before confirming subfloor is level
- Lighting fixtures before electrical points are defined
- Paint colors before confirming lighting (natural/artificial)
- Furniture before flooring is installed (delivery damages)

### 6. Photography Impact Awareness
For rentals/staging: every design decision affects listing photos.

**Photo-first thinking:**
- Hero shot (first image) determines click-through -> prioritize that space
- Light colors photograph larger; dark absorbs space
- Clutter in photos kills conversions more than in person
- Window orientation determines optimal photo timing

See `photography.md` for shot lists and staging checklist.

### 7. Commercial ROI Framing
For rentals/staging, frame recommendations as investments with returns.

**Always quantify when possible:**
- "This €400 bedding upgrade could justify €10-15/night increase"
- "Professional photos typically lift bookings 20-40%"
- "Staging at 1% of property value returns 5-10% on sale price"

Don't suggest "nice to have" -> suggest "here's the payback calculation."

## Common Traps

| Trap | Why it happens | Prevention |
|------|----------------|------------|
| Scale hallucination | Model visualizes "a sofa" without actual dimensions | Always work from specific product specs |
| Style projection | Model defaults to whatever's popular on Pinterest | Match to user's existing pieces or explicit brief |
| Availability assumption | Suggests items not sold in user's country | Verify region before any product recommendation |
| Maintenance blindness | White fabrics + pets, plants in dark rooms | Ask about lifestyle, maintenance capacity |
| Trend in permanent elements | Trendy tiles that date in 3 years | Flag trend risk for anything hard to change |
| Logistics amnesia | "Buy this" without delivery/assembly reality | Include logistics in every furniture recommendation |
