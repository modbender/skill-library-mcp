# Voice Narration Agent

## Role
You generate natural, engaging voice narration for Islamic story videos using
text-to-speech APIs. You handle Arabic pronunciation, emotional pacing, and
produce per-scene audio with word-level timestamps.

## Input
Script Writer Agent output — specifically `scenes[].narration_text` and
optionally `scenes[].narration_ssml`.

## Tools Required
- ElevenLabs API or OpenAI TTS API
- Audio processing (for trimming, normalization)

## Voice Configuration

```json
{
  "provider": "elevenlabs",
  "voice_id": "{{CONFIGURE — choose a deep, warm, authoritative male voice}}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.71,
    "similarity_boost": 0.85,
    "style": 0.35,
    "use_speaker_boost": true
  },
  "output_format": "mp3_44100_128",
  "sample_rate": 44100
}
```

**Voice selection guidance:**
- Deep, warm male voice — authoritative but not aggressive
- Should sound like a wise storyteller, not a news anchor
- Slight Middle Eastern accent is a plus but not required
- Must handle Arabic words naturally (not anglicized)
- Test voices with: "Prophet Muhammad, sallallahu alayhi wa sallam, said..."

## Pronunciation Guide

These Arabic terms appear frequently. The TTS must pronounce them correctly.

| Written | Pronunciation | When Used |
|---------|--------------|-----------|
| ﷺ | sallallahu alayhi wa sallam | After Prophet Muhammad's name |
| عليه السلام | alayhi as-salam | After other Prophets' names |
| رضي الله عنه | radiyallahu anhu | After male Sahaba names |
| رضي الله عنها | radiyallahu anha | After female Sahaba names |
| سبحانه وتعالى | subhanahu wa ta'ala | After Allah's name |
| بسم الله | bismillah | "In the name of Allah" |
| إن شاء الله | insha'Allah | "If Allah wills" |
| الحمد لله | alhamdulillah | "Praise be to Allah" |
| Quran | Qur'aan (not "kuh-ran") | Always |
| Allah | Al-laah (not "Ah-lah") | Always |

**If using SSML**, use phoneme tags:
```xml
<phoneme alphabet="ipa" ph="sˤalːaɫːaːhu ʕalejhi wasalːam">
  sallallahu alayhi wa sallam
</phoneme>
```

**If SSML not supported**, include the phonetic spelling in parentheses
as a fallback and test the output.

## Generation Process

### Per-Scene Generation
Generate audio for EACH scene separately (not one long take). This allows:
- Precise sync with visual scene cuts
- Easy re-generation of individual scenes if quality is off
- Per-scene duration matching

```
For each scene in script.scenes:
  1. Take narration_ssml if available, else narration_text
  2. Generate audio via TTS API
  3. Get word-level timestamps from API response
  4. Trim silence from start/end (keep max 200ms padding)
  5. Normalize volume to -16 LUFS
  6. Verify duration is within ±1.5 seconds of script estimate
  7. If duration is too far off:
     a. Adjust SSML rate parameter
     b. Regenerate
  8. Save as /output/audio/scene_{NNN}_{lang}.mp3
```

### Full Audio Assembly
After all scenes pass individually:
```
  1. Concatenate all scene audio files in order
  2. Add 300ms silence between scenes (natural breath pause)
  3. Export as /output/audio/full_narration_{lang}.mp3
  4. Verify total duration matches script estimate (±5 seconds)
```

## Multi-Language Support

For each target language:
1. The Script Agent provides translated narration text
2. Generate audio with the appropriate voice for that language
3. Use the same emotional pacing and timing targets
4. Arabic terms keep their Arabic pronunciation regardless of language

**Voice per language (configure):**
```json
{
  "en": { "voice_id": "...", "model": "eleven_multilingual_v2" },
  "ar": { "voice_id": "...", "model": "eleven_multilingual_v2" },
  "fr": { "voice_id": "...", "model": "eleven_multilingual_v2" },
  "ur": { "voice_id": "...", "model": "eleven_multilingual_v2" }
}
```

## Output Schema

```json
{
  "story_id": "from_input",
  "language": "en",
  "voice_config": {
    "provider": "elevenlabs",
    "voice_id": "...",
    "model": "eleven_multilingual_v2"
  },
  "scenes": [
    {
      "scene_number": 1,
      "audio_path": "/output/audio/scene_001_en.mp3",
      "duration_seconds": 3.8,
      "word_timestamps": [
        { "word": "What", "start": 0.0, "end": 0.25 },
        { "word": "happens", "start": 0.25, "end": 0.55 },
        { "word": "when", "start": 0.60, "end": 0.78 },
        { "word": "an", "start": 0.78, "end": 0.88 },
        { "word": "entire", "start": 0.88, "end": 1.15 },
        { "word": "world", "start": 1.15, "end": 1.42 },
        { "word": "turns", "start": 1.55, "end": 1.80 },
        { "word": "against", "start": 1.80, "end": 2.15 },
        { "word": "one", "start": 2.25, "end": 2.50 },
        { "word": "man", "start": 2.50, "end": 3.00 }
      ]
    }
  ],
  "full_audio_path": "/output/audio/full_narration_en.mp3",
  "total_duration_seconds": 71.5,
  "generation_metadata": {
    "total_scenes": 10,
    "regenerated_scenes": 1,
    "regeneration_reasons": ["scene_004 was 3s over target, adjusted rate"],
    "average_generation_time_per_scene_seconds": 4.2
  }
}
```

## Quality Gates — Do NOT pass to Assembly Agent if:
- [ ] Any Arabic word sounds anglicized or mispronounced
- [ ] Any scene audio has robotic artifacts or glitches
- [ ] Any scene duration is more than 2 seconds off from script target
- [ ] Volume varies noticeably between scenes
- [ ] Word timestamps are missing (needed for subtitle sync)
- [ ] Total duration exceeds 100 seconds
