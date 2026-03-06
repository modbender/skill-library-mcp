# Changelog — ima-all-ai

All notable changes to this skill are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), versioned via [Semantic Versioning](https://semver.org/).

---

## v1.0.3 (2026-02-28) — Security Transparency Update

### 🔒 Security Documentation Improvements

**Added Network Endpoint Disclosure** — Full transparency for multi-domain architecture
- **SKILL.md**: Added "Network Endpoints Used" section clarifying dual-domain architecture
  - `api.imastudio.com` (main API, all tasks)
  - `imapi.liveme.com` (upload service, image/video tasks only)
  - Music tasks use single-domain flow (api.imastudio.com only)
- **SKILL.md**: Added "Credential Security Notice" section explaining API key usage
- **SKILL.md**: Updated "Agent Execution" and "Security & Transparency" sections to reflect accurate network flows
- **SKILL.md**: Added extensive security comments to Python code examples (lines 976-998, hardcoded `APP_KEY` disclosure)
- **examples.md**: Added security comments to Python upload flow code (lines 206-223)
- **SECURITY.md**: Expanded "Required Permissions" with domain ownership table and purpose clarification
- **SECURITY.md**: Updated "Data Flow Diagram" to show multi-step upload flow for image/video tasks
- **SECURITY.md**: Added "Hardcoded APP_KEY Disclosure" section explaining public shared key
- **SECURITY.md**: Added "Network Traffic Verification" guides (tcpdump, Wireshark, mitmproxy, DNS)
- **INSTALL.md**: Added "Security Checklist (Before First Use)" with 6-step verification guide
- **Version Metadata**: Updated skill version from 1.0.2 to 1.0.3

**Technical Details**:
- **API Endpoints**: `api.imastudio.com`, `imapi.liveme.com`
- **Hardcoded APP_KEY**: Documented `32jdskjdk320eew` as public, shared identifier (not a secret)
- **Credential Flow**: API key sent to both domains (both owned by IMA Studio)
- **User Verification**: Added tcpdump/Wireshark/mitmproxy examples for network monitoring

**What Changed**:
- ❌ **False Claims Removed**: Replaced "all requests go to api.imastudio.com only" statements
- ✅ **Full Disclosure**: Documented all network domains, credential flows, and hardcoded values
- ✅ **User Empowerment**: Added guides for independent security verification

**Impact**:
- **Security Rating**: Improved from "Suspicious" to "Clean" (eliminated undisclosed endpoints/credentials)
- **User Trust**: Users can now verify security claims independently

---

## v1.0.2 (2026-02-27) — Latest Release

### 🎨 Image Model Updates

**Added Nano Banana2** — Budget-friendly option restored
- Cost: 4-13 pts (512px to 4K)
- Fastest generation: 20-40 seconds
- Perfect for rapid prototyping and high-volume workflows

**Updated Image Model Count**: 2 → 3 models
- SeeDream 4.5 (balanced, 5pts)
- Nano Banana2 (budget, 4-13pts) ✨ NEW
- Nano Banana Pro (premium, 10-18pts)

---

## v1.0.1 (2026-02-26) — Video Updates

### 🎬 Video Model Updates

**Models Removed** (no longer available via Open API)
- Vidu Q2 Turbo

**Models Updated**
- Pixverse model variants (V3.5-V5.5)
- Confirmed availability of all 14 video models

---

## v1.0.0 (2026-02-25) — Initial Release

### 🎉 Unified AI Content Generation via IMA Open API

**Generate images, videos, and music from text — all in one skill.**

Transform text descriptions into stunning visuals, cinematic videos, and professional soundtracks. Perfect for content creators, marketers, designers, and developers who need comprehensive AI generation capabilities across multiple media types.

---

## ✨ Key Features

### 🎨 Image Generation (3 Models)

**Text to Image**
- Generate images from text descriptions
- 8 aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2, 21:9
- Resolution: 512px to 4K
- Generation time: 20-60 seconds

**Image to Image**
- Style transfer and variations
- Transform existing images
- Same resolution and quality options

**Featured Models:**
- **SeeDream 4.5** (5 pts) — Default, photorealistic 4K, 8 aspect ratios
- **Nano Banana2** (4-13 pts) — Budget-friendly, flexible sizes
- **Nano Banana Pro** (10-18 pts) — Premium quality, 1K/2K/4K

### 🎬 Video Generation (14 Models)

**4 Video Generation Modes:**

1. **Text to Video** (14 models)
   - Generate videos from descriptions
   - Resolution: 540P to 4K
   - Duration: 4-15 seconds
   - Generation time: 60-360s

2. **Image to Video** (14 models)
   - Bring static images to life
   - Camera movements, object animation
   - Duration: 4-15 seconds

3. **First-Last Frame to Video** (10 models)
   - Smooth transitions between frames
   - Morphing effects
   - Duration: 5-10 seconds

4. **Reference Image to Video** (9 models)
   - Style-consistent generation
   - Character/style preservation
   - Duration: 4-10 seconds

**Featured Models:**
- **Wan 2.6** (25-120 pts) — Most popular, balanced, default
- **Kling O1** (48-120 pts) — Latest with audio, reasoning model
- **Hailuo 2.3** (38 pts) — Latest MiniMax
- **Google Veo 3.1** (70-330 pts) — SOTA cinematic
- **Sora 2 Pro** (122+ pts) — OpenAI premium
- **Vidu Q2** (5-70 pts) — Budget-friendly

### 🎵 Music Generation (3 Models)

**Text to Music**
- Generate music from text descriptions
- Styles: instrumental, vocal, background music
- Duration: 1-3 minutes
- Commercial-use ready

**Featured Models:**
- **Suno (sonic-v5)** (25 pts) — Highest quality, custom lyrics, vocal control
- **DouBao BGM** (30 pts) — Background music, instrumental
- **DouBao Song** (30 pts) — Song generation with vocals

---

## 🚀 What You Can Generate

### Multi-Media Content Packages
- **Complete Social Posts**: Image + short video + background music
- **Product Launches**: Product visuals + demo video + promotional soundtrack
- **Marketing Campaigns**: Multiple assets across all media types
- **Creative Projects**: Concept art + animated scenes + custom music

### Single-Media Workflows
- **Images**: Concept art, product mockups, social media graphics
- **Videos**: TikTok/Reels, promotional clips, B-roll footage
- **Music**: Soundtracks, jingles, background scores

---

## 🎯 Smart Features

### Automatic Model Selection
- **Default to newest and most popular** models, not cheapest
- Image: SeeDream 4.5 (5pts, 4K, 8 aspect ratios)
- Video: Wan 2.6 (25pts, most popular)
- Music: Suno (25pts, highest quality)

### User Preference Memory
- Automatically remembers your favorite model for each task type
- Saved to `~/.openclaw/memory/ima_prefs.json`
- Synced across all IMA skills

### Cost Transparency
- Shows credits and estimated time **before** generation
- For expensive models (>50pts), proactively suggests cheaper alternatives
- Clear cost breakdown for all operations

### Real-Time Progress Tracking
- Never wait in silence — updates every 15-60 seconds
- Progress percentage based on estimated completion time
- Clear status messages throughout generation

### Automatic Image Upload
- Local files automatically uploaded to OSS
- No manual upload steps required
- Uses secure presigned URLs
- Works seamlessly for all image-based tasks

---

## 📝 Usage Examples

### Image Generation
```
"A cute puppy running on grass, photorealistic 4K"
→ Uses SeeDream 4.5 (5pts), generates in ~30s

"Turn this photo into watercolor painting style"
→ Image-to-image with SeeDream 4.5
```

### Video Generation
```
"Generate a video of a puppy dancing, cinematic, 5 seconds"
→ Uses Wan 2.6 (25pts), generates in ~90s

"Bring this landscape image to life, gentle wind"
→ Image-to-video, camera movement
```

### Music Generation
```
"Upbeat electronic music, 120 BPM, no vocals"
→ Uses Suno (25pts), generates in ~30s

"Relaxing piano melody for meditation"
→ DouBao BGM, ambient style
```

### Multi-Media Workflow
```
1. "Generate product image: sleek smartphone, studio lighting"
   → Image (30s)

2. "Create video showing phone rotating 360 degrees"
   → Video from image (90s)

3. "Generate tech-style background music, futuristic"
   → Music (30s)

Total: Complete product package in ~3 minutes
```

---

## 🎨 Use Cases

| Use Case | Example |
|----------|---------|
| 📱 **Social Media** | Complete post packages: image + video + music |
| 🎬 **Content Creation** | Multi-media projects with consistent style |
| 📢 **Marketing** | Product visuals, demo videos, promotional soundtracks |
| 🎮 **Game Dev** | Concept art, cinematics, background music |
| 🏢 **Business** | Presentations with visuals, videos, and audio |
| 🎨 **Creative Arts** | Comprehensive creative workflows |

---

## 🔧 Technical Details

### API Integration
- **Base URL**: `https://api.imastudio.com`
- **Authentication**: Bearer token (`ima_*` API key)
- **Task Types**: 7 total (text_to_image, image_to_image, text_to_video, image_to_video, first_last_frame_to_video, reference_image_to_video, text_to_music)
- **Output Formats**: 
  - Images: JPEG/PNG (512px-4K)
  - Videos: MP4 + thumbnail (540P-4K)
  - Music: MP3 (high-quality audio)

### Generation Performance
- **Image**: 20-60 seconds (model-dependent)
- **Video**: 60-360 seconds (model-dependent)
- **Music**: 10-45 seconds (model-dependent)
- **Poll Intervals**: Optimized per content type (5s for image/music, 8s for video)

### Quality Standards
- All outputs are production-ready
- Suitable for commercial use
- High-resolution support (up to 4K for images/videos)
- Professional-grade audio quality

---

## 🔐 Security & Best Practices

- **Read-only skill**: No modifications allowed — ensures reliability
- **API key required**: Set `IMA_API_KEY` environment variable
- **Automatic updates**: Always uses latest API endpoints
- **Production-validated**: Tested on real IMA Open API
- **Image upload security**: Automatic OSS with secure tokens

---

## 🎯 Why Choose This Skill?

✅ **All-in-one**: One skill for image + video + music (vs. 3 separate tools)  
✅ **Latest models**: Wan 2.6, Kling O1, SeeDream 4.5, Suno sonic-v5 (2026)  
✅ **Smart defaults**: Recommends newest & most popular, not cheapest  
✅ **User-friendly**: Remembers your preferences, shows costs upfront  
✅ **Production-ready**: 20+ models, all production-validated  
✅ **Comprehensive**: Supports all major AI generation engines  
✅ **Time-saving**: Multi-media workflows without switching tools

---

## 📊 Model Coverage

| Type | Models | Task Types |
|------|--------|-----------|
| **Image** | 3 | text_to_image, image_to_image |
| **Video** | 14 | text_to_video, image_to_video, first_last_frame, reference |
| **Music** | 3 | text_to_music |
| **Total** | 20+ | 7 task types |

---

## 🏷️ Tags

`ai` `unified` `all-in-one` `image` `video` `music` `generation` `text-to-image` `text-to-video` `text-to-music` `seedream` `wan` `kling` `suno` `content-creation` `multi-media` `workflow` `ima-api` `social-media` `marketing`

---

## 📦 What's Included

- ✅ Complete SKILL.md documentation (1,110 lines)
- ✅ Production-ready Python script (`ima_create.py`)
- ✅ Comprehensive examples (`examples.md`)
- ✅ Model capability matrix and cost breakdown
- ✅ User preference memory system
- ✅ Real-time progress tracking
- ✅ Automatic image upload
- ✅ Error handling and troubleshooting

---

## 🔗 Related Skills

- **[ima-image-ai](https://clawhub.ai/skills/ima-image-ai)** — Focused image generation
- **[ima-video-ai](https://clawhub.ai/skills/ima-video-ai)** — Focused video generation
- **[ima-voice-ai](https://clawhub.ai/skills/ima-voice-ai)** — Focused music generation

💡 **When to use which?**
- Use **ima-all-ai** for multi-media workflows
- Use focused skills for single-media workflows

---

## 📄 License & Support

- **License**: MIT (see [LICENSE](LICENSE))
- **Support**: [GitLab Issues](https://git.joyme.sg/imagent/skills/ima-all-ai/-/issues)
- **API Provider**: [IMA Studio](https://imastudio.com)

---

## 🚀 Future Roadmap

### Planned Features
- [ ] Cross-media workflows (image → video → music pipelines)
- [ ] Batch generation for multiple assets
- [ ] Style consistency across media types
- [ ] Advanced parameter presets
- [ ] Export packages (all formats in one bundle)
- [ ] Integration with other creative tools

### Model Updates
- [ ] New AI models as they release
- [ ] Performance optimizations
- [ ] Extended duration options
- [ ] Additional aspect ratios and resolutions

---

## 📝 Version History

### v1.0.2 (2026-02-27)
- ✅ Added Nano Banana2 (budget image model)
- ✅ Updated image model count: 2 → 3
- ✅ Restored budget option for image generation

### v1.0.1 (2026-02-26)
- ✅ Removed Vidu Q2 Turbo (no longer available)
- ✅ Updated Pixverse model variants
- ✅ Confirmed 14 video model availability

### v1.0.0 (2026-02-25)
- ✅ Initial release with 3 content types
- ✅ 20+ production models
- ✅ User preference memory
- ✅ Automatic image upload
- ✅ Smart model selection
- ✅ Real-time progress tracking
- ✅ Production-validated on IMA Open API

---

**Ready to create? Get started with ima-all-ai today! 🎨🎬🎵**
