#!/usr/bin/env python3
"""
Qwen3-TTS VoiceDesign Server — OpenAI-compatible TTS API

Environment variables:
  TTS_SEED        Default random seed for voice timbre (default: 4096)
  TTS_INSTRUCT    Default voice description prompt
  TTS_MODEL_PATH  Path to VoiceDesign model weights
  TTS_PORT        Server port (default: 8881)
  TTS_HOST        Bind address (default: 0.0.0.0)

Endpoints:
  POST /v1/audio/speech   OpenAI-compatible (input, model, voice, response_format, speed)
  POST /tts               Custom (text, seed, instruct, format)
  GET  /tts               Quick test (?text=...&seed=...&format=...)
  GET  /health            Health check
  GET  /v1/models         Model list
"""
import os, io, time

# Clear proxy env (avoid corporate proxy interference)
for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch, numpy as np, random
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import soundfile as sf
import uvicorn

# ---------- Config from env ----------
DEFAULT_SEED = int(os.environ.get("TTS_SEED", "4096"))
DEFAULT_INSTRUCT = os.environ.get("TTS_INSTRUCT", (
    "A warm and gentle female voice, soft and clear, "
    "with a natural, unhurried pace. Pleasant and inviting."
))
MODEL_PATH = os.environ.get("TTS_MODEL_PATH", "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
PORT = int(os.environ.get("TTS_PORT", "8881"))
HOST = os.environ.get("TTS_HOST", "0.0.0.0")

app = FastAPI(title="Qwen3-TTS VoiceDesign Server")
model = None


def load_model():
    global model
    if model is None:
        from qwen_tts import Qwen3TTSModel
        print(f"Loading VoiceDesign model from {MODEL_PATH}...")
        model = Qwen3TTSModel.from_pretrained(
            MODEL_PATH, device_map="cuda", torch_dtype="auto"
        )
        print(f"Model loaded! Default seed={DEFAULT_SEED}")
    return model


# ---------- Request schemas ----------
class TTSRequest(BaseModel):
    text: str
    seed: Optional[int] = None
    instruct: Optional[str] = None
    format: Optional[str] = "mp3"

class OpenAITTSRequest(BaseModel):
    model: str = "qwen3-tts"
    input: str
    voice: str = "default"
    response_format: str = "mp3"
    speed: float = 1.0


# ---------- Endpoints ----------
@app.post("/v1/audio/speech")
async def openai_tts(req: OpenAITTSRequest):
    return await generate(req.input, DEFAULT_SEED, None, req.response_format)

@app.post("/tts")
async def tts(req: TTSRequest):
    return await generate(req.text, req.seed, req.instruct, req.format)

@app.get("/tts")
async def tts_get(text: str, seed: int = DEFAULT_SEED, format: str = "mp3"):
    return await generate(text, seed, None, format)


async def generate(text: str, seed: Optional[int], instruct: Optional[str], fmt: str):
    m = load_model()
    inst = instruct or DEFAULT_INSTRUCT
    s = seed if seed is not None else DEFAULT_SEED

    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)
    np.random.seed(s)
    random.seed(s)

    t0 = time.time()
    wavs, sr = m.generate_voice_design(text=text, instruct=inst)
    wav = wavs[0]
    elapsed = time.time() - t0
    print(f"Generated: {len(wav)/sr:.1f}s audio in {elapsed:.1f}s (seed={s})")

    buf = io.BytesIO()
    if fmt == "wav":
        sf.write(buf, wav, sr, format="WAV")
        media = "audio/wav"
    else:
        sf.write(buf, wav, sr, format="WAV")
        buf.seek(0)
        from pydub import AudioSegment
        audio = AudioSegment.from_wav(buf)
        buf = io.BytesIO()
        audio.export(buf, format="mp3")
        media = "audio/mpeg"

    buf.seek(0)
    return StreamingResponse(buf, media_type=media,
        headers={"X-Generation-Time": f"{elapsed:.2f}s", "X-Seed": str(s)})


@app.get("/v1/models")
def models():
    return {"object": "list", "data": [
        {"id": "qwen3-tts", "object": "model", "created": 1738368000, "owned_by": "local"},
    ]}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "seed": DEFAULT_SEED,
        "model": MODEL_PATH.split("/")[-1] if "/" in MODEL_PATH else MODEL_PATH,
        "port": PORT,
    }


if __name__ == "__main__":
    load_model()
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
