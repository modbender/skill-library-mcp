# AI Logo Generation

## Model Ranking (2026)

| Model | Best For | Text | Quality | Speed |
|-------|----------|------|---------|-------|
| **Nano Banana Pro** | Overall best, text + icons | Excellent | Excellent | Fast |
| **GPT Image 1.5** | Conversational iteration | Excellent | Excellent | Medium |
| **Ideogram** | Typography-focused logos | Excellent | Good | Fast |
| **Midjourney v7** | Artistic/stylized icons | Poor | Beautiful | Medium |
| **Flux Pro** | Photorealistic emblems | Good | Excellent | Slow |

**Start with Nano Banana Pro** for most logos. It's currently the best balance of quality, text rendering, and ease of use.

---

## Nano Banana Pro

Uses Google's Gemini 3 Pro Image. Excellent text rendering, character consistency, and up to 4K output.

### The 7-Step Prompt Framework

This structure consistently produces better logos:

**1. Brand personality:**
```
clean and trustworthy | bold and energetic | playful and creative
```

**2. Main element:**
```
a minimal electric bicycle | a stylized mountain peak | an abstract flame
```

**3. Style direction:**
```
minimalist line art | bold geometric shapes | hand-drawn illustration
```

**4. Color specification:**
```
bright golden yellow (#FFD700) background with black icon
navy blue (#1E3A5A) and orange (#FF6B35) accent
```

**5. Symbolic meaning:**
```
integrate a lightning bolt into the bicycle frame to represent electric power
the mountain peak forms a subtle letter "A" representing achievement
```

**6. Technical requirements:**
```
consistent thick outlines | works at 32px favicon size | no gradients
high contrast for readability | simple geometric forms
```

**7. Layout:**
```
centered design | icon above text | horizontal lockup
```

### Complete Prompt Template

```
Create a [STYLE] logo featuring [MAIN ELEMENT] on [BACKGROUND].
The [MAIN ELEMENT] should be rendered in [ART STYLE] using [COLORS],
viewed from [ANGLE]. The design should include [COMPONENTS].
Most importantly, integrate [SYMBOLIC ELEMENT] that [CONNECTION TO BRAND].
The entire design should use [TECHNICAL SPECS] in a [MOOD] style.
The logo should look good at 32px with recognizable shapes.
[Optional: Render just logo symbol. No text.]
```

### Example: Electric Bike Company

```
Create a minimalist logo featuring a black electric bicycle icon 
centered on a bright golden yellow background.
The bicycle should be rendered in clean line art style using thick 
black strokes, viewed from the side. The design should include two 
circular wheels, handlebars, and a seat.
Most importantly, integrate a lightning bolt symbol into the bicycle 
frame structure - the lightning bolt should form part of the frame 
geometry, creating a visual representation of electric power.
The entire icon should be drawn with consistent thick black outlines 
in a geometric, modern style.
The logo should look good at 32px with recognizable shapes.
```

### Nano Banana Tips

- **Iterate in batches:** Generate 10-20 variations, pick best direction, refine
- **New chat for edits:** When it stops listening, start fresh chat and upload latest image
- **Masking instructions:** Add "Do not change the symbol shape. Only adjust spacing."
- **Negative prompting:** "No gradients. No 3D. No drop shadows. No small interior details."

---

## GPT Image 1.5

OpenAI's latest image model. Best used through ChatGPT for conversational refinement.

### Strengths
- Natural language understanding (just describe what you want)
- Iterative editing ("make the blue darker", "add more space around it")
- Excellent text rendering
- Can work from reference images

### Prompt Structure

With GPT Image, you can be more conversational:

```
Create a logo for a tech startup called "Apex Labs". 
It should be minimalist, using just a geometric shape and the company name.
Use navy blue as the primary color. The design should work as a favicon.
```

Then iterate:
```
Make the "A" more prominent
Try a lighter shade of blue
Remove the tagline, just keep the symbol and name
```

### Best Practices
- Start simple, add complexity through conversation
- Ask for multiple options: "Show me 3 different directions"
- Request specific changes: "Move text 20px lower"
- Use for concepts, then recreate in vector software

---

## iOS App Icons & Liquid Glass

iOS 26 introduced Liquid Glass design. App icons now have depth, translucency, and dynamic lighting.

### App Icon Requirements

| Platform | Size | Format |
|----------|------|--------|
| App Store | 1024×1024px | PNG, no transparency |
| iPhone | 60×60pt (@2x, @3x) | Auto-generated |
| iPad | 83.5×83.5pt (@2x) | Auto-generated |
| Favicon test | Works at 32px | Critical check |

### iOS 26 Liquid Glass Prompt

Tested prompt that matches Apple's new icon style:

```
Create a highly polished, modern app icon in the style of iOS system icons.
The icon should feature [YOUR ELEMENT] as the central motif.
The icon background must be a perfectly rounded square with smooth corners,
filled with a vibrant gradient using [COLOR - recommend single color family].
The gradient should be subtle yet vivid, giving depth and luminosity.
The central symbol should be minimalist, geometric, and instantly recognizable,
rendered in white or very light color.
Center it with generous, even padding from all edges.
Apply soft, diffused drop shadows beneath the symbol and gentle inner shadows
on the background to create depth and a slight 3D, glassy effect,
while maintaining an overall flat and clean appearance.
Surfaces should be ultra-smooth, no harsh outlines, no pixelation, no textures.
Add a subtle top-gloss or light reflection to enhance the glassy, premium feel.
The icon should embody a friendly, approachable, and modern aesthetic.
The design must be visually cohesive with Apple's iOS system icons.
The icon represents [APP PURPOSE].
```

### Liquid Glass Design Principles

1. **Layer separation:** Foreground symbol + translucent background
2. **Bold silhouettes:** Symbol must be recognizable at 60px
3. **Single focal point:** One clear shape, not multiple competing elements
4. **System consistency:** Match Apple's native app icons in feel
5. **Mode testing:** Check Light, Dark, Clear, and Tinted appearances

### What to Avoid for iOS Icons
- Thin lines that disappear at small sizes
- Complex gradients that muddy in Liquid Glass rendering
- Text within the icon (except single letters)
- Sharp corners or edges near the mask boundary
- Low contrast between symbol and background

---

## Ideogram

Best for logos that absolutely need perfect text rendering.

### Prompt Structure
```
Logo with text "BRAND NAME" featuring [description],
[typography style], [colors], white background, vector style
```

### Examples
```
Logo with text "Summit Labs" featuring a minimal mountain peak icon,
modern sans-serif typography, navy and orange, white background, vector

Minimalist logo with text "APEX" in bold geometric letters,
abstract triangle above, blue gradient, centered, white background
```

---

## Midjourney v7

Still the king of aesthetics, but struggles with text. Use for icon-only concepts.

### Parameters
- `--stylize 50-100` — Lower = more literal to prompt
- `--ar 1:1` — Square for logos
- `--no text, letters, words` — Prevents garbled text

### Example
```
minimalist fox logo, geometric shapes, orange and white, 
simple clean lines, vector style --ar 1:1 --stylize 50 --no text
```

---

## Quality Check Loop (CRITICAL)

**NEVER deliver an AI-generated logo without visual inspection.** Every output must be reviewed before sharing or finalizing.

### Mandatory Review Process

1. **Generate** — Create the image
2. **Inspect** — Look at the actual output, not the prompt
3. **Evaluate** — Check against the issues list below
4. **Fix or regenerate** — Crop, edit, or generate again
5. **Repeat** — Until quality threshold is met (max 5-7 attempts per direction)

### Common Issues to Check

| Problem | Solution |
|---------|----------|
| Unwanted padding/margins | Crop the image |
| Elements cut off at edges | Regenerate with "centered composition" |
| Text misspelled or garbled | Use Nano Banana/Ideogram, or add text manually |
| Wrong colors | Specify hex codes, regenerate |
| Too complex for small sizes | Simplify prompt, request "minimalist" |
| Asymmetric or unbalanced | Request "centered", "balanced composition" |
| Unwanted background elements | Request "clean background", "no decorations" |
| Low contrast | Specify contrasting colors explicitly |

### When to Change Strategy

After 5-7 failed attempts with the same approach:
- Try a different model
- Simplify the concept significantly
- Change the style direction entirely
- Generate icon-only, add text manually

### Quick Fixes

**Crop:** Many issues (padding, partial unwanted elements) are solved by cropping. Don't regenerate if a crop fixes it.

**Prompt tweaks that help:**
- "centered composition, no margins"
- "clean white background, nothing else"
- "simple geometric shapes only"
- "no text, symbol only" (then add text in vector software)

**Validation at multiple sizes:**
After fixing, always check at 32px, 180px, and 1024px. Issues visible at small sizes mean more simplification needed.

---

## Post-Generation Workflow

AI output is never the final logo. Always:

1. **Vectorize** — Use vectorizer.ai, Adobe Illustrator Image Trace, or Figma
2. **Clean shapes** — Fix imperfect curves, align elements
3. **Add/fix text** — Manually add typography in vector software
4. **Create variants** — Horizontal, stacked, icon-only, dark/light
5. **Test sizes** — Verify at 16px, 32px, 180px, 1024px
6. **Export properly** — SVG source, PNG at all required sizes

### Vectorization Tools
- **vectorizer.ai** — Best automatic conversion
- **Adobe Illustrator** — Image Trace for manual control
- **Figma** — Quick vectorization for simple logos
- **Inkscape** — Free alternative

---

## Common Mistakes

1. **Using AI output directly** — Always vectorize and refine
2. **Wrong model for text** — Use Nano Banana or Ideogram, not Midjourney
3. **Too much detail** — Complex designs fail at small sizes
4. **No favicon test** — Always check at 32px before finalizing
5. **Ignoring variants** — Create horizontal, stacked, icon-only versions
6. **Skipping vectorization** — PNGs don't scale; always produce SVG
