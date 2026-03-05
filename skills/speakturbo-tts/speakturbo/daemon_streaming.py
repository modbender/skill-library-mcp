#!/usr/bin/env python3
"""
speakturbo daemon - Ultra-fast TTS with TRUE streaming.
Auto-shuts down after 1 hour idle.
"""

import asyncio
import struct
import threading
import time
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse

from pocket_tts import TTSModel

# High-quality built-in voices only
VOICES = ["alba", "marius", "javert", "jean", "fantine", "cosette", "eponine", "azelma"]

# Auto-shutdown after 1 hour idle
IDLE_TIMEOUT_SECONDS = 3600

_model: Optional[TTSModel] = None
_voice_states: dict = {}
_last_request_time: float = time.time()


def get_model() -> TTSModel:
    global _model
    if _model is None:
        print("Loading TTS model...")
        _model = TTSModel.load_model()
    return _model


def get_voice_state(voice: str) -> dict:
    global _voice_states
    if voice not in _voice_states:
        print(f"Loading voice: {voice}")
        _voice_states[voice] = get_model().get_state_for_audio_prompt(voice)
    return _voice_states[voice]


def wav_header(sample_rate: int) -> bytes:
    """Streaming WAV header with max size."""
    return struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 0x7FFFFFFF + 36, b'WAVE', b'fmt ', 16, 1, 1,
        sample_rate, sample_rate * 2, 2, 16, b'data', 0x7FFFFFFF,
    )


def idle_monitor():
    """Background thread that shuts down after idle timeout."""
    import os
    import signal
    
    while True:
        time.sleep(60)  # Check every minute
        idle_time = time.time() - _last_request_time
        
        if idle_time > IDLE_TIMEOUT_SECONDS:
            print(f"\nIdle for {idle_time/60:.0f} minutes. Shutting down...")
            os.kill(os.getpid(), signal.SIGTERM)
            break


app = FastAPI(title="speakturbo")


# DNS rebinding protection - only allow localhost
@app.middleware("http")
async def validate_host(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0]
    if host not in {"127.0.0.1", "localhost"}:
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)


@app.get("/health")
async def health():
    global _last_request_time
    _last_request_time = time.time()
    
    idle_mins = (time.time() - _last_request_time) / 60
    return {
        "status": "ready",
        "voices": VOICES,
        "idle_timeout_mins": IDLE_TIMEOUT_SECONDS / 60,
    }


@app.get("/tts")
async def tts(text: str, voice: str = "alba"):
    """Ultra-fast streaming TTS."""
    global _last_request_time
    _last_request_time = time.time()
    
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if voice not in VOICES:
        raise HTTPException(status_code=400, detail=f"Voice must be one of: {VOICES}")
    
    model = get_model()
    voice_state = get_voice_state(voice)
    
    async def generate():
        yield wav_header(model.sample_rate)
        for chunk in model.generate_audio_stream(voice_state, text.strip()):
            yield (chunk.clamp(-1, 1) * 32767).short().numpy().tobytes()
            await asyncio.sleep(0)
        yield bytes(int(model.sample_rate * 0.15) * 2)  # Trailing silence
    
    return StreamingResponse(generate(), media_type="audio/wav")


def main():
    """Start the speakturbo daemon."""
    get_model()
    get_voice_state("alba")  # Pre-warm default
    
    # Start idle monitor thread
    monitor = threading.Thread(target=idle_monitor, daemon=True)
    monitor.start()
    
    print(f"Voices: {VOICES}")
    print(f"Auto-shutdown after {IDLE_TIMEOUT_SECONDS/60:.0f} min idle")
    print("Starting on :7125")
    uvicorn.run(app, host="127.0.0.1", port=7125, log_level="warning")


if __name__ == "__main__":
    main()
