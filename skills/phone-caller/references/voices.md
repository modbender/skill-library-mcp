# ElevenLabs Voice Reference

Curated voices for phone calls. All tested with `eleven_turbo_v2_5`.

## Recommended Defaults

| Voice ID | Name | Description | Best For |
|----------|------|-------------|----------|
| `tyepWYJJwJM9TTFIg5U7` | **Clara** | Australian female, warm, professional | Default — works for most calls |
| `U9VgC8Xinl7nnNsyDd3J` | **Rachel** | Australian female, fun, casual | Friendly/personal calls |
| `JBFqnCBsd6RMkjVDRZzb` | **George** | British male, warm storyteller | Formal/professional calls |
| `EXAVITQu4vr4xnSDxMaL` | **Sarah** | American female, mature, confident | Customer service tone |
| `CwhRBWXzGAHq8TQ4Fs17` | **Roger** | American male, laid-back, casual | Relaxed outreach |

## All Premade Voices

| Voice ID | Name | Gender | Accent | Style |
|----------|------|--------|--------|-------|
| `CwhRBWXzGAHq8TQ4Fs17` | Roger | Male | American | Laid-back, casual |
| `EXAVITQu4vr4xnSDxMaL` | Sarah | Female | American | Mature, reassuring |
| `FGY2WhTYpPnrIDTdsKH5` | Laura | Female | American | Enthusiastic, quirky |
| `IKne3meq5aSn9XLyUdCD` | Charlie | Male | Australian | Deep, confident |
| `JBFqnCBsd6RMkjVDRZzb` | George | Male | British | Warm, captivating |
| `N2lVS1w4EtoT3dr4eOWO` | Callum | Male | American | Husky, edgy |
| `SAz9YHcvj6GT2YYXdXww` | River | Neutral | American | Relaxed, informative |
| `TX3LPaxmHKxFdv7VOQHJ` | Liam | Male | American | Energetic, social |
| `Xb7hH8MSUJpSbSDYk0k2` | Alice | Female | British | Clear, engaging |

## Australian Female (Shared Library)

| Voice ID | Name | Description |
|----------|------|-------------|
| `tyepWYJJwJM9TTFIg5U7` | Clara | Professional, warm, trustworthy |
| `U9VgC8Xinl7nnNsyDd3J` | Rachel | Fun, casual, natural |
| `TcrlBgVmqvmPFJi2o2AO` | Kylie | Advertising, upbeat, social |

## Voice Settings Guide

```json
{
  "stability": 0.45,        // Lower = more expressive, Higher = more consistent
  "similarity_boost": 0.8,  // Higher = closer to original voice character
  "style": 0.5              // Higher = more dramatic/expressive delivery
}
```

For phone calls: stability 0.4–0.5, similarity_boost 0.75–0.85, style 0.4–0.6 works well.

## Finding More Voices

```bash
# Search shared library by accent + gender
curl "https://api.elevenlabs.io/v1/shared-voices?accent=british&gender=female&page_size=10" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -m json.tool
```

Accent options: `american`, `british`, `australian`, `irish`, `indian`, `french`, `german`, etc.
