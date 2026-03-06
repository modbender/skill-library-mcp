---
name: voice-stt-tts
description: Full voice message setup (STT + TTS) for OpenClaw using faster-whisper and Edge TTS
homepage: https://docs.openclaw.ai/nodes/audio
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "install": [
          {
            "id": "faster-whisper-venv",
            "kind": "bash",
            "label": "Install faster-whisper in venv",
            "command": "python3 -m venv ~/.openclaw/workspace/voice-messages && ~/.openclaw/workspace/voice-messages/bin/pip install faster-whisper"
          },
          {
            "id": "transcribe-script",
            "kind": "bash",
            "label": "Create transcribe.py script",
            "command": "cat > ~/.openclaw/workspace/voice-messages/transcribe.py << 'EOF'\n#!/usr/bin/env python3\nimport argparse\nfrom faster_whisper import WhisperModel\n\ndef transcribe(audio_path: str, model_name: str = \"small\", lang: str = \"en\", device: str = \"cpu\") -> str:\n    model = WhisperModel(\n        model_name,\n        device=device,\n        compute_type=\"int8\" if device == \"cpu\" else \"float16\",\n    )\n    segments, _ = model.transcribe(audio_path, language=lang, vad_filter=True)\n    text = \" \".join(seg.text.strip() for seg in segments if seg.text and seg.text.strip()).strip()\n    return text\n\ndef main():\n    p = argparse.ArgumentParser()\n    p.add_argument(\"--audio\", required=True)\n    p.add_argument(\"--model\", default=\"small\")\n    p.add_argument(\"--lang\", default=\"en\")\n    p.add_argument(\"--device\", default=\"cpu\", choices=[\"cpu\", \"cuda\"])\n    args = p.parse_args()\n    text = transcribe(args.audio, args.model, args.lang, args.device)\n    print(text if text else \"\")\nif __name__ == \"__main__\":\n    main()\nEOF"
          }
        ]
      }
  }
---

# Voice Messages (STT + TTS) for OpenClaw 🎙️

Complete voice message setup using **faster-whisper** for transcription and **Edge TTS** for voice replies.

## What we configure

- ✅ **STT** (Speech-to-Text) — transcribe voice messages via faster-whisper
- ✅ **TTS** (Text-to-Speech) — voice replies via Edge TTS
- 🎯 **Result:** voice → text → reply with voice

---

## Installation

### 1. Create virtual environment (venv)

For Ubuntu create an isolated venv:

```bash
python3 -m venv ~/.openclaw/workspace/voice-messages
```

### 2. Install faster-whisper

Install packages in venv:

```bash
~/.openclaw/workspace/voice-messages/bin/pip install faster-whisper
```

**What gets installed:**
- `faster-whisper` — Python library for transcription
- Dependencies: `ctranslate2`, `onnxruntime`, `huggingface-hub`, `av`, `numpy`, and others.
- Size: ~250 MB

---

## Transcription Script

### Path and content

**File:** `~/.openclaw/workspace/voice-messages/transcribe.py`

```python
#!/usr/bin/env python3
import argparse
from faster_whisper import WhisperModel


def transcribe(audio_path: str, model_name: str = "small", lang: str = "en", device: str = "cpu") -> str:
    model = WhisperModel(
        model_name,
        device=device,
        compute_type="int8" if device == "cpu" else "float16",
    )
    segments, _ = model.transcribe(audio_path, language=lang, vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments if seg.text and seg.text.strip()).strip()
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True)
    p.add_argument("--model", default="small")
    p.add_argument("--lang", default="en")
    p.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    args = p.parse_args()

    text = transcribe(args.audio, args.model, args.lang, args.device)
    print(text if text else "")


if __name__ == "__main__":
    main()
```

**What the script does:**
1. Accepts audio file path (`--audio`)
2. Loads Whisper model (`--model`): `small` by default
3. Sets language (`--lang`): `en` for English
4. Transcribes with VAD filter (Voice Activity Detection)
5. Outputs clean text to stdout

### Make file executable:

```bash
chmod +x ~/.openclaw/workspace/voice-messages/transcribe.py
```

---

## OpenClaw Configuration

### 1. Configure STT (`tools.media.audio`)

Add to `~/.openclaw/openclaw.json`:

```json5
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "maxBytes": 20971520,
        "models": [
          {
            "type": "cli",
            "command": "~/.openclaw/workspace/voice-messages/bin/python",
            "args": [
              "~/.openclaw/workspace/voice-messages/transcribe.py",
              "--audio",
              "{{MediaPath}}",
              "--lang",
              "en",
              "--model",
              "small"
            ],
            "timeoutSeconds": 120
          }
        ]
      }
    }
  }
}
```

**Parameters:**

| Parameter | Value | Description |
|-----------|----------|-----------|
| `enabled` | `true` | Enable audio transcription |
| `maxBytes` | `20971520` | Max file size (20 MB) |
| `type` | `"cli"` | Model type: CLI command |
| `command` | Python path | Path to python in venv |
| `args` | argument array | Arguments for script |
| `{{MediaPath}}` | placeholder | Replaced with audio file path |
| `timeoutSeconds` | `120` | Transcription timeout (2 minutes) |

### 2. Configure TTS (`messages.tts`)

Add to `~/.openclaw/openclaw.json`:

```json5
{
  "messages": {
    "tts": {
      "auto": "inbound",
      "provider": "edge",
      "edge": {
        "voice": "en-US-JennyNeural",
        "lang": "en-US"
      }
    }
  }
}
```

**Parameters:**

| Parameter | Value | Description |
|-----------|----------|-----------|
| `auto` | `"inbound"` | **Key mode!** — reply with voice only on incoming voice messages |
| `provider` | `"edge"` | TTS provider (free, no API key) |
| `voice` | `"en-US-JennyNeural"` | Voice (see available below) |
| `lang` | `"en-US"` | Locale (en-US for US english) |

### 3. Full configuration example

```json5
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "maxBytes": 20971520,
        "models": [
          {
            "type": "cli",
            "command": "~/.openclaw/workspace/voice-messages/bin/python",
            "args": [
              "~/.openclaw/workspace/voice-messages/transcribe.py",
              "--audio",
              "{{MediaPath}}",
              "--lang",
              "en",
              "--model",
              "small"
            ],
            "timeoutSeconds": 120
          }
        ]
      }
    },
  },
  "messages": {
    "tts": {
      "auto": "inbound",
      "provider": "edge",
      "edge": {
        "voice": "en-US-JennyNeural",
        "lang": "en-US"
      }
    },
    "ackReactionScope": "group-mentions"
  }
}
```

---

## Apply Changes

### Restart Gateway

```bash
# Method 1: via openclaw CLI
openclaw gateway restart

# Method 2: via systemd
systemctl --user restart openclaw-gateway

# Check status
systemctl --user status openclaw-gateway
# Should show: active (running)
```

---

## Testing

### Test STT (transcription)

**Action:** Send a voice message to your Telegram bot

**Expected result:**
```
[Audio] User text: [Telegram ...] <media:audio> Transcript: <transcribed text>
```

**Example response:**
```
[Audio] User text: [Telegram kd (@someuser) id:12345678 +5s ...] <media:audio> Transcript: Hello. How are you?
```

### Test TTS (voice replies)

**Action:** After successful transcription, bot should send a voice reply

**Expected result:**
- Voice file arrives in Telegram
- Voice note (round bubble)

**Expected behavior:**
- Incoming voice → bot replies with voice
- Text messages → bot replies with text (this is normal!)

---

## Available Edge TTS Voices

### Female voices

| Voice | ID | Usage example |
|--------|-----|------------------|
| Jenny | `en-US-JennyNeural` | ← current |
| Ana | `en-US-AnaNeural` | Softer |

### Male voices

| Voice | ID | Usage example |
|--------|-----|------------------|
| Dmitry | `en-US-RogerNeural` | More bass |

**How to change voice:**
```bash
cat ~/.openclaw/openclaw.json | \
  jq '.messages.tts.edge.voice = "en-US-MichelleNeural"' > ~/.openclaw/openclaw.json.tmp
mv ~/.openclaw/openclaw.json.tmp ~/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway
```

---

## Additional Edge TTS Parameters

### Adjusting speed, pitch, volume

```json5
{
  "messages": {
    "tts": {
      "edge": {
        "voice": "en-US-JennyNeural",
        "lang": "en-US",
        "rate": "+10%",      // Speed: -50% to +100%
        "pitch": "-5%",     // Pitch: -50% to +50%
        "volume": "+5%"     // Volume: -100% to +100%
      }
    }
  }
}
```

---

## Troubleshooting

### Problem: Voice not transcribed

**Logs show:**
```
[ERROR] Transcription failed
```

**Possible causes:**
1. **File too large** — > 20 MB
   ```bash
   # Solution: Increase maxBytes in config
   maxBytes: 52428800  # 50 MB
   ```

2. **Timeout** — transcription took > 2 minutes
   ```bash
   # Solution: Increase timeoutSeconds
   timeoutSeconds: 180  # 3 minutes
   ```

3. **Model not downloaded** — first run
   ```bash
   # Solution: Wait while it downloads (1-2 minutes)
   # Models are cached in ~/.cache/huggingface/
   ```

### Problem: No voice reply

**Possible causes:**
1. **Reply too short** (< 10 characters)
   - TTS skips very short replies
   - Solution: this is expected behavior

2. **auto: "inbound"** but text message
   - TTS in `inbound` mode replies with voice only on **voice messages**
   - Text messages get text replies — this is correct!

3. **Edge TTS unavailable**
   ```bash
   # Check
   curl -s "https://speech.platform.bing.com/consumer/api/v1/tts" | head -c 100
   # If error — temporarily unavailable
   ```

---

## Performance

### Transcription time (Raspberry Pi 4/ARM)

| Whisper Model | Est. time | Quality |
|---------------|--------------|---------|
| `tiny` | ~5-10 sec | Low |
| `base` | ~10-20 sec | Medium |
| `small` | ~20-40 sec | High ← current |
| `medium` | ~40-80 sec | Very high |
| `large` | ~80-160 sec | Maximum |

**Recommendation:** For Raspberry Pi use `small` or `base`. `medium`/`large` will be very slow.

### Where Whisper models are stored

```bash
~/.cache/huggingface/
```

Models download automatically on first run.

## Done! 🎉

After completing these steps:

1. ✅ faster-whisper installed in venv
2. ✅ `transcribe.py` script created
3. ✅ OpenClaw configured (STT + TTS)
4. ✅ Gateway restarted
5. ✅ Voice messages working

Now your Telegram bot:
- 🎙️ **Accepts voice** → transcribes via faster-whisper
- 🎤 **Replies with voice** → generates via Edge TTS
- 💬 **Accepts text** → replies with text (as usual)

---

**Useful links:**
- OpenClaw docs: https://docs.openclaw.ai
- TTS docs: https://docs.openclaw.ai/tts
- Audio docs: https://docs.openclaw.ai/nodes/audio
- Install skills: `npx clawhub search voice`

---

*Created: 2026-03-01 for OpenClaw 2026.2.26*
