"""
Qwen3-TTS Local Inference — Configuration

All settings can be overridden via environment variables.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Model directory — where downloaded model weights are stored
# ---------------------------------------------------------------------------
_DEFAULT_MODEL_DIR = os.path.join(
    Path(__file__).resolve().parent.parent.as_posix(), "models"
)
MODEL_DIR: str = os.environ.get("QWEN_TTS_MODEL_DIR", _DEFAULT_MODEL_DIR)

# ---------------------------------------------------------------------------
# Model size selection: "small" (0.6B, default) or "large" (1.7B)
# ---------------------------------------------------------------------------
_MODEL_SIZE_RAW = os.environ.get("QWEN_TTS_MODEL_SIZE", "small").strip().lower()
USE_SMALL_MODEL: bool = _MODEL_SIZE_RAW != "large"
MODEL_SIZE_LABEL: str = "small" if USE_SMALL_MODEL else "large"

# ---------------------------------------------------------------------------
# Hugging Face model IDs
# ---------------------------------------------------------------------------
LARGE_MODELS = {
    "custom-voice": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "voice-design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "voice-clone": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
}

SMALL_MODELS = {
    "custom-voice": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    "voice-design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",  # no 0.6B VoiceDesign
    "voice-clone": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
}

TOKENIZER_ID = "Qwen/Qwen3-TTS-Tokenizer-12Hz"

MODEL_VARIANTS: dict[str, str] = SMALL_MODELS if USE_SMALL_MODEL else LARGE_MODELS

# ---------------------------------------------------------------------------
# Device & dtype
# ---------------------------------------------------------------------------
try:
    import torch as _torch

    _HAS_CUDA = _torch.cuda.is_available()
except Exception:
    _HAS_CUDA = False

DEVICE: str = os.environ.get("QWEN_TTS_DEVICE", "cuda:0" if _HAS_CUDA else "cpu")
_DEFAULT_DTYPE = "bfloat16" if _HAS_CUDA else "float32"
DTYPE: str = os.environ.get("QWEN_TTS_DTYPE", _DEFAULT_DTYPE)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
OUTPUT_DIR: str = os.environ.get(
    "QWEN_TTS_OUTPUT_DIR", os.path.join(os.getcwd(), "tts_output")
)

# ---------------------------------------------------------------------------
# Available speakers for CustomVoice models
# ---------------------------------------------------------------------------
SPEAKERS: list[dict[str, str]] = [
    {"name": "Vivian", "description": "Bright, slightly edgy young female voice", "native_lang": "Chinese"},
    {"name": "Serena", "description": "Warm, gentle young female voice", "native_lang": "Chinese"},
    {"name": "Uncle_Fu", "description": "Seasoned male voice with a low, mellow timbre", "native_lang": "Chinese"},
    {"name": "Dylan", "description": "Youthful Beijing male voice with a clear, natural timbre", "native_lang": "Chinese (Beijing Dialect)"},
    {"name": "Eric", "description": "Lively Chengdu male voice with a slightly husky brightness", "native_lang": "Chinese (Sichuan Dialect)"},
    {"name": "Ryan", "description": "Dynamic male voice with strong rhythmic drive", "native_lang": "English"},
    {"name": "Aiden", "description": "Sunny American male voice with a clear midrange", "native_lang": "English"},
    {"name": "Ono_Anna", "description": "Playful Japanese female voice with a light, nimble timbre", "native_lang": "Japanese"},
    {"name": "Sohee", "description": "Warm Korean female voice with rich emotion", "native_lang": "Korean"},
]

SPEAKER_NAMES: list[str] = [s["name"] for s in SPEAKERS]

# ---------------------------------------------------------------------------
# Supported languages
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES: list[str] = [
    "Chinese", "English", "Japanese", "Korean",
    "German", "French", "Russian", "Portuguese",
    "Spanish", "Italian", "Auto",
]
