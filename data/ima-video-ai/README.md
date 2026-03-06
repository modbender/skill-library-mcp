# IMA Video AI — AI Video Generation 🎬

**Generate professional videos from text or images in minutes**

Transform text descriptions or images into complete video clips using Wan, Kling, Hailuo, Google Veo, Sora, and Pixverse AI models. Perfect for content creators, social media managers, marketers, and video producers.

[![ClawHub](https://img.shields.io/badge/ClawHub-Creative-blueviolet)](https://clawhub.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](CHANGELOG_CLAWHUB.md)

---

## ✨ Features

🎥 **4 Video Generation Modes**
- **Text to Video** (14 models) — Generate videos from descriptions
- **Image to Video** (14 models) — Bring static images to life
- **First-Last Frame** (10 models) — Smooth transitions between frames
- **Reference Image** (9 models) — Style-consistent video generation

⚡ **Fast Generation**
- 60-360 seconds per video (model-dependent)
- Real-time progress tracking
- MP4 output with thumbnail

🎨 **Rich Customization**
- Resolution: 540P to 4K
- Aspect ratio: 16:9, 9:16, 1:1, 4:3
- Duration: 4-15 seconds
- Camera controls, lighting, negative prompts

💎 **Professional Quality**
- Cinematic camera work
- High-quality MP4 video
- Commercial-use ready
- First-frame JPEG thumbnail

---

## 🚀 Quick Start

### 1. Get API Key
Get your IMA API key at https://imastudio.com

### 2. Set Environment Variable
```bash
export IMA_API_KEY=ima_your_key_here
```

### 3. Generate Video
Just describe what you want in natural language:

**Examples:**
```
"Generate a cute puppy running across a sunny meadow, cinematic 4K"
→ Adorable pet video with professional camera work

"City skyline at sunset, camera slowly panning right, golden hour lighting"
→ Cinematic establishing shot

"Underwater scene with colorful tropical fish, slow motion, coral reef"
→ Nature documentary style
```

---

## 🎯 Use Cases

| Use Case | Example |
|----------|---------|
| 📱 **Social Media** | TikTok/Instagram Reels, viral content |
| 🎬 **Content Creation** | YouTube videos, B-roll footage |
| 📢 **Marketing** | Product demos, promotional videos |
| 🎮 **Game Dev** | Cinematics, cutscenes, trailers |
| 🏢 **Business** | Presentations, training videos |
| 🎨 **Creative Arts** | Music videos, art projects |

---

## 🎥 Supported Models

### Most Popular (Recommended Defaults)

| Model | Cost | Best For | Generation Time |
|-------|------|----------|----------------|
| **Wan 2.6** (t2v) | 25-120 pts | Text to video, balanced quality/cost | 60-120s |
| **Wan 2.6** (i2v) | 25-120 pts | Image to video, most popular | 60-120s |
| **Kling O1** | 48-120 pts | Latest reasoning model, with audio | 180-360s |

### Premium Models

| Model | Cost | Features |
|-------|------|----------|
| **Google Veo 3.1** | 70-330 pts | SOTA cinematic, 720P-4K |
| **Sora 2 Pro** | 122+ pts | OpenAI premium |
| **Hailuo 2.3** | 38 pts | Latest MiniMax |

### Budget Options

| Model | Cost | Features |
|-------|------|----------|
| **Vidu Q2** | 5-70 pts | Fastest, most affordable |
| **Pixverse V3.5-V5.5** | 12-48 pts | Cost-effective series |

---

## 📝 Prompt Examples

### Text to Video
```
"a cute puppy running across a sunny meadow, cinematic 4K"
"city skyline at sunset, camera slowly panning right, golden hour"
"underwater tropical fish, slow motion, coral reef"
"futuristic neon cityscape, cyberpunk, night, rain reflections"
```

### Image to Video
```
"camera slowly zooms in"
→ Ken Burns effect

"bring this landscape alive with gentle wind and moving clouds"
→ Subtle animation

"object rotates 360 degrees, studio lighting"
→ Product showcase
```

### First-Last Frame to Video
```
"smooth transition between frames"
→ Morphing effect

"character walks from A to B, natural motion"
→ Animation interpolation
```

---

## 🔧 Advanced Features

- **Resolution Control**: 540P, 720P, 1080P, 2K, 4K
- **Aspect Ratios**: 16:9 (widescreen), 9:16 (vertical), 1:1 (square), 4:3
- **Duration**: 4-15 seconds per clip
- **Shot Types**: Single shot, multi-shot transitions
- **Negative Prompts**: Exclude unwanted elements
- **Prompt Enhancement**: AI-powered optimization
- **Seed Control**: Reproducible results
- **Automatic Image Upload**: Local files → OSS seamlessly

---

## 📖 Documentation

- **[SKILL.md](SKILL.md)** — Complete technical documentation
- **[CHANGELOG_CLAWHUB.md](CHANGELOG_CLAWHUB.md)** — Version history and features
- **[scripts/ima_video_create.py](scripts/ima_video_create.py)** — Production script

---

## 🔗 Related Skills

- **[ima-image-ai](https://clawhub.ai/skills/ima-image-ai)** — AI image generation (text-to-image, image-to-image, upscale)
- **[ima-voice-ai](https://clawhub.ai/skills/ima-voice-ai)** — AI music generation (text-to-music, background music)
- **[ima-all-ai](https://clawhub.ai/skills/ima-all-ai)** — All-in-one image/video/music workflows

---

## 🔐 Security & Best Practices

✅ **Read-only skill** — No modifications allowed, ensures reliability  
✅ **API key required** — Set `IMA_API_KEY` environment variable  
✅ **Automatic updates** — Always uses latest API endpoints  
✅ **Production-validated** — Tested on real IMA infrastructure  
✅ **Secure uploads** — Automatic OSS upload with token authentication

---

## 📊 Why Choose This Skill?

| Feature | This Skill | Others |
|---------|-----------|--------|
| **Latest Models** | ✅ Wan 2.6, Kling O1, Veo 3.1 (2026) | ❌ Outdated |
| **Generation Speed** | ✅ 60-360s | ❌ 600s+ |
| **Model Coverage** | ✅ 14 models | ❌ <5 |
| **Cost Transparency** | ✅ Shown upfront | ❌ Hidden |
| **User Memory** | ✅ Remembers preferences | ❌ No memory |
| **Image Upload** | ✅ Automatic OSS | ❌ Manual only |

---

## 💻 CLI Usage

### Text to Video
```bash
python3 scripts/ima_video_create.py \
  --api-key $IMA_API_KEY \
  --task-type text_to_video \
  --model-id wan2.6-t2v \
  --prompt "a cute puppy running on grass" \
  --output-json
```

### Image to Video
```bash
python3 scripts/ima_video_create.py \
  --api-key $IMA_API_KEY \
  --task-type image_to_video \
  --model-id wan2.6-i2v \
  --prompt "camera slowly zooms in" \
  --input-images https://example.com/photo.jpg \
  --output-json
```

### List Available Models
```bash
python3 scripts/ima_video_create.py \
  --api-key $IMA_API_KEY \
  --task-type text_to_video \
  --list-models
```

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🌟 Support

- **GitLab Issues**: [Report bugs or request features](https://git.joyme.sg/imagent/skills/ima-video-ai/-/issues)
- **ClawHub Comments**: Leave feedback on the skill page
- **API Provider**: [IMA Studio](https://imastudio.com)

---

## 🎉 Get Started

1. Install the skill from [ClawHub](https://clawhub.ai/skills/ima-video-ai)
2. Set your `IMA_API_KEY`
3. Start generating videos!

**Happy creating! 🎬**
