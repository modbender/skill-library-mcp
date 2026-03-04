# Voice Assistant Architecture

## Source Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/assistant.py` | ~300 | Main orchestration loop (wake → record → transcribe → gateway → speak → follow-up) |
| `src/audio_pipeline.py` | ~325 | Mic stream, Porcupine wake word, silence detection, Whisper STT, mic suppression |
| `src/gateway_client.py` | ~190 | Async WebSocket client for OpenClaw gateway with queue-based message routing |
| `src/tts_player.py` | ~140 | ElevenLabs TTS with MP3→WAV decode via PyAV, blocking playback via winsound |
| `src/config.py` | ~40 | .env loader with defaults |

## Data Flow

```
          ┌──────────────┐
          │  Microphone   │
          └──────┬───────┘
                 │ int16 PCM @ 16kHz
                 ▼
     ┌───────────────────────┐
     │   AudioPipeline       │
     │  ┌─────────────────┐  │
     │  │ Porcupine       │  │◄── wake word detection (idle mode)
     │  └────────┬────────┘  │
     │           │ wake!     │
     │  ┌────────▼────────┐  │
     │  │ Recording +     │  │◄── silence detection (RMS < 300 for 1.5s)
     │  │ Silence Detect  │  │    2s grace period ignores initial silence
     │  └────────┬────────┘  │
     │           │ audio     │
     │  ┌────────▼────────┐  │
     │  │ faster-whisper   │  │◄── CPU, int8 quantization
     │  │ (STT)           │  │
     │  └────────┬────────┘  │
     └───────────│───────────┘
                 │ text
                 ▼
     ┌───────────────────────┐
     │   GatewayClient       │
     │   WebSocket to        │──► ws://127.0.0.1:18789
     │   OpenClaw Gateway    │
     └───────────┬───────────┘
                 │ streamed response
                 ▼
     ┌───────────────────────┐
     │   tts_player          │
     │   ElevenLabs API      │──► mp3_44100_128
     │   PyAV MP3→WAV        │
     │   winsound playback   │──► Speaker
     └───────────┬───────────┘
                 │ done
                 ▼
          Follow-up listen
          (5s window)
```

## WebSocket Protocol

The gateway client uses OpenClaw's WebSocket protocol v3:

**Handshake:**
1. Gateway sends `connect.challenge` with nonce
2. Client sends `connect` request with auth token, client ID `node-host`, mode `node`
3. Gateway responds with `hello-ok`

**Chat messages:**
- Client sends `chat.send` request with `sessionKey: "main"` and text
- Gateway ACKs the request
- Gateway streams `chat` events with states: `delta` (partial), `final` (complete), `error`, `aborted`
- Response text is in `payload.message.content[0].text`

**Concurrency model:**
- WebSockets library only allows one concurrent `recv()` per connection
- Solution: single background task `_handle_events()` reads all frames
- Per-request UUID queues route responses back to callers

## Mic Suppression

Every sound playback follows:
```
suppress_mic() → play audio (blocking) → sleep(0.15s) → unsuppress_mic()
```

This prevents:
- Wake word false triggers from speaker output
- Whisper transcribing the AI's own response as user input
- Feedback loops between mic and speaker

The 0.15s delay accounts for speaker echo decay time.

## Conversation Mode

After TTS finishes, the assistant enters follow-up mode:
1. 0.15s echo decay
2. 0.8s breathing room (POST_SPEECH_PAUSE)
3. Plays chime, starts recording
4. Waits up to 5s for speech (FOLLOW_UP_WINDOW)
5. If speech detected → transcribe → send → speak → loop
6. If 5s silence → conversation ends, returns to idle wake word detection

## Platform Notes

- **Windows only**: Uses `winsound` for audio playback (avoids conflicts with active `sounddevice.InputStream`)
- **sounddevice over PyAudio**: PyAudio doesn't build on Python 3.14+ Windows
- **PyAV for MP3 decode**: ElevenLabs Starter tier only supports MP3 (PCM needs Pro at $22/mo)
- **System tray**: `pystray` + `Pillow` for background operation with Pause/Resume/Quit
- **Global hotkey**: `pynput.keyboard.GlobalHotKeys` as wake word alternative

## ElevenLabs Tier Requirements

| Tier | Cost | Supports |
|------|------|----------|
| Free | $0 | Default voices only (e.g. Matilda). 10k chars/mo |
| Starter | $5/mo | + library voices (e.g. Ivy), 30k chars/mo |
| Pro | $22/mo | + PCM format (lower latency), 100k chars/mo |

Default voice: Matilda (`XrExE9yKIg1WjnnlVkGX`, free tier).
Recommended upgrade: Ivy (`MClEFoImJXBTgLwdLI5n`, Starter tier).
