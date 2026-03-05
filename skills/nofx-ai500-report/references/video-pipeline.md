# Video Report Pipeline

Generate animated video reports from AI500 data using Remotion or Playwright screencast.

## Option A: Remotion (React-based)

Best for high-quality, consistent output with animated charts and transitions.

1. Build React components for each report section (title, coin detail, OI chart, flow chart, summary)
2. Use `@remotion/google-fonts` for Inter font family
3. Scene durations matched to TTS narration length + 1.5s buffer
4. Render: `npx remotion render CompositionId output.mp4`

## Option B: Playwright Screencast (HTML-based)

Best for rapid iteration. Build report as multi-page HTML with CSS animations.

**Critical**: Do NOT use auto-play opacity transitions — they cause flickering in Playwright screencast. Instead:
- Record each page separately via `showPage(n)` function
- Each page uses CSS `@keyframes` for element animations (fadeUp, slideIn, etc.)
- Combine segments with ffmpeg

### Per-Page Recording Script Pattern

```javascript
const { chromium } = require('playwright');
for (let page = 1; page <= totalPages; page++) {
  await browserPage.evaluate(n => showPage(n), page);
  // Start screencast, wait for animation duration, stop
}
```

## TTS Narration

Use MiniMax TTS API (`speech-02-hd` model, `cute_girl` voice):

```python
payload = {
    "model": "speech-02-hd",
    "text": narration_text,
    "stream": False,
    "voice_setting": {"voice_id": "cute_girl", "speed": 1.0, "vol": 1.0, "pitch": 0},
    "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3"}
}
# POST to https://api.minimax.chat/v1/t2a_v2
# Response: data.data.audio (hex-encoded MP3)
```

## Assembly with ffmpeg

```bash
# Combine video segment + narration per page
ffmpeg -y -i segment_p1.webm -i narr1.mp3 -c:v libx264 -c:a aac -t <duration> page1.mp4

# Concat all pages
ffmpeg -y -f concat -i filelist.txt -c copy merged.mp4

# Add BGM (volume 0.10-0.12)
ffmpeg -y -i merged.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.12,afade=t=in:d=2,afade=t=out:st=<fade_start>:d=5[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac final.mp4
```

## Design System

- Background: #080810 or #0C0C18
- Accent: Purple #7060F4/#8172FF
- Green: #00E096 (positive), Red: #FF405F (negative), Blue: #1F8BFF
- Cards: glassmorphism (rgba white background, blur, subtle border)
- Font: Inter (Google Fonts)
- Footer: VergeX branding bar
