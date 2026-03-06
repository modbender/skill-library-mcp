---
name: "Skill: telegram-media"
description: Send rich media through Telegram — photos, charts, voice messages,
  and documents. Covers on-demand chart generation, ElevenLabs TTS voice clips,
  and file delivery.
---

# Skill: telegram-media

## CRITICAL RULE — NO FABRICATION
**You MUST actually execute every command using your shell/exec tool.** Never pretend you sent a photo, voice note, or chart. If a command fails, report the actual error to Boss Man.

## Purpose
Send rich media through Telegram — photos, charts, voice messages, and documents. Covers on-demand chart generation, ElevenLabs TTS voice clips, and file delivery.

## When to Use
- Boss Man asks "show me the BTC chart" or "send me the charts"
- Boss Man asks to hear something as a voice note
- Sending generated images, PDFs, or files through Telegram
- "Generate a voice clip saying X"
- Any request to send media (not just text) via Telegram

## Environment
All commands run from `~/clawd` where `load_env.py` loads the `.env` file containing `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `ELEVEN_API_KEY`, and `ELEVEN_VOICE_ID`.

Boss Man's chat ID: `7887978276`

## Send a Photo/Chart via Telegram
```bash
cd ~/clawd && python3 -c "
import os, sys, requests
sys.path.insert(0, '.')
import load_env
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '7887978276')
with open('PHOTO_PATH', 'rb') as f:
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto',
        data={'chat_id': CHAT, 'caption': 'CAPTION_HERE'},
        files={'photo': f}, timeout=30)
print(r.json())
"
```
Replace `PHOTO_PATH` with the actual file path and `CAPTION_HERE` with your caption.

## Send a Document/File via Telegram
```bash
cd ~/clawd && python3 -c "
import os, sys, requests
sys.path.insert(0, '.')
import load_env
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '7887978276')
with open('FILE_PATH', 'rb') as f:
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendDocument',
        data={'chat_id': CHAT, 'caption': 'CAPTION_HERE'},
        files={'document': f}, timeout=30)
print(r.json())
"
```

## Generate and Send Charts

### Full Suite (All Assets)
Generates candlestick + Fibonacci + SMA + RSI charts for all tracked assets.
```bash
cd ~/clawd && python3 crypto_charts.py
```
Charts are saved to `~/clawd/charts/` as PNG files (e.g., `chart_btc.png`, `chart_eth.png`, `chart_xrp.png`, `chart_sui.png`, `chart_xau.png`, `chart_xag.png`).

### Single Asset Chart
```bash
cd ~/clawd && python3 crypto_charts.py --coin bitcoin
```

### Send a Generated Chart
After generating, send it:
```bash
cd ~/clawd && python3 -c "
import os, sys, requests
sys.path.insert(0, '.')
import load_env
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '7887978276')
with open('charts/chart_btc.png', 'rb') as f:
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto',
        data={'chat_id': CHAT, 'caption': 'BTC — Daily TA Chart'},
        files={'photo': f}, timeout=30)
print(r.json())
"
```

### Generate + Send All Charts (One-Shot)
```bash
cd ~/clawd && python3 crypto_charts.py && python3 -c "
import os, sys, glob, requests, time
sys.path.insert(0, '.')
import load_env
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '7887978276')
for chart in sorted(glob.glob('charts/chart_*.png')):
    name = os.path.basename(chart).replace('chart_', '').replace('.png', '').upper()
    with open(chart, 'rb') as f:
        r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto',
            data={'chat_id': CHAT, 'caption': f'{name} — Daily TA Chart'},
            files={'photo': f}, timeout=30)
    print(f'Sent {name}: {r.status_code}')
    time.sleep(0.5)
"
```

## ElevenLabs TTS — Generate Voice Notes

### Generate a Voice Clip
```bash
cd ~/clawd && python3 -c "
import os, sys, requests
sys.path.insert(0, '.')
import load_env
API_KEY = os.getenv('ELEVEN_API_KEY') or os.getenv('ELEVENLABS_API_KEY')
VOICE_ID = os.getenv('ELEVEN_VOICE_ID', '1SM7GgM6IMuvQlz2BwM3')
text = '''TEXT_TO_SPEAK'''
r = requests.post(
    f'https://api.xi-labs.com/v1/text-to-speech/{VOICE_ID}',
    headers={'xi-api-key': API_KEY, 'Content-Type': 'application/json'},
    json={'text': text, 'model_id': 'eleven_multilingual_v2',
          'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75}},
    timeout=30)
if r.status_code == 200:
    with open('/tmp/frank_voice.mp3', 'wb') as f:
        f.write(r.content)
    print('Voice clip saved to /tmp/frank_voice.mp3')
else:
    print(f'TTS error: {r.status_code} {r.text[:200]}')
"
```

### Send Voice Note via Telegram
```bash
cd ~/clawd && python3 -c "
import os, sys, requests
sys.path.insert(0, '.')
import load_env
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '7887978276')
with open('/tmp/frank_voice.mp3', 'rb') as f:
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendVoice',
        data={'chat_id': CHAT, 'caption': 'Voice note from Frank'},
        files={'voice': f}, timeout=30)
print(r.json())
"
```

### One-Shot: Generate TTS + Send as Voice Note
```bash
cd ~/clawd && python3 -c "
import os, sys, requests
sys.path.insert(0, '.')
import load_env
API_KEY = os.getenv('ELEVEN_API_KEY') or os.getenv('ELEVENLABS_API_KEY')
VOICE_ID = os.getenv('ELEVEN_VOICE_ID', '1SM7GgM6IMuvQlz2BwM3')
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '7887978276')
text = '''TEXT_TO_SPEAK'''
r = requests.post(
    f'https://api.xi-labs.com/v1/text-to-speech/{VOICE_ID}',
    headers={'xi-api-key': API_KEY, 'Content-Type': 'application/json'},
    json={'text': text, 'model_id': 'eleven_multilingual_v2',
          'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75}},
    timeout=30)
if r.status_code == 200:
    with open('/tmp/frank_voice.mp3', 'wb') as f:
        f.write(r.content)
    import time; time.sleep(0.5)
    with open('/tmp/frank_voice.mp3', 'rb') as f:
        r2 = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendVoice',
            data={'chat_id': CHAT},
            files={'voice': f}, timeout=30)
    print(f'Voice sent: {r2.status_code}')
else:
    print(f'TTS error: {r.status_code}')
"
```

## Rules
- **EXECUTE EVERY COMMAND FOR REAL** — use your shell/exec tool. Never pretend you sent media.
- Always print the API response so you can confirm delivery
- Charts must be generated BEFORE sending — run `crypto_charts.py` first if charts don't exist or are stale
- For TTS, replace `TEXT_TO_SPEAK` with the actual text (keep under 5000 chars for ElevenLabs)
- If Boss Man says "show me the charts" — generate fresh ones and send all of them
- If Boss Man says "send me a voice note about X" — generate TTS of your analysis, then send
- Clawdbot already has TTS auto-mode for inbound messages, but this skill is for ON-DEMAND voice clips you choose to send
