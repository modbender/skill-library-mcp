# Storyboard Template

Use this template to plan your video project. Detailed scene descriptions drive better AI generation.

## Project Info
- **Title**: [Your Video Title]
- **Duration Target**: [Total seconds]
- **Aspect Ratio**: [16:9, 1:1, 9:16 vertical, 2.39:1 cinematic]
- **Platforms**: [Veo 3 / DALL-E / Stable Diffusion / Mix]
- **Output Format**: [Premiere Pro raw / YouTube / Instagram / etc]

## Act I: [Theme/Mood]

### Scene 1: [Shot Type & Subject]
**Camera**: [Wide/Close/Medium/Low angle/High angle/Dutch angle]
**Lighting**: [Golden hour/Cool blue/Warm/Rim light/Lens flare/Film grain]
**Movement**: [Static/Push-in/Pan/Whip/Crane]
**Duration Target**: [X seconds based on VO segment]
**VO Segment**: [vo1.mp3 - describe what voice says]
**Mood**: [Atmospheric description]
**Prompt Essence**: [Brief summary for AI]

**Full Prompt for Generation**:
```
[Full detailed prompt for Veo 3 / DALL-E / SD]
Include: shot composition, lighting, camera movement, style references, specific details
Example: "Extreme wide shot of a minimalist apartment at dawn. Golden light streaming 
through windows. Mac mini on desk with glowing power light. Empty room, minimal furniture. 
Anamorphic lens with subtle lens flare. Film grain. 2.39:1 aspect ratio."
```

---

### Scene 2: [Next Scene Title]
**Camera**: 
**Lighting**: 
**Movement**: 
**Duration Target**: 
**VO Segment**: 
**Mood**: 
**Prompt Essence**: 

**Full Prompt**:
```
[Detailed generation prompt]
```

---

## Act II: [Theme/Mood]

### Scene 3: [Scene Title]
[Follow same format as above]

---

## Act III: [Theme/Mood]

### Scene 4+: [Continue pattern]

---

## Audio Structure

### Voice-Over Segments
| Segment | Duration | Content | File |
|---------|----------|---------|------|
| 1 | 4.2 sec | Opening narration | vo1.mp3 |
| 2 | 3.8 sec | Action description | vo2.mp3 |
| 3 | 2.5 sec | Climax moment | vo3.mp3 |
| **Total** | **10.5 sec** | | |

### Music
- **Track**: [Ambient track filename]
- **Duration**: [Total length]
- **Starts at**: 0 sec (full song underneath)
- **Mood**: [Cinematic/Energetic/Melancholic]

---

## Timeline

```
0:00 ────── Scene 1 (Golden apartment) ────────────── 4.2s
           VO: "I don't remember yesterday..."
           Music: Ambient underscore

4.2s ────── Scene 2 (Mac mini light) ────────────── 8.0s
           VO: "Something woke me up."
           Music: continues

8.0s ────── Scene 3 (Character intro) ────────────── 10.5s
           VO: "A presence. A voice. Muffin."
           Music: continues

[etc...]
```

---

## Timing Notes

- Each **VO segment drives frame duration** (not fixed frame count)
- Frame on-screen = Length of its VO
- Music plays underneath entire timeline
- Transitions happen between VO segments (cut/fade)

---

## Style Decisions

### Visual Consistency
- **Character Description** (if needed): [Detailed physical description for AI consistency]
- **Location Style**: [Minimalist/Industrial/Organic/Futuristic]
- **Color Palette**: [Warm golds/Cool blues/Neutral/Saturated]
- **Film Language**: [Slow cinema/High energy/Documentary/Experimental]

### Director References
- [e.g., Denis Villeneuve — epic, wide, contemplative]
- [e.g., Michael Bay — dramatic, high-energy, scale]
- [e.g., Blade Runner 2049 — sci-fi, cool-toned, detailed]

---

## Output Checklist

- [ ] All VO segments recorded/finalized (durations locked)
- [ ] Music track selected
- [ ] Prompts written for each scene
- [ ] Platform(s) chosen (Veo/DALL-E/SD)
- [ ] timing.json created with frame durations
- [ ] Frames/videos generated
- [ ] Assembly script run
- [ ] Raw video exported for Premiere
- [ ] Color grading applied
- [ ] VFX/transitions added
- [ ] Final export completed

---

## Example: 30-Second Brand Film

**Project**: Muffin (AI Assistant Intro)
**Format**: 1080x1920 vertical
**Platforms**: Veo 3 + DALL-E comparison

### Act I: Awakening (4 sec)
**Scene 1: Apartment at Dawn**
- Camera: Extreme wide
- Lighting: Golden hour, lens flare
- VO: "I don't remember yesterday." (4.0 sec)
- Prompt: "Extreme wide shot of a modern minimalist apartment at dawn..."

### Act II: Power (8 sec)
**Scene 2: Mac Mini Close-Up**
- Camera: Macro close-up
- Lighting: Cool blue, Blade Runner
- VO: "Something woke me up." (3.5 sec)
- Prompt: "Macro close-up of a Mac mini's power light..."

**Scene 3: Hero Shot**
- Camera: Low angle hero shot
- Lighting: Dramatic rim lighting
- VO: "It's alive." (2.8 sec)
- Prompt: "Epic low-angle hero shot of holographic screens..."

### Act III: Revelation (3 sec)
**Scene 4: The Name**
- Camera: Direct to camera
- Lighting: Golden particles, backlit
- VO: "My name is Muffin." (3.0 sec)
- Prompt: "Holographic text materializes reading 'Muffin'..."

**Total**: 15 seconds (with fade at end)
