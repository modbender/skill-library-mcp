"""
tts_server.py — Qwen3-TTS FastAPI Server (OpenAI-compatible).

Provides a comprehensive TTS API with:
  - OpenAI-compatible /v1/audio/speech endpoint
  - Voice design from natural language descriptions
  - Voice cloning from reference audio
  - Persistent named voice management (save/load/list/rename/delete)
  - Audio format conversion
  - Telegram & WhatsApp PTT voice message delivery

Uses the official qwen_tts.Qwen3TTSModel API.

Author: daMustermann · Version: 1.0
"""

import json
import os
import sys
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Any

import soundfile as sf
import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Add server directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from audio_converter import convert_audio, convert_to_ogg_opus, get_audio_info
from model_loader import load_model, download_and_fix_model
from voice_cloner import VoiceCloner
from voice_designer import VoiceDesigner
from voice_manager import VoiceManager

# ─── Configuration ───
SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from config.json."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "models": {
            "default_model": "custom-voice-1.7b",
            "cache_dir": str(SKILL_DIR / "models"),
            "auto_download": True,
            "device": "auto",
        },
        "audio": {
            "sample_rate": 24000,
            "default_format": "wav",
            "output_dir": str(SKILL_DIR / "output"),
        },
        "voices": {
            "dir": str(SKILL_DIR / "voices"),
        },
    }


# ─── Model registry ───
MODELS = {
    "custom-voice-0.6b": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    "custom-voice-1.7b": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "base-0.6b": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    "base-1.7b": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "voice-design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
}

# Models that support generate_custom_voice (built-in speakers)
CUSTOM_VOICE_MODELS = {"custom-voice-0.6b", "custom-voice-1.7b"}

# Auto-correction: if user requests a base/design model for speech, swap to custom-voice
MODEL_AUTO_CORRECT = {
    "base-0.6b": "custom-voice-0.6b",
    "base-1.7b": "custom-voice-1.7b",
    "voice-design": "custom-voice-1.7b",
}


# ─── Language mapping (OpenAI-compatible short codes → Qwen3-TTS full names) ───
LANG_MAP = {
    "en": "English", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
    "de": "German", "fr": "French", "ru": "Russian", "pt": "Portuguese",
    "es": "Spanish", "it": "Italian", "auto": "Auto",
    # Also accept full names directly
    "english": "English", "chinese": "Chinese", "japanese": "Japanese",
    "korean": "Korean", "german": "German", "french": "French",
    "russian": "Russian", "portuguese": "Portuguese", "spanish": "Spanish",
    "italian": "Italian",
}


def normalize_language(lang: str) -> str:
    """Convert short language codes to Qwen3-TTS format."""
    return LANG_MAP.get(lang.lower(), lang)


# ─── Device detection ───
def get_device(override: Optional[str] = None) -> str:
    if override and override != "auto":
        return override
    if torch.cuda.is_available():
        return "cuda:0"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return "xpu:0"
    return "cpu"


def get_attn_impl() -> str:
    try:
        import flash_attn
        return "flash_attention_2"
    except ImportError:
        return "sdpa"


# ─── Globals (initialized at startup) ───
config: dict = {}
voice_manager: Optional[VoiceManager] = None
voice_designer: Optional[VoiceDesigner] = None
voice_cloner: Optional[VoiceCloner] = None
tts_model = None
tts_model_id: Optional[str] = None
output_dir: Path = SKILL_DIR / "output"

# Temporary storage for voice data from recent design/clone operations
# Maps voice_id -> { "ref_audio_path": str, "ref_text": str, "audio_data": ndarray, "sample_rate": int }
_temp_voice_store: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources at startup."""
    global config, voice_manager, output_dir

    config = load_config()

    # Initialize voice manager
    voices_dir = config.get("voices", {}).get("dir", str(SKILL_DIR / "voices"))
    voice_manager = VoiceManager(voices_dir)

    # Ensure output directory exists
    output_dir = Path(config.get("audio", {}).get("output_dir", str(SKILL_DIR / "output")))
    output_dir.mkdir(parents=True, exist_ok=True)

    device = get_device(config.get("models", {}).get("device"))
    attn = get_attn_impl()
    print(f"[INFO] Qwen3-TTS server starting on device: {device}, attention: {attn}")
    print(f"[INFO] Voices directory: {voices_dir}")
    print(f"[INFO] Output directory: {output_dir}")
    print(f"[INFO] Loaded {len(voice_manager.list_voices())} saved voices")

    yield

    # Cleanup
    if voice_designer:
        voice_designer.unload()
    if voice_cloner:
        voice_cloner.unload()
    _temp_voice_store.clear()


app = FastAPI(
    title="Qwen3-TTS OpenClaw Skill",
    description="High-quality TTS with voice design, voice cloning, and named voice persistence.",
    version="1.0",
    lifespan=lifespan,
)


# ═══════════════════════════════════════════════
#  Request/Response Models
# ═══════════════════════════════════════════════

class SpeechRequest(BaseModel):
    model: str = "custom-voice-1.7b"
    input: str
    voice: str = "default"
    speaker: str = "Chelsie"
    language: str = "en"
    instruct: str = ""
    response_format: str = "wav"
    speed: float = 1.0


class VoiceDesignRequest(BaseModel):
    model: str = "voice-design"
    input: str
    voice_description: str
    language: str = "en"
    response_format: str = "wav"


class VoiceSaveRequest(BaseModel):
    name: str
    source_voice_id: Optional[str] = None
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    language: str = "en"


class VoiceUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = None


class TelegramSendRequest(BaseModel):
    audio_file: str
    chat_id: str
    bot_token: Optional[str] = None
    caption: Optional[str] = None


class WhatsAppSendRequest(BaseModel):
    audio_file: str
    phone_number_id: Optional[str] = None
    recipient: str
    access_token: Optional[str] = None


# ═══════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════

def _get_tts_model(model_name: str = "custom-voice-1.7b"):
    """Lazy-load a TTS model. Pre-downloads and fixes speech_tokenizer if needed."""
    global tts_model, tts_model_id

    if tts_model is not None and tts_model_id == model_name:
        return tts_model

    model_hf_id = MODELS.get(model_name)
    if not model_hf_id:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model_name}. Available: {list(MODELS.keys())}")

    try:
        cache_dir = config.get("models", {}).get("cache_dir")
        device = get_device(config.get("models", {}).get("device"))

        print(f"[INFO] Loading model {model_name} ({model_hf_id})")
        tts_model = load_model(model_hf_id, cache_dir=cache_dir, device=device)
        tts_model_id = model_name
        print(f"[OK] Model {model_name} ready")
        return tts_model

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="qwen-tts package not installed. Run: pip install qwen-tts",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")


def _get_voice_designer():
    """Lazy-load the voice designer."""
    global voice_designer
    if voice_designer is None:
        cache_dir = config.get("models", {}).get("cache_dir")
        device = get_device(config.get("models", {}).get("device"))
        voice_designer = VoiceDesigner(cache_dir=cache_dir, device=device)
    return voice_designer


def _get_voice_cloner():
    """Lazy-load the voice cloner."""
    global voice_cloner
    if voice_cloner is None:
        cache_dir = config.get("models", {}).get("cache_dir")
        device = get_device(config.get("models", {}).get("device"))
        voice_cloner = VoiceCloner(cache_dir=cache_dir, device=device)
    return voice_cloner


def _generate_output_path(prefix: str = "speech", fmt: str = "wav") -> str:
    """Generate a unique output file path."""
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}.{fmt}"
    return str(output_dir / filename)


def _convert_if_needed(audio_path: str, target_format: str) -> str:
    """Convert audio to target format if different."""
    if target_format == "wav":
        return audio_path
    output_path = str(Path(audio_path).with_suffix(f".{target_format}"))
    return convert_audio(audio_path, output_path, target_format)


# ═══════════════════════════════════════════════
#  Health Check
# ═══════════════════════════════════════════════

@app.get("/health")
async def health_check():
    device = get_device(config.get("models", {}).get("device"))
    voices = voice_manager.list_voices() if voice_manager else []
    return {
        "status": "ok",
        "device": device,
        "attn_implementation": get_attn_impl(),
        "cuda_available": torch.cuda.is_available(),
        "saved_voices": len(voices),
        "version": "1.0",
    }


# ═══════════════════════════════════════════════
#  Speech Generation (OpenAI-compatible)
# ═══════════════════════════════════════════════

@app.post("/v1/audio/speech")
async def generate_speech(request: SpeechRequest):
    """
    Generate speech from text. OpenAI-compatible endpoint.

    Uses the CustomVoice model with built-in speakers (Chelsie, Ethan, etc.)
    or a saved voice via the voice cloner.
    """
    language = normalize_language(request.language)
    output_path = _generate_output_path("speech", "wav")

    try:
        # Auto-correct model: base/design models don't support generate_custom_voice
        model_name = request.model
        if model_name in MODEL_AUTO_CORRECT:
            corrected = MODEL_AUTO_CORRECT[model_name]
            print(f"[INFO] Auto-correcting model {model_name} → {corrected} for speech endpoint")
            model_name = corrected

        # Check if voice is a saved profile → use voice cloner
        if request.voice != "default" and voice_manager and voice_manager.voice_exists(request.voice):
            cloner = _get_voice_cloner()

            # Load the saved voice's reference audio for cloning
            profile = voice_manager.get_voice(request.voice)
            if profile is None:
                raise HTTPException(status_code=404, detail=f"Voice '{request.voice}' not found")

            # Load the saved reference audio and create a clone prompt
            sample_path = voice_manager.voices_dir / profile.sample_audio if profile.sample_audio else None
            if sample_path and sample_path.exists():
                result = cloner.clone(
                    text=request.input,
                    reference_audio_path=str(sample_path),
                    reference_text="",
                    language=language,
                    output_path=output_path,
                )
                # Increment usage
                voice_manager.load_embedding(request.voice)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Voice '{request.voice}' has no saved sample audio for cloning.",
                )
        else:
            # Use CustomVoice model with built-in speakers
            model = _get_tts_model(model_name)

            wavs, sr = model.generate_custom_voice(
                text=request.input,
                language=language,
                speaker=request.speaker,
                instruct=request.instruct if request.instruct else None,
            )

            audio = wavs[0]
            sf.write(output_path, audio, sr)

        # Convert to requested format
        final_path = _convert_if_needed(output_path, request.response_format)

        return FileResponse(
            final_path,
            media_type=f"audio/{request.response_format}",
            filename=Path(final_path).name,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {e}")


# ═══════════════════════════════════════════════
#  Voice Design
# ═══════════════════════════════════════════════

@app.post("/v1/audio/voice-design")
async def design_voice(request: VoiceDesignRequest):
    """Generate speech with a natural-language voice description."""
    designer = _get_voice_designer()
    language = normalize_language(request.language)
    output_path = _generate_output_path("vdesign", "wav")

    try:
        result = designer.generate(
            text=request.input,
            voice_description=request.voice_description,
            language=language,
            output_path=output_path,
        )

        # Store reference data for potential saving
        voice_id = result.get("voice_id", "")
        _temp_voice_store[voice_id] = {
            "audio_path": result["audio_path"],
            "audio_data": result.get("audio_data"),
            "sample_rate": result.get("sample_rate"),
            "ref_text": result.get("ref_text", request.input),
            "source": "voice-design",
            "description": request.voice_description,
        }

        # Convert to requested format
        final_path = _convert_if_needed(output_path, request.response_format)

        return FileResponse(
            final_path,
            media_type=f"audio/{request.response_format}",
            filename=Path(final_path).name,
            headers={"X-Voice-Id": voice_id},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice design failed: {e}")


# ═══════════════════════════════════════════════
#  Voice Cloning
# ═══════════════════════════════════════════════

@app.post("/v1/audio/voice-clone")
async def clone_voice(
    input: str = Form(...),
    reference_audio: UploadFile = File(...),
    reference_text: str = Form(""),
    language: str = Form("en"),
    response_format: str = Form("wav"),
):
    """Clone a voice from reference audio and generate new speech."""
    cloner = _get_voice_cloner()
    lang = normalize_language(language)
    output_path = _generate_output_path("vclone", "wav")

    # Save uploaded reference audio to temp file
    ref_suffix = Path(reference_audio.filename or "ref.wav").suffix or ".wav"
    fd, ref_path = tempfile.mkstemp(suffix=ref_suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            content = await reference_audio.read()
            f.write(content)

        result = cloner.clone(
            text=input,
            reference_audio_path=ref_path,
            reference_text=reference_text,
            language=lang,
            output_path=output_path,
        )

        # Store reference data for potential saving
        voice_id = result.get("voice_id", "")

        # Copy ref audio to a persistent temp location (don't delete yet)
        import shutil
        persist_ref_path = str(output_dir / f"ref_{voice_id}.wav")
        shutil.copy2(ref_path, persist_ref_path)

        _temp_voice_store[voice_id] = {
            "audio_path": result["audio_path"],
            "ref_audio_path": persist_ref_path,
            "ref_text": reference_text,
            "source": "voice-clone",
            "description": f"Cloned from uploaded audio",
        }

        # Convert to requested format
        final_path = _convert_if_needed(output_path, response_format)

        return FileResponse(
            final_path,
            media_type=f"audio/{response_format}",
            filename=Path(final_path).name,
            headers={"X-Voice-Id": voice_id},
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {e}")
    finally:
        # Clean up temp reference file (we saved a copy)
        if os.path.exists(ref_path):
            os.remove(ref_path)


# ═══════════════════════════════════════════════
#  Voice Management (CRUD)
# ═══════════════════════════════════════════════

@app.get("/v1/voices")
async def list_voices():
    """List all saved voice profiles, sorted by usage count."""
    if not voice_manager:
        raise HTTPException(status_code=500, detail="Voice manager not initialized")
    return {"voices": voice_manager.list_voices()}


@app.post("/v1/voices")
async def save_voice(request: VoiceSaveRequest):
    """
    Save/persist a voice profile with a user-chosen name.

    The source_voice_id must match a voice_id from a recent voice-design
    or voice-clone operation.
    """
    if not voice_manager:
        raise HTTPException(status_code=500, detail="Voice manager not initialized")

    if voice_manager.voice_exists(request.name):
        raise HTTPException(
            status_code=409,
            detail=f"Voice '{request.name}' already exists. Choose a different name or delete the existing one.",
        )

    # Get stored voice data
    voice_data = None
    if request.source_voice_id:
        voice_data = _temp_voice_store.pop(request.source_voice_id, None)

    if voice_data is None:
        raise HTTPException(
            status_code=400,
            detail="No voice data found. Generate a voice first using voice-design or voice-clone.",
        )

    try:
        # Save the reference audio as the voice's sample
        sample_audio_path = voice_data.get("audio_path") or voice_data.get("ref_audio_path")

        # Create a dummy embedding (the actual voice is stored as sample audio for re-cloning)
        embedding = torch.zeros(1)  # Placeholder — the real data is the sample audio

        profile = voice_manager.save_voice(
            name=request.name,
            embedding=embedding,
            description=request.description or voice_data.get("description", ""),
            source=voice_data.get("source", "unknown"),
            source_description=voice_data.get("description", ""),
            language=request.language,
            tags=request.tags,
            sample_audio_path=sample_audio_path,
        )
        return {"status": "saved", "voice": profile.to_dict()}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/voices/{name}")
async def get_voice(name: str):
    """Get details for a specific voice profile."""
    if not voice_manager:
        raise HTTPException(status_code=500, detail="Voice manager not initialized")

    profile = voice_manager.get_voice(name)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Voice '{name}' not found")

    return {"voice": profile.to_dict()}


@app.patch("/v1/voices/{name}")
async def update_voice(name: str, request: VoiceUpdateRequest):
    """Rename or update a voice profile."""
    if not voice_manager:
        raise HTTPException(status_code=500, detail="Voice manager not initialized")

    profile = voice_manager.get_voice(name)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Voice '{name}' not found")

    # Handle rename
    if request.name and request.name != name:
        try:
            profile = voice_manager.rename_voice(name, request.name)
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    # Handle metadata updates
    updated = voice_manager.update_voice(
        request.name or name,
        description=request.description,
        tags=request.tags,
        language=request.language,
    )

    if updated:
        return {"status": "updated", "voice": updated.to_dict()}
    return {"status": "no changes"}


@app.delete("/v1/voices/{name}")
async def delete_voice(name: str):
    """Delete a voice profile and all associated files."""
    if not voice_manager:
        raise HTTPException(status_code=500, detail="Voice manager not initialized")

    if not voice_manager.delete_voice(name):
        raise HTTPException(status_code=404, detail=f"Voice '{name}' not found")

    return {"status": "deleted", "name": name}


# ═══════════════════════════════════════════════
#  Audio Conversion
# ═══════════════════════════════════════════════

@app.post("/v1/audio/convert")
async def convert_audio_format(
    audio: UploadFile = File(...),
    target_format: str = Form("ogg"),
):
    """Convert audio between formats (WAV, MP3, OGG/Opus, FLAC)."""
    in_suffix = Path(audio.filename or "input.wav").suffix or ".wav"
    fd, input_path = tempfile.mkstemp(suffix=in_suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            content = await audio.read()
            f.write(content)

        output_path = _generate_output_path("converted", target_format)
        convert_audio(input_path, output_path, target_format)

        return FileResponse(
            output_path,
            media_type=f"audio/{target_format}",
            filename=Path(output_path).name,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)


# ═══════════════════════════════════════════════
#  Telegram Integration
# ═══════════════════════════════════════════════

@app.post("/v1/audio/send/telegram")
async def send_telegram(request: TelegramSendRequest):
    """Send audio as a Telegram PTT voice message."""
    from messaging.telegram_sender import send_voice_message

    bot_token = request.bot_token or config.get("telegram", {}).get("bot_token", "")
    if not bot_token:
        raise HTTPException(
            status_code=400,
            detail="Telegram bot_token required (in request or config.json)",
        )

    audio_path = os.path.expanduser(request.audio_file)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_path}")

    try:
        result = await send_voice_message(
            audio_path=audio_path,
            bot_token=bot_token,
            chat_id=request.chat_id,
            caption=request.caption,
        )
        return {"status": "sent", "telegram_response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram send failed: {e}")


# ═══════════════════════════════════════════════
#  WhatsApp Integration
# ═══════════════════════════════════════════════

@app.post("/v1/audio/send/whatsapp")
async def send_whatsapp(request: WhatsAppSendRequest):
    """Send audio as a WhatsApp PTT voice message."""
    from messaging.whatsapp_sender import send_voice_message

    phone_number_id = request.phone_number_id or config.get("whatsapp", {}).get("phone_number_id", "")
    access_token = request.access_token or config.get("whatsapp", {}).get("access_token", "")

    if not phone_number_id or not access_token:
        raise HTTPException(
            status_code=400,
            detail="WhatsApp phone_number_id and access_token required (in request or config.json)",
        )

    audio_path = os.path.expanduser(request.audio_file)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_path}")

    try:
        result = await send_voice_message(
            audio_path=audio_path,
            phone_number_id=phone_number_id,
            recipient=request.recipient,
            access_token=access_token,
        )
        return {"status": "sent", "whatsapp_response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WhatsApp send failed: {e}")


# ═══════════════════════════════════════════════
#  Server Info
# ═══════════════════════════════════════════════

@app.get("/v1/models")
async def list_models():
    """List available TTS models."""
    return {
        "models": [
            {"id": key, "hf_id": val, "object": "model"}
            for key, val in MODELS.items()
        ]
    }


@app.get("/v1/speakers")
async def list_speakers():
    """List built-in speakers for CustomVoice models."""
    try:
        model = _get_tts_model()
        speakers = model.get_supported_speakers()
        return {"speakers": speakers}
    except Exception:
        # Fallback if model not loaded
        return {
            "speakers": [
                "Chelsie", "Ethan", "Aidan", "Serena", "Ryan",
                "Vivian", "Claire", "Lucas", "Eleanor", "Benjamin",
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8880)
