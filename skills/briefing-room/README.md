# Briefing Room 📻

**Your personal daily news briefing — audio + document.**

Ask for a briefing and get a comprehensive, conversational radio-host-style update on everything that matters today. Configurable location, language, and sections.

## Features

- 📻 **Radio-Host Style** — Natural, conversational monologue — not a list of headlines
- 🔊 **Audio Briefing** — ~10 minute MP3, perfect for your commute
- 📄 **Formatted Document** — DOCX with sections, key facts, and source links
- 🌍 **11 Sections** — Weather → X Trends → Web Trends → World → Politics → Tech → Local → Sports → Markets → Crypto → This Day in History
- 🌐 **Multi-Language** — English (MLX-Audio Kokoro), Slovak, German, or any macOS voice
- ⚙️ **Configurable** — Location, language, voice, sections — all in `~/.briefing-room/config.json`
- 🆓 **100% Free** — No subscriptions, API keys, or paid services

## Quick Start

Just ask your agent:

- "Give me a briefing"
- "Morning update"
- "What's happening today?"
- "Ranný brífing" (Slovak mode)
- "Tägliches Briefing" (German mode)

## First Run

The skill auto-creates a config on first use. Customize your location:

```bash
python3 scripts/config.py set location.city "Vienna"
python3 scripts/config.py set location.latitude 48.21
python3 scripts/config.py set location.longitude 16.37
python3 scripts/config.py set location.timezone "Europe/Vienna"
```

Check your setup:
```bash
python3 scripts/config.py status
```

## What You Get

```
~/Documents/Briefing Room/2026-02-10/
├── briefing-2026-02-10-0830.docx    # Formatted document with sections
└── briefing-2026-02-10-0830.mp3     # Audio briefing (~10 min)
```

## Configuration

All settings in `~/.briefing-room/config.json`:

| Setting | Default | Description |
|---------|---------|-------------|
| `location.city` | Bratislava | City for weather + local news |
| `location.latitude` | 48.15 | Weather API latitude |
| `location.longitude` | 17.11 | Weather API longitude |
| `language` | en | Briefing language |
| `output.folder` | ~/Documents/Briefing Room | Where briefings are saved |
| `sections` | all 11 | Which sections to include |
| `host.name` | (auto = agent name) | Radio host name for the briefing |
| `trends.regions` | us, uk, worldwide | X/Twitter trend regions (getdaytrends.com slugs) |
| `webtrends.regions` | US, GB, worldwide | Google Trends regions (ISO codes) |

### Voice Per Language

```json
{
  "voices": {
    "en": {"engine": "mlx", "mlx_voice": "af_heart", "speed": 1.05},
    "sk": {"engine": "builtin", "builtin_voice": "Laura (Enhanced)", "builtin_rate": 220},
    "de": {"engine": "builtin", "builtin_voice": "Petra (Premium)", "builtin_rate": 200}
  }
}
```

Add any language — just pick a voice from `say -v '?'` on macOS.
If you set a language without a voice config, it auto-detects a matching macOS voice.

**Supported out of the box:** English, Slovak, German.
**Works with any language** macOS supports — French, Spanish, Italian, Japanese, Chinese, etc.

## Sections

| # | Section | Source |
|---|---------|--------|
| 1 | 🌤️ Weather | Open-Meteo API (your location) |
| 2 | 🐦 Trending on X | getdaytrends.com (real-time X/Twitter trends) |
| 3 | 🔍 Web Trends | Google Trends RSS (what people are searching) |
| 4 | 🌍 World | Web search |
| 5 | 🏛️ Politics | Web search |
| 6 | 💻 Tech & AI | Web search |
| 7 | 🏠 Local | Web search (your city) |
| 8 | ⚽ Sports | Web search |
| 9 | 📈 Markets | Web search + APIs |
| 10 | ₿ Crypto | Coinbase API + Web search |
| 11 | 📜 This Day in History | Agent knowledge (no API needed) |

## Dependencies

**Required:**
- macOS (uses `afplay`, `say`, `curl` — all built-in)
- OpenClaw with `web_search`

**Recommended (enhance quality):**
- [MLX-Audio Kokoro](https://github.com/ml-explore/mlx-audio) — fast English TTS on Apple Silicon
- `pandoc` — DOCX generation (`brew install pandoc`)
- `ffmpeg` — MP3 conversion (`brew install ffmpeg`)

**No pip packages required** — included scripts use only Python standard library.

**Always available:**
- Apple `say` — multilingual TTS fallback (built into macOS)

## Install

```bash
clawhub install briefing-room
```
