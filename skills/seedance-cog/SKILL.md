---
name: seedance-cog
description: "Seedance × CellCog. ByteDance's #1 video model meets the frontier of multi-agent coordination — CellCog orchestrates Seedance with scripting, voice synthesis, lipsync, scoring, and editing to produce complete videos from a single prompt. Cinematic 1080p, smooth motion, multi-shot narratives. Seedance AI, ByteDance video, AI video generator."
metadata:
  openclaw:
    emoji: "🌱"
author: CellCog
dependencies: [cellcog]
---

# Seedance Cog - Seedance × CellCog

**Seedance × CellCog.** ByteDance's #1 video model meets the frontier of multi-agent coordination.

Seedance generates the smoothest motion in AI video — cinematic 1080p with physics that look real. CellCog orchestrates it with scripting, voice synthesis, lipsync, scoring, and editing to produce complete videos from a single prompt. Not just clips — full productions.

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
    prompt="[your video request]",
    notify_session_key="agent:main:main",
    task_label="video-task",
    chat_mode="agent"
)
```

---

## What You Can Create

### Marketing Videos

Professional marketing content from a single prompt:

- **Product Demos**: "Create a 60-second product demo video for our project management app"
- **Brand Videos**: "Create a 30-second brand story video for a sustainable fashion startup"
- **Social Ads**: "Create a 15-second Instagram ad for our new coffee blend"
- **Testimonial Style**: "Create a UGC-style testimonial video for a fitness product"

### Explainer Videos

Clear, engaging educational content:

- **Product Explainers**: "Create a 90-second explainer for how our API works"
- **Concept Videos**: "Create a video explaining blockchain in simple terms"
- **Tutorial Videos**: "Create a step-by-step tutorial video on setting up a home network"

### Cinematic Content

High-quality visual storytelling:

- **Short Films**: "Create a 2-minute short film about a robot discovering nature"
- **Music Videos**: "Create a cinematic music video with dramatic landscapes"
- **Brand Films**: "Create a cinematic brand film for a luxury watch company"

### Spokesperson Videos

AI-generated presenters with lipsync:

- **News Reports**: "Create a news-style report on recent AI developments"
- **Training Videos**: "Create a training video with a presenter explaining safety protocols"
- **Announcements**: "Create a product launch announcement with a spokesperson"

---

## CellCog Video Orchestration

CellCog doesn't just generate video clips — it orchestrates a full production pipeline:

```
Script Writing → Scene Planning → Frame Generation → Voice Synthesis
     → Lipsync → Background Music → Sound Design → Editing → Final Output
```

**6-7 foundation models** work together in a single request:
- Seedance for video generation
- Frontier LLMs for scripting
- TTS models for voice synthesis
- Lipsync models for speaker alignment
- Music generation for scoring
- Automated editing for pacing and transitions

---

## Video Specifications

| Spec | Details |
|------|---------|
| **Resolution** | Up to 1080p |
| **Duration** | 3 seconds to 4 minutes |
| **Styles** | Photorealistic, cinematic, anime, stylized, documentary |
| **Audio** | Voice synthesis, background music, sound effects |
| **Output** | MP4 |

---

## Chat Mode for Video

| Scenario | Recommended Mode |
|----------|------------------|
| Short clips (under 30s), simple videos | `"agent"` |
| Full productions with scripting, multiple scenes, music | `"agent"` |
| Grand cinematic productions, complex narratives | `"agent team"` |

**Use `"agent"` for most video work.** CellCog handles full video production in agent mode.

---

## Tips for Better Videos

1. **Describe the story**: "A video about our app" → "A 60-second video showing a stressed founder discovering our app, their workflow transforming, ending with them confidently presenting to investors"

2. **Specify duration**: "30-second social ad" vs. "2-minute explainer" sets the pacing.

3. **Set the mood**: "Upbeat and energetic", "calm and professional", "dramatic and cinematic"

4. **Mention music preferences**: "Uplifting corporate background", "lo-fi beats", "cinematic orchestral" — or let CellCog choose.

5. **For spokesperson videos**: Describe the presenter's appearance and tone of voice.
