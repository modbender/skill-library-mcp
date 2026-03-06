# Typography for Logo Wordmarks

Typeface selection and treatment for professional wordmarks.

---

## Type Categories & When to Use

### Geometric Sans-Serif
**Characteristics:** Constructed from circles, squares, consistent stroke width
**Personality:** Modern, technical, clean, futuristic
**Best for:** Tech, startups, SaaS, AI, fintech

| Typeface | Notes | Example Brands |
|----------|-------|----------------|
| Futura | The original geometric, bold and confident | Dolce & Gabbana, Supreme |
| Century Gothic | Softer Futura, more approachable | |
| Avenir | Humanized geometric, warm | |
| Proxima Nova | Web-optimized geometric | Spotify, BuzzFeed |
| Montserrat | Free alternative to Proxima/Gotham | |

### Grotesque / Neo-Grotesque Sans-Serif
**Characteristics:** Neutral, uniform, little personality
**Personality:** Universal, professional, trustworthy
**Best for:** Corporate, enterprise, institutions, global brands

| Typeface | Notes | Example Brands |
|----------|-------|----------------|
| Helvetica Neue | The standard, Swiss perfection | Apple (historical), 3M |
| Arial | Helvetica's less refined cousin | Microsoft |
| Inter | Modern web-native, excellent at all sizes | GitHub |
| SF Pro | Apple's system font, tech-native | Apple ecosystem |
| Söhne | Modern Helvetica evolution | Stripe |

### Humanist Sans-Serif
**Characteristics:** Organic curves, varied stroke widths, calligraphic roots
**Personality:** Friendly, approachable, warm, human
**Best for:** Consumer brands, wellness, education, accessibility

| Typeface | Notes | Example Brands |
|----------|-------|----------------|
| Gill Sans | Classic humanist, British | BBC, Tommy Hilfiger |
| Frutiger | Wayfinding clarity, warm | Apple (current) |
| Myriad Pro | Adobe's humanist standard | Apple (2002-2017) |
| Open Sans | Highly legible, web-native | Google |
| Nunito | Rounded humanist, very friendly | |

### Modern/Didone Serifs
**Characteristics:** High contrast, thin serifs, vertical stress
**Personality:** Elegant, luxurious, editorial, fashion
**Best for:** Fashion, luxury, publishing, beauty

| Typeface | Notes | Example Brands |
|----------|-------|----------------|
| Didot | French elegance | Giorgio Armani, Vogue |
| Bodoni | Italian precision | Elizabeth Arden |
| Playfair Display | Free Didone, web-optimized | |

### Transitional Serifs
**Characteristics:** Medium contrast, bracketed serifs
**Personality:** Traditional, established, trustworthy
**Best for:** Finance, law, institutions, heritage brands

| Typeface | Notes | Example Brands |
|----------|-------|----------------|
| Times New Roman | The newspaper standard | |
| Georgia | Screen-optimized transitional | |
| Baskerville | British elegance | |

### Slab Serifs
**Characteristics:** Block serifs, heavy weight, industrial
**Personality:** Bold, confident, mechanical, approachable
**Best for:** Hardware, industrial, construction, startup

| Typeface | Notes | Example Brands |
|----------|-------|----------------|
| Rockwell | Classic slab | |
| Roboto Slab | Google's slab | |
| Clarendon | Victorian era, distinctive | |

---

## Wordmark Treatment

### Tracking (Letter-spacing)
| Treatment | Value | When to Use |
|-----------|-------|-------------|
| Tight | -20 to -10 | Short names (3-5 chars), bold weights |
| Normal | 0 | Most applications |
| Loose | +20 to +50 | Luxury, editorial, all-caps |
| Very Loose | +100+ | Display, minimalist, fashion |

### Weight Selection
| Weight | When to Use |
|--------|-------------|
| Light (300) | Luxury, elegance, fashion |
| Regular (400) | Legibility priority, long names |
| Medium (500) | Balanced presence |
| Semibold (600) | Modern, confident |
| Bold (700) | Impact, startup, short names |

### Case
| Case | Personality | When to Use |
|------|-------------|-------------|
| ALL CAPS | Authority, impact, fashion | Strong brands, short names |
| lowercase | Friendly, tech, accessible | Startups, consumer tech |
| Title Case | Traditional, proper | Professional services |
| camelCase | Developer, technical | Dev tools, APIs |

---

## SVG Wordmark Process

1. **Set type** in vector software (Figma, Illustrator)
2. **Apply tracking/kerning** adjustments
3. **Outline text** → Convert to paths
4. **Merge paths** into single compound path
5. **Optimize** → Remove unnecessary points
6. **Export SVG** → Clean, single-path output

**Critical:** Never ship live text in logos. Always outline.

---

## Type Pairing with Icons

| Icon Style | Wordmark Style |
|------------|----------------|
| Geometric icon | Geometric sans or neo-grotesque |
| Organic icon | Humanist sans |
| Abstract icon | Bold sans or geometric |
| Minimal icon | Light weight, loose tracking |
| Complex icon | Simple, heavy wordmark |

**Rule:** Icon complexity + Wordmark complexity = constant

If icon is complex → wordmark is simple
If icon is simple → wordmark can be more distinctive

---

## Modern Typeface Recommendations (2026)

### For Tech/SaaS
1. Inter (free, excellent)
2. Söhne (Stripe-level quality)
3. Geist (Vercel)
4. SF Pro (Apple ecosystem)

### For Startups
1. Manrope (free geometric)
2. Plus Jakarta Sans (friendly geometric)
3. Space Grotesk (distinctive)

### For Consumer
1. Poppins (friendly, free)
2. Nunito (very approachable)
3. DM Sans (clean, free)

### For Enterprise
1. IBM Plex Sans (serious, free)
2. Source Sans Pro (neutral, free)
3. Roboto (universal)

---

## Anti-Patterns

- Using more than one typeface in a wordmark
- Script fonts for primary logos (legibility issues)
- Trendy display fonts that will date
- Live text in exported SVGs
- Extreme tracking that breaks at small sizes
- Mixing weights within wordmark
