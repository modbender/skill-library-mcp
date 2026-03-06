# voice-devotional Skill - Directory Structure

```
voice-devotional/
│
├─── 📄 Documentation (6 files - ~35KB)
│    ├── SKILL.md                   # Complete technical specification
│    ├── README.md                  # User guide and quick start  
│    ├── INDEX.md                   # File structure and API reference
│    ├── IMPLEMENTATION.md          # Implementation details and checklist
│    ├── DEPLOYMENT.md              # Deployment and installation guide
│    └── BUILD_SUMMARY.txt          # Build summary (text format)
│
├─── 📜 Scripts (4 files - ~37KB)
│    ├── scripts/voice-devotional.js     # Main orchestrator class
│    │   ├─ generateDaily()              # Daily devotional generation
│    │   ├─ generateScripture()          # Scripture reading
│    │   ├─ generatePlan()               # Multi-day reading plans
│    │   ├─ generateRomanRoad()          # Gospel presentation
│    │   ├─ generateBatch()              # Batch generation
│    │   └─ [utilities]                  # Format & metadata functions
│    │
│    ├── scripts/lesson-generator.js     # Content generation engine
│    │   ├─ generateDailyDevotion()     # Daily content
│    │   ├─ generateScriptureReading()  # Scripture with notes
│    │   ├─ generatePlanDay()           # Plan day content
│    │   ├─ generateRomanRoad()         # Gospel content
│    │   └─ [lookups]                   # Scripture/prayer/reflection lookups
│    │
│    ├── scripts/tts-generator.js        # ElevenLabs TTS API
│    │   ├─ generate()                   # Text-to-speech
│    │   ├─ generateChunked()            # Long text handling
│    │   ├─ getVoices()                  # List voices
│    │   ├─ getUsage()                   # Check API usage
│    │   └─ validateApiKey()             # Validate API key
│    │
│    └── scripts/cli.js                  # Command-line interface
│        ├─ daily command                # Generate daily devotional
│        ├─ scripture command            # Read scripture
│        ├─ plan command                 # Create reading plan
│        ├─ roman-road command           # Gospel presentation
│        ├─ batch command                # Batch generation
│        └─ help system                  # Full help with examples
│
├─── ⚙️  Configuration (4 JSON files - ~32KB)
│    │
│    ├── config/devotional-templates.json    # Content templates
│    │   ├─ daily-devotional              # 10 theme templates
│    │   │  ├─ peace                      # Template + scripture + reflection
│    │   │  ├─ hope
│    │   │  ├─ faith
│    │   │  ├─ love
│    │   │  └─ [6 more themes]
│    │   ├─ reading-plan                  # 3 complete 7-day plans
│    │   │  ├─ hope [7 days with topics]
│    │   │  ├─ faith [7 days with topics]
│    │   │  └─ peace [7 days with topics]
│    │   └─ reflections                   # Reflection library
│    │
│    ├── config/voice-settings.json          # Voice presets
│    │   ├─ josh                          # Devotional voice
│    │   ├─ chris                         # Teaching voice
│    │   ├─ bella                         # Meditation voice
│    │   ├─ adam                          # Conversational voice
│    │   ├─ sam                           # Narrative voice
│    │   └─ defaults & presets
│    │
│    ├── config/scripture-library.json       # 20 scripture passages
│    │   ├─ John 3:16                    # With full text
│    │   ├─ Romans 3:23                  # With context & notes
│    │   ├─ Psalm 23
│    │   ├─ 1 Peter series
│    │   └─ [16 more key passages]
│    │
│    └── config/prayers-library.json         # Prayer templates
│        ├─ peace [multiple variations]
│        ├─ hope [multiple variations]
│        ├─ faith
│        ├─ love
│        └─ [6 more themes]
│
├─── 📚 Examples (3 files - ~3KB)
│    ├── examples/basic.js                # Complete usage example
│    │   ├─ Generate daily devotional
│    │   ├─ Generate scripture reading
│    │   ├─ Generate reading plan
│    │   └─ Generate roman road
│    │
│    ├── examples/batch.js                # Batch generation example
│    │   ├─ Batch multiple themes
│    │   ├─ Rate limiting
│    │   └─ Manifest output
│    │
│    └── examples/themes.json             # Sample theme list
│
├─── 🧪 Tests (1 file - 8.5KB, 25+ tests)
│    └── tests/voice-devotional.test.js
│        ├─ LessonGenerator tests
│        ├─ VoiceDevotion tests
│        ├─ Format utility tests
│        ├─ Voice settings tests
│        ├─ Integration tests
│        └─ Error handling tests
│
├─── 🔧 Support Files (4 files)
│    ├── package.json                    # Node.js dependencies & scripts
│    ├── .env.example                    # Configuration template
│    ├── .gitignore                      # Git ignore rules
│    └── BUILD_SUMMARY.txt               # This build summary
│
├─── 📁 output/ (generated at runtime)
│    └── [Generated MP3 files and metadata JSON]
│
└─── .git/ (repository metadata)
     └── [Git history and configuration]
```

## File Statistics

| Category | Files | Size | LOC |
|----------|-------|------|-----|
| Documentation | 6 | ~35KB | ~3,000 |
| Scripts | 4 | ~37KB | ~2,000 |
| Configuration | 4 | ~32KB | ~1,200 |
| Examples | 3 | ~3KB | ~150 |
| Tests | 1 | ~8.5KB | ~300 |
| Support | 4 | ~2KB | ~100 |
| **TOTAL** | **22** | **~120KB** | **~6,700** |

## Quick Navigation

### For Users
- Start with: `README.md`
- Commands: Run `voice-devotional help`
- Examples: Check `examples/` folder

### For Developers
- Technical details: `SKILL.md`
- File structure: `STRUCTURE.md` (this file)
- API reference: `INDEX.md`
- Implementation: `IMPLEMENTATION.md`

### For Integration
- API: `scripts/voice-devotional.js`
- Content generation: `scripts/lesson-generator.js`
- TTS: `scripts/tts-generator.js`
- CLI: `scripts/cli.js`

### For Content
- Templates: `config/devotional-templates.json`
- Scripture: `config/scripture-library.json`
- Prayers: `config/prayers-library.json`
- Voices: `config/voice-settings.json`

## File Dependencies

```
CLI (cli.js)
    ↓
Main Class (voice-devotional.js)
    ↓
├─ Lesson Generator (lesson-generator.js)
│   ├─ Scripture Library (config/scripture-library.json)
│   ├─ Templates (config/devotional-templates.json)
│   └─ Prayers Library (config/prayers-library.json)
│
└─ TTS Generator (tts-generator.js)
    └─ Voice Settings (config/voice-settings.json)
        └─ ElevenLabs API

Output
    ├─ MP3 Audio Files
    └─ JSON Metadata
```

## Module Structure

```javascript
// Main Entry Point
const VoiceDevotion = require('./scripts/voice-devotional.js');

// Internally uses:
const LessonGenerator = require('./scripts/lesson-generator.js');
const TTSGenerator = require('./scripts/tts-generator.js');

// Which load:
const templates = require('./config/devotional-templates.json');
const voices = require('./config/voice-settings.json');
const scripture = require('./config/scripture-library.json');
const prayers = require('./config/prayers-library.json');
```

## Data Flow

```
User Input
    ↓
CLI Parser (cli.js)
    ↓
VoiceDevotion Class
    ├─→ LessonGenerator.generateDailyDevotion()
    │   ├─→ Load templates
    │   ├─→ Load scripture
    │   ├─→ Load reflections
    │   └─→ Load prayers
    │       ↓
    │   Content Object
    │
    └─→ TTSGenerator.generate()
        ├─→ Format text
        ├─→ Chunk if needed
        └─→ Call ElevenLabs API
            ↓
        Audio Buffer
            ↓
        Write to File
            ↓
        Generate Metadata
            ↓
        Return Result

Output
    ├─ MP3 Audio File
    ├─ JSON Metadata
    └─ Formatted Result
```

## Configuration Hierarchy

```
Environment Variables (.env)
    ↓
Package Configuration (package.json)
    ↓
Voice Settings (voice-settings.json)
    ├─ Individual voices
    └─ Default presets
    
Devotional Templates (devotional-templates.json)
    ├─ Daily templates per theme
    ├─ Reading plan structures
    └─ Reflection collections

Scripture Data (scripture-library.json)
    └─ Built-in scripture passages

Prayer Data (prayers-library.json)
    └─ Built-in prayer templates
```

## API Hierarchy

```
VoiceDevotion
├─ generateDaily(options)
├─ generateScripture(options)
├─ generatePlan(options)
├─ generateRomanRoad(options)
├─ generateBatch(themes, options)
├─ generateAudio(text, voice, options)
├─ saveMetadata(metadata, dir)
└─ [utility methods]

LessonGenerator
├─ generateDailyDevotion(theme)
├─ generateScriptureReading(passage, options)
├─ generatePlanDay(topic, day, totalDays)
├─ generateRomanRoad(length)
├─ getScripture(reference)
├─ getReflection(theme, key)
├─ getPrayer(theme, key)
└─ [lookup methods]

TTSGenerator
├─ generate(text, options)
├─ generateSingle(text, options)
├─ generateChunked(text, options)
├─ getVoices()
├─ getUsage()
└─ validateApiKey()
```

## Testing Coverage

```
Tests (voice-devotional.test.js)
├─ LessonGenerator Tests
│  ├─ Daily devotion generation
│  ├─ Scripture reading
│  ├─ Plan generation
│  ├─ Roman Road
│  └─ Lookup functions
│
├─ VoiceDevotion Tests
│  ├─ Format utilities
│  ├─ Voice settings
│  ├─ Initialization
│  └─ Error handling
│
└─ Integration Tests
   ├─ Full workflow
   ├─ API validation
   └─ Edge cases
```

## Key Features Location

| Feature | File |
|---------|------|
| Daily devotional generation | scripts/voice-devotional.js:generateDaily() |
| Scripture reading | scripts/voice-devotional.js:generateScripture() |
| Reading plans | scripts/voice-devotional.js:generatePlan() |
| Roman Road presentation | scripts/voice-devotional.js:generateRomanRoad() |
| Batch generation | scripts/voice-devotional.js:generateBatch() |
| ElevenLabs integration | scripts/tts-generator.js:generate() |
| CLI interface | scripts/cli.js |
| Content templates | config/devotional-templates.json |
| Voice presets | config/voice-settings.json |
| Scripture data | config/scripture-library.json |
| Prayer templates | config/prayers-library.json |

---

**Last Updated:** 2024-01-15  
**Skill Version:** 1.0.0  
**Status:** Complete and Production-Ready
