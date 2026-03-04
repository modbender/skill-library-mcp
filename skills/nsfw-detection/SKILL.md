# NSFW Detection Skills

Skills for detecting adult/inappropriate content.

## Essential Skills

### 1. NSFW Detector Pro
**Skill ID**: `nsfw-detector-pro`

**Purpose**: Advanced NSFW content detection

**Features**:
- Multi-category classification (porn, sexy, hentai, drawings)
- Confidence scoring (0-100%)
- Skin tone detection
- Context awareness (medical, art exceptions)
- Local ONNX model (no external API)

**Installation**:
```bash
npm install @clawhub/nsfw-detector
```

**Configuration**:
```javascript
{
  "skill": "nsfw-detector-pro",
  "settings": {
    "categories": ["porn", "sexy", "hentai"],
    "threshold": 0.7,
    "contextAware": true,
    "allowArt": true,
    "allowMedical": true,
    "localModel": true
  }
}
```

**Usage**:
```javascript
import { detectNSFW } from '@clawhub/nsfw-detector';

const result = await detectNSFW(imageUrl);
// {
//   isNSFW: true,
//   confidence: 0.92,
//   categories: { porn: 0.92, sexy: 0.15 },
//   action: 'block'
// }
```

**Accuracy**: 92-95% on explicit content, 75-80% on suggestive

**Use Cases**:
- Block pornography and explicit imagery
- Filter adult websites
- Protect children online

**Troubleshooting**:
- False positives on art? Enable `allowArt`
- Medical images blocked? Enable `allowMedical`
- Increase threshold for fewer false positives

**Related Skills**: `url-reputation`, `content-blur`

---

### 2. URL Reputation Checker
**Skill ID**: `url-reputation`

**Purpose**: Check if domains are adult/inappropriate sites

**Features**:
- Domain reputation database
- Adult site detection
- Phishing/malware detection
- Cached lookups

**Installation**:
```bash
npm install @clawhub/url-reputation
```

**Use Cases**:
- Block adult websites by domain
- Fast pre-filtering before image analysis
- Supplement visual detection

---



## Installation

### Via ClawHub
```
https://clawhub.ai/raghulpasupathi/nsfw-detection
```

### Via npm
```bash
npm install @raghulpasupathi/nsfw-detection
```

## Configuration Examples

### Child Protection (Strict)
```json
{
  "nsfw-detector-pro": {
    "threshold": 0.3,
    "blockAll": true,
    "allowArt": false,
    "allowMedical": false,
    "allowOverride": false
  }
}
```

### Teen Protection (Balanced)
```json
{
  "nsfw-detector-pro": {
    "threshold": 0.7,
    "allowArt": true,
    "allowMedical": true,
    "allowOverride": false
  }
}
```

### Adult Filtering (Lenient)
```json
{
  "nsfw-detector-pro": {
    "threshold": 0.9,
    "warnOnly": true,
    "allowOverride": true
  }
}
```

---

*For violence detection, see [VIOLENCE_DETECTION.md](VIOLENCE_DETECTION.md).*
