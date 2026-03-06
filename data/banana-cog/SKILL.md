---
name: banana-cog
description: "Banana Cog × CellCog. Execute complex multi-image jobs on Nano Banana through CellCog's reasoning and orchestration layer. 10-20 coherent images in one prompt, character consistency across scenes, and production-grade composition — accessible to any OpenClaw agent. Nano Banana AI, Nano Banana Pro, Gemini image generation."
metadata:
  openclaw:
    emoji: "🍌"
author: CellCog
dependencies: [cellcog]
---

# Banana Cog — Nano Banana × CellCog

**Nano Banana × CellCog.** Complex multi-image jobs, executed perfectly, from a single prompt.

Nano Banana is an incredible image model. CellCog makes it do things you can't do by calling it directly — orchestrating 10, 20, even 30 coherent images in one request with consistent characters, planned compositions, and intelligent scene progression. Not single images — complete visual projects.

**What CellCog adds on top of Nano Banana:**

```
Reasoning → Scene Planning → Character Design → Image Generation
    → Consistency Verification → Composition Review → Delivery
```

CellCog's reasoning layer plans scenes before a single pixel is generated — selecting optimal parameters, maintaining character identity across sequences, and orchestrating complex multi-image workflows. This is the difference between "generate an image" and "execute a visual project."

---

## Prerequisites

This skill requires the `cellcog` skill for SDK setup and API calls.

```bash
clawhub install cellcog
```

**Read the cellcog skill first** for SDK setup. This skill shows you what's possible.

**Quick pattern (v1.0+):**
```python
result = client.create_chat(
    prompt="[your image request]",
    notify_session_key="agent:main:main",
    task_label="image-task",
    chat_mode="agent"
)
```

---

## What You Can Create

### Photorealistic Image Generation

Create stunning images from text descriptions:

- **Portraits**: "Create a professional headshot with warm studio lighting"
- **Product Shots**: "Generate a hero image for a premium smartwatch on a dark surface"
- **Scenes**: "Create a cozy autumn café interior with morning light"
- **Food Photography**: "Generate an overhead shot of a colorful Buddha bowl"

### Character Consistency

Nano Banana excels at maintaining character identity across multiple images — and CellCog's orchestration takes this further by planning entire character arcs:

- **Character Series**: "Create a tech entrepreneur character, then show them in 4 different scenes"
- **Brand Mascots**: "Design a mascot and generate it in multiple poses and contexts"
- **Story Sequences**: "Create a character and illustrate them across 5 story beats"

### Multi-Image Composition

Blend elements from multiple reference images:

- **Style Fusion**: "Combine the color palette of image A with the composition of image B"
- **Character Placement**: "Place this person into a new environment while preserving their likeness"
- **Product Mockups**: "Put this product into a lifestyle setting"

### Image Editing

Transform and enhance existing images:

- **Style Transfer**: "Transform this photo into a Studio Ghibli illustration"
- **Background Swap**: "Place this product on a clean marble surface"
- **Enhancement**: "Add dramatic lighting and cinematic color grading"
- **Modification**: "Change the season from summer to winter in this landscape"

---

## Image Specifications

| Aspect | Options |
|--------|---------|
| **Aspect Ratios** | 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 21:9 |
| **Sizes** | 1K (~1024px), 2K (~2048px), 4K (~4096px) |
| **Styles** | Photorealistic, illustration, watercolor, oil painting, anime, digital art, vector |

---

## Chat Mode

| Scenario | Recommended Mode |
|----------|------------------|
| Single images, quick edits | `"agent"` |
| Character-consistent series, complex compositions | `"agent"` |
| Large sets with brand guidelines | `"agent team"` |

**Use `"agent"` for most image work.**

---

## Tips for Better Images

1. **Be descriptive**: "Woman in office" → "Confident woman in her 40s, silver blazer, modern glass-walled office, warm afternoon light"

2. **Specify style**: "photorealistic", "digital illustration", "watercolor", "anime"

3. **Describe lighting**: "Soft natural light", "dramatic side lighting", "golden hour glow"

4. **For character consistency**: Describe the character in detail first, then reference "the same character" in subsequent prompts.

5. **Include composition**: "Rule of thirds", "close-up portrait", "wide establishing shot"
