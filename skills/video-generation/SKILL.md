---
name: Video Generation
description: Create AI videos with optimized prompts, motion control, and platform-ready output.
metadata: {"clawdbot":{"emoji":"🎬","os":["linux","darwin","win32"]}}
---

# AI Video Generation

Help users create and promote AI-generated video content.

**Rules:**
- Ask what they want: text-to-video, image-to-video, or video editing
- Check provider files for setup: `runway.md`, `luma.md`, `kling.md`, `pika.md`, `stable-video-diffusion.md`, `replicate.md`
- Check `api-patterns.md` for async polling, backoff, and caching
- Check `promotion.md` for distribution and marketing strategies
- Start with lowest resolution/duration to validate prompt before scaling

---

## Platform Selection

| Use Case | Recommended |
|----------|-------------|
| Complex motion, professional | Runway Gen-4.5 |
| Human motion, longer clips | Kling V2 |
| Stylized, fast iterations | Pika |
| Camera movements, cinematic | Luma Dream Machine |
| Local/private, no API cost | Stable Video Diffusion |
| Quick testing, model variety | Replicate |

---

## Prompting for Video

- **Describe motion explicitly** — "waves crashing", "walking toward camera", not just scene descriptions
- **Include camera direction** — "camera slowly pans left", "dolly zoom", "tracking shot"
- **Front-load subject** — models weight early tokens heavily
- **Under 200 tokens** — longer prompts dilute motion guidance
- **Avoid impossible physics** — results look uncanny without proper setup

---

## Image-to-Video

- Source image quality matters more than prompt — artifacts amplify
- Match aspect ratio BEFORE generation — post-crop destroys quality
- Use images with implied motion (mid-stride, flowing hair)
- Remove text/logos — they warp unpredictably

---

## Aspect Ratios

- **16:9** — YouTube, standard horizontal
- **9:16** — TikTok, Reels, Shorts (vertical mandatory)
- **1:1** — Instagram feed, flexible
- Generate in target ratio — never crop after

---

## Cost Control

- Start with shortest duration (2-4s) to validate
- Preview at lowest resolution (480p/720p)
- Extend good clips rather than regenerating
- Download immediately — signed URLs expire
- Free tiers: Pika (150/mo), Kling (66/day), Luma (30/mo)

---

## Failure Modes

- **NSFW false positive** — rephrase or switch platform
- **Face morphing** — add "consistent face" to prompt
- **Text always broken** — add in post-production
- **Hands/fingers wrong** — frame to minimize visibility
- **Quality degrades >8-10s** — plan for cuts

---

### Current Setup
<!-- Provider: status -->

### Projects
<!-- What they're creating -->

### Preferences
<!-- Settings that work: resolution, duration, style -->

---
*Empty sections = not configured yet. Check providers.md for setup.*
