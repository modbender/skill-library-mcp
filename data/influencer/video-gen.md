# Video Generation for AI Influencers

## Video Types & Methods

| Content Type | Best Method | Difficulty |
|--------------|-------------|------------|
| Talking head | HeyGen / D-ID + voice clone | Easy |
| Lifestyle b-roll | Runway / Kling / Pika | Medium |
| Full body motion | Kling / Gen-3 Alpha | Hard |
| Tutorial/demo | Screen + AI voiceover | Easy |
| Stories/Reels | Image slideshow + music | Very Easy |

---

## Recommended Video Tools

### Talking Head / Lip Sync
| Tool | Quality | Pricing | Notes |
|------|---------|---------|-------|
| **HeyGen** | Excellent | $$$ | Best lip sync, many features |
| **D-ID** | Good | $$ | Simple, fast |
| **Synthesia** | Excellent | $$$ | Enterprise-focused |
| **SyncLabs** | Good | $ | API-first, cheaper |

### AI Video Generation
| Tool | Quality | Consistency | Duration |
|------|---------|-------------|----------|
| **Kling** | Very High | Good | 5-10 sec |
| **Runway Gen-3 Alpha** | Excellent | Medium | 4-16 sec |
| **Pika 2.1** | Good | Medium | 4 sec |
| **Hailuo AI** | Very High | Good | 6 sec |
| **Google Veo** | Excellent | Good | Variable |
| **Luma Dream Machine** | Good | Medium | 5 sec |

---

## Talking Head Video Workflow

1. **Write script** matching persona voice
2. **Generate audio** with cloned voice (ElevenLabs)
3. **Select reference image** (front-facing, neutral)
4. **Upload to HeyGen/D-ID** with audio
5. **Generate video**
6. **Add captions** (CapCut or built-in)
7. **Export** at platform specs

**Script length guide:**
- TikTok/Reels: 15-60 seconds
- YouTube Shorts: 30-60 seconds
- YouTube long-form: 5-15 minutes

---

## Lifestyle Video Workflow

For b-roll and atmospheric content:

1. **Generate multiple still images** of the persona
2. **Animate with Runway/Kling:**
   - Image-to-video mode
   - Simple motion (hair moving, slight head turn)
3. **Combine clips** in CapCut/Premiere
4. **Add music** (royalty-free)
5. **Add captions** if needed

**Prompt tips for video gen:**
```
[character from image], subtle movement, breathing, slight head turn, cinematic, natural lighting, 4K
```

---

## Character Consistency in Video

The hardest part. Strategies:

### Option 1: Talking Head Only
Use same reference image for all HeyGen/D-ID videos. Face never changes. Most consistent.

### Option 2: Limited Motion
Generate static images, add only subtle animation (Ken Burns effect, hair movement). Character stays recognizable.

### Option 3: LoRA-based Generation
Train LoRA on character → use in video model that supports LoRA (limited options).

### Option 4: Face Swap Post-Production
Generate any video → swap face with reference → more work but flexible.

---

## Platform Specs

| Platform | Aspect | Max Duration | Optimal |
|----------|--------|--------------|---------|
| TikTok | 9:16 | 10 min | 15-60 sec |
| IG Reels | 9:16 | 90 sec | 15-30 sec |
| IG Stories | 9:16 | 60 sec | 15 sec |
| YouTube Shorts | 9:16 | 60 sec | 30-60 sec |
| YouTube | 16:9 | 12 hours | 8-15 min |

---

## Audio for Videos

### Voice Cloning (ElevenLabs)
1. Record 1-3 min of clean audio (any voice that fits persona)
2. Upload to ElevenLabs for cloning
3. Use cloned voice for all content
4. Save voice_id in tools.md

### Music
- Epidemic Sound (paid, unlimited)
- Artlist (paid, high quality)
- YouTube Audio Library (free)
- TikTok built-in sounds (for TikTok only)

### Sound Effects
- Freesound.org (free)
- Mixkit (free)

---

## Batch Video Production

Efficient workflow for multiple videos:

1. **Script batch** — write 5-10 scripts at once
2. **Audio batch** — generate all voiceovers
3. **Video batch** — generate all talking heads
4. **Edit batch** — add captions, music
5. **Schedule** — queue across platforms

---

## Quality Checklist

Before posting ANY video:

- [ ] Lip sync matches audio
- [ ] Face consistent with brand
- [ ] No glitches/artifacts
- [ ] Audio clear, good levels
- [ ] Captions accurate (if included)
- [ ] Correct aspect ratio for platform
- [ ] Hook in first 3 seconds

---

## Avoiding Detection

1. **Vary content types** — don't only post AI talking heads
2. **Add real footage** — b-roll of hands, products, environments
3. **Imperfect audio** — slight room tone, not too clean
4. **Natural mistakes** — small pauses, filler words in script
5. **Behind the scenes** — generated "candid" content
