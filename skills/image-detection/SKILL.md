# Image Detection Skills

Skills for analyzing and detecting AI-generated images.

## Essential Skills

### 1. Image Analyzer
**Skill ID**: `image-analyzer`

**Purpose**: Local image analysis without external APIs

**Features**:
- EXIF metadata extraction
- AI artifact detection (weird hands, blurred backgrounds)
- Visual similarity comparison
- Reverse image search integration

**Installation**:
```bash
npm install @clawhub/image-analyzer
```

**Configuration**:
```javascript
{
  "skill": "image-analyzer",
  "settings": {
    "detectArtifacts": true,
    "extractMetadata": true,
    "localOnly": true,
    "checkSignatures": ["DALL-E", "Midjourney", "Stable-Diffusion"]
  }
}
```

**Use Cases**: Fast local detection, metadata verification, artifact identification

---

### 2. HuggingFace Image Detector
**Skill ID**: `hf-image-detector`

**Purpose**: ML-based AI image detection

**Features**:
- Pre-trained models (umm-maybe/AI-image-detector)
- High accuracy (90-95%)
- Supports SD, Midjourney, DALL-E
- Local inference (no API calls)

**Installation**:
```bash
npm install @clawhub/hf-image-detector
```

**Use Cases**: High-accuracy detection, privacy-focused analysis

---

### 3. Hive Moderation API
**Skill ID**: `hive-api`

**Purpose**: Cloud-based image analysis

**Features**:
- AI-generated detection
- NSFW filtering
- Object detection
- Fast inference (500ms)

**Installation**: API integration via REST

**Use Cases**: Quick detection, multi-purpose analysis, NSFW filtering

---



## Installation

### Via ClawHub
```
https://clawhub.ai/raghulpasupathi/image-detection
```

### Via npm
```bash
npm install @raghulpasupathi/image-detection
```

## Configuration Examples

### High Accuracy Stack
```json
{
  "skills": ["image-analyzer", "hf-image-detector", "hive-api"],
  "votingStrategy": "majority"
}
```

### Privacy-Focused Stack
```json
{
  "skills": ["image-analyzer", "hf-image-detector"],
  "externalAPIs": false
}
```

### Fast Detection Stack
```json
{
  "skills": ["hive-api"],
  "cacheResults": true
}
```

---

*For video detection, see [VIDEO_DETECTION.md](VIDEO_DETECTION.md).*
