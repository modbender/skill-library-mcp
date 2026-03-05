---
name: midjourney
description: "AI image generation via Midjourney Discord bot: create images from prompts, upscale, create variations, blend images, describe images. Use when: (1) generating artwork from text descriptions, (2) creating variations of existing images, (3) upscaling low-res images, (4) analyzing images for prompts. NOT for: commercial licensing questions (check Midjourney ToS), API access (Discord-only)."
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["discord"] },
        "install":
          [
            {
              "id": "discord",
              "kind": "app",
              "package": "discord",
              "bins": ["discord"],
              "label": "Install Discord (required for Midjourney bot)",
            },
          ],
      },
  }
---

# Midjourney Skill

Generate AI artwork via the Midjourney Discord bot. All commands are run through Discord.

## ⚠️ Prerequisites

1. **Discord account** — Required
2. **Midjourney subscription** — Free trials limited, paid plans at midjourney.com
3. **Join Midjourney Discord** — https://discord.gg/midjourney
4. **Bot access** — Use `/imagine` in #newbies channels or your own server

---

## Quick Start

```
/imagine prompt: a cyberpunk cat sitting on a neon rooftop, detailed, cinematic lighting --ar 16:9 --v 6
```

**Workflow:**
1. Type `/imagine` in Discord
2. Enter your prompt
3. Wait ~60 seconds for 4 variations
4. Use U1-4 to upscale, V1-4 for variations

---

## When to Use

✅ **USE this skill when:**

- Generating artwork, illustrations, or concept art from text
- Creating variations of an existing image
- Upscaling low-resolution images
- Blending multiple images together
- Getting prompt ideas from existing images (describe)
- Experimenting with artistic styles and parameters

❌ **DON'T use this skill when:**

- Need commercial licensing info → check midjourney.com/terms
- Want API access → Discord-only, no public API
- Need exact text rendering → MJ struggles with text
- Require photorealistic faces → may have artifacts

---

## Core Commands

### /imagine — Generate Images

```
/imagine prompt: <your description> [parameters]
```

**Examples:**

```
/imagine prompt: portrait of a warrior princess, golden armor, dramatic lighting, fantasy art --ar 2:3 --stylize 750

/imagine prompt: minimalist logo for a tech startup, geometric, blue and white --v 6

/imagine prompt: isometric 3D render of a cozy coffee shop, warm lighting, blender style --ar 1:1
```

### /upscale — Increase Resolution

After generation, click **U1, U2, U3, or U4** buttons under the image grid.

**Or use command:**
```
/upscale --image <job-id> --index 1
```

### /variations — Create Variations

After generation, click **V1, V2, V3, or V4** buttons.

**Or use command:**
```
/variations --image <job-id> --index 1 --strength subtle
```

### /blend — Merge Images

```
/blend
```

Upload 2-5 images. Midjourney merges them stylistically.

**Example use:**
- Blend a photo with a painting style
- Merge character concepts
- Combine color palettes

### /describe — Analyze Image

```
/describe
```

Upload an image → get 4 prompt suggestions that would create similar results.

**Use for:**
- Reverse-engineering styles
- Learning prompt patterns
- Getting inspiration from existing art

### /remix — Modify Prompts

Enable remix mode to change prompts when creating variations:

```
/remix
```

Then use V1-V4 buttons with modified prompts.

---

## Parameters Reference

### Aspect Ratio (--ar)

```
--ar 1:1      # Square (default)
--ar 16:9     # Widescreen
--ar 9:16     # Portrait (phone)
--ar 2:3      # Classic portrait
--ar 3:2      # Landscape photo
```

### Version (--v)

```
--v 6         # Latest (default)
--v 5.2       # Previous version
--v 5.1       # Older, more artistic
--niji 6      # Anime/manga style
```

### Stylize (--s or --stylize)

```
--s 100       # Low stylization (follows prompt closely)
--s 250       # Default
--s 750       # High stylization (more artistic freedom)
--s 1000      # Maximum
```

### Chaos (--chaos)

```
--chaos 0     # Consistent results (default)
--chaos 50    # More varied
--chaos 100   # Maximum variation
```

### Quality (--quality or --q)

```
--q 0.5       # Half quality, faster
--q 1         # Default
--q 2         # Double quality, slower, more detail
```

### Seed (--seed)

```
--seed 1234   # Reproducible results
```

Same seed + same prompt = similar images.

### No (--no)

```
--no text     # Avoid text in image
--no blur     # Avoid blur
--no people   # Avoid people
```

### Style Raw (--style raw)

```
--style raw   # Less opinionated, more literal prompt interpretation
```

### Weird (--weird)

```
--weird 0     # Normal (default)
--weird 500   # Unconventional compositions
--weird 3000  # Maximum weirdness
```

---

## Advanced Techniques

### Multi-Prompt (::)

Weight different parts of your prompt:

```
/imagine prompt: cat::2 dog::1
# Cat is 2x more important than dog
```

### Image Prompts

Use an image URL as part of your prompt:

```
/imagine prompt: https://example.com/image.jpg a futuristic cityscape
```

### Character Reference (--cref)

```
/imagine prompt: character in different scene --cref <image-url>
```

Maintains character consistency across images.

### Style Reference (--sref)

```
/imagine prompt: original content --sref <image-url>
```

Applies the style of a reference image.

---

## Workflow Examples

### Logo Design

```
/imagine prompt: minimalist tech logo, geometric shapes, gradient blue, vector style --ar 1:1 --v 6
# Review 4 options
# Click U2 to upscale best one
# Click V2 for variations of that style
# Repeat until satisfied
```

### Character Concept Art

```
/imagine prompt: full body character design, fantasy rogue, leather armor, daggers, dynamic pose --ar 2:3 --niji 6
# Upscale favorite
# Use /variations for pose variations
# Use --cref to maintain character in new scenes
```

### Product Visualization

```
/imagine prompt: product photography, wireless headphones on marble surface, soft studio lighting, commercial --ar 4:5 --q 2
```

### Album Cover

```
/imagine prompt: psychedelic album cover, abstract swirls, vibrant colors, 1970s style --ar 1:1 --stylize 500
```

---

## Tips

1. **Be specific but not restrictive** — "cinematic lighting" good, "exactly 47 degree angle" bad
2. **Use artist names carefully** — "in the style of Greg Rutkowski" works, but consider living artists ethically
3. **Iterate** — First result rarely perfect. Use V buttons to explore variations
4. **Save job IDs** — Useful for referencing later
5. **Check Discord** — All generations saved in your Discord DMs with bot
6. **Use --v 6** — Latest version has best prompt understanding
7. **Niji for anime** --niji 6 for manga/anime style

---

## Troubleshooting

**"Queue full"** — Wait a few minutes, try again during off-peak hours

**"Invalid parameter"** — Check parameter syntax, some require specific values

**"Content policy violation"** — Adjust prompt to avoid restricted content

**"Can't upscale"** — Job may have expired (24hr limit on free accounts)

**"Text looks wrong"** — MJ struggles with text. Try --no text or use DALL-E 3 for text-heavy images

**"Faces look distorted"** — Common issue. Try --v 6, add "photorealistic" or use inpainting

---

## Pricing (as of 2026)

- **Free trial** — ~25 images (one-time)
- **Basic** — $10/mo, ~200 images
- **Standard** — $30/mo, unlimited relaxed mode
- **Pro** — $60/mo, faster, more concurrent jobs
- **Mega** — $120/mo, maximum capacity

Check midjourney.com for current pricing.

---

## Resources

- **Official docs:** docs.midjourney.com
- **Discord:** discord.gg/midjourney
- **Community showcase:** midjourney.com/showcase
- **Prompt guide:** docs.midjourney.com/docs/prompt-guide
