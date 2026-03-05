# Image Generation Tips

## Platform-Specific Settings

### Midjourney
```
--ar [ratio]    Aspect ratio (16:9, 4:5, 1:1)
--v [number]    Version (6, 7)
--style raw     Cleaner, less stylized output
--q 2           Higher quality (slower)
--s [0-1000]    Stylization level
--c [0-100]     Chaos/variation level
```

**For UI work**: Use `--style raw --v 7` (or v6 for flatter)
**For concept art**: Default style, higher --s

### DALL-E / GPT-4
- Natural language works well
- Be specific about style and composition
- Can edit existing images
- Good for quick iterations

### Stable Diffusion
- Negative prompts help refine
- ControlNet for structure guidance
- Custom models for specific styles
- More technical, more control

## Quality Modifiers

### Resolution/Quality
- "High resolution", "4K", "detailed"
- "Sharp focus", "crisp details"
- Avoid: "HD" (often ignored)

### Lighting
- "Soft lighting", "studio lighting"
- "Natural light", "golden hour"
- "Dramatic shadows", "rim light"

### Composition
- "Centered", "rule of thirds"
- "Close-up", "wide shot", "aerial view"
- "Negative space", "minimal background"

## Style References

### Photography Styles
- "Product photography, white background"
- "Editorial photography, magazine quality"
- "Documentary style, authentic"
- "Portrait, shallow depth of field"

### Illustration Styles
- "Flat illustration, vector style"
- "Isometric, technical illustration"
- "Hand-drawn, sketch style"
- "3D render, Blender style"

### Brand References
- "Apple product photography style"
- "Stripe website illustration style"
- "Notion clean aesthetic"
- "Linear app interface"

## Iteration Strategies

### Upscaling
After finding a good variant:
- Midjourney: U1-U4 buttons
- Run through dedicated upscaler
- Regenerate at higher resolution

### Variations
- Subtle: Request same image with minor tweaks
- Remix: Combine elements from multiple outputs
- Evolve: "More like this, but [direction]"

### Inpainting
- Regenerate specific areas
- Fix hands, faces, text (AI weaknesses)
- Blend AI output with real elements

## Common Failures and Fixes

### Text in Images
AI-generated text is usually wrong.
Fix: Generate without text, add in design tool.

### Hands/Fingers
Often malformed.
Fix: Crop out, regenerate, or fix in editing tool.

### Brand Elements
AI can't match your exact brand.
Fix: Use AI for concept, apply brand elements manually.

### Consistency Across Set
Multiple generations won't match perfectly.
Fix: Use style reference features, or establish strong prompt consistency.
