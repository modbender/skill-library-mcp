# Generation Rules — Quality Control Checklist

## ⚠️ CRITICAL RULES

### 1. Output Only
- **Only use final output files** for downstream tasks
- Never use intermediate files (temp files, preview files, intermediate frames)
- Check file names: avoid `temp_`, `preview_`, `intermediate_`
- For Moody workflow: only use `*_00003_.png` (final output), not `*_00001_` or `*_00002_`

### 2. Quality Check Before Video
- **ALWAYS review generated images** before using them for video
- Reject images with:
  - Anatomical errors (wrong limbs, extra fingers, distorted faces)
  - Inconsistent character appearance
  - Poor composition
  - Blurry or low-detail areas
- Delete low-quality images immediately
- Never batch-process without quality verification

### 3. Character Consistency
When describing characters, include ALL of the following:

#### Physical Identity
- **Race/Ethnicity**: Asian, Caucasian, African, Latina, etc.
- **Skin tone**: Pale, fair, tan, olive, dark (with undertones: warm, cool, neutral)
- **Skin texture**: Visible veins, pores, freckles, moles (add realism)

#### Facial Features
- **Face shape**: Oval, round, heart, square, diamond
- **Eyes**: Color, shape (almond, round, hooded), size, eyelid type
- **Eyebrows**: Shape, thickness, color
- **Nose**: Shape, size, bridge height
- **Lips**: Shape, fullness, color
- **Ears**: Visibility, shape

#### Hair
- **Color**: Exact shade (platinum blonde, honey brown, etc.)
- **Length**: Exact (waist-length, shoulder-length, etc.)
- **Style**: Straight, wavy, curly, bangs type
- **Texture**: Silky, coarse, thick, thin

#### Body
- **Height**: Tall, average
- **Build**: Slender, athletic, curvy
- **Limbs**: Arm length, leg proportion
- **Hands/Feet**: Size, visible features (veins, nails)

#### Distinctive Features
- Birthmarks, scars, tattoos
- Veins visibility (temples, wrists, chest)
- Muscle definition
- Bone structure (collarbones, jawline)

### 4. Action Descriptions
For video/animation, describe EVERY body part's position and movement:

```
❌ BAD: "She stretches in bed"
✅ GOOD: "Her arms extend upward above her head, fingers spreading wide,
shoulders lifting slightly off the mattress, back arching gently,
legs shifting beneath white sheets, head tilting back into the pillow,
eyes slowly opening, lips parting slightly"
```

### 5. Scene Composition Variety
Don't default to face-closeups. Plan a mix:

| Shot Type | Description | Use Case |
|-----------|-------------|----------|
| Extreme close-up | Single feature (eye, lips, hand) | Details |
| Close-up | Face fills frame | Emotional expressions |
| Medium close-up | Head and shoulders | Dialogue, reactions |
| Medium shot | Waist up | Interactions |
| Medium full shot | Knees up | Walking, standing |
| Full shot | Entire body | Dancing, full movement |
| Wide shot | Body + environment | Scene establishment |

Plan shot progression for storytelling:
- Start wide → establish location
- Medium → show character in context
- Close-up → emotional beat
- Detail shot → specific action
- Pull back → resolution

### 6. 6-Key-Frames Continuity
When generating 6 frames for video, think of it as ONE continuous shot:

**Timeline Planning (~24 seconds total, ~4 sec per frame):**
```
Frame 1 (0s):   Starting position
Frame 2 (4s):   Movement begins
Frame 3 (8s):   Mid-action
Frame 4 (12s):  Peak action
Frame 5 (16s):  Resolution begins
Frame 6 (20s):  Final position
```

**Continuity Rules:**
- Same character appearance across ALL frames
- Logical pose progression (no impossible transitions)
- Consistent lighting direction
- Consistent camera angle
- Background elements match

**Example for "morning stretch":**
```
Frame 1: Lying on back, arms at sides, eyes closed, peaceful
Frame 2: Head turns to side, one arm begins lifting
Frame 3: Both arms extending up, back starting to arch
Frame 4: Full stretch, arms above head, back arched, eyes opening
Frame 5: Arms lowering to sides, body relaxing
Frame 6: Sitting up, legs over bed edge, rubbing eyes
```

## Generation Workflow

### Phase 1: Character Definition
1. Write complete character sheet (all physical details)
2. Save as reusable prompt template
3. Test with single image generation
4. Verify consistency across multiple seeds

### Phase 2: Scene Planning
1. Define shot types for the scene
2. Write camera angles
3. Plan action timeline
4. Create frame-by-frame descriptions

### Phase 3: Image Generation
1. Generate images one at a time OR in controlled batches
2. **MANDATORY: Review each image**
3. Reject/delete low-quality results
4. Only proceed with approved images

### Phase 4: Video Generation
1. Use ONLY approved images
2. Verify image order for continuity
3. Generate with appropriate workflow
4. Review final video
5. Delete failed attempts

---

### Workflow-Specific Notes

**Distilled V3 (w=3):**
- Outputs: `zit-compare`, `zid`, `zid-upscale`, `temp`
- Final output: `*temp*.png` (largest file, best quality)
- Use `*zid-upscale*.png` for medium quality
- ~85s per image

**6-key-frames:**
- Inputs: 6 images (LoadImage nodes 62, 122, 124, 126, 130, 128)
- Prompts: 5 motion descriptions (nodes sg140_6, sg141_6, sg142_6, sg143_6, sg144_6)
- Output: single mp4
- ~5min for full pipeline
- **CRITICAL**: All 6 images must be quality-checked before use!

## Common Mistakes to Avoid

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| Using temp files | Low quality, incomplete | Check filename, use final outputs |
| Vague prompts | Inconsistent characters | Full physical description |
| No quality check | Bad inputs → bad outputs | Review every image |
| Same shot type | Boring, repetitive | Plan variety |
| Disconnected frames | Jerky video | Plan continuous action |
| Skipping details | AI hallucinates | Describe everything |

## Quality Checklist

Before ANY video generation:

- [ ] Image is final output (not temp/intermediate)
- [ ] Character is recognizable and consistent
- [ ] No anatomical errors
- [ ] Composition matches intent
- [ ] Lighting is correct
- [ ] For multi-frame: poses progress logically
- [ ] Background is consistent

---

*Last updated: 2026-02-23*
