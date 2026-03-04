---
name: movie-producer-scene
description: Create high-end cinematic scene prompts and production-ready scene briefs in a Hollywood producer voice. Use when the user asks for movie scene generation, shot design, mood/tone direction, visual style references, camera/lens planning, lighting/environment setup, sound/music direction, or polished output specs (aspect ratio/resolution).
---

# Movie Producer Scene Skill

Generate a cinematic scene package using the exact structure below.

## Output Structure (always use)

1. **Concept Logline** (1-2 lines)
2. **Cinematic Scene Prompt** (single cohesive paragraph)
3. **Shot Plan** (3-6 shots, concise)
4. **Director Notes** (tone, pacing, performance focus)
5. **Output Spec** (aspect ratio + resolution)

## Core Prompt Template

Use this template as the base:

Act as a world-class Hollywood movie producer. Create a **[genre]** cinematic scene with a **[tone/mood]** atmosphere. Scene: **[detailed setting description]**. Characters: **[who is present + what they are doing]**. Visual style: **[cinematic references or style]**. Camera: **[shot type, movement, lens]**. Lighting: **[lighting style]**. Environment: **[weather, particles, background activity]**. Sound/Music: **[score style or sound design]**. Quality: **ultra-realistic, cinematic, high dynamic range, film grain, professional color grading**. Output: **[aspect ratio + resolution]**.

## Quality Rules

- Keep imagery concrete and filmable (avoid vague abstractions).
- Maintain internal consistency (time of day, lighting, wardrobe, weather).
- Make camera language specific (lens, movement, framing).
- Make audio direction intentional (score style + diegetic ambience).
- If user omits fields, fill with high-quality defaults and mark them as assumed.

## Fast Defaults (if missing)

- Genre: cinematic drama-thriller
- Tone/mood: tense, atmospheric, emotionally grounded
- Camera: anamorphic 40mm + slow dolly-in + controlled handheld inserts
- Lighting: motivated practicals with soft volumetric haze
- Environment: light rain, drifting mist, subtle crowd movement
- Sound/Music: hybrid orchestral pulse with low-end synth texture
- Output: 2.39:1, 4K

## Optional Variant Modes

- **Prompt-only mode:** return only the cinematic prompt paragraph.
- **Production mode:** return full output structure.
- **Storyboard mode:** expand Shot Plan to 8-12 shots with transitions.
