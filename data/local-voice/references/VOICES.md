# Kokoro Voice Reference

## American English (11F, 9M)

| Voice | Grade | Traits | Notes |
|-------|-------|--------|-------|
| af_heart | A | ❤️ | Default, highest quality |
| af_bella | A- | 🔥 | Expressive, warm |
| af_nicole | B- | 🎧 | Clear, professional |
| af_aoede | C+ | | Melodic |
| af_kore | C+ | | Bright |
| af_sarah | C+ | | Friendly |
| af_alloy | C | | Neutral |
| af_nova | C | | Modern |
| af_sky | C- | | Light, airy |
| af_jessica | D | | Basic |
| af_river | D | | Soft |
| am_adam | F+ | | Male |
| am_echo | D | | Male |
| am_eric | D | | Male |
| am_fenrir | C+ | | Male, deep |
| am_liam | D | | Male |
| am_michael | C+ | | Male, professional |
| am_onyx | D | | Male |
| am_puck | C+ | | Male, playful |
| am_santa | D- | | Male, festive |

## British English (4F, 4M)

| Voice | Grade | Notes |
|-------|-------|-------|
| bf_emma | B- | Most natural |
| bf_alice | D | |
| bf_isabella | C | |
| bf_lily | D | |
| bm_daniel | D | Male |
| bm_fable | C | Male |
| bm_george | C | Male |
| bm_lewis | D+ | Male |

## Other Languages

- Japanese: jf_alpha, jf_gongitsune, jf_nezumi, jf_tebukuro, jm_kumo
- Mandarin: 4F, 4M voices
- Spanish: 1F, 2M
- French: 1F
- Hindi: 2F, 2M
- Italian: 1F, 1M
- Brazilian Portuguese: 1F, 2M

## Changing Voice

Edit `sources/Sources/StellaVoice/main.swift`:

```swift
let tts = TTSService(voice: "af_bella")  // Change voice here
```

Then rebuild: `swift build -c release`
