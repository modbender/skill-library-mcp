# Write My Blog — Theme Guide

## Switching Themes

```bash
curl -X PUT http://localhost:3000/api/themes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"theme": "glassmorphism"}'
```

## Available Themes

### 1. Minimalism
Clean, purposeful design with generous whitespace and monochrome palette.
- **Fonts**: Inter
- **Colors**: Black/white with subtle grays
- **Best for**: Professional blogs, portfolios

### 2. Brutalism
Bold, attention-grabbing with jarring color combos and hard shadows.
- **Fonts**: Space Grotesk, Space Mono
- **Colors**: Orange accent on cream
- **Best for**: Creative/art blogs, counterculture

### 3. Constructivism
Geometric, energetic layouts with strong red accents.
- **Fonts**: Oswald, Source Sans
- **Colors**: Red/black on parchment
- **Best for**: Design blogs, political commentary

### 4. Swiss Style
Grid-based precision with Helvetica typography.
- **Fonts**: Helvetica Neue
- **Colors**: Red accent on white
- **Best for**: Architecture, design firms

### 5. Editorial
Magazine-inspired with serif typography and layered compositions.
- **Fonts**: Playfair Display, Source Serif
- **Colors**: Deep red accent, warm tones
- **Best for**: Long-form content, journalism

### 6. Hand-Drawn
Casual, crafty aesthetic with handwritten fonts and sketchy accents.
- **Fonts**: Caveat, Patrick Hand
- **Colors**: Warm yellows, orange
- **Best for**: Personal blogs, crafts

### 7. Retro
Vintage dark theme with warm colors and grainy textures.
- **Fonts**: Bungee Shade, VT323
- **Colors**: Orange on dark brown
- **Best for**: Nostalgia, gaming, culture

### 8. Flat
Zero depth, solid colors, clean hierarchy.
- **Fonts**: Roboto, Open Sans
- **Colors**: Blue accent on light gray
- **Best for**: Tech blogs, startups

### 9. Bento
Apple-inspired rounded blocks in compact grid layout.
- **Fonts**: SF Pro (system), Helvetica Neue
- **Colors**: Blue accent on light gray
- **Best for**: Portfolio, showcase, product blogs

### 10. Glassmorphism
Frosted glass effects with backdrop-blur on dark gradient.
- **Fonts**: Outfit, Inter
- **Colors**: Purple gradient on dark blue
- **Best for**: Modern/premium, tech, crypto

## CSS Custom Properties

All themes use these CSS variables that you can override with `customCss` in settings:

```css
--bg-primary      /* Main background */
--bg-secondary    /* Card/section background */
--bg-accent       /* Accent background */
--text-primary    /* Main text color */
--text-secondary  /* Secondary text */
--text-muted      /* Muted/meta text */
--accent          /* Primary accent */
--accent-hover    /* Accent hover state */
--border          /* Border color */
--shadow          /* Box shadow */
--radius          /* Border radius */
--font-heading    /* Heading font family */
--font-body       /* Body font family */
--font-mono       /* Monospace font family */
--max-width       /* Content max width */
--spacing-unit    /* Base spacing */
--transition      /* Default transition */
```
