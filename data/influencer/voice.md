# Voice & Audio for AI Influencers

## Voice Cloning Setup

### ElevenLabs (Recommended)
1. **Record source audio** (1-5 min of clean speech)
   - Match target persona's tone/energy
   - Clear recording, no background noise
   - Various emotional tones for range
2. **Create voice clone** in ElevenLabs dashboard
3. **Test with sample scripts** before production
4. **Save voice_id** in persona's `tools.md`

```bash
# Generate audio via API
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your script here",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75
    }
  }' --output audio.mp3
```

### Alternative Voice Tools
| Tool | Quality | Price | Best For |
|------|---------|-------|----------|
| PlayHT | Very Good | $$ | Natural voices |
| Resemble.AI | Excellent | $$$ | Custom clones |
| Speechify | Good | $ | Quick TTS |
| OpenAI TTS | Good | $ | API integration |

---

## Voice Consistency Rules

**Always maintain:**
- Same voice_id across all content
- Consistent speaking pace
- Consistent energy level (unless intentional variation)
- Same audio processing (EQ, compression)

**Voice settings to lock:**
```
stability: 0.5        # Lower = more expressive
similarity_boost: 0.75  # Higher = more like original
```

---

## Audio Processing Pipeline

Raw TTS → Processing → Final audio

```bash
# Normalize loudness
ffmpeg -i raw.mp3 -af "loudnorm=I=-14:TP=-1.5:LRA=11" normalized.mp3

# Add subtle room tone (more natural)
ffmpeg -i normalized.mp3 -af "highpass=f=80,acompressor=threshold=-20dB:ratio=3" final.mp3
```

---

## Script Writing for TTS

### Do:
- Write like speaking, not like reading
- Use contractions (I'm, you're, we'll)
- Short sentences
- Natural pauses (use commas, periods)
- Occasional filler words ("so", "like", "you know")

### Don't:
- Complex sentences
- Technical jargon (unless fits persona)
- Run-on paragraphs
- Robotic transitions

**Example:**
```
Hey guys! So I've been trying this new thing and... honestly? It's been kind of life-changing. Let me tell you why.
```

---

## Content Scripts by Type

### Hook (first 3 seconds)
```
"Wait, you're still doing [common mistake]?"
"Okay but this changed everything for me"
"I have to tell you about this"
```

### Educational
```
"Here's the thing about [topic]. Most people think [misconception], but actually [truth]. Let me show you what I mean..."
```

### Story time
```
"So the craziest thing happened to me yesterday. I was [setting up story], and then [unexpected thing]..."
```

### Promotional
```
"I've been using [product] for [time], and I have to be honest with you about my experience..."
```

---

## Podcast/Long-form Audio

For YouTube or podcast content:

1. **Write full script** or detailed outline
2. **Record in segments** (easier to edit)
3. **Generate audio** for each segment
4. **Stitch together** with transitions
5. **Add music bed** (low volume, instrumental)
6. **Master audio** (normalize, EQ)

---

## Voice Personas by Niche

| Niche | Voice Style | Energy | Pacing |
|-------|-------------|--------|--------|
| Fitness | Motivational, loud | High | Fast |
| Lifestyle | Calm, friendly | Medium | Relaxed |
| Tech | Clear, informative | Medium | Measured |
| Fashion | Excited, trendy | High | Fast |
| Finance | Professional, trustworthy | Medium | Slower |
| Gaming | Energetic, casual | High | Fast |

---

## Multilingual Content

For reaching multiple markets:

1. **Write script in primary language**
2. **Translate** (human or AI, then human review)
3. **Clone voice in each language** (ElevenLabs supports many)
4. **Generate audio per language**
5. **Separate channels** or multi-language captions

---

## Audio Checklist

Before using any audio:
- [ ] No obvious TTS artifacts
- [ ] Natural pacing (not too robotic)
- [ ] Correct pronunciation
- [ ] Good volume levels (-14 to -16 LUFS)
- [ ] No clipping/distortion
- [ ] Matches persona energy
