---
name: seedance
description: "Generate cinematic video prompts for Seedance 2.0 (ByteDance). Use
  when user asks for video prompts, Seedance prompts, AI video generation
  prompts, or anything related to Seedance 2.0 prompt crafting. Triggers on:
  seedance, video prompt, AI video, text to video prompt, seedance prompt."
---


# Seedance 2.0 Prompt Generator

Generate production-ready prompts for ByteDance's Seedance 2.0 AI video model.

## Prompt Architecture

Every prompt follows this strict order. Deviating causes drift.

```
Subject → Action → Camera → Style → Audio → Constraints
```

### 1. Subject (WHO/WHAT)
- One primary subject. Multiple subjects split model attention.
- Include: age/material, clothing, distinguishing features
- Example: "Wooden Koda creature with glowing orange eyes, green gems on head, purple cape"

### 2. Action (WHAT HAPPENS)
- Specific verb phrases, present tense
- Describe beat by beat for complex sequences
- One action per beat. Chain beats chronologically.
- Example: "walks to cliff edge, pauses, turns head slowly to camera, cape billowing"

### 3. Camera (HOW WE SEE IT)
- Shot size FIRST: wide / medium / close-up / extreme close-up
- Movement SECOND: dolly-in, dolly-out, track left/right, crane up/down, pan, tilt, handheld, gimbal, locked-off
- Angle: eye level, low angle, high angle, bird's eye, Dutch
- Lens feel: wide (24-28mm), normal (35-50mm), telephoto (85mm+)
- ONE verb per shot. Compound moves = separate beats: "Start: slow dolly-in. Then: gentle pan right for final 2s"

**Shot Cheat Sheet:**
| Shot | Use | Pair With |
|------|-----|-----------|
| Wide | Establish space/context | Slow dolly, locked-off |
| Medium | Subject + context, dialogue | Handheld (personal), gimbal (polished) |
| Close-up | Detail, emotion | Tiny push-in, avoid pans |
| Tracking | Movement, energy | Lateral follow, side profile |

### 4. Style (THE LOOK)
- ONE visual anchor > six adjectives
- Lighting: key light type, time of day, practical sources
- Color treatment: muted/saturated/monochrome/specific palette
- Texture: film grain, clean digital, anamorphic, etc.
- Reference format: "[film/artist/era] aesthetic"

### 5. Audio (WHAT WE HEAR)
- Seedance 2.0 generates dual-channel stereo audio
- Specify: background music genre, environmental sounds, dialogue/VO, silence
- Audio syncs to visual action automatically
- Example: "ambient wind, distant thunder, no music, footsteps on stone"

### 6. Constraints (GUARDRAILS)
- Ban list: no text overlays, no extra characters, no snap zooms, no watermarks
- Timing: hold frames, beat durations, total length (5s or 10s for testing, 15s max)
- Consistency: "maintain character identity throughout", "no morphing"
- Physics: "realistic cloth physics", "gravity-accurate"

## Reference System (@Tags)

When user provides images/videos, use @tags:
- `@Image1`, `@Image2`, etc. for uploaded images
- `@Video1`, `@Video2`, etc. for uploaded videos
- `@Audio1`, etc. for uploaded audio

**Usage patterns:**
- Character identity: "@Image1 is the main character"
- First/last frame: "@Image1 as first frame, @Image2 as last frame"
- Motion transfer: "@Image1 performs the dance from @Video1"
- Style reference: "match the color palette of @Image3"
- Multi-reference: up to 9 images + 3 videos + 3 audio clips

## Prompt Templates

### Cinematic Scene
```
[Scene type] style. [Subject with details]. [Action beat 1], [action beat 2], [action beat 3].
[Camera: shot size], [movement], [angle], [lens feel].
[Lighting description], [color treatment], [texture/grain].
[Audio: music/sfx/ambience].
[Constraints: bans, timing, consistency notes].
```

### Multi-Shot Narrative
```
Shot 1: [Wide/establishing]. [Scene description]. [Camera movement]. [Duration].
Shot 2: [Medium/close]. [Character action]. [Camera movement]. [Duration].
Shot 3: [Close-up/detail]. [Emotional beat]. [Camera movement]. [Duration].
[Overall style], [color grade], [audio design].
[Constraints].
```

### Action Sequence
```
[Genre] action sequence. [Setup description].
Beat 1: [Action], [camera follows with movement type].
Beat 2: [Reaction/counter], [cut to shot size], [slow motion if needed].
Beat 3: [Resolution], [camera pulls to reveal].
[Style: reference film/show]. [Audio: impact sounds, score].
[Constraints: physics accuracy, no artifacts].
```

## Negative Prompt Checklist (pick 3-5 per generation)

**Visual noise:** no text overlays, no watermarks, no floating UI, no lens flares
**Identity drift:** no extra characters, no crowd, no mirrors reflecting others
**Camera chaos:** no snap zooms, no whip pans, no Dutch angles, no jump cuts
**Body artifacts:** no extra fingers, no deformed hands, no warped objects, no melting edges
**Branding:** no logos, no labels, no recognizable brands
**Color:** no neon lighting, no heavy teal/orange, no cartoon saturation
**Environment:** no rain/fog/smoke unless stated, no confetti, no dust particles

## Advanced: Clean High-Motion Technique

Learned from real-world results. These techniques produce sharp, blur-free motion even at extreme speed.

### The Continuous Shot Lock
- Declare "single continuous shot" upfront — forces temporal coherence, prevents inter-scene interpolation artifacts
- The model treats the entire generation as one fluid motion path instead of stitched segments

### Physics-Motivated Camera
- Every camera move needs a VERB with physical motivation: dive, slingshot, whip, dart, blast
- Never say "dynamic camera" — say WHY the camera moves (following subject, reacting to explosion, releasing into reveal)
- Camera attached to subject ("lock-on," "staying glued") = subject stays sharp because relative motion is zero

### Environmental Anchoring
- Scatter static reference geometry throughout: walls, arches, furniture, hanging objects
- The model needs stable background to render motion AGAINST — parallax creates perceived speed without subject blur
- Static objects streaking past a centered subject = clean speed

### Scale Progression Arc
- Structure as Macro → Micro → Macro (wide establish → tight detail → wide reveal)
- Gives model clear resolution targets at each stage — doesn't try to render everything at once
- The "reveal" at the end (pulling wide after sustained close action) creates cinematic payoff

### Sensory Render Instructions (Not Mood Words)
- Replace adjectives with computable effects: "heat haze" not "hot," "grit snapping off ledge" not "dusty," "mist turning into rainbow" not "magical"
- Each detail should be something the model can physically simulate

### Rhythm Through Verbs
- Pacing lives in action chain length, not "hold for Xs" timers
- Quick beat: "snaps a last-inch swerve" (short clause = fast)
- Sustained beat: "threads through hanging laundry lines and open windows in one fluid line" (long clause = flowing)
- Climax: contrast — "sudden calm" after chaos = tension release

### Reference Prompt (Proven Clean High-Motion)
```
Speeder chase across a cliff city (single continuous shot)
From a monumental cliffside city carved into stone, the camera dives toward a tiny streak of light ripping along a narrow ledge-road. Lock-on: a speeder hugging the wall at insane speed. The camera slingshots ahead, whips back, then drops tight to the rear thrusters: heat haze, grit snapping off the ledge, warning lights flashing. A collapsing balcony rains debris; the rider snaps a last-inch swerve under a falling arch, then threads through hanging laundry lines and open windows in one fluid line. The camera darts through the same openings, staying glued to the motion. One final bend and sudden calm: the camera blasts outward into a reveal of the city opening onto a boundless waterfall-fed valley, mist turning into rainbow.
```

## Pro Tips

1. **High-res references** — 2K/4K input images = better output. Blurry in = blurry out
2. **Test at 5s first** — iterate fast, extend to 10-15s once the motion is right
3. **One change at a time** — don't rewrite the whole prompt on a miss, tweak one element
4. **Creativity/Consistency sliders** — 60% consistency / 40% creativity is the sweet spot
5. **Beat timing** — write "hold for 2s" or "pause 1s" to control pacing
6. **Compound camera = separate beats** — never jam two movements in one clause
7. **Style anchor > adjective soup** — "Blade Runner 2049 aesthetic" > "cinematic dark moody neon futuristic"
8. **Environmental audio** — even without dialogue, specify ambient sounds for immersion

## ⚠️ Content Policy Rules (CRITICAL)

Seedance is a **video diffusion model with no internet access**. It does not know:
- "Otherside" — means nothing to it
- "BAYC," "Koda," "Other Games" — proprietary names get flagged
- Gaming/metaverse/NFT terminology — triggers content moderation
- Crowd scenes — flagged automatically
- Any brand, game title, or IP name

**The rule: Never use brand names. Describe what you see, not what it's called.**

### Translation Layer — Concept → Visual Description

| What you mean | What to write in the prompt |
|---|---|
| Otherside world | "alien landscape with bioluminescent terrain, floating rock formations, purple and teal crystal growths, twin moons visible through violet sky" |
| Otherside biome | "ancient stone ruins overtaken by glowing fungal growth, rivers of liquid light flowing through cracked earth" |
| Otherside portal | "swirling circular energy vortex of purple and gold light, crackling at the edges, suspended in midair" |
| Koda character | "small wooden creature with bark-textured skin, glowing amber eyes in a dark hollow face, green teardrop gems across the top of its head, dark feathered collar, flowing purple cape, small dark armored clawed hands, chibi proportions" |
| Other Games event | "large gathering of stylized 3D avatar characters in a glowing arena, spotlights, festive atmosphere" (avoid "crowd" — use "scattered figures" or "a handful of characters") |
| Gaming/metaverse | Use: "virtual world," "digital realm," "fantastical landscape," "animated environment" |

### Banned Words (will trigger rejection)
- Otherside, Yuga, BAYC, Koda, ApeCoin, NFT, metaverse, web3, blockchain, cryptocurrency
- crowd, mob, large group, mass of people
- Any real brand name, game title, or IP

## Koda-Specific Prompts (Other Games IP)

When generating Koda content:
- **NEVER say "Koda"** — describe the character visually every time
- Use: "small wooden creature with bark-textured skin, glowing amber eyes in a dark hollow face, green teardrop gems across the top of its head, dark feathered collar, flowing purple cape, small dark armored clawed hands, chibi proportions"
- **NEVER say "Otherside"** — describe the environment visually
- Use: "alien landscape with bioluminescent terrain, floating rock formations, purple and teal crystal growths"
- Maintain character consistency across shots
- Always provide Honey B's Koda image as @Image1 for I2V generations (best result)
- Test at 5s first to confirm character renders correctly before extending

## Platform Access
- Jimeng AI (即梦): jimeng.jianying.com → Video Generation → Seedance 2.0
- Doubao App: dialogue box → Seedance 2.0 → select 2.0 model
- Volcano Engine: experience center → Doubao-Seedance-2.0

## When User Asks for a Prompt

1. Ask what scene/concept they want (or use their description)
2. Determine: T2V (text only), I2V (image + text), or R2V (multi-reference)
3. Pick the right template
4. Fill in all 6 layers (subject → constraints)
5. Add 3-5 relevant negative constraints
6. Output the final prompt ready to paste
7. Suggest aspect ratio (16:9 cinematic, 9:16 social, 1:1 square)
8. Suggest starting duration (5s test → extend)
