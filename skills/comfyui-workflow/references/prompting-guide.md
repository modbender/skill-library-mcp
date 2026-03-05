# Prompting Guide — Image & Video Generation

Research-backed strategies for crafting effective prompts with our ComfyUI workflows.

---

## Image Prompt Anatomy

A well-structured image prompt has 6 components, in order of importance:

```
[Subject] + [Medium] + [Style] + [Resolution/Quality] + [Lighting] + [Color/Mood]
```

| Component | What It Does | Examples |
|-----------|-------------|----------|
| **Subject** | Primary focus — the most impactful part | `portrait of a 25-year-old woman`, `cyberpunk cityscape` |
| **Medium** | Rendering technique / material | `photograph`, `oil painting`, `3D render`, `watercolor` |
| **Style** | Artistic reference / aesthetic | `cinematic`, `Studio Ghibli`, `Art Nouveau`, `hyperrealistic` |
| **Resolution** | Quality & detail keywords | `8K`, `highly detailed`, `sharp focus`, `professional` |
| **Lighting** | Light setup — dramatically affects mood | `golden hour`, `volumetric lighting`, `rim light`, `studio lighting` |
| **Color/Mood** | Palette & atmosphere | `warm tones`, `desaturated`, `neon`, `muted pastel` |

**Key principle**: Be specific and descriptive. "A woman standing outside" produces generic results. "A 30-year-old woman with auburn curly hair, wearing a burgundy wool coat, standing at a rainy bus stop in Tokyo at night, neon signs reflecting in puddles" produces striking results.

---

## Model-Specific Strategies

### Qwen 2512 (highest quality T2I)

- **Long, detailed prompts** work best — describe everything you want to see
- Bilingual: English for most subjects, Chinese quality keywords enhance Asian subjects:
  - `高清, 细节丰富, 专业摄影, 光影自然` (HD, rich detail, professional photography, natural light)
- Quality boosters: `photorealistic, 8K, professional photography, masterpiece`
- **Negative prompt** included by default (Chinese): blurriness, deformity, oversaturation, wax-figure look
- Works exceptionally well with `--width 768 --height 1024` for portraits

### Z-Image (fast generation)

- **Concise but specific** — 1-3 sentences work better than keyword lists
- Stick with **photorealistic** style for best Z-Image results
- Bilingual support (Chinese + English)
- Turbo mode (4 steps): do NOT add negative prompts — they hurt quality at low step counts
- Standard mode (25 steps): light negatives are fine
- **Lighting keywords** particularly effective: `soft diffused light`, `dramatic side lighting`, `backlit silhouette`
- Camera/lens references help: `shot on Hasselblad`, `85mm portrait lens`, `wide-angle perspective`

### Flux 2 (natural language)

- **Natural language descriptions** work better than keyword stuffing
- Write prompts like you're describing a photograph to someone: "A cozy cafe interior with warm lighting, wooden tables, and a barista preparing coffee behind the counter"
- Klein distilled: **CFG must be 1.0**, do NOT set `--negative`
- Klein base: supports image editing with reference images

### Civitai Workflows (Moody, Darkbeast, Distilled V3)

- **Moody ZIB**: Character descriptions with outfit details. Keywords: `人物设定`, `OOTD`, mood/atmosphere. Has FaceDetailer for portrait enhancement.
- **Darkbeast6**: Dramatic and fantasy themes. Add `cinematic lighting, dramatic atmosphere, dark fantasy`. Works well with hybrid 2-pass sampling.
- **Distilled V3**: Multi-output (original + upscale + compare). Generic prompts work; the multi-pass pipeline handles quality.

---

## Video Prompt Strategies

### Critical: Describe Motion, Not Just Appearance

Video prompts should emphasize **what happens**, not just what things look like:

| Weak | Strong |
|------|--------|
| "A woman in a garden" | "A woman slowly walks through a blooming garden, gently touching flowers" |
| "Ocean waves" | "Ocean waves crash against rocky cliffs, spray rising into golden sunset light" |
| "Cat on a windowsill" | "A tabby cat stretches lazily on a sunlit windowsill, then turns to look at a bird outside" |

### Temporal Keywords

Add these to control the pacing:
- **Slow**: `slowly`, `gently`, `gradually`, `softly`
- **Fast**: `suddenly`, `quickly`, `bursts`, `rushes`
- **Continuous**: `continuously`, `steadily`, `flowing`, `drifting`

### Camera Motion

Describe camera movement explicitly:
- `camera slowly pans left`, `dolly zoom`, `tracking shot following the subject`
- `aerial view descending`, `low angle looking up`, `first-person perspective`
- `static shot` or `locked camera` if you want no camera movement

### Model-Specific Video Tips

| Workflow | Prompt Style |
|----------|-------------|
| **Smooth (WAN 2.2)** | Concise, 1-2 sentences. Describe the primary action clearly. Auto-adds audio. |
| **Hunyuan 1.5** | Cinematic descriptions with camera directions. Supports `slow motion`, `timelapse`. |
| **DaSiWa** | Focus on subject motion. Works best with clear, simple actions. |
| **6-key-frames** | Per-segment prompts: describe what happens between each pair of keyframes. |

### Image-to-Video Best Practices

When converting a still image to video:
1. **Refine the source image first** — if the still isn't good, the video won't be either
2. **Describe the intended motion**, not what's already visible in the image
3. Use **separate seeds** for image and video generation for more variety
4. **Resolution**: video size should match or be proportional to image size
5. **Frame count**: minimum 65 frames for coherent motion, 81-121 for standard quality

---

## Negative Prompts

### When to Use

| Model | Negative Prompt Guidance |
|-------|------------------------|
| Qwen 2512 | Default negative is good. Override only for specific artifact control. |
| Z-Image standard | Light negatives help: `blurry, low quality, watermark` |
| Z-Image turbo | **Do NOT use negatives** — they hurt at 4 steps |
| Flux 2 Klein distilled | **No negative** (uses ConditioningZeroOut) |
| Flux 2 Klein base | Light negatives OK |
| Moody/Darkbeast | Pre-tuned defaults work well |
| Video workflows | `blurry, static, frozen, flickering, jittery` for motion quality |

### Effective Negative Keywords

- **General**: `low quality, blurry, deformed, bad anatomy, extra fingers, watermark, text, signature`
- **Faces**: `deformed face, asymmetric eyes, extra teeth, unnatural skin`
- **Video**: `static image, frozen, flickering, jittery motion, frame drops`

---

## Concrete Workflow Recipes

### Recipe 1: Photorealistic Portrait (Best Quality)

```bash
$VENV $SCRIPT -w "qwen_2512" \
  --prompt "25-year-old Japanese woman in a traditional silk kimono with cherry \
blossom pattern, standing under a canopy of blooming sakura trees, soft pink \
petals drifting in the breeze, golden hour sunlight filtering through branches, \
shallow depth of field, photorealistic, shot on Phase One XF IQ4 150MP, \
natural skin texture, 8K detail" \
  --width 768 --height 1024 -o /tmp
```

### Recipe 2: Fast Concept Exploration

```bash
# Quick iteration with Z-Image Turbo (15 seconds per image)
$VENV $SCRIPT -w "z_image_turbo" \
  --prompt "Futuristic Tokyo street market at night, holographic signs, rain, \
neon reflections on wet pavement, cyberpunk atmosphere" \
  --seed 42 -o /tmp
```

### Recipe 3: Image Editing

```bash
$VENV $SCRIPT -w "image_edit_2511" \
  --prompt "Change the background to a tropical beach sunset, keep the subject \
exactly the same, warm orange and pink sky" \
  --image /path/to/portrait.jpg \
  -o /tmp
```

### Recipe 4: Cinematic Video from Text

```bash
$VENV $SCRIPT -w "txt2vid" \
  --prompt "A golden retriever puppy runs joyfully through a sunlit meadow of \
wildflowers, camera tracking at ground level, shallow depth of field, warm \
afternoon light, gentle breeze moving the grass" \
  --seed 42 -o /tmp
```

### Recipe 5: Animate a Still Portrait

```bash
$VENV $SCRIPT -w "img2vid" \
  --prompt "The woman slowly turns her head toward the camera, a gentle smile \
forming on her lips, hair softly moving in a slight breeze" \
  --image /path/to/portrait.jpg \
  -o /tmp
```

### Recipe 6: Extended Video with SVI-28

```bash
$VENV $SCRIPT -w "SVI-28" \
  --prompt "A ballerina performs a graceful pirouette on stage, spotlight \
following her movement, flowing white dress" \
  --image /path/to/dancer.jpg \
  --extend-steps 5 \
  -o /tmp
```

### Recipe 7: Multi-Keyframe Story Video

```bash
$VENV $SCRIPT -w "6-key" \
  --image scene1.png scene2.png scene3.png scene4.png scene5.png scene6.png \
  --override '{
    "sg140_6": {"text": "camera slowly zooms in on the forest clearing"},
    "sg141_6": {"text": "a deer cautiously steps into the clearing"},
    "sg142_6": {"text": "the deer drinks from the stream, ears alert"},
    "sg143_6": {"text": "a butterfly lands on the deer antler"},
    "sg144_6": {"text": "the deer looks up and walks away into the forest"}
  }' \
  -o /tmp
```

---

## Iterative Refinement Workflow

1. **Start fast**: Use Z-Image Turbo for quick concept validation
2. **Fix the seed**: Once you find a composition you like, lock `--seed`
3. **Enhance the prompt**: Add details progressively — subject → setting → lighting → quality
4. **Switch to quality**: Move to Qwen 2512 or Distilled V3 for final render
5. **For video**: Generate the best still first, then use it as source for i2v workflows

---

## Verified E2E Results

These prompt + workflow combinations have been validated end-to-end with real outputs:

| Workflow | Prompt | Seed | Result |
|----------|--------|------|--------|
| **Smooth txt2vid** | "A cat sitting by a window, watching rain outside, cozy warm lighting" | 42 | 3 files: MP4 (3.5 MB) + preview PNG + last frame PNG |
| **Smooth img2vid** | "Girl turns and smiles gently, hair moves in breeze" | — | 3 files: MP4 (2.6 MB) + preview PNG + last frame PNG |
| **Smooth audio** | (default video) | — | 1 MP4 with generated audio |
| **DaSiWa AiO-52** | "A red car driving on mountain road, cinematic, 4k" | — | 1 WebM (0.1 MB) with audio |
| **DaSiWa SVI-28** (extend-steps 4) | "A red car driving on mountain road, cinematic, 4k" | — | 5 WebM: SVI + S1 + S2 + S3 + SVI-Interp |
| **Z-Image Turbo** | concise scene descriptions | — | 1 PNG (~15s) |
| **Qwen 2512** | detailed multi-component prompts | — | 1 PNG (~130s) |
| **Qwen ControlNet** | prompt + edge/depth map | — | 1 PNG (~130s) |
| **6-key-frames** | per-segment prompts via `--override` | — | 1 video from 6 keyframe images |

**Key observation**: Smooth workflows produce the richest output set (video + frames + audio). DaSiWa SVI-28 with `--extend-steps` produces multiple segment clips plus an interpolated result. Simple image workflows produce a single PNG.
