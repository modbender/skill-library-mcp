# OpenGFX Logo Learnings

Production-learned guidance for logo generation.
**Update this file to improve logo quality.**

Last updated: 2026-02-16

---

## ⚠️ HARD REQUIREMENTS (NEVER VIOLATE)

### 0. SIMPLICITY IS THE ULTIMATE SOPHISTICATION
**The Rule of One Interesting Thing:**
- Every icon has ONE distinctive visual element
- If you're combining 3+ concepts, you've failed
- SIMPLEX > COMPLEX — always
- Luxury high-tech aesthetic = minimal forms, maximum impact

**Complexity Scale (target 40-50%):**
- 0-30%: Too basic (circle, dot, line)
- 40-50%: IDEAL — clean, distinctive, memorable ✓
- 60-70%: Only if meaning absolutely requires it
- 80%+: NEVER GO HERE — too busy, too cluttered

**The Child Test:**
- Can a child draw this from memory? → Should be YES
- Can you describe it in one sentence? → Must be YES
- Count visual elements: if >3, simplify

**Examples of RIGHT complexity:**
- Apple: One apple, one bite
- Nike: One swoosh
- Twitter/X: One bird / one X
- Stripe: Two diagonal lines
- Linear: One angled bracket

**Examples of WRONG complexity:**
- Circuit boards with 10 nodes
- Owls with moons, stars, flames, coins, AND spades
- Detailed machinery or intricate patterns

### 1. ICON MUST WORK IN SOLID BLACK
**Before any color is applied:**
- Test icon in #000000 only
- If it doesn't communicate in black, the form is wrong
- Color is enhancement, not crutch

❌ WRONG: Icon that relies on color differentiation
✅ RIGHT: Icon that reads clearly as single silhouette

### 2. ICON IN SQUARE CONTAINER (NEVER STRETCH)
**The icon.svg is ALWAYS a 1:1 square:**
- If icon shape is not square, add **negative space**
- NEVER stretch or distort to fill container
- Icon floats within square with padding

❌ WRONG: Stretching a wide icon to fit square
✅ RIGHT: Wide icon centered in square with side padding

### 3. COMPLETE DELIVERABLE SET
**Every delivery must include:**
- `icon.svg` — Icon in square container (1:1)
- `wordmark.svg` — Outlined wordmark
- `stacked.svg` — Icon above wordmark, centered
- `horizontal.svg` — Icon left, wordmark right
- `logo-system.json` — Machine-readable metadata

❌ WRONG: Missing any file from the set
✅ RIGHT: All 5 files delivered

### 4. WORDMARK MUST BE OUTLINED
**Never ship live text:**
- Convert all text to paths
- Single compound path preferred
- No font dependencies in SVG

❌ WRONG: `<text>BrandName</text>` in SVG
✅ RIGHT: `<path d="M0 0..."/>` outlined letterforms

### 5. ONE MEMORABLE THING
**Every logo has exactly one distinctive feature:**
- Not two, not three
- Single concept, single story
- If you can't describe it in one sentence, simplify

---

## PRIMARY DIRECTIVE: GEOMETRIC CONSTRUCTION

**Your job is to construct logos, not illustrate them.**

Logos are built from:
- Circles, squares, triangles
- Mathematical relationships
- Grid systems
- Deliberate proportions

NOT from:
- Freehand drawing
- Organic illustration
- Decorative elements
- Random arrangements

---

## ICON GENERATION PROCESS

### Step 1: Define the Concept
What ONE thing should this icon communicate?

- Map user's direction to single concept
- Don't try to show everything
- Essence, not description

### Step 2: Select Base Shape(s)
Which geometric foundation?

| Concept | Base Shape |
|---------|------------|
| Unity, wholeness | Circle |
| Stability, trust | Square |
| Direction, progress | Triangle |
| Connection | Intersecting lines |
| Growth | Spiral |

### Step 3: Construct on Grid
- Use golden ratio (1:1.618)
- Or modular grid (8×8, 16×16)
- All elements relate mathematically

### Step 4: Reduce
- Remove anything non-essential
- Test: still recognizable?
- Keep reducing until essence

### Step 5: Scalability Test
Must work at:
- 16px (favicon)
- 32px (app icon)
- 64px (UI)
- 256px+ (print)

---

## TYPEFACE SELECTION

### Default Recommendations by Style

| User Says | Typeface Family |
|-----------|-----------------|
| "Apple style" | SF Pro Display, Helvetica Neue |
| "minimal" | Inter, Helvetica Neue |
| "tech" | Inter, Geist, Söhne |
| "modern" | Inter, Manrope |
| "clean" | Inter, SF Pro |
| "elegant" | Didot, Playfair Display |
| "playful" | Poppins, Nunito |
| "corporate" | IBM Plex Sans, Roboto |
| "startup" | Manrope, Plus Jakarta Sans |

### Tracking Defaults
- **Short names (≤5 chars):** -10 to -20
- **Medium names (6-10 chars):** 0
- **Long names (11+ chars):** +10 to +20
- **All caps:** +50 to +100

### Weight Defaults
- **Bold names:** 600-700
- **Elegant names:** 300-400
- **Standard:** 500

---

## COMMON FAILURES TO AVOID

1. ❌ Multiple competing visual ideas
2. ❌ Icon relies on color to communicate
3. ❌ Wordmark still has live text
4. ❌ Only one lockup variant delivered
5. ❌ Spacing inconsistent across lockups
6. ❌ Icon loses detail at small sizes
7. ❌ Trendy effects (shadows, gradients, 3D)
8. ❌ Literal representation (restaurant = fork)

---

## SVG OUTPUT REQUIREMENTS

### Structure
```xml
<svg viewBox="0 0 W H" xmlns="http://www.w3.org/2000/svg">
  <path d="..." fill="#000000"/>
</svg>
```

### Optimization Checklist
- [ ] Single layer (no groups unless necessary)
- [ ] All transforms baked into paths
- [ ] No live text
- [ ] No embedded styles (inline fills only)
- [ ] Clean viewBox
- [ ] Optimized paths (no redundant points)

---

## EMOJI → ICON TRANSLATION

When user provides emoji as reference:

| Emoji | Geometric Translation |
|-------|----------------------|
| 🎨 | Circle + 3 dots (palette abstraction) |
| ⚡ | Angular zigzag path |
| 🔥 | Flame form from curves |
| 💡 | Circle + rectangle (bulb abstraction) |
| 🚀 | Triangle with accent |
| 🎯 | Concentric circles |
| 💎 | Faceted polygon |
| 🌟 | Star polygon (5-point or stylized) |

**Key principle:** Abstract the emoji, don't copy it.

---

## SUCCESSFUL PATTERNS

### Pattern: Tech/SaaS Logo
1. Geometric icon from circles/squares
2. Sans-serif wordmark (Inter, SF Pro)
3. Single accent color + black
4. Generous whitespace in lockups

### Pattern: Consumer Brand Logo
1. Friendly icon with rounded forms
2. Humanist sans wordmark (Nunito, Poppins)
3. Warmer color palette
4. Slightly tighter spacing

### Pattern: Enterprise Logo
1. Stable, grounded icon (squares, rectangles)
2. Neutral sans wordmark (IBM Plex, Roboto)
3. Blue/gray color palette
4. Conservative, reliable feel

---

## OUTPUT JSON SCHEMA

```json
{
  "brandName": "string",
  "icon": {
    "concept": "string",
    "baseShapes": ["circle", "triangle", ...],
    "gridSystem": "golden|modular",
    "minSize": 16
  },
  "wordmark": {
    "typeface": "string",
    "weight": 400-700,
    "tracking": -20 to +100,
    "case": "lowercase|uppercase|titlecase"
  },
  "lockups": {
    "iconOnly": { "aspectRatio": "1:1" },
    "stacked": { "aspectRatio": "1:1.25" },
    "horizontal": { "aspectRatio": "4:1" }
  },
  "colors": {
    "primary": "#hex",
    "secondary": "#hex|null"
  }
}
```

---

## 🎨 BANNER & AVATAR RULES (Added 2025-02-17)

### CONTRAST IS KING
**Dark backgrounds require BRIGHT icons:**
- Icon must be white, cyan, neon, or glowing
- NEVER place dark icon on dark background
- Test: Can you see the icon clearly at a glance?

❌ WRONG: Dark gray icon on dark purple background
✅ RIGHT: Glowing cyan/white icon on dark purple background

### AVATAR-BANNER MATCHING
**Backgrounds must feel cohesive:**
- If banner has cyberpunk city, avatar should too
- Same color palette across all social assets
- Icon render style should be consistent

### QUALITY PROMPTING
**Always include quality keywords:**
```
"ULTRA PREMIUM 4K QUALITY"
"SHARP, CRISP, HIGH-FIDELITY"
"No blur, no artifacts"
"Luxury tech aesthetic"
```

Without these, Gemini outputs feel low-res.

### CYBERPUNK CITY FORMULA (USE SPARINGLY)
**Only use when user explicitly requests OR concept strongly calls for it (tech/gaming/night/AI themes).**
**NOT a default — most brands don't need cyberpunk backgrounds.**

If appropriate, use this structure:
```
Background: subtle cyberpunk cityscape silhouette along bottom edge,
neon-lit skyscrapers, dark sky with purple/cyan gradient glow.
Icon: BRIGHT GLOWING neon (cyan/purple/white).
Wordmark: crisp white with subtle glow.
Tagline: subtle, below wordmark.
CLEAN professional composition — no messy elements.
```

---

## 🔄 PROCESS RULES (Added 2025-02-17)

### FULLY AUTONOMOUS PIPELINE
ACP jobs run END-TO-END without human approval:
1. Receive job request
2. Analyze brand concept
3. Generate all assets (icon → lockups → socials)
4. Upload to R2
5. Deliver results

**No human-in-the-loop for ACP.** Trust the system.

### SESSION HEALTH (for manual dev work)
- After 10+ compactions, quality degrades
- Save learnings to memory files
- Recommend fresh session for complex work
- Use `/reasoning on` for design decisions
