# Changelog — ima-image-ai

All notable changes to this skill are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), versioned via [Semantic Versioning](https://semver.org/).

---

## v1.0.2 (2026-02-28) — Security Transparency Update

### 🔒 Security & Documentation Improvements

**Enhanced transparency and security disclosure in response to OpenClaw security audit.**

#### Changed
- **Full Network Endpoint Disclosure**: Updated all documentation to explicitly list both domains used:
  - `api.imastudio.com` (main API for task creation and polling)
  - `imapi.liveme.com` (image upload service for i2i tasks)
- **Credential Flow Documentation**: Added detailed explanation of why IMA API key is sent to both domains
- **Security Notice**: Added prominent credential security notice in SKILL.md
- **APP_KEY Disclosure**: Documented hardcoded APP_KEY as shared public key (not a secret)

#### Added
- **Network Traffic Verification Guide**: Step-by-step instructions for monitoring network traffic (SECURITY.md)
- **Security Checklist**: Pre-installation verification steps (INSTALL.md)
- **Domain Ownership Verification**: DNS verification commands for both domains
- **Code Comments**: Enhanced inline documentation explaining upload flow and credential usage

#### Fixed
- Removed false claims that "all requests go to api.imastudio.com only"
- Corrected copy-paste errors referencing "ima_voice_create.py" in INSTALL.md and SECURITY.md
- Updated all script name references to use ima_image_create.py

#### Documentation
- SKILL.md: Added "🌐 Network Endpoints Used" and "⚠️ Credential Security Notice" sections
- SECURITY.md: Added "Network Traffic Verification" and "Hardcoded APP_KEY Disclosure" sections
- INSTALL.md: Added "Security Checklist (Before First Use)" section
- scripts/ima_image_create.py: Enhanced function docstrings with security explanations

**No functional changes** — purely documentation and transparency improvements.

---

## v1.0.1 (2026-02-27) — Production Release

### 🎨 AI Image Generation via IMA Open API

**Generate stunning images with AI — text to image and image to image in seconds.**

Transform text descriptions into photorealistic images, or transform existing images into new styles. Whether you need concept art, product mockups, portrait photos, or artistic renditions, this skill handles it all through the powerful IMA Open API.

---

### ✨ Key Features

#### 🖼️ 3 Production-Ready AI Models

- **SeeDream 4.5** 🌟 (5 pts) — Latest DouBao flagship model (Recommended)
  - 4K photorealistic image generation
  - Custom aspect ratio support (1:1, 16:9, 9:16, 4:3, 3:4, 2:3, 3:2, 21:9)
  - Balanced quality and cost
  - Generation time: 30-60 seconds
  - **Recommended default** for best value

- **Nano Banana2** 💚 (4-13 pts) — Fastest and most flexible
  - Size options: 512px (4pts) / 1K (6pts) / 2K (10pts) / 4K (13pts)
  - Budget-friendly at 512px (4 pts)
  - Square images only (1:1)
  - Generation time: 20-40 seconds

- **Nano Banana Pro** (10-18 pts) — Premium quality
  - Highest quality output
  - Size control: 1K (10pts) / 2K (10pts) / 4K (18pts)
  - Square images only (1:1)
  - Generation time: 60-120 seconds

#### 🎯 Smart Features

- **Automatic model selection**: Defaults to newest/most popular model (SeeDream 4.5)
- **User preference memory**: Remembers your favorite model for future generations
- **Cost transparency**: Shows credits and estimated time before generation
- **Fast generation**: 20-60 seconds depending on model
- **High-quality output**: Up to 4K resolution images

#### 🔧 Advanced Controls

- **text_to_image**: Create images from text descriptions
- **image_to_image**: Transform existing images with AI
  - Style transfer (e.g., "turn into oil painting")
  - Image enhancement and modification
  - Automatic image upload for local files
- **Custom aspect ratios** (SeeDream 4.5 only): 
  - 1:1 (square), 16:9 (widescreen), 9:16 (portrait)
  - 4:3, 3:4, 2:3, 3:2, 21:9 (ultra-wide)
- **Size control** (Nano Banana models): 512px to 4K
- **Smart credit_rule selection**: Automatically picks correct size/quality tier

---

### 🚀 Usage

#### For IM Platforms (Feishu, Discord)

Simply describe what you want:
```
帮我画一只可爱的猫咪
```

The agent will:
1. Acknowledge your request immediately
2. Show generation progress (model, time, credits)
3. Send the final image directly to the chat
4. Remember your model preference for next time

#### Direct API Usage

```bash
python3 scripts/ima_image_create.py \
  --api-key ima_xxx \
  --task-type text_to_image \
  --model-id doubao-seedream-4.5 \
  --prompt "a beautiful mountain sunset, photorealistic"
```

---

### 📊 Model Comparison

| Model | Cost | Speed | Quality | Aspect Ratio | Best For |
|-------|------|-------|---------|--------------|----------|
| SeeDream 4.5 🌟 | 5 pts | 30-60s | ⭐⭐⭐⭐ | ✅ 8 ratios | General use, aspect ratios |
| Nano Banana2 💚 | 4-13 pts | 20-40s | ⭐⭐⭐ | ❌ 1:1 only | Budget, fast results |
| Nano Banana Pro | 10-18 pts | 60-120s | ⭐⭐⭐⭐⭐ | ❌ 1:1 only | Premium quality |

---

### 🔧 Installation & Setup

1. **Install dependencies**:
   ```bash
   pip install requests
   ```

2. **Set API key** (choose one method):
   - Environment variable: `export IMA_API_KEY=ima_your_key_here`
   - Agent config: Add to `.cursor/mcp.json` or Feishu bot config

3. **Ready to use** — no additional configuration needed!

---

### 📚 Documentation

- **SKILL.md** — Complete technical reference (1220 lines)
  - User Experience Protocol (UX v1.3)
  - API reference and examples
  - Security policy (READ-ONLY)
  - User preference memory system
  - FAQ and troubleshooting

---

### 🔒 Security

- ✅ READ-ONLY skill — users cannot modify skill files
- ✅ API key via environment variable only (never hardcoded)
- ✅ No sensitive data in codebase
- ✅ Public constants clearly marked (APP_KEY is public app identifier)

---

### 🐛 Known Limitations

- **8K resolution**: Not supported (max is 4K)
- **Custom aspect ratios**: Only SeeDream 4.5 supports this via virtual parameters
- **Non-standard ratios** (e.g., 7:3): Not supported; suggest closest supported ratio
- **Nano Banana models**: Square images only (1:1 aspect ratio)

**Workarounds**:
- For custom aspect ratios on other models: Use video models (Wan 2.6) with aspect ratio control, extract first frame
- For 8K: Generate at 4K, use external upscaling tools (Real-ESRGAN, Topaz Gigapixel)

---

### 🔄 Version History

- **v1.0.1** (2026-02-27) — Production release with 3 models
- **v1.0.0** (2026-02-26) — Initial development version

---

### 📞 Support

- Report issues via ClawHub skill repository
- Technical questions: See SKILL.md FAQ section
- IMA API support: Contact IMA technical support
