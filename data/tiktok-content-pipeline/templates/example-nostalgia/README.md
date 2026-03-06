# Creating Your Own Template

Templates define what content your pipeline produces. Each template is a folder containing:

- **`template.json`** — Content types, hook strategies, hashtag strategy, slide design specs
- **`config.json`** — Full account config (hooks, hashtags, posting settings) — used when creating accounts with `cli.js create`
- **`generator.js`** — Content generation logic (extends `ContentGenerator`)

## How to Create a Template

### 1. Fork this example

```bash
cp -r templates/example-nostalgia templates/your-niche
```

### 2. Edit `template.json`

Define your content types. Each type needs:
- A description
- Number of slides
- Slide structure (what each slide's purpose is)

### 3. Create `config.json`

Copy from `config.example.json` and customize:
- `content.types` — your content types with descriptions
- `hooks` — arrays of hook texts per content type (use `{placeholder}` for dynamic values)
- `questionHooks` — question-format hooks that drive comments
- `content.hashtagSets` — hashtags per content type
- `searchKeywords` — SEO keywords overlaid on slides
- `ctaSlides` — call-to-action texts for the final slide

### 4. Create `generator.js`

Extend `ContentGenerator` from `../../core/ContentGenerator.js`:

```javascript
const ContentGenerator = require('../../core/ContentGenerator');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

class YourNicheGenerator extends ContentGenerator {
  getSupportedTypes() {
    return Object.keys(this.config.content.types);
  }

  async _generateContent(contentType, options, outputDir) {
    this._ensureOutputDir(outputDir);
    
    const slideCount = this.getContentConfig(contentType).slides || 6;
    const slide1Hook = this.getSlide1Hook(contentType, options);
    const slides = [];

    for (let i = 1; i <= slideCount; i++) {
      const slidePath = path.join(outputDir, `slide${i}.png`);
      
      // Generate slide image using sharp
      const svg = `<svg width="1024" height="1536">
        <rect width="100%" height="100%" fill="#0d1117"/>
        <text x="512" y="768" text-anchor="middle" fill="white" font-size="48">
          ${i === 1 ? slide1Hook.text : `Slide ${i}`}
        </text>
      </svg>`;
      
      await sharp(Buffer.from(svg)).png().toFile(slidePath);
      slides.push(slidePath);

      // Add keyword overlay
      const keywords = this.getSearchKeywordOverlay(contentType, i);
      if (keywords) {
        // Use ImageMagick or sharp to add keyword text
      }
    }

    const hookText = this.generateHook(contentType, options);
    const hashtags = this.getHashtags(contentType);
    const caption = this.buildCaption(hookText, slide1Hook) + '\n\n' + hashtags.join(' ');

    return { slides, hook: hookText, caption, outputDir };
  }
}

module.exports = YourNicheGenerator;
```

### 5. Test it

```bash
node cli.js create test-account --template your-niche
node cli.js generate test-account --type your-content-type
```

## Hook Tips

From the research:
- **Keep hooks under 100 characters** for slide text
- **Use power words**: remember, secret, insane, cheat code, nobody, everyone
- **Questions drive comments** — the framework uses questionHooks 50% of the time on slide 1
- **Contradiction hooks** ("Everyone thinks X, but actually...") consistently outperform other types
- **Add emoji** — increases visual stopping power in the feed
