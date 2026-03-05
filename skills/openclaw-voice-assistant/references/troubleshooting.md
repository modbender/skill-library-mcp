# Voice Assistant Troubleshooting

## Gateway Connection

**"Failed to connect to gateway"**
- Ensure OpenClaw gateway is running on the configured `GATEWAY_URL` (default: `ws://127.0.0.1:18789`)
- Check that `GATEWAY_TOKEN` in `.env` matches your gateway's auth token
- Verify the port isn't blocked by firewall

**"Gateway auth failed"**
- Token mismatch: double-check `GATEWAY_TOKEN` value
- The client must use ID `node-host` with mode `node` — other IDs are rejected

## Microphone

**No audio / wake word never triggers**
- Check that your mic is set as the default input device in Windows Sound settings
- Test the mic in another app first
- Try increasing `WAKE_SENSITIVITY` (e.g. `0.9`) — range is 0.0 to 1.0
- Ensure no other app is exclusively holding the mic

**Wake word triggers too easily (false positives)**
- Lower `WAKE_SENSITIVITY` (e.g. `0.5`)
- Use a more distinctive custom wake word via Picovoice Console

**Recording stops too early / too late**
- Adjust `SILENCE_TIMEOUT` — lower values (e.g. `1.0`) cut faster, higher values (e.g. `2.5`) wait longer
- The 2-second grace period at the start is hardcoded to prevent premature cutoffs

## Speech-to-Text

**Whisper transcribes silence as random words**
- This is a known Whisper behavior — the RMS threshold (300) and 2s grace period mitigate it
- If it persists, try the `small` model (`WHISPER_MODEL=small`) which is more accurate but slower

**First transcription is slow**
- Whisper downloads the model on first use (~150MB for `base`)
- Subsequent runs use the cached model

**Model options** (speed vs accuracy tradeoff):
| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~75MB | Fastest | Lower |
| base | ~150MB | Fast | Good (default) |
| small | ~500MB | Medium | Better |
| medium | ~1.5GB | Slow | High |
| large | ~3GB | Slowest | Highest |

## Text-to-Speech

**"402 Payment Required" from ElevenLabs**
- Free tier works with default voices (e.g. Matilda: `XrExE9yKIg1WjnnlVkGX`)
- Library/community voices (e.g. Ivy: `MClEFoImJXBTgLwdLI5n`) require Starter tier ($5/mo)
- If you get a 402, switch to a default voice or upgrade your plan

**No audio plays / TTS error**
- Verify `ELEVENLABS_API_KEY` is valid
- Check `ELEVENLABS_VOICE_ID` exists in your ElevenLabs account
- Ensure `av` (PyAV) is installed: `pip install av`

**Choppy or garbled audio**
- The MP3→WAV decode handles multi-channel and float audio automatically
- If issues persist, try a different `ELEVENLABS_MODEL_ID`

## Wake Word (Porcupine)

**"PORCUPINE_ACCESS_KEY not set"**
- Sign up free at https://picovoice.ai
- Copy your access key to `.env`

**Custom wake word not recognized**
- Ensure `PORCUPINE_MODEL_PATH` points to a valid `.ppn` file
- The `.ppn` file must match your platform (download the Windows version)
- Without a custom model, falls back to built-in "hey google"

**"Access key expired"**
- Free Picovoice keys expire periodically — generate a new one at picovoice.ai

## System Tray

**No tray icon appears**
- Ensure `pystray` and `Pillow` are installed
- The assistant falls back to console mode if pystray isn't available
- Run `generate_assets.py` to create the tray icon if `assets/icon.png` is missing

## General

**Python version issues**
- Requires Python 3.10+ (uses `X | Y` union syntax)
- Tested on Python 3.14 — PyAudio doesn't build on 3.14, which is why we use `sounddevice`

**Hotkey doesn't work**
- Some hotkey combos conflict with Windows shortcuts
- Try a different combo in `.env` (e.g. `HOTKEY=ctrl+alt+v`)
- Hotkey requires `pynput` to be installed

**Speaker feedback / echo**
- Mic suppression should prevent this automatically
- If you still hear feedback, try lowering your speaker volume or using headphones
- The 0.15s post-playback buffer accounts for echo decay
