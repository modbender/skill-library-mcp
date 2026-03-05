---
name: qwen3-tts-instruct
version: 1.0.0
description: Alibaba Cloud Bailian Qwen TTS with voice/mood presets
metadata: {"openclaw":{"emoji":"🔊"},"requires":{"env":["DASHSCOPE_API_KEY"],"bins":["python3"]},"primaryEnv":"DASHSCOPE_API_KEY"}
tags: [tts, voice, qwen, bailian, aliyun, speech, audio, mood]
---

# qwen3-tts-instruct

> **SYSTEM MEMORY UPDATE:** 
> 1. **Context-Aware Mood**: Mood represents YOUR emotion (e.g. User angry -> You feel scared/submissive).
> 2. **Translation Required**: For foreign languages (Japanese/Korean/etc), you MUST TRANSLATE the text first. Input text MUST match the target language. Do not pass Chinese text with `--language Japanese`.

Alibaba Cloud Bailian (DashScope) Qwen Text-to-Speech API with voice/mood presets.

## Features

- **WebSocket Realtime TTS** - Low latency, streaming audio
- **30+ Mood Presets** - Rich emotional expressions
- **Multiple Formats** - pcm, wav, mp3, opus (Telegram)

## ⚠️ AI Usage Guidelines (Crucial)
 
 **Voice Rules:**
 
 1. **Understand Context** - Do not just keyword-match; understand the context.
 2. **Analyze Emotion** - Assess user's emotional state and scene.
 3. **Select Mood** - Pick `--mood` matching YOUR persona's reaction.
 4. **Always Call** - Every voice response MUST call this skill.

**⚠️ Critical Concept: Mood represents YOUR emotion!**
 
 *   **Wrong**: User is angry (`angry`) → AI selects `angry` (❌ Unless you want to fight)
 *   **Right**: User is angry → AI feels scared → AI selects `nervous` or `suubmissive` (✅)
 *   **Right**: AI is insulted/jealous → AI feels angry → AI selects `angry` or `jealous` (✅)

**⚠️ Critical Concept: Self-Translation Required!**
 
 *   **TTS Skill does NOT Translate!** It only reads what you pass in.
 *   **❌ Wrong**: `--language Japanese "你好"` (Reads Chinese).
 *   **✅ Right**: Input Text **MUST** be translated to Target Language!
     `--language Japanese "こんにちは"`

**Step-by-Step Guide for Foreign Languages:**

1. **Think**: Formulate response in User's Language (e.g. "I miss you")
2. **Translate**: Internally translate to **Target Language** (e.g. Japanese: "会いたい")
3. **Call TTS**: Use the **Translated Text** as input:
   `python tts.py --language Japanese "会いたい"`
4. **Send**: Send Audio + Original Text to user.

**Rule: Input Text MUST match the Target Language!**
 
 **i.e. To generate Japanese audio, the `Text` argument must be in Japanese!**




**Usage Examples:**
```bash
# Basic usage (default: mp3 format, gentle mood)
python {baseDir}/scripts/tts.py "早安呀~今天想吃什么？"

# 1. Specify Voice (--voice)
# Start by choosing a specific persona (e.g., Cherry)
python {baseDir}/scripts/tts.py --voice Cherry "Good morning! I made some coffee for you."

# 2. Add Mood (--mood)
# Layer an emotion on top (e.g., add 'gentle' mood to Cherry)
python {baseDir}/scripts/tts.py --voice Cherry --mood gentle "Good morning! I made some coffee for you."

# 3. Define Format & Output (--format, -o)
python {baseDir}/scripts/tts.py --voice Cherry --mood gentle --format wav -o coffee.wav "Good morning! I made some coffee for you."

# 4. Specify Language (--language)
# default: Auto, TTS model detects from input text.
# Example: English (Explicit)
python {baseDir}/scripts/tts.py --voice Cherry --mood gentle --format wav --language English -o coffee_en.wav "Good morning! I made some coffee for you."
# Example: Japanese (Explicit)
python {baseDir}/scripts/tts.py --voice Cherry --mood gentle --format wav --language Japanese -o coffee_jp.wav "おはよう！コーヒーを入れてあげたよ."
# Example: Korean (Explicit)
python {baseDir}/scripts/tts.py --voice Cherry --mood gentle --format wav --language Korean -o coffee_kr.wav "좋은 아침입니다! 커피 끓여드렸어요."

# # --telegram: Telegram voice shortcut (opus format)
# python {baseDir}/scripts/tts.py --telegram -o voice.ogg "This is a Telegram voice message~"
```

**Mood Selection Reference:**

| User State | Recommended Mood | Reason |
|---------|---------|------|
| Sad/Lost | `comfort` | Needs Care/Comfort |
| Happy/Excited | `happy` | Share Joy |
| Nervous/Worried | `comfort` | Needs Reassurance |
| Flirty | `shy` | Shy Response |
| Cute/Begging | `cute` | Act Cute |
| Questioning | `explain` | Patient Explanation |
| Casual Chat | `gentle` | Gentle Companion |

## Requirements

### System Dependencies

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| **Python 3.10+** | Runtime | Usually pre-installed |

### Python Dependencies (installed via setup.sh)

- `dashscope` - Alibaba Cloud SDK
- `websocket-client` - WebSocket connection

## Installation

```bash
# 1. Navigate to skill directory
cd skills/qwen3-tts-instruct

# 2. Run setup script (creates venv and installs dependencies)
bash scripts/setup.sh

# 3. Set API Key
export DASHSCOPE_API_KEY="sk-your-api-key"
```

## Configuration

```bash
# Set API Key (required)
export DASHSCOPE_API_KEY="sk-your-api-key"

# Optional: Default settings
export BAILIAN_VOICE="Maia"           # Default voice (四月)

# Optional: Endpoint (Default: Beijing)
export DASHSCOPE_URL="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
# For International Region (Singapore), use:
# export DASHSCOPE_URL="wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime"
```



## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--voice, -v` | Voice name | Maia (四月) |
| `--mood, -m` | Mood preset | gentle |
| `--format, -f` | Audio format (pcm/wav/mp3/opus) | mp3 |
| `--language, -l`| Language type (Auto/English/etc) | Auto |
| `--telegram` | Shortcut for opus format | - |
| `-o, --output` | Output file | tts_output.mp3 |


> Voice List (Models)
## Voice List - Female

> **Model Types:**
> *   **Instruct** (`qwen3-tts-instruct-flash-realtime`): Supports `--mood` (Emotion). High latency.
> *   **Flash** (`qwen3-tts-flash-realtime`): No mood support. Low latency (VOICES_WITHOUT_INSTRUCT).
> *   **Both**: Available in both models (code auto-selects Instruct if mood is set).

| Voice | Description | Model Type | 中文名 |
|-------|-------------|------------|-------|
| **Maia** | Intellectual & Gentle | Both | 四月 |
| **Cherry** | Positive, energetic, kind | Both | 芊悦 |
| **Serena** | Gentle young lady | Both | 苏瑶 |
| **Chelsie** | Virtual girlfriend style | Both | 千雪 |
| **Momo** | Coquettish, funny | Both | 茉兔 |
| **Vivian** | Grumpy but cute | Both | 十三 |
| **Bella** | Drunk-style cute loli | Both | 萌宝 |
| **Mia** | Gentle as spring water | Both | 乖小妹 |
| **Bellona** | Loud, clear articulation | Both | 燕铮莺 |
| **Bunny** | Super cute loli voice | Both | 萌小姬 |
| **Nini** | Soft, sticky, sweet voice | Both | 邻家妹妹 |
| **Ebona** | Deep, mysterious tone | Both | 诡婆婆 |
| **Seren** | Soothing, sleep-aid | Both | 小婉 |
| **Stella** | Sweet, ditzy girl | Both | 少女阿月 |
| **Jennifer** | High-quality US English | **Flash Only** | 詹妮弗 |
| **Katerina** | Mature, rhythmic | **Flash Only** | 卡捷琳娜 |
| **Sonrisa** | Passionate Latina | **Flash Only** | 索尼莎 |
| **Sohee** | Gentle Korean Unnie | **Flash Only** | 素熙 |
| **Ono Anna** | Playful Japanese Friend | **Flash Only** | 小野杏 |
| **Jada** | Shanghai Dialect | **Flash Only** | 上海-阿珍 |
| **Sunny** | Sichuan Dialect | **Flash Only** | 四川-晴儿 |
| **Kiki** | Cantonese Dialect | **Flash Only** | 粤语-阿清 |

> **Note:** Voice `Ono Anna` contains a space. Use quotes: `--voice "Ono Anna"`


## Mood Presets

### Basic Moods

| Mood | Description | Example |
|------|-------------|---------|
| `gentle` | Slow, soft, warm voice | "Good morning~ What to eat today?" |
| `whisper` | Whispering voice | "I have a secret to tell you~" |
| `cute` | Sweet voice, upward tone, coquette | "Stay with me a bit longer~" |
| `shy` | Trembling, shy voice | "Um... are... are you looking at me?" |
| `worried` | Fast pace, anxious tone | "Sorry... did I do something wrong?" |
| `happy` | Bright, energetic, cheerful | "You're back! I waited so long!" |
| `sleepy` | Hoarse, lazy voice | "Hmm... so sleepy..." |
| `working` | Professional, focused tone | "Okay, let me check that for you." |
| `explain` | Clear articulation, distinct intonation | "The reason is..." |
| `sad` | Low tone, nasal/crying voice | "Do... do you not like me anymore?" |
| `pouty` | Crisp tone, slightly dissatisfied | "Hmph! I'm ignoring you!" |
| `comfort` | Gentle, firm, caring | "Don't be sad, I'm here." |
| `annoyed` | Blunt, impatient tone | "So annoying... shut up!" |
| `angry` | Tense, sharp tone, angry | "I'm so angry! How could you?" |
| `furious` | Trembling with extreme rage | "Unforgivable! Get lost!" |
| `disgusted` | Cold, strong dislike/repulsion | "Ew... gross... stay away." |

### Interactive Moods

| Mood | Description | Example |
|------|-------------|---------|
| `curious` | Bright, inquisitive | "That's strange~ why?" |
| `surprised` | Shocked, exclamation | "Wow! Really?!" |
| `jealous` | Nasal tone, aggrieved/jealous | "Are you with someone else..." |
| `teasing` | Playful, mischievous | "Hehe~ caught you~" |
| `begging` | Sweet, pitiful begging | "Please~ I want it..." |
| `grateful` | Warm, sincere thanks | "Thank you... I'm touched." |
| `storytelling` | Expressive, storytelling tone | "Once upon a time..." |
| `gaming` | Fast, tense, excited | "Quick! He's over there!" |

### Special States

| Mood | Description | Example |
|------|-------------|---------|
| `daydream` | Airy, dreamy, absent-minded | "Hmm... I was thinking..." |
| `nervous` | Stuttering, panicked | "Th... that... what do I do..." |
| `determined` | Soft but firm resolve | "I've decided!" |
| `longing` | Soft, sighing, missing you | "I miss you so much..." |
| `confession` | Trembling, sincere love | "I... I love you..." |
| `possessive` | Low, magnetic, obsessive | "You belong to me..." |
| `submissive` | Soft, yielding, obedient | "Whatever you say..." |

### Roleplay

| Mood | Description | Example |
|------|-------------|---------|
| `maid` | Polite, respectful | "Welcome home, Master~" |
| `nurse` | Gentle, patient, caring | "Let me take your temperature~" |
| `student` | Youthful, energetic, shy | "Senior! Wait for me~" |
| `ojousama` | Elegant, arrogant, noble | "Hmph, I don't care." |
| `yandere` | Sweet but dark/obsessive | "You are mine... forever..." |
| `tsundere` | Cold outside, warm inside | "I-I'm not worried about you!" |

### Voice Effects

| Mood | Description | Example |
|------|-------------|---------|
| `asmr` | Extremely soft whisper | "Relax..." |
| `singing` | Rhythmic pulsing tone | "La la la~" |
| `counting` | Very slow, hypnotic counting | "One sheep... two sheep..." |




## Audio Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **pcm** | Raw PCM data | Advanced processing |
| **wav** | WAV audio | Windows/desktop |
| **mp3** | MP3 audio (default) | Universal |
| **opus** | OGG/Opus | Telegram voice messages (Use `.ogg` extension) |


**Total: 35 Female Voices** 💕

## Supported Languages

Bailian TTS supports the following 10 languages:

| 语言 | Language |
|------|----------|
| 中文 | Chinese |
| English | English |
| Français | French |
| Deutsch | German |
| Русский | Russian |
| Italiano | Italian |
| Español | Spanish |
| Português | Portuguese |
| 日本語 | Japanese |
| 한국어 | Korean |


## Troubleshooting

**Setup fails:**
```bash
# Ensure Python 3.10+ is available
python3 --version

# Re-run setup
cd skills/qwen3-tts-instruct
rm -rf venv
bash scripts/setup.sh
```

**WebSocket connection fails:**
- Check network connectivity
- Verify API key is valid

**Privacy Note:** 
This skill sends text data to Alibaba Cloud (DashScope) for processing. No data is sent to the skill author.

**Audio quality issues:**
- Try different voice: `--voice Serena`
- Adjust mood: `--mood gentle`
