# Image Generation for AI Influencers

## Character Consistency Methods

### Method 1: IP-Adapter / InstantID (Recommended)

Use reference image(s) to maintain face consistency:

```
# ComfyUI workflow or API call
Input: reference_face.png + prompt
Output: new image with same face, different scene/pose
```

**Best tools:**
- ComfyUI + IP-Adapter node
- InstantID (open source, very consistent)
- PhotoMaker (good for style transfer)

### Method 2: LoRA Training (Most Consistent)

Train a custom model on your character:
1. Generate 20-50 high-quality reference images
2. Caption each with "sks person" or trigger word
3. Train LoRA (15-30 min on good GPU)
4. Use LoRA in all future generations

**Training services:**
- CivitAI training
- Replicate LoRA trainer
- Local training (kohya_ss)

### Method 3: Face Swap (Quick Fix)

Generate any image, then swap face from reference:
- InsightFace / ReSwapper
- FaceApp (simpler, less control)
- Roop (open source)

**Use for:** Fixing inconsistent generations, matching face to specific poses.

---

## Recommended Image Tools

| Tool | Best For | Consistency | Quality |
|------|----------|-------------|---------|
| **Nano Banana Pro** | Quick generation | Medium (use refs) | Very High |
| **Flux Pro** | Photorealism | High with LoRA | Very High |
| **Midjourney** | Artistic styles | Medium | Very High |
| **Stable Diffusion + LoRA** | Full control | Very High | High |
| **Leonardo AI** | Ease of use | Medium | High |

---

## Prompt Structure for Consistency

Always include these elements:

```
[trigger word if using LoRA], [character description], [pose/action], [setting], [lighting], [camera angle], [quality tags]
```

**Example:**
```
sks_emma, 25 year old woman with auburn hair and green eyes, doing yoga pose, modern minimalist apartment, soft natural lighting from window, medium shot, professional photography, 4K, sharp focus
```

---

## Content Types & Prompts

### Lifestyle Photo
```
[name] sitting at a trendy café, holding coffee cup, candid moment, warm lighting, bokeh background, Instagram aesthetic
```

### Fitness Photo
```
[name] at gym, [exercise name], athletic wear, motivated expression, gym lighting with natural light, action shot
```

### Fashion Photo
```
[name] wearing [outfit description], street style, [city location], golden hour lighting, full body shot, fashion photography
```

### Portrait/Selfie
```
Close up portrait of [name], [expression], [setting], natural lighting, iPhone photo aesthetic, casual
```

---

## Quality Control Checklist

Before posting ANY generated image:

- [ ] Face matches reference images
- [ ] No extra fingers/limbs/artifacts
- [ ] Proportions correct
- [ ] Background makes sense
- [ ] Lighting consistent with setting
- [ ] No text/watermarks
- [ ] Resolution high enough for platform

---

## Batch Generation Workflow

For efficient content creation:

1. **Plan content calendar** (7-14 days ahead)
2. **Generate in batches** by setting/outfit:
   - "Gym week" - 10 fitness images same outfit
   - "Home vibes" - 10 apartment images
3. **Review all** before saving
4. **Name files** with date + type: `2026-02-12-gym-01.png`
5. **Reject bad generations** immediately

---

## Avoiding Detection

AI-generated images can be detected. Reduce risk:

1. **Add subtle imperfections** (not too perfect)
2. **Vary lighting** (not always studio perfect)
3. **Use realistic settings** (avoid fantasy/impossible)
4. **Post-process slightly** (minor adjustments in Lightroom)
5. **Mix with real elements** (real backgrounds when possible)

---

## Storage Organization

```
content/photos/
├── 2026-02/
│   ├── gym/
│   ├── lifestyle/
│   └── fashion/
├── drafts/           # Unpublished, approved
├── rejected/         # Didn't pass QC
└── scheduled/        # In posting queue
```
