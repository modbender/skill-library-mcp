---
name: wavespeed-minimax-speech-26
description: Convert text to speech using MiniMax Speech 2.6 Turbo via WaveSpeed AI. Features ultra-human voice cloning, sub-250ms latency, 40+ languages, emotion control, and 200+ voice presets. Use when the user wants to generate speech audio from text.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI MiniMax Speech 2.6 Turbo

Convert text to speech using MiniMax Speech 2.6 Turbo via the WaveSpeed AI platform. Features ultra-human voice cloning, sub-250ms latency, 40+ language support, and emotion control.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "minimax/speech-2.6-turbo",
  {
    text: "Hello, welcome to WaveSpeed AI!",
    voice_id: "English_CalmWoman"
  }
))["outputs"][0];
```

## API Endpoint

**Model ID:** `minimax/speech-2.6-turbo`

Convert text to speech with configurable voice, emotion, speed, pitch, and audio format.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | -- | Text to convert to speech. Max 10,000 characters. Use `<#x#>` between words to insert pauses (0.01-99.99 seconds). |
| `voice_id` | string | Yes | -- | Voice preset ID. See [Voice IDs](#voice-ids) below. |
| `speed` | number | No | `1` | Speech speed. Range: 0.50-2.00 |
| `volume` | number | No | `1` | Speech volume. Range: 0.10-10.00 |
| `pitch` | number | No | `0` | Speech pitch. Range: -12 to 12 |
| `emotion` | string | No | `happy` | Emotional tone. One of: `happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`, `neutral` |
| `english_normalization` | boolean | No | `false` | Improve English number reading normalization |
| `sample_rate` | integer | No | -- | Sample rate in Hz. One of: `8000`, `16000`, `22050`, `24000`, `32000`, `44100` |
| `bitrate` | integer | No | -- | Bitrate in bps. One of: `32000`, `64000`, `128000`, `256000` |
| `channel` | string | No | -- | Audio channels. `1` (mono) or `2` (stereo) |
| `format` | string | No | -- | Output format. One of: `mp3`, `wav`, `pcm`, `flac` |
| `language_boost` | string | No | -- | Enhance recognition for a specific language. See [Supported Languages](#supported-languages). |

### Example

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "minimax/speech-2.6-turbo",
  {
    text: "The quick brown fox jumps over the lazy dog.",
    voice_id: "English_expressive_narrator",
    speed: 1.0,
    pitch: 0,
    emotion: "neutral",
    format: "mp3",
    sample_rate: 24000,
    bitrate: 128000
  }
))["outputs"][0];
```

### Pause Control

Insert pauses in speech using `<#x#>` syntax where `x` is seconds (0.01-99.99):

```javascript
const output_url = (await wavespeed.run(
  "minimax/speech-2.6-turbo",
  {
    text: "And the winner is <#2.0#> WaveSpeed AI!",
    voice_id: "English_CaptivatingStoryteller"
  }
))["outputs"][0];
```

## Advanced Usage

### Sync Mode

```javascript
const output_url = (await wavespeed.run(
  "minimax/speech-2.6-turbo",
  {
    text: "Hello world!",
    voice_id: "English_CalmWoman"
  },
  { enableSyncMode: true }
))["outputs"][0];
```

### Custom Client with Retry Configuration

```javascript
import { Client } from 'wavespeed';

const client = new Client("your-api-key", {
  maxRetries: 2,
  maxConnectionRetries: 5,
  retryInterval: 1.0,
});

const output_url = (await client.run(
  "minimax/speech-2.6-turbo",
  {
    text: "Welcome to our platform.",
    voice_id: "English_Trustworth_Man"
  }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "minimax/speech-2.6-turbo",
  {
    text: "Testing speech generation.",
    voice_id: "English_CalmWoman"
  }
);

if (result.outputs) {
  console.log("Audio URL:", result.outputs[0]);
  console.log("Task ID:", result.detail.taskId);
} else {
  console.log("Failed:", result.detail.error.message);
  if (result.detail.error instanceof WavespeedTimeoutException) {
    console.log("Request timed out - try increasing timeout");
  } else if (result.detail.error instanceof WavespeedPredictionException) {
    console.log("Prediction failed");
  }
}
```

## Voice IDs

### English Voices (Popular)

| Voice ID | Description |
|----------|-------------|
| `English_CalmWoman` | Calm female voice |
| `English_Trustworth_Man` | Trustworthy male voice |
| `English_expressive_narrator` | Expressive narrator |
| `English_radiant_girl` | Radiant girl voice |
| `English_magnetic_voiced_man` | Magnetic male voice |
| `English_CaptivatingStoryteller` | Storyteller voice |
| `English_Upbeat_Woman` | Upbeat female voice |
| `English_GentleTeacher` | Gentle teacher voice |
| `English_PlayfulGirl` | Playful girl voice |
| `English_ManWithDeepVoice` | Deep male voice |
| `English_ConfidentWoman` | Confident female voice |
| `English_Comedian` | Comedic voice |
| `English_SereneWoman` | Serene female voice |
| `English_WiseScholar` | Scholarly voice |
| `English_Cute_Girl` | Cute girl voice |
| `English_Sharp_Commentator` | Sharp commentator |
| `English_Lucky_Robot` | Robot voice |

### General Voices

`Wise_Woman`, `Friendly_Person`, `Inspirational_girl`, `Deep_Voice_Man`, `Calm_Woman`, `Casual_Guy`, `Lively_Girl`, `Patient_Man`, `Young_Knight`, `Determined_Man`, `Lovely_Girl`, `Decent_Boy`, `Imposing_Manner`, `Elegant_Man`, `Abbess`, `Sweet_Girl_2`, `Exuberant_Girl`

### Special Voices

`whisper_man`, `whisper_woman_1`, `angry_pirate_1`, `massive_kind_troll`, `movie_trailer_deep`, `peace_and_ease`

### Other Languages

Voices are available for: Chinese (Mandarin), Cantonese, Arabic, Russian, Spanish, French, Portuguese, German, Turkish, Dutch, Ukrainian, Vietnamese, Indonesian, Japanese, Italian, Korean, Thai, Polish, Romanian, Greek, Czech, Finnish, Hindi, Bulgarian, Danish, Hebrew, Malay, Persian, Slovak, Swedish, Croatian, Filipino, Hungarian, Norwegian, Slovenian, Catalan, Nynorsk, Tamil, Afrikaans.

Voice IDs follow the pattern `{Language}_{VoiceName}` (e.g., `Japanese_KindLady`, `Korean_SweetGirl`, `French_CasualMan`).

## Supported Languages

For `language_boost`: `Chinese`, `Chinese,Yue`, `English`, `Arabic`, `Russian`, `Spanish`, `French`, `Portuguese`, `German`, `Turkish`, `Dutch`, `Ukrainian`, `Vietnamese`, `Indonesian`, `Japanese`, `Italian`, `Korean`, `Thai`, `Polish`, `Romanian`, `Greek`, `Czech`, `Finnish`, `Hindi`, `Bulgarian`, `Danish`, `Hebrew`, `Malay`, `Persian`, `Slovak`, `Swedish`, `Croatian`, `Filipino`, `Hungarian`, `Norwegian`, `Slovenian`, `Catalan`, `Nynorsk`, `Tamil`, `Afrikaans`

## Pricing

$0.06 per 1,000 characters.

## Security Constraints

- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate text content before sending requests.
