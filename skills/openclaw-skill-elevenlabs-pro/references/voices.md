# ElevenLabs — Popular Voices & API Parameters

## Popular Voices

### Female Voices

| Name | Voice ID | Language | Description |
|------|----------|----------|-------------|
| Sarah | EXAVITQu4vr4xnSDxMaL | en | Mature, reassuring, confident |
| Laura | FGY2WhTYpPnrIDTdsKH5 | en | Enthusiastic, quirky attitude |
| Alice | Xb7hH8MSUJpSbSDYk0k2 | en | Clear, engaging educator |
| Matilda | XrExE9yKIg1WjnnlVkGX | en | Knowledgeable, professional |
| Jessica | cgSgspJ2msm6clMCkdW9 | en | Playful, bright, warm |
| Bella | hpp4J3VqNfWAUOO0d1Us | en | Professional, bright, warm |
| Lily | pFZP5JQG7iQjIQuC4Bku | en | Velvety actress |
| Charlotte | XB0fDUnXU5powFXDhCwa | en-GB | Seductive, whisper, Swedish |

### Male Voices

| Name | Voice ID | Language | Description |
|------|----------|----------|-------------|
| Roger | CwhRBWXzGAHq8TQ4Fs17 | en | Laid-back, casual, resonant |
| Charlie | IKne3meq5aSn9XLyUdCD | en | Deep, confident, energetic |
| George | JBFqnCBsd6RMkjVDRZzb | en | Warm, captivating storyteller |
| Brian | nPczCjzI2devNBz1zQrb | en | Deep, resonant, comforting |
| Daniel | onwK4e9ZLuTAKqWW03F9 | en | Steady broadcaster |
| Adam | pNInz6obpgDQGcFmaJgB | en | Dominant, firm |
| Eric | cjVigY5qzO86Huf0OWal | en | Smooth, trustworthy |
| Chris | iP95p4xoKVk53GoZ742B | en | Charming, down-to-earth |
| Harry | SOYHLrjzK2X1ezoPC6cr | en | Fierce warrior |
| Liam | TX3LPaxmHKxFdv7VOQHJ | en | Energetic, social media creator |
| Bill | pqHfZKP75CvOlQylNhV4 | en | Wise, mature, balanced |

### Neutral / Other

| Name | Voice ID | Language | Description |
|------|----------|----------|-------------|
| River | SAz9YHcvj6GT2YYXdXww | en | Relaxed, neutral, informative |

---

## Voice Settings Parameters

### stability (0.0 – 1.0)
Controls how consistent the voice sounds across generations.
- **Low (0.1–0.3):** More expressive and varied, but less predictable
- **Medium (0.4–0.6):** Balanced expressiveness and consistency ✅ Default: 0.5
- **High (0.7–1.0):** Very stable and monotone, great for narration

### similarity_boost (0.0 – 1.0)
How closely the output should match the original voice.
- **Low:** More creative interpretation
- **High (0.7–0.9):** Closer to original voice ✅ Default: 0.75
- **Very High (>0.9):** Risk of artifacts, use carefully

### style (0.0 – 1.0)
Style exaggeration — amplifies the voice's natural style.
- **0.0:** No exaggeration (most natural) ✅ Default: 0.0
- **0.3–0.5:** Moderate expressiveness
- **0.8–1.0:** Very exaggerated (can sound unnatural)
- ⚠️ Increases latency when > 0

### use_speaker_boost (true/false)
Enhances similarity to original speaker. Slightly increases latency.
- **true:** Closer to original voice ✅ Default: true
- **false:** Faster generation

---

## Available Models

| Model ID | Speed | Quality | Multilingual | Notes |
|----------|-------|---------|--------------|-------|
| `eleven_turbo_v2_5` | ⚡⚡⚡ | Good | No | Best for free tier; low latency |
| `eleven_turbo_v2` | ⚡⚡ | Good | No | Older turbo |
| `eleven_flash_v2_5` | ⚡⚡⚡⚡ | Moderate | Yes | Ultra-low latency |
| `eleven_multilingual_v2` | ⚡ | Excellent | Yes | Best quality, 29 languages |
| `eleven_multilingual_v1` | ⚡ | Very Good | Yes | Legacy multilingual |

---

## Multilingual Support

`eleven_multilingual_v2` supports: English, Spanish, French, German, Italian, Portuguese,
Polish, Hindi, Arabic, Chinese, Japanese, Korean, Dutch, Turkish, Swedish, Norwegian,
Danish, Finnish, Romanian, Czech, Slovak, Bulgarian, Croatian, Greek, Hungarian, Ukrainian,
and more.

---

## Recommended Settings by Use Case

| Use Case | stability | similarity | style | model |
|----------|-----------|------------|-------|-------|
| Narration / Podcast | 0.6 | 0.75 | 0.0 | eleven_multilingual_v2 |
| Conversational / Chat | 0.4 | 0.75 | 0.2 | eleven_turbo_v2_5 |
| News / Documentary | 0.7 | 0.8 | 0.0 | eleven_multilingual_v2 |
| Dramatic / Story | 0.3 | 0.7 | 0.4 | eleven_multilingual_v2 |
| Real-time / Low Latency | 0.5 | 0.75 | 0.0 | eleven_flash_v2_5 |
