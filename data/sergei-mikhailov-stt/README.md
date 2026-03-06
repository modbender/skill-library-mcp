# Speech to Text Skill for OpenClaw

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

An OpenClaw skill that transcribes voice messages to text using Yandex SpeechKit (with an extensible architecture for other providers).

Works with any messenger connected to OpenClaw. OpenClaw receives the voice file, saves it locally, and passes the path to this skill. The skill converts audio to text and returns the result.

Example path OpenClaw provides:
```
~/.openclaw/media/inbound/file_1---9a53bac2-0392-41e7-8300-1c08e8eec027.ogg
```

---

## Prerequisites

Before installing, make sure you have:

- **Python 3.8+** — `python3 --version`
- **FFmpeg** — required for audio conversion ([install guide](https://ffmpeg.org/download.html))
- **Node.js** — required for the ClawHub CLI
- **Yandex Cloud account** — to get your API key for Yandex SpeechKit ([Yandex Cloud Console](https://console.yandex.cloud))

Install FFmpeg if missing:
```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg

# Windows — download from https://ffmpeg.org/download.html and add to PATH
```

---

## Installation

### Step 1 — Install the ClawHub CLI

```bash
npm install -g clawhub
# or
pnpm add -g clawhub
```

### Step 2 — Install the skill

Run this from your OpenClaw workspace directory (or any directory — the skill installs into `./skills/`):

```bash
clawhub install sergei-mikhailov-stt
```

The skill will be placed at `./skills/sergei-mikhailov-stt/`.

> If you have an OpenClaw workspace configured, `clawhub` will automatically use `<workspace>/skills/` as the destination.

### Step 3 — Install Python dependencies

Navigate to the installed skill folder and install dependencies:

```bash
cd skills/sergei-mikhailov-stt
pip install -r requirements.txt
```

---

## Configuration

The skill requires two environment variables to work:

| Variable | Description |
|----------|-------------|
| `YANDEX_API_KEY` | Your Yandex SpeechKit API key |
| `YANDEX_FOLDER_ID` | Your Yandex Cloud folder (project) ID |

### Option A — Via `~/.openclaw/openclaw.json` (recommended)

This is the OpenClaw-native way. Add the variables to your OpenClaw configuration file:

```json
{
  "skills": {
    "entries": {
      "sergei-mikhailov-stt": {
        "env": {
          "YANDEX_API_KEY": "your_api_key_here",
          "YANDEX_FOLDER_ID": "your_folder_id_here"
        }
      }
    }
  }
}
```

OpenClaw will inject these variables when the skill runs, without exposing them in the skill folder.

### Option B — Via `.env` file in the skill folder

```bash
cd skills/sergei-mikhailov-stt
cp assets/env.example .env
```

Edit `.env`:
```
YANDEX_API_KEY=your_api_key_here
YANDEX_FOLDER_ID=your_folder_id_here
STT_DEFAULT_PROVIDER=yandex
```

### Option C — Via `config.json` in the skill folder

```bash
cd skills/sergei-mikhailov-stt
cp assets/config.example.json config.json
```

Edit `config.json` and fill in `api_key` and `folder_id` under the `yandex` provider section.

> **Note:** The skill is gated — OpenClaw will not load it until `YANDEX_API_KEY` and `YANDEX_FOLDER_ID` are set (via any of the options above).

---

## How to Get a Yandex API Key

1. Open [Yandex Cloud Console](https://console.yandex.cloud)
2. Create a project (folder) if you don't have one — note the **Folder ID**
3. Go to **Service Accounts** → create a service account with the `ai.speechkit.user` role
4. Go to **API Keys** → create an API key for the service account — note the **API Key**
5. Make sure SpeechKit is enabled in your project

---

## Usage

Once installed and configured, start a new OpenClaw session. The skill activates automatically when you:

- Send a voice message via any messenger while OpenClaw is connected
- Ask the assistant to transcribe a voice message
- Provide a path to an audio file for transcription

OpenClaw will automatically pass the file path to this skill. No manual invocation is needed.

### Examples

```
User: [sends a voice message]
OpenClaw: Recognized text: "Meeting tomorrow at 3 PM"

User: Transcribe this English voice message
OpenClaw: Recognized text (en-US): "Hello, how are you today?"
```

---

## Updating the Skill

```bash
clawhub install sergei-mikhailov-stt --force
cd skills/sergei-mikhailov-stt
pip install -r requirements.txt
```

Then start a new OpenClaw session to pick up the update.

---

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenClaw      │───▶│  STT Processor   │───▶│  STT Provider   │
│                 │    │                  │    │                 │
│ • Messenger API │    │ • Audio Handler  │    │ • Yandex API    │
│ • File Manager  │    │ • Config Manager │    │ • (extensible)  │
│ • Skill Router  │    │ • Error Handler  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Modules

- **`scripts/stt_processor.py`** — main orchestrator, entry point for OpenClaw
- **`scripts/audio_processor.py`** — audio conversion and validation via FFmpeg
- **`scripts/config_manager.py`** — loads config from JSON + env variables
- **`scripts/providers/`** — STT provider implementations (Yandex SpeechKit; extensible)

---

## Project Structure

```
sergei-mikhailov-stt/
├── SKILL.md                    # OpenClaw skill metadata and instructions
├── README.md                   # This file
├── LICENSE                     # MIT license
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── stt_processor.py        # Main STT orchestrator
│   ├── audio_processor.py      # Audio conversion via FFmpeg
│   ├── config_manager.py       # Configuration management
│   └── providers/
│       ├── __init__.py
│       ├── base_provider.py    # Abstract base class for providers
│       └── yandex_speechkit.py # Yandex SpeechKit integration
└── assets/
    ├── config.example.json     # Configuration template
    └── .env.example            # Environment variables template
```

---

## Adding a Custom STT Provider

### 1. Create the provider class

```python
# scripts/providers/your_provider.py
from .base_provider import BaseSTTProvider
from typing import Dict, Any, List

class YourProvider(BaseSTTProvider):
    name = "your_provider"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')

    def recognize(self, audio_file_path: str, language: str = 'ru-RU') -> str:
        # Your implementation here
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        return bool(config.get('api_key'))

    def get_supported_formats(self) -> List[str]:
        return ['ogg', 'wav', 'mp3']
```

### 2. Register the provider

In `scripts/stt_processor.py`, add to the `_get_provider` method:

```python
from providers.your_provider import YourProvider

if provider_name == 'your_provider':
    return YourProvider(provider_config)
```

### 3. Add provider configuration

In `config.json`:

```json
{
  "providers": {
    "your_provider": {
      "api_key": "${YOUR_PROVIDER_API_KEY}",
      "timeout": 30
    }
  }
}
```

---

## Troubleshooting

**Skill does not appear in OpenClaw**
- Check that `YANDEX_API_KEY` and `YANDEX_FOLDER_ID` are set — the skill is gated on these
- Check that `python3` and `ffmpeg` are on your PATH
- Start a new OpenClaw session after installation

**FFmpeg not found**
```bash
ffmpeg -version          # check
brew install ffmpeg      # macOS
sudo apt install ffmpeg  # Ubuntu/Debian
```

**API key errors**
- Verify the key and folder ID in your config
- Ensure the service account has the `ai.speechkit.user` role
- Check your Yandex Cloud account balance

**File too large**
- Yandex SpeechKit v1 sync API limit is 1 MB per request
- For longer recordings, consider upgrading to the async API

**Enable debug logging**
```bash
python -m scripts.stt_processor --file audio.ogg --verbose
```

---

## Development

For contributors who want to work with the source directly:

```bash
git clone https://github.com/bzSega/sergei-mikhailov-stt.git
cd sergei-mikhailov-stt
pip install -r requirements.txt
cp assets/env.example .env
# Edit .env with your credentials
```

Please follow PEP 8 and add docstrings to all public functions. Pull requests are welcome.

---

## Limitations

- Yandex SpeechKit v1 sync API: 1 MB per request (~30 seconds of voice)
- Supported formats: OGG, WAV, MP3, M4A, FLAC, AAC
- Languages: Russian (`ru-RU`), English (`en-US`)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Sergei Mikhailov** — [github.com/bzSega](https://github.com/bzSega)

Issues: [github.com/bzSega/sergei-mikhailov-stt/issues](https://github.com/bzSega/sergei-mikhailov-stt/issues)

## Acknowledgements

- Yandex for the SpeechKit API
- The OpenClaw community
