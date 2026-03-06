---
name: image-studio
version: 1.0.0
description: Generate professional AI image prompts for any platform and niche — Instagram, LinkedIn, blog headers, YouTube thumbnails, brand visuals, and ads. Works with DALL-E, Midjourney, Stable Diffusion, and Ideogram. Includes style guides and platform sizing specs.
tags: [image-generation, dall-e, midjourney, visual-content, design, ai-art, social-media, branding]
author: contentai-suite
license: MIT
---

# Image Studio — Universal AI Image Prompt System

## What This Skill Does

Generates optimized AI image prompts for any platform, any niche, and any visual style. Takes your content brief and creates detailed prompts ready for DALL-E, Midjourney, Stable Diffusion, or Ideogram.

## How to Use This Skill

**Input format:**
```
BRAND NAME: [Your brand]
NICHE: [Your industry]
VISUAL STYLE: [Photorealistic / Illustrated / Minimalist / Bold/Graphic / Corporate / Lifestyle]
BRAND COLORS: [Primary and secondary colors or "default"]
PLATFORM: [Instagram / LinkedIn / Blog / YouTube / Twitter / Ad]
IMAGE TYPE: [Post background / Profile visual / Product / Person / Abstract concept / Infographic]
MOOD: [Energetic / Professional / Warm / Bold / Calm / Inspiring]
CONTENT CONTEXT: [What is the image for — the post topic]
```

---

## Platform Specifications

| Platform | Recommended Size | Aspect Ratio | Notes |
|----------|-----------------|-------------|-------|
| Instagram Feed | 1080×1080px | 1:1 | Also 1080×1350 (4:5) for more screen space |
| Instagram Stories/Reels | 1080×1920px | 9:16 | Full screen vertical |
| LinkedIn Post | 1200×628px | 1.91:1 | Landscape preferred |
| LinkedIn Profile Banner | 1584×396px | 4:1 | Background header image |
| Twitter/X Header | 1500×500px | 3:1 | Cover image |
| Blog Header | 1200×628px | 1.91:1 | Also works for Open Graph |
| YouTube Thumbnail | 1280×720px | 16:9 | High contrast for clickability |
| Facebook Ad | 1200×628px | 1.91:1 | Same as LinkedIn post |

---

## Prompt Structure Formula

A great AI image prompt has these components:

```
[SUBJECT] + [ACTION/POSE] + [SETTING/BACKGROUND] + [STYLE] + [LIGHTING] + [MOOD] + [TECHNICAL SPECS]
```

**Example:**
```
A confident professional in modern business casual clothing, standing in a minimalist office with natural light,
looking at camera with a warm smile, photorealistic photography style,
soft natural window lighting from the left, professional and approachable mood,
high resolution, 16:9 aspect ratio, sharp focus
```

---

## Prompt Templates by Category

### 1. Professional Portrait / Headshot Style
```
[Person description: gender-neutral if needed, professional appearance],
[specific clothing style matching brand],
[location: office / outdoor urban / studio background],
professional headshot photography,
[lighting: studio lighting / natural window light / golden hour],
[mood: confident / approachable / authoritative],
high resolution, sharp focus, clean background,
[brand colors if applicable] color palette
```

**Generator prompt:**
```
Create a DALL-E prompt for a professional portrait image for [BRAND NAME] in [NICHE].
The person should: [appearance guidelines without specific race/gender unless needed]
Setting: [SETTING]
Style: photorealistic, professional photography
Mood: [MOOD]
Must work as: [PLATFORM] image at [SIZE]
```

### 2. Lifestyle / Action Shot
```
[Scene description: person doing specific activity related to niche],
authentic candid photography style,
[setting: specific location type],
[time of day: morning light / golden hour / indoor artificial warm light],
[emotion: focused / joyful / determined / relaxed],
documentary photography style, high resolution
```

### 3. Conceptual / Abstract (for quotes, tips, ideas)
```
Abstract concept representing [TOPIC/THEME],
[style: geometric / watercolor / gradient / minimal line art],
color palette: [BRAND COLORS or descriptive colors like "deep navy and gold"],
[mood: sophisticated / energetic / calm],
suitable as social media background,
16:9 / 1:1 format [choose for platform],
no text, clean and modern
```

### 4. Infographic Background / Data Visualization
```
Clean minimal background for [TOPIC] infographic,
[style: flat design / light gradient / dark elegant],
color scheme: [BRAND COLORS],
subtle geometric patterns or lines as texture,
professional and modern,
high contrast areas for text overlay,
[platform] format
```

### 5. Product / Service Visual
```
[Product/service concept] displayed professionally,
[setting: on a surface / floating / in use / lifestyle context],
[photography style: product photography / lifestyle / editorial],
[background: white studio / contextual / branded colored],
professional lighting, high resolution, sharp details
```

### 6. Quote / Text-Background Image
```
Simple, elegant background suitable for text overlay,
[style: gradient / solid color with texture / subtle pattern / blurred photo background],
color: [BRAND COLORS],
mood: [inspirational / professional / energetic],
minimal visual noise,
[platform] format,
no people, no existing text
```

---

## Style Guide by Brand Personality

### Corporate / Professional Brand
```
Style keywords: clean, minimal, sophisticated, structured
Colors: navy, white, silver, deep green
Lighting: studio, natural diffused
Avoid: chaotic compositions, oversaturated colors, casual/playful elements
```

### Coach / Personal Brand (Warm & Approachable)
```
Style keywords: authentic, warm, real, human
Colors: warm tones, earth tones, soft gradients
Lighting: golden hour, natural window light
Avoid: overly corporate, cold blue tones, stock photo look
```

### Fitness / Health Brand
```
Style keywords: energetic, dynamic, powerful, clean
Colors: bold primary colors, black/white with accent color
Lighting: dramatic, high contrast, natural outdoor
Avoid: static poses, dull backgrounds, overly clinical
```

### Creative / Design Brand
```
Style keywords: artistic, bold, distinctive, expressive
Colors: brand-specific palette, can be unconventional
Lighting: dramatic, creative, stylized
Avoid: generic stock photo look, overly literal interpretations
```

### Food / Lifestyle Brand
```
Style keywords: appetizing, warm, inviting, authentic
Colors: warm golden tones, earthy, fresh natural colors
Lighting: natural top-down or 45-degree angle
Avoid: cold lighting, clinical presentation, artificial colors
```

---

## Batch Image Prompt Generator

For creating a week of content visuals at once:

**Prompt:**
```
Generate 7 AI image prompts for [BRAND NAME] in [NICHE] for a week of Instagram content.
Each prompt: [describe image type for that day's content topic]
Days: [list each day's content theme]
Style consistency: all images should feel cohesive using [BRAND COLORS] color palette
Include: platform specs (1080×1080), no text in images
Tool compatibility: optimized for DALL-E 3 / Midjourney v6 [choose]
```

---

## Quality Checklist

Before using an AI image:
- [ ] Does it match your brand's visual style?
- [ ] Is the lighting and mood appropriate for the platform?
- [ ] Are there any AI artifacts (distorted hands, weird text, odd backgrounds)?
- [ ] Does it need text overlay? Is there enough negative space?
- [ ] Is it appropriate for all audiences?
- [ ] Does it feel authentic, not stock-photo generic?
- [ ] Does it compress well at the required platform size?

---

## Use with ContentAI Suite

This skill works seamlessly with **[ContentAI Suite](https://contentai-suite.vercel.app)** — a free multi-agent marketing platform that generates professional content for any business in minutes.

→ **Try it free:** https://contentai-suite.vercel.app
