# Setup Guide

## Prerequisites

- **Node.js** v18+ (`node --version`)
- **Postiz account** — [postiz.com](https://postiz.com) (self-hosted or cloud)
- **Postiz CLI** — `npm install -g postiz-cli`
- **TikTok account** connected to Postiz as an integration
- **ImageMagick** (optional, for keyword overlays) — `brew install imagemagick`

## Install

```bash
cd /path/to/tiktok-content-pipeline
npm install
```

Dependencies: `canvas`, `cheerio`, `sharp` (for image generation).

## Configure Your First Account

### 1. Copy the example config

```bash
cp config.example.json accounts/my-brand/config.json
```

### 2. Edit `accounts/my-brand/config.json`

```json
{
  "account": {
    "name": "my-brand",
    "handle": "@mytiktok",
    "niche": "gaming-nostalgia",
    "createdAt": "2026-02-01T00:00:00Z"
  },
  "postiz": {
    "apiKey": "your-postiz-api-key",
    "integrationId": "your-tiktok-integration-id"
  },
  "posting": {
    "timezone": "Europe/London"
  }
}
```

**Where to find your Postiz integration ID:**
1. Log into Postiz → Settings → Integrations
2. Find your TikTok integration
3. Copy the integration ID from the URL or settings panel

**Account `createdAt`:** Set this to when your TikTok account was created. The scheduler uses this to determine posting frequency (daily for new accounts, 3-4/week for established ones).

### 3. Create from template

```bash
node cli.js create my-brand --template example-nostalgia
```

## Create a Custom Template

### 1. Create the template directory

```bash
mkdir -p templates/your-niche
```

### 2. Create `templates/your-niche/config.json`

Define your content types, hooks, hashtags. See `templates/example-nostalgia/config.json` for the full structure.

Key sections:
- `content.types` — What kinds of content you produce (each gets a `--type` flag in the CLI)
- `hooks` — Array of hook texts per content type. Use `{placeholder}` for dynamic values.
- `questionHooks` — Optional question-format hooks that drive comment engagement (50% chance of being used on slide 1)
- `content.hashtagSets` — Hashtags per content type
- `searchKeywords` — Keywords overlaid on slides for TikTok SEO
- `ctaSlides` — Call-to-action text for final slides

### 3. Create `templates/your-niche/generator.js`

Extend `ContentGenerator` and implement `getSupportedTypes()` and `_generateContent()`.

```javascript
const ContentGenerator = require('../../core/ContentGenerator');
const sharp = require('sharp');
const path = require('path');

class YourNicheGenerator extends ContentGenerator {
  getSupportedTypes() {
    return Object.keys(this.config.content.types);
  }

  async _generateContent(contentType, options, outputDir) {
    this._ensureOutputDir(outputDir);

    // Get hook for slide 1
    const slide1Hook = this.getSlide1Hook(contentType, options);

    // Generate your slides here using sharp, canvas, or ImageMagick
    const slides = [];
    // ... your slide generation logic ...

    // Build caption
    const hookText = this.generateHook(contentType, options);
    const hashtags = this.getHashtags(contentType);
    const caption = this.buildCaption(hookText, slide1Hook) + '\n\n' + hashtags.join(' ');

    return {
      slides,
      hook: hookText,
      caption,
      outputDir
    };
  }
}

module.exports = YourNicheGenerator;
```

## Run Daily Generation

### Manual

```bash
# Generate content
node cli.js generate my-brand --type showcase

# Generate and auto-post as draft
node cli.js generate my-brand --type showcase --post

# Check schedule
node cli.js schedule my-brand --next
```

### Automated (cron)

```bash
# Add to crontab (runs daily at 2pm)
0 14 * * * cd /path/to/tiktok-content-pipeline && node cli.js generate my-brand --type showcase --post
```

### Analytics

```bash
# Weekly report
node cli.js analytics my-brand --days 7

# Auto-optimize based on results
node cli.js analytics my-brand --days 7 --auto-improve
```

## Multi-Account Setup

Run multiple accounts from one install:

```bash
node cli.js create brand-a --template example-nostalgia
node cli.js create brand-b --template your-custom-template
node cli.js list  # See all accounts
```

Each account gets its own config, output directory, and analytics.
