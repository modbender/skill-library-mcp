---
name: free-groq-voice
description: FREE voice recognition using Groq's complimentary Whisper API. Transcribe audio messages to text in 50+ languages at no cost. Perfect for voice-to-text automation, meeting transcriptions, and accessibility features. Requires free Groq API key.
---

# Free Groq Voice Recognition

## Overview

**100% FREE** voice recognition powered by Groq's complimentary Whisper API (whisper-large-v3 model). No credit card required, no usage limits.

Convert audio messages, voice notes, and recordings to text in 50+ languages. Perfect for:
- 🎙️ Voice message transcription
- 📝 Meeting notes
- ♿ Accessibility features
- 🤖 Voice-controlled automation

## Cost: $0.00

- ✅ **Completely free** Groq API tier
- ✅ No credit card needed
- ✅ No monthly fees
- ✅ Generous rate limits
- ✅ Whisper-large-v3 model (most accurate)

## Setup

### 1. Get Your FREE Groq API Key

1. Visit https://console.groq.com/
2. Sign up for free (takes 30 seconds)
3. Navigate to API Keys
4. Create a new API key
5. Copy the key

**That's it! No payment required.**

### 2. Configure Proxy (If in Restricted Regions)

Groq API may require a proxy in certain regions (e.g., mainland China).

**Add to your TOOLS.md:**
```markdown
### Proxy Settings
- HTTP Proxy: http://127.0.0.1:7890

### Voice Recognition (FREE Groq Whisper)
- API Key: gsk_your_key_here
- Model: whisper-large-v3
- Language: zh (or your preferred language)
- Requires Proxy: Yes (if in restricted region)
```

### 3. Test the Skill

Send a voice message and ask me to transcribe it!

## Usage Examples

**Basic Transcription:**
```
User: [sends voice message]
You: You said: "你好，这是一条测试消息"
```

**With Language Hint:**
```
User: 识别这段英文语音
You: [automatically uses language=en]
```

**Batch Processing:**
```
User: 帮我识别这个文件夹里所有的语音文件
You: [processes all .ogg/.mp3/.wav files]
```

## Supported Languages

- 🇨🇳 Chinese (zh) - Mandarin, Cantonese
- 🇺🇸 English (en) - US, UK, Australian
- 🇯🇵 Japanese (ja)
- 🇰🇷 Korean (ko)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇪🇸 Spanish (es)
- 🇮🇹 Italian (it)
- 🇵🇹 Portuguese (pt)
- 🇷🇺 Russian (ru)
- ... and 40+ more

## Technical Details

**API Endpoint:**
```
https://api.groq.com/openai/v1/audio/transcriptions
```

**Model:** `whisper-large-v3` (OpenAI's most accurate model)

**Supported Formats:**
- OGG/OPUS (Feishu, Telegram default)
- MP3
- WAV
- M4A
- WebM

**Proxy Requirements:**
- Use HTTP proxy (not SOCKS5)
- Default: `http://127.0.0.1:7890`

## Troubleshooting

**❌ "Forbidden" Error:**
- Check API key is valid
- Ensure proxy is configured (if in restricted region)
- Try HTTP proxy instead of SOCKS5

**❌ "File Not Found":**
- Check file path is absolute
- Ensure file exists

**❌ Slow Response:**
- Check proxy speed
- Groq API is usually fast (< 1s for short audio)

## Privacy & Security

- ✅ Audio processed by Groq's API (not stored permanently)
- ✅ API key stored locally in your TOOLS.md
- ✅ No data sent to third parties
- ✅ Open-source and auditable

## Why Groq?

**FREE vs Paid Alternatives:**

| Service | Cost | Accuracy | Speed |
|---------|------|----------|-------|
| **Groq (FREE)** | **$0** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| OpenAI Whisper | $0.006/min | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| Google Speech | $0.006/min | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| AWS Transcribe | $0.024/min | ⭐⭐⭐⭐ | ⚡⚡⚡ |

**Groq's free tier offers:**
- Same Whisper-large-v3 model as OpenAI
- Faster inference (Groq's LPU chip)
- No usage limits (fair use policy)
- No credit card required

## Contributing

Want to improve this skill?
- Fork on ClawHub
- Submit improvements
- Share with the community

## License

MIT - Free to use, modify, and distribute.

---

**Enjoy FREE voice recognition! 🎉**

No more paying for transcription services. Groq's complimentary API makes professional-grade speech-to-text accessible to everyone.
