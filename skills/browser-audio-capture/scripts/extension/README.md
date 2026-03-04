# Percept Audio Capture Extension

Chrome extension for capturing tab audio and streaming to the Percept transcription pipeline. Zero configuration, fully local.

## Install

1. Open `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select this folder (`percept/src/browser_capture/extension/`)

## Use

1. Open a meeting tab (Zoom, Google Meet, Teams, etc.)
2. Click the Percept extension icon (red circle)
3. Click "Start Capturing This Tab"
4. Audio streams to Percept receiver at `localhost:8900`

The extension captures tab audio using `chrome.tabCapture` — no screen picker, no user gesture needed after the initial click.

## How It Works

```
Tab Audio → chrome.tabCapture → Offscreen Doc → PCM16 @ 16kHz → HTTP POST → Percept Receiver → Whisper → Pipeline
```

- **Background (service worker):** Manages capture sessions, coordinates with popup
- **Offscreen document:** Processes audio (MV3 workers can't access MediaStream)  
- **Popup:** One-click start/stop UI

## Integration with CLI

```bash
# Auto-detect mode watches for meetings and prompts to capture
percept capture-browser watch

# Status shows active extension captures
percept capture-browser status
```

## Requirements

- Chrome 116+ (offscreen document support)
- Percept receiver running (`percept serve` or receiver on port 8900)
