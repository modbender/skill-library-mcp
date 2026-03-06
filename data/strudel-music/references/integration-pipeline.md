# Strudel Integration Pipeline — Headless Rendering to Discord VC

## Architecture

```
Agent                     Headless Browser              Audio Pipeline
┌──────────┐  pattern.js  ┌──────────────────┐  WAV    ┌────────────┐
│ Generate  │ ──────────→ │ Chromium +        │ ─────→ │ ffmpeg     │
│ pattern   │             │ Strudel REPL      │        │ WAV → Opus │
│ from mood │             │                   │        └─────┬──────┘
│ params    │             │ evaluate(code)    │              │ Opus
└──────────┘             │ renderPatternAudio│              ▼
                          └──────────────────┘        ┌────────────┐
                                                      │ Discord VC │
                                                      │ Bridge     │
                                                      └────────────┘
```

## Key Components

### 1. renderPatternAudio() — Offline Rendering

Located in `@strudel/webaudio` (`packages/webaudio/webaudio.mjs`).
Uses `OfflineAudioContext` to render patterns to WAV without real-time playback.

```javascript
await renderPatternAudio(
  pattern,      // evaluated Strudel pattern object
  cps,          // cycles per second (BPM / 60 / 4)
  0,            // begin cycle
  8,            // end cycle
  44100,        // sample rate
  64,           // max polyphony
  false,        // multi-channel orbits
  'output'      // download filename
);
```

**Limitation**: `OfflineAudioContext` is a Web API — requires browser context.
Server-side rendering uses headless Chromium (Puppeteer/Playwright).

### 2. Headless Browser Setup

```javascript
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required']
});
const page = await browser.newPage();
await page.goto('https://strudel.cc', { waitUntil: 'networkidle2' });

// Wait for Strudel to initialize
await page.waitForFunction(() => typeof globalThis.evaluate === 'function');

// Evaluate pattern
await page.evaluate((code) => evaluate(code), patternCode);

// Render to WAV (triggers download)
await page.evaluate(() => renderPatternAudio(...));
```

### 3. Audio Conversion

```bash
# WAV → Opus (Discord native, low latency)
ffmpeg -i input.wav -c:a libopus -b:a 128k -ar 48000 output.opus

# WAV → PCM (for direct streaming)
ffmpeg -i input.wav -f s16le -acodec pcm_s16le -ar 48000 -ac 2 output.pcm
```

### 4. Discord VC Bridge

If using an existing VC bridge (e.g., openclaw-discord-vc-bootstrap):
1. Render pattern to Opus file
2. Feed Opus to the bridge's audio input
3. Bridge handles Discord voice connection, encoding, and transmission

## Real-Time vs Batch

| Mode | Approach | Latency | Use Case |
|------|----------|---------|----------|
| Batch | renderPatternAudio → WAV → convert | 5-30s | Pre-rendered scenes, exports |
| Near-real-time | Live REPL in headless browser, capture output stream | <1s | Live mood transitions |
| True real-time | Browser audio capture → PCM pipe | ~100ms | Interactive performance |

For most agent-driven use cases, **batch rendering** is sufficient.
Near-real-time is needed for reactive mood transitions during live sessions.

## Sample Management

Default samples: `github:tidalcycles/dirt-samples` (CC-licensed, loaded automatically by Strudel).

Custom samples:
```javascript
samples('local:')  // loads from local ./samples/ directory
```

For domain-specific atmospheres, create sample packs and host them on GitHub
or serve locally. Each sample pack is a directory of `.wav` files organized by name.
