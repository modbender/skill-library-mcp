# voice-devotional Skill Index

## 📁 File Structure

```
voice-devotional/
├── SKILL.md                          # Technical documentation
├── README.md                         # User guide and quick start
├── INDEX.md                          # This file
├── package.json                      # Node dependencies
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
│
├── scripts/
│   ├── voice-devotional.js          # Main class/orchestrator
│   ├── lesson-generator.js          # Content generation
│   ├── tts-generator.js             # ElevenLabs API integration
│   ├── cli.js                       # Command-line interface
│   └── utils.js                     # Utility functions
│
├── config/
│   ├── devotional-templates.json    # Lesson templates & content
│   ├── voice-settings.json          # Voice presets & settings
│   ├── scripture-library.json       # Built-in scripture data
│   └── prayers-library.json         # Prayer templates
│
├── examples/
│   ├── basic.js                     # Basic usage example
│   └── batch.js                     # Batch generation example
│
├── tests/
│   └── voice-devotional.test.js     # Unit tests
│
└── output/                          # Generated files (gitignored)
```

## 🎯 Quick Reference

### Starting Points
1. **New User?** → Read [README.md](README.md)
2. **Technical Details?** → See [SKILL.md](SKILL.md)
3. **Examples?** → Check [examples/](examples/)
4. **Need Help?** → Run `voice-devotional help`

### Configuration
- **API Setup:** Copy `.env.example` to `.env`, add your ElevenLabs API key
- **Voice Settings:** Modify `config/voice-settings.json` for voice tuning
- **Add Scripture:** Edit `config/scripture-library.json`
- **Add Prayers:** Edit `config/prayers-library.json`

### Key Classes

#### VoiceDevotion (main orchestrator)
- `generateDaily(options)` — Daily devotional
- `generateScripture(options)` — Scripture reading
- `generatePlan(options)` — Multi-day plan
- `generateRomanRoad(options)` — Gospel presentation
- `generateBatch(themes, options)` — Batch generation

#### LessonGenerator (content creation)
- `generateDailyDevotion(theme)` — Create daily content
- `generateScriptureReading(passage, options)` — Scripture with notes
- `generatePlanDay(topic, day, totalDays)` — Plan day content
- `generateRomanRoad(length)` — Gospel presentation content

#### TTSGenerator (ElevenLabs API)
- `generate(text, options)` — Convert text to audio
- `getVoices()` — List available voices
- `getUsage()` — Check API usage
- `validateApiKey()` — Validate API key

## 📖 Common Tasks

### Generate a Daily Devotional
```bash
voice-devotional daily --theme peace --voice josh
```
See: [scripts/cli.js](scripts/cli.js#L156)

### Create a Reading Plan
```bash
voice-devotional plan --topic hope --days 7
```
See: [scripts/voice-devotional.js](scripts/voice-devotional.js#L144)

### Read Scripture Aloud
```bash
voice-devotional scripture --passage "John 3:16"
```
See: [scripts/voice-devotional.js](scripts/voice-devotional.js#L120)

### Generate Multiple Devotionals
```javascript
const vd = new VoiceDevotion({ apiKey: process.env.ELEVEN_LABS_API_KEY });
const results = await vd.generateBatch(['peace', 'hope', 'faith']);
```
See: [scripts/voice-devotional.js](scripts/voice-devotional.js#L395)

## 🔧 Configuration Details

### Voice Presets
Located in: `config/voice-settings.json`

| Voice | Tone | Best For | Speed |
|-------|------|----------|-------|
| josh | devotional | Devotionals, meditation | 1.0x |
| chris | teaching | Teaching, explanations | 1.1x |
| bella | meditation | Sleep, reflection | 0.9x |

### Devotional Themes
Available themes in templates:
- peace, hope, faith, love, strength, joy, grace, trust, forgiveness

Each theme has:
- Scripture reference
- Reflection(s)
- Prayer(s)

See: [config/devotional-templates.json](config/devotional-templates.json)

### ElevenLabs Settings
- **Model:** eleven_monolingual_v1 (or eleven_turbo_v2)
- **Stability:** Controls consistency (0.0-1.0)
- **Similarity Boost:** Voice accuracy (0.0-1.0)
- **Style:** Expressiveness (0.0-1.0)

## 📚 API Reference

### CLI Commands
```bash
voice-devotional daily
voice-devotional scripture
voice-devotional plan
voice-devotional roman-road
voice-devotional generate
voice-devotional batch
voice-devotional help
```

Run `voice-devotional help <command>` for command-specific help.

### Programmatic API
```javascript
const VoiceDevotion = require('./scripts/voice-devotional');
const vd = new VoiceDevotion({ apiKey: 'sk_...' });

// Generate
await vd.generateDaily({ theme: 'peace' });
await vd.generateScripture({ passage: 'John 3:16' });
await vd.generatePlan({ topic: 'hope', days: 7 });
await vd.generateRomanRoad({ voiceId: 'josh' });
await vd.generateBatch(['peace', 'hope', 'faith']);
```

## 🔌 Integration Points

### scripture-curated Skill
Can integrate with scripture-curated for extended verse data:
```javascript
const scripture = await scriptureData.lookup('Romans 8:1-17');
```

### Telegram Integration
Send generated audio to Telegram:
```bash
telegram send --file output/devotional-*.mp3 --chat my-channel
```

## 📊 Output Format

Each generation creates:
1. **MP3 File** — Audio content
2. **JSON Metadata** — Information about the generation

Example metadata:
```json
{
  "id": "devotional-2024-01-15-peace",
  "type": "daily-devotional",
  "audioPath": "./output/devotional-2024-01-15-peace.mp3",
  "duration": 245,
  "durationFormatted": "4:05",
  "transcript": "Good morning...",
  "references": ["Psalm 4:8", "John 14:27"],
  "voicePreset": "josh",
  "generatedAt": "2024-01-15T08:30:00Z"
}
```

## 🧪 Testing

Run tests:
```bash
npm test
```

Test coverage:
- Unit tests for lesson generation
- Voice settings validation
- Text formatting
- Integration tests

## 🚀 Performance Notes

- **Generation time:** 30-120 seconds
- **File size:** ~500KB per minute of audio
- **API cost:** ~$0.30 per devotional
- **Rate limit:** Default 1000ms delay between requests

## 🐛 Troubleshooting

### Common Issues

**"API key not found"**
- Check `.env` file exists
- Verify `ELEVEN_LABS_API_KEY` is set

**"Rate limit exceeded"**
- Increase `--delay` parameter
- Batch process during off-peak hours

**"Audio sounds robotic"**
- Try different voice: `--voice bella`
- Adjust stability in voice-settings.json
- Lower stability (0.1-0.3) for more variance

**"Output file doesn't exist"**
- Check output directory is writable
- Ensure no disk space issues
- Verify ElevenLabs API key is valid

## 📝 Examples

### Daily Devotional Generation
See: [examples/basic.js](examples/basic.js)

### Batch Generation
See: [examples/batch.js](examples/batch.js)

## 🔐 Security Notes

- API keys stored in `.env` (not committed)
- No personal data transmitted
- Audio files stored locally
- Can be shared/deleted safely

## 📄 License

Part of Clawdbot ecosystem. See root LICENSE.

## 🔗 Related Skills

- **scripture-curated** — Scripture data integration
- **telegram-integration** — Send audio to chats
- **meditation-guide** — Schedule devotionals

## 📞 Support

For issues or feature requests:
1. Check README.md for common solutions
2. Review SKILL.md technical documentation
3. Check test cases for usage examples
4. File issue on Clawdbot repository

---

**Skill Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Status:** Active & Maintained
