# AI Image Galleries — Deep Dive

Finding the right AI-generated reference images by model and style.

## By Model

### Midjourney

**Official Showcase:** https://midjourney.com/showcase
Best for: Curated picks from the community, trending styles, what's possible with latest versions.

**Community Collections:**
- **Midlibrary** (https://midlibrary.io) — Searchable style library with prompt breakdowns
- **MJ Prompt Tool** (https://prompt.noonshot.com) — Explore prompts by style/subject
- **r/midjourney** — Reddit community with latest experiments

**What Midjourney excels at:**
- Photorealistic portraits and scenes
- Artistic interpretations
- Product mockups
- Architecture visualization
- Fantasy and sci-fi concepts

### Stable Diffusion

**Civitai** (https://civitai.com) — The hub for SD models
- Browse by model (SDXL, SD 1.5, Pony, etc.)
- Filter by image style, subject, NSFW level
- Download models and LoRAs
- See what settings produced each image

**Lexica** (https://lexica.art) — SD image search engine
- Search by text or image
- See exact prompts used
- Great for finding style references

**PromptHero** (https://prompthero.com) — Multi-model with strong SD coverage
- Filter by model version
- Copy prompts directly
- Community voting surfaces best results

**What Stable Diffusion excels at:**
- Anime and illustration styles (with right models)
- Consistent character generation (with LoRAs)
- Style transfer and fine-tuning
- NSFW content (model dependent)
- Local/private generation

### DALL-E

**OpenAI Labs** (https://labs.openai.com) — Official gallery
- Curated examples
- Editorial illustrations
- Brand-safe content

**What DALL-E excels at:**
- Clean, editorial illustrations
- Text rendering (DALL-E 3)
- Brand-appropriate imagery
- Photorealistic people (with natural diversity)

### Other Models

**Ideogram** (https://ideogram.ai) — Best for text in images
- Typography integration
- Logo concepts
- Poster designs

**Leonardo.AI** (https://leonardo.ai) — Game asset focused
- Character design
- Game environments
- Consistent style training

**Flux** — Latest open model
- Check Civitai for Flux galleries
- Realistic human generation
- High prompt adherence

## By Style

### Photorealistic

**Best sources:**
- Midjourney Showcase (filter by "photorealistic")
- Civitai → Filter by "Realistic" model type
- PromptHero → Stable Diffusion → Realistic

**Key models/styles:**
- Midjourney v6+
- SDXL + Realistic Vision
- Flux

### Illustration / Concept Art

**Best sources:**
- PromptHero → Filter by "Illustration"
- ArtStation (still has AI section)
- Civitai → "Artistic" models

**Key models/styles:**
- Midjourney with --style raw
- SD with anime/illustration LoRAs
- DALL-E for editorial illustration

### Anime / Manga

**Best sources:**
- Civitai → Filter by "Anime"
- PromptHero → Anime category
- Danbooru-trained models

**Key models:**
- NovelAI
- Anything V5
- CounterfeitXL
- Pony Diffusion

### 3D / Rendered

**Best sources:**
- Midjourney (specify "3D render" in prompt)
- Blender + AI workflows
- PromptHero → 3D category

**Key techniques:**
- "octane render" in prompts
- "unreal engine" style
- "blender 3d" aesthetic

### Logo / Branding

**Best sources:**
- Ideogram (best for text integration)
- Midjourney with specific prompts
- DALL-E 3 for clean vectors

**Key approaches:**
- Keep it simple (AI struggles with complex logos)
- Multiple variations, then refine manually
- Use as starting point, not final output

## Finding Prompts

### Reverse Engineering

**From image:**
1. Upload to Lexica → "Search by image"
2. Find similar images with visible prompts
3. Adapt the prompt elements you like

**From URL:**
1. Most galleries show prompts
2. Civitai always includes generation data
3. Midjourney Showcase links to Discord with prompts

### Prompt Databases

| Source | Focus |
|--------|-------|
| PromptHero | Multi-model, searchable |
| PromptBase | Marketplace (paid prompts) |
| Civitai | SD-focused, free |
| Midlibrary | MJ styles organized |

## Style Consistency

### Character Consistency

**Problem:** AI generates different characters each time.

**Solutions:**
1. **LoRAs** — Train on specific character
2. **IP-Adapter** — Reference image conditioning
3. **Consistent character prompts** — Detailed description reused
4. **Seed locking** — Same seed = similar results

### Brand Consistency

**Approach:**
1. Generate multiple options
2. Pick one direction
3. Train LoRA or use img2img
4. Keep detailed prompt notes

## Quality Filtering

### Red Flags

- Anatomical errors (hands, fingers, limbs)
- Inconsistent lighting
- Artifacting in complex areas
- Uncanny valley faces

### What to Look For

- Coherent composition
- Proper anatomy
- Consistent style throughout image
- No obvious AI artifacts

### Platforms with Quality Control

| Platform | Filtering |
|----------|-----------|
| Midjourney Showcase | Heavily curated |
| Civitai Top | Community votes |
| PromptHero Trending | Engagement-based |

## Workflow Tips

### For UI/Product Design

1. Start with Midjourney or DALL-E for concepts
2. Generate many variations quickly
3. Use as mood board, not final assets
4. Hand off to designer for refinement

### For Marketing / Social

1. Match model to content type
2. Editorial → DALL-E
3. Lifestyle → Midjourney
4. Custom brand → Trained SD model

### For Concept Art

1. Explore broadly first (many styles)
2. Find what resonates
3. Generate variations
4. Composite and paint over as needed
