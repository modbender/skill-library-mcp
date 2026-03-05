# Changelog — ima-voice-ai

All notable changes to this skill are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), versioned via [Semantic Versioning](https://semver.org/).

---

## v1.0.1 (2026-02-28) — Security Clarity Update

### 🔒 Documentation Clarification

**Enhanced clarity to distinguish this skill's simpler network architecture from image/video skills.**

#### Added
- **Network Architecture Comparison**: New section explaining why this skill uses only `api.imastudio.com` (music generation doesn't need image uploads)
- **Comparison Table**: Shows difference between voice/image/video skills' network architectures
- **Security Verification**: Enhanced verification commands with clear expected output

#### Changed
- **Clarified Network Claims**: Updated "only api.imastudio.com" statements to explain **why** (to differentiate from image/video skills that use two domains)
- **Enhanced Transparency**: Added context explaining the architectural difference is intentional and correct

**No functional changes** — purely documentation clarity improvements to help users understand the single-domain architecture is correct for music generation.

---

## v1.0.0 (2026-02-27) — Initial Release

### 🎵 AI Music Generation via IMA Open API

**Generate professional music and audio with AI — text to music in seconds.**

Transform text descriptions into complete music tracks. Whether you need background music for videos, custom jingles, lo-fi beats, or full vocal songs, this skill handles it all through the powerful IMA Open API.

---

### ✨ Key Features

#### 🎹 3 Production-Ready AI Models
- **Suno sonic-v5** (25 pts) — Latest Suno engine, most powerful and full-featured
  - Custom lyrics and vocal arrangements
  - Style tags (pop, rock, electronic, classical, ambient...)
  - Vocal gender control (male/female/none)
  - Duration: 4-180 seconds
  - **Recommended default** for best quality

- **DouBao BGM** (30 pts) — Background music specialist
  - Perfect for ambient tracks, video backgrounds, game loops
  - Duration: 15-180 seconds
  - Budget-friendly option

- **DouBao Song** (30 pts) — Vocal song generator
  - Structured song compositions with vocals
  - Duration: 15-180 seconds
  - Budget-friendly option

#### 🎯 Smart Features
- **Automatic model selection**: Defaults to newest/most popular model (Suno sonic-v5)
- **User preference memory**: Remembers your favorite model for future generations
- **Cost transparency**: Shows credits and estimated time before generation
- **Fast generation**: 10-45 seconds depending on model
- **High-quality output**: MP3 audio files ready for download

#### 🔧 Advanced Controls (Suno)
- **Custom mode**: Write your own lyrics or let AI generate them
- **Instrumental mode**: Pure instrumental tracks without vocals
- **Style tags**: Choose from 100+ genre tags (lo-fi, cinematic, jazz, metal, EDM...)
- **Negative tags**: Exclude unwanted styles (e.g., "no heavy metal, no distortion")
- **Tempo control**: Set BPM (beats per minute) for precise rhythm
- **Duration**: Flexible length from 4 to 180 seconds

---

### 🚀 What You Can Generate

- **Background Music**: Lo-fi, ambient, cinematic, corporate, game soundtracks
- **Custom Jingles**: Brand themes, podcast intros, YouTube intros
- **Full Songs**: Pop, rock, electronic, classical, jazz, country...
- **Mood-Based Tracks**: Happy, melancholic, energetic, tense, dramatic
- **Specific Styles**: 80s synthwave, 90s hip-hop, medieval folk, modern trap...
- **Instrumental Loops**: Guitar, piano, synth, orchestral arrangements

---

### 📝 Prompt Examples

```
"upbeat lo-fi hip hop, 90 BPM, no vocals, chill vibes"
→ Perfect study/work background music

"epic orchestral cinematic, dramatic strings, 120 BPM, 60 seconds"
→ Movie trailer-style music

"80s synthwave with retro drums, nostalgic, instrumental"
→ Stranger Things vibe

"acoustic guitar, calm and peaceful, coffee shop ambiance"
→ Relaxing café background

"female vocals, indie pop, uplifting and happy, medium tempo"
→ Radio-ready song
```

---

### 🎨 Use Cases

- **Content Creators**: Background music for YouTube, TikTok, Instagram
- **Podcasters**: Custom intro/outro music
- **Game Developers**: Dynamic soundtracks and ambient loops
- **Video Producers**: Royalty-free music for commercial projects
- **Musicians**: Quick demos and inspiration for songwriting
- **Businesses**: Corporate presentations, on-hold music, brand themes

---

### 🔐 Security & Best Practices

- **Read-only skill**: No modifications allowed — ensures reliability and security
- **API key required**: Set `IMA_API_KEY` environment variable
- **Automatic updates**: Always uses latest API endpoints and model versions
- **Production-validated**: Tested on real IMA Open API infrastructure

---

### 📊 Technical Details

- **Base URL**: `https://api.imastudio.com`
- **Authentication**: Bearer token (`ima_*` API key)
- **Task Type**: `text_to_music`
- **Output Format**: MP3 audio files
- **Generation Time**: 
  - DouBao BGM/Song: 10-25 seconds
  - Suno: 20-45 seconds
- **Quality**: Professional-grade audio suitable for commercial use

---

### 🎯 Why Choose This Skill?

✅ **Always up-to-date**: Automatically queries latest models from IMA API  
✅ **Smart defaults**: Recommends best model, not cheapest  
✅ **User-friendly**: No technical knowledge required — just describe what you want  
✅ **Cost-efficient**: Transparent credit usage, from 6 to 30 points per generation  
✅ **Production-ready**: Used by real businesses and content creators  
✅ **Comprehensive**: Supports all major AI music generation engines

---

### 🏷️ Tags

`ai` `music` `audio` `generation` `text-to-music` `background-music` `suno` `doubao` `ima-api` `content-creation` `video-production` `podcast` `jingle` `soundtrack` `ambient` `lo-fi` `instrumental` `vocal` `song` `lyrics`

---

### 📦 What's Included

- ✅ Complete SKILL.md documentation with examples
- ✅ Production-ready Python script (`ima_voice_create.py`)
- ✅ Model capability matrix and cost breakdown
- ✅ Error handling and troubleshooting guide
- ✅ Style tag reference with 100+ genres
- ✅ User preference memory system
- ✅ Real-time progress tracking

---

### 🔗 Related Skills

- **ima-image-ai**: AI image generation (text-to-image, image-to-image)
- **ima-video-ai**: AI video generation (text/image-to-video, frame interpolation)
- **ima-ai-creation**: All-in-one skill for image + video + music workflows

---

### 📄 License & Support

- **License**: MIT (see skill repository)
- **Support**: Issues via GitHub or IMA technical support
- **API Provider**: IMA Studio (https://api.imastudio.com)

---

## Future Roadmap

- [ ] Support for more Suno model versions as they release
- [ ] Additional DouBao music models (if API adds them)
- [ ] Audio mixing and merging capabilities
- [ ] Batch generation for multiple tracks
- [ ] Style preset library for quick generation
