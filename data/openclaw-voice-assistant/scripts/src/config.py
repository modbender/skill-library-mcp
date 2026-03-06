"""Configuration loader — reads settings from .env file."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

# OpenClaw Gateway
GATEWAY_URL = os.getenv("GATEWAY_URL", "ws://127.0.0.1:18789")
GATEWAY_TOKEN = os.getenv("GATEWAY_TOKEN", "")

# ElevenLabs TTS
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "XrExE9yKIg1WjnnlVkGX")  # Matilda (free)
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")

# Porcupine Wake Word
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "")
_raw_model_path = os.getenv("PORCUPINE_MODEL_PATH", "")
# Resolve relative paths against project root
if _raw_model_path and not Path(_raw_model_path).is_absolute():
    PORCUPINE_MODEL_PATH = str(_project_root / _raw_model_path)
else:
    PORCUPINE_MODEL_PATH = _raw_model_path

# Whisper STT
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Audio settings
WAKE_SENSITIVITY = float(os.getenv("WAKE_SENSITIVITY", "0.7"))
SILENCE_TIMEOUT = float(os.getenv("SILENCE_TIMEOUT", "1.5"))
SAMPLE_RATE = 16000

# Hotkey
HOTKEY = os.getenv("HOTKEY", "ctrl+shift+k")

# Paths
ASSETS_DIR = _project_root / "assets"
