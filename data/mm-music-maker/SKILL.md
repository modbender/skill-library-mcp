---
name: mm-music-maker
description: Create music with MiniMax music models (e.g., music-2.5). Use when generating songs or instrumental tracks from lyrics and style prompts, or when integrating MiniMax Music Generation API into scripts.
---

# MiniMax Music Maker

Use this skill to generate music with MiniMax's Music Generation API. All usage and outputs are designed for **music-2.5** unless specified otherwise.

## Quick start

1) Set the API key:
```bash
export MINIMAX_MUSIC_API_KEY="your_api_key"
```

2) Generate music from lyrics (and optional prompt):
```bash
python scripts/generate_music.py \
  --lyrics "[Verse]\n...\n[Chorus]\n..." \
  --prompt "indie folk, melancholic, introspective" \
  --output ./output.mp3
```

## Script location

- `scripts/generate_music.py` — main generator (lyrics + prompt → audio)
- `scripts/utils_audio.py` — hex decoding + save helpers

## References

Read **references/minimax_music_api.md** for:
- Endpoint, auth header, payload schema
- Required/optional fields
- Output formats (hex/url) and constraints

## Core Modes

This skill supports **3 generation modes**:

### 1. Standard Song (with lyrics)
- User provides or wants lyrics + music
- Use structured lyrics with prompt for style

### 2. Pure Music (Instrumental)
- User requests: "纯音乐", "纯音乐，无人声", "pure music", "instrumental"
- No lyrics, just instrumental arrangement
- See "Pure Music Generation" section below

### 3. Melodic Chanting/Humming
- User requests: "哼唱", "吟唱", "humming", "chanting"
- Music with vocal syllables instead of full lyrics
- See "Melodic Chanting Generation" section below

## Notes

- `lyrics` is **required** by the API.
- `prompt` is optional for `music-2.5`.
- `output_format` defaults to `hex` (inline audio). Use `url` if you prefer a download URL.
- URLs expire (24h). Download immediately if using `url`.

## Prompt crafting (Important)

**Core Principles**: Use "descriptions" instead of "commands", keep it structured, clear, and parseable.

### Required Elements (Recommended)
- **Genre/Subgenre** (with era or region)
- **Mood/Emotion** (2-3 emotional descriptors)
- **Tempo/BPM** (specify BPM if possible)
- **Key Instruments** (3-5 key instruments/timbres)
- **Vocals** (vocal type, processing, or instrumental)
- **Use case** (purpose/scene)

### Optional Enhancements
- **Structure** (section structure)
- **References** (1-2 style references)
- **Avoid/Negative** (exclusions)

### Prompt Templates
**Basic Template (Beginner)**
```
[Genre], [Mood], [Tempo/BPM], [Key Instruments], [Vocal Style]
```

**Standard Template (Recommended)**
```
Genre: [Specific genre + era]
Mood: [2-3 descriptors]
Tempo: [BPM or speed]
Instruments: [3-5 key instruments]
Vocals: [Type or instrumental only]
Use case: [scene/usage]
Avoid: [unwanted elements]
References: [1-2 artists/songs]
```

**Advanced Template (Production Brief)**
```
Genre: … | Era: …
BPM: … | Key: …
Mood: ... (can include emotional arc, e.g., "from restrained to explosive")
Lead: …
Rhythm: …
Bass: …
Texture: …
Vocals: …
Structure: Intro / Verse / Chorus / Bridge / Outro
Avoid: …
Reference: …
```

### Structure Tags (in lyrics)
```
[Intro]
[Verse]
[Pre-Chorus]
[Chorus]
[Bridge]
[Outro]
[Instrumental]
```

### Negative Prompt Examples
- `No vocals` / `Instrumental only`
- `Avoid autotune`
- `No distorted guitars`
- `Avoid heavy reverb`
- `No trap hi-hats`

### Common Issue Fixes
- **Style inaccurate**: Add "era + sub-genre + instrument anchors + reference artists"
- **Rhythm wrong**: Specify BPM + rhythm description (e.g., four-on-the-floor)
- **Intro too generic**: Write [Intro] in lyrics and describe the opening
- **Vocals off**: Move Vocals to front of prompt and add negative constraints

## Prompt Quality Checklist
- Contains: Genre / Mood / BPM / Instruments / Vocals / Use case
- Check for conflicts (e.g., "very slow + high energy")
- Has Avoid items to filter unwanted elements
- Is structured (avoid long prose paragraphs)

---

## Pure Music Generation

Use this mode when user wants instrumental tracks **without lyrics**.

### Detection Keywords
- 纯音乐、纯音乐无人声、无人声
- pure music、instrumental、no lyrics
- 背景音乐、轻音乐、器乐
- 无歌词

### Prompt Format
```
pure music, [scene/style description], no lyrics
```

### Lyrics Field
Use placeholder tags: `[intro] [outro]`

### Important Notes
⚠️ **Duration**: Pure music tracks are typically **shorter (1-2 minutes)** because there's no lyrics to guide the musical progression.

### Pure Music Prompt Examples

| # | Prompt | Scene |
|---|--------|-----------|
| 1 | pure music, coffee shop, no lyrics | 咖啡馆氛围 |
| 2 | pure music, rainy night, no lyrics | 雨夜 |
| 3 | pure music, morning sunshine, no lyrics | 晨光 |
| 4 | pure music, jazz bar, no lyrics | 爵士酒吧 |
| 5 | pure music, city walk, no lyrics | 城市漫步 |
| 6 | pure music, night drive, no lyrics | 夜间驾驶 |
| 7 | pure music, piano solo, no lyrics | 钢琴独奏 |
| 8 | pure music, lofi chill, no lyrics | Lo-Fi轻松 |
| 9 | pure music, bookstore, no lyrics | 书店 |
| 10 | pure music, cafe closing time, no lyrics | 咖啡馆打烊 |

### CLI Examples

Generate pure music for coffee shop:
```bash
python scripts/generate_music.py \
  --lyrics "[intro] [outro]" \
  --prompt "pure music, coffee shop, no lyrics" \
  --output ./coffee_shop.mp3
```

Generate rainy night atmosphere:
```bash
python scripts/generate_music.py \
  --lyrics "[intro] [outro]" \
  --prompt "pure music, rainy night, no lyrics" \
  --output ./rainy_night.mp3
```

Generate piano solo:
```bash
python scripts/generate_music.py \
  --lyrics "[intro] [outro]" \
  --prompt "pure music, piano solo, no lyrics" \
  --output ./piano_solo.mp3
```

---

## Melodic Chanting/Humming Generation

Use this mode when user wants music with **vocal syllables** instead of full lyrics (humming, chanting).

### Detection Keywords
- Humming, chanting, vocalizing
- humming、chanting
- Healing, vocal accompaniment
- Melodic
- Harmony, ooh ah la

### Prompt Format
```
pure music, [风格/场景描述], no lyrics
```

### Lyrics Field (Syllable Patterns)

Use vocal syllables instead of words:

| Syllable Pattern | Vibe |
|-----------------|----------|
| `ah, ah, ah, ah...` | 柔和吟唱 |
| `la, la, la, la...` | 旋律哼唱 |
| `mmm, mmm, mmm...` | 治愈系哼鸣 |
| `ooh, ooh, ooh...` | 空灵吟唱 |
| `hum, hum, hum...` | 持续哼唱 |

### Lyrics Structure Template
```
[intro] [verse] [chorus] [verse] [outro]
```
Replace sections with chosen syllables.

### Chanting Prompt Examples

| Scene | Prompt | Lyrics |
|-------|--------|--------|
| Healing | pure music, healing, relaxing, no lyrics | `[intro] mmm, mmm, mmm... [verse] mmm, mmm, mmm... [outro]` |
| Meditation | pure music, meditation, calming, no lyrics | `[intro] ooh, ooh, ooh... [verse] ooh, ooh, ooh... [outro]` |
| Happy | pure music, happy, uplifting, no lyrics | `[intro] la, la, la, la... [chorus] la, la, la, la... [outro]` |
| Mystical | pure music, mystical, ethereal, no lyrics | `[intro] ah, ah, ah... [verse] ah, ah, ah... [outro]` |

### CLI Examples

Generate healing chant music:
```bash
python scripts/generate_music.py \
  --lyrics "[intro] mmm, mmm, mmm... [verse] mmm, mmm, mmm... [chorus] mmm, mmm, mmm... [outro]" \
  --prompt "pure music, healing, relaxing, no lyrics" \
  --output ./healing_chant.mp3
```

Generate meditation chant:
```bash
python scripts/generate_music.py \
  --lyrics "[intro] ooh, ooh, ooh... [verse] ooh, ooh, ooh... [outro]" \
  --prompt "pure music, meditation, calming, no lyrics" \
  --output ./meditation.mp3
```

Generate happy humming:
```bash
python scripts/generate_music.py \
  --lyrics "[intro] la, la, la... [verse] la, la, la... [chorus] la, la, la... [outro]" \
  --prompt "pure music, happy, uplifting, no lyrics" \
  --output ./happy_humming.mp3
```

---

## Mode Detection Logic

When user requests music, detect the mode:

1. **Standard Song** → User provides lyrics OR asks for "song with lyrics"
2. **Pure Music** → Keywords: "纯音乐", "pure music", "instrumental", "no lyrics", "无人声"
3. **Chanting/Humming** → Keywords: "哼唱", "吟唱", "humming", "chanting", "治愈系"

### Decision Flow
```
User Request
    ↓
Contains "纯音乐"/"pure music"/"instrumental"?
    ├─ Yes → Is "哼唱"/"humming" also mentioned?
    │   ├─ Yes → Melodic Chanting Mode
    │   └─ No → Pure Music Mode
    └─ No → Standard Song Mode (requires lyrics)
```

## Recommended CLI patterns

Generate MP3 (hex response → file):
```bash
python scripts/generate_music.py \
  --lyrics "[Intro]\n..." \
  --prompt "cinematic, uplifting" \
  --output ./music.mp3 \
  --format mp3 \
  --bitrate 256000 \
  --sample-rate 44100
```

Generate with structured prompt fields (auto-build):
```bash
python scripts/generate_music.py \
  --lyrics "[Verse]\n..." \
  --genre "1980s synthwave" \
  --mood "nostalgic, energetic" \
  --bpm 120 \
  --instruments "analog synths, drum machine, bass guitar" \
  --vocals "female vocals" \
  --use-case "retro game trailer" \
  --avoid "no acoustic guitar" \
  --references "The Midnight, FM-84" \
  --output ./music.mp3
```

Generate and download from URL:
```bash
python scripts/generate_music.py \
  --lyrics "[Verse]\n..." \
  --prompt "lofi, rainy night" \
  --output ./music.mp3 \
  --output-format url \
  --download
```

---

## API Reference

For detailed API documentation (endpoints, authentication, request/response formats), see:

**`references/minimax_music_api.md`**

Key points for all modes:

- **Endpoint**: `POST https://api.minimaxi.com/v1/music_generation`
- **Auth**: `Authorization: Bearer <token>`
- **Model**: `music-2.5`
- **lyrics**: Required field - use `[intro] [outro]` for pure music, or syllable patterns for chanting

### Quick API Payload Examples

**Standard Song:**
```json
{
  "model": "music-2.5",
  "prompt": "indie folk, melancholic, introspective",
  "lyrics": "[verse]\n...\n[chorus]\n..."
}
```

**Pure Music:**
```json
{
  "model": "music-2.5",
  "prompt": "pure music, coffee shop, no lyrics",
  "lyrics": "[intro] [outro]"
}
```

**Melodic Chanting:**
```json
{
  "model": "music-2.5",
  "prompt": "pure music, healing, relaxing, no lyrics",
  "lyrics": "[intro] mmm, mmm, mmm... [verse] mmm, mmm, mmm... [outro]"
}
```

### Response Format

- `data.audio`: hex string (default) or URL (valid 24 hours)
- `data.status`: generation status
- `extra_info`: duration, sample rate, channels, bitrate, size
- `base_resp.status_code`: `0` on success
