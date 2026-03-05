"""
videochat-withme — Real-time AI video chat routed through your OpenClaw agent.
Conversation flows via OpenClaw chatCompletions API with full agent personality and memory.
"""

import os
import re
import uuid
import subprocess
import json
import base64
import struct
import tempfile
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import httpx

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("videochat-withme")

app = FastAPI()

AUDIO_DIR = Path(tempfile.gettempdir()) / "videochat_me_audio"
AUDIO_DIR.mkdir(exist_ok=True)

# ─── Configuration ───

AGENT_NAME = os.environ.get("AGENT_NAME", "AI Assistant")
USER_NAME = os.environ.get("USER_NAME", "User")


def _load_groq_key() -> str:
    """Load Groq API key for STT."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    fallback = Path(os.path.expanduser("~/.openclaw/secrets/groq_api_key.txt"))
    if fallback.exists():
        return fallback.read_text().strip()
    raise RuntimeError(
        "GROQ_API_KEY not set. Export it or put it in ~/.openclaw/secrets/groq_api_key.txt"
    )


def _load_gateway_config() -> tuple[int, str]:
    """Load OpenClaw gateway port and auth token from config file.

    Note: We read the token from the config file, NOT from OPENCLAW_GATEWAY_TOKEN
    env var, because OpenClaw sets that env var to an agent-scoped token which
    differs from the gateway HTTP auth token needed for /v1/chat/completions.
    """
    config_path = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
    if not config_path.exists():
        raise RuntimeError("OpenClaw config not found at ~/.openclaw/openclaw.json")

    config = json.loads(config_path.read_text())
    gw = config.get("gateway", {})
    port = gw.get("port", 18789)
    token = gw.get("auth", {}).get("token", "")
    if not token:
        raise RuntimeError("No gateway auth token found in config")
    return port, token


GROQ_API_KEY = _load_groq_key()
GROQ_BASE = "https://api.groq.com/openai/v1"

GW_PORT, GW_TOKEN = _load_gateway_config()
OPENCLAW_BASE = f"http://127.0.0.1:{GW_PORT}"

logger.info("Gateway configured on port %d", GW_PORT)

PORT = int(os.environ.get("PORT", "8766"))

ASSETS_DIR = Path(__file__).parent.parent / "assets"


# ─── Routes ───


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = ASSETS_DIR / "index.html"
    return HTMLResponse(
        content=html_path.read_text(encoding="utf-8"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"},
    )


@app.get("/api/config")
async def config():
    return JSONResponse({
        "agent_name": AGENT_NAME,
        "user_name": USER_NAME,
    })


@app.post("/api/chat")
async def chat(
    audio: UploadFile = File(...),
    image: Optional[UploadFile] = File(None),
    speed: str = Form("normal"),
    language: str = Form("zh"),
    voice: str = Form("zh-CN-XiaoxiaoNeural"),
):
    req_id = uuid.uuid4().hex

    # Save uploads
    audio_path = AUDIO_DIR / f"{req_id}.webm"
    audio_bytes = await audio.read()
    audio_path.write_bytes(audio_bytes)

    image_bytes = None
    if image is not None:
        image_bytes = await image.read()
        if image_bytes:
            image_path = AUDIO_DIR / f"{req_id}.jpg"
            image_path.write_bytes(image_bytes)

    # Convert audio for Whisper
    wav_path = AUDIO_DIR / f"{req_id}.wav"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(audio_path), "-ar", "16000", "-ac", "1", str(wav_path)],
            capture_output=True, timeout=30,
        )
        if result.returncode != 0 or not wav_path.exists():
            logger.warning("ffmpeg failed (rc=%d)", result.returncode)
            wav_path = audio_path
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning("ffmpeg exception: %s", e)
        wav_path = audio_path

    # Pipeline: STT → OpenClaw Chat → TTS
    transcription = transcribe_audio(wav_path)

    img_b64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else None
    reply_text = await get_openclaw_reply(transcription, img_b64, language)

    # TTS with speed and voice
    reply_filename = f"{req_id}_reply.mp3"
    reply_path = AUDIO_DIR / reply_filename
    generate_tts(reply_text, reply_path, voice=voice, speed=speed)

    return {
        "text": reply_text,
        "audio_url": f"/audio/{reply_filename}",
        "transcription": transcription,
    }


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    safe_name = Path(filename).name
    file_path = AUDIO_DIR / safe_name
    if not file_path.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    media = "audio/mpeg" if safe_name.endswith(".mp3") else "audio/wav"
    return FileResponse(file_path, media_type=media)


# ─── Pipeline Stage 1: STT (Groq Whisper) ───


def transcribe_audio(audio_path: Path) -> str:
    try:
        with open(audio_path, "rb") as f:
            resp = httpx.post(
                f"{GROQ_BASE}/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": (audio_path.name, f, "audio/wav")},
                data={"model": "whisper-large-v3-turbo", "language": "zh"},
                timeout=15,
            )
        if resp.status_code == 200:
            text = resp.json().get("text", "").strip()
            return text if text else "[空白录音]"
        return f"[STT error: {resp.status_code}]"
    except Exception as e:
        return f"[STT error: {e}]"


# ─── Pipeline Stage 2: Chat via OpenClaw ───


async def get_openclaw_reply(transcript: str, image_b64: str | None, language: str = "zh") -> str:
    """
    Send message to OpenClaw chatCompletions API.
    Routes to the main agent with full memory and personality.
    The 'user' field creates a stable session for videochat conversations.
    """
    try:
        lang_instruction = (
            "Please reply in English. Reply in English."
            if language == "en"
            else "请用中文回复。"
        )

        if image_b64:
            prompt_text = (
                f"[Video Call] {USER_NAME} says: \"{transcript}\"\n\n"
                f"You are on a video call with {USER_NAME}. A camera frame is attached. "
                "Respond naturally as in a real video call: short, conversational, 1-3 sentences. "
                "No markdown formatting. Feel free to comment on what you see in the frame. "
                f"Stay in character as {AGENT_NAME}. {lang_instruction}"
            )
            content = [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
            ]
        else:
            content = (
                f"[Video Call] {USER_NAME} says: \"{transcript}\"\n\n"
                f"You are on a video call with {USER_NAME} (camera is off, no video). "
                "Respond naturally as in a real video call: short, conversational, 1-3 sentences. "
                f"No markdown formatting. Stay in character as {AGENT_NAME}. {lang_instruction}"
            )

        headers = {
            "Authorization": f"Bearer {GW_TOKEN}",
            "Content-Type": "application/json",
            "x-openclaw-agent-id": "main",
        }
        payload = {
            "model": "openclaw",
            "messages": [{"role": "user", "content": content}],
            "user": "videochat-session",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{OPENCLAW_BASE}/v1/chat/completions",
                headers=headers,
                json=payload,
            )

        if resp.status_code == 200:
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return text.strip() if text else "Hmm... I spaced out for a moment."
        else:
            logger.error("OpenClaw API error %d: %s", resp.status_code, resp.text[:200])
            return "I heard you, but my brain glitched for a sec..."

    except httpx.TimeoutException:
        return f"I heard: {transcript}... but I took too long thinking, sorry!"
    except Exception as e:
        logger.error("OpenClaw error: %s", e)
        return f"I heard: {transcript} (connection issue)"


# ─── Pipeline Stage 3: TTS (edge-tts) ───


def _run_edge_tts(text: str, output_path: Path, voice: str, rate: str, max_retries: int = 3) -> bool:
    """Run edge-tts with retry. Returns True on success."""
    import time
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("TTS attempt %d/%d for %d chars", attempt, max_retries, len(text))
            result = subprocess.run(
                [
                    "edge-tts",
                    "--voice", voice,
                    "--rate", rate,
                    "--text", text,
                    "--write-media", str(output_path),
                ],
                capture_output=True,
                timeout=30,
            )
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                return True
            stderr = result.stderr.decode(errors="replace") if result.stderr else ""
            logger.warning("TTS attempt %d failed: rc=%d, stderr=%s", attempt, result.returncode, stderr[:300])
        except subprocess.TimeoutExpired:
            logger.warning("TTS attempt %d timed out", attempt)
        except FileNotFoundError:
            logger.error("edge-tts not found in PATH")
            return False
        except Exception as e:
            logger.warning("TTS attempt %d exception: %s", attempt, e)
        if attempt < max_retries:
            time.sleep(1)
    return False


def _split_text(text: str, max_len: int = 200) -> list[str]:
    """Split text into chunks at sentence boundaries, each ≤ max_len chars."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    sentences = re.split(r'(?<=[。！？.!?\n])', text)
    current = ""
    for s in sentences:
        if not s:
            continue
        if len(current) + len(s) > max_len and current:
            chunks.append(current)
            current = s
        else:
            current += s
    if current:
        chunks.append(current)
    result = []
    for chunk in chunks:
        while len(chunk) > max_len:
            result.append(chunk[:max_len])
            chunk = chunk[max_len:]
        if chunk:
            result.append(chunk)
    return result


def generate_tts(text: str, output_path: Path, voice: str = "zh-CN-XiaoxiaoNeural", speed: str = "normal") -> None:
    rate_map = {"fast": "+30%", "slow": "-30%", "normal": "+0%"}
    rate = rate_map.get(speed, "+0%")

    chunks = _split_text(text)

    if len(chunks) == 1:
        if _run_edge_tts(text, output_path, voice, rate):
            return
    else:
        logger.info("Long text (%d chars) split into %d chunks", len(text), len(chunks))
        part_paths = []
        all_ok = True
        for i, chunk in enumerate(chunks):
            part_path = output_path.with_name(f"{output_path.stem}_part{i}.mp3")
            if _run_edge_tts(chunk, part_path, voice, rate):
                part_paths.append(part_path)
            else:
                logger.warning("Chunk %d failed, aborting concat", i)
                all_ok = False
                break

        if all_ok and part_paths:
            try:
                list_file = output_path.with_suffix(".txt")
                list_file.write_text(
                    "\n".join(f"file '{p}'" for p in part_paths),
                    encoding="utf-8",
                )
                result = subprocess.run(
                    [
                        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", str(list_file), "-c", "copy", str(output_path),
                    ],
                    capture_output=True,
                    timeout=30,
                )
                if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
                    for p in part_paths:
                        p.unlink(missing_ok=True)
                    list_file.unlink(missing_ok=True)
                    return
                stderr = result.stderr.decode(errors="replace") if result.stderr else ""
                logger.warning("ffmpeg concat failed: rc=%d, stderr=%s", result.returncode, stderr[:300])
            except Exception as e:
                logger.warning("ffmpeg concat exception: %s", e)

        for p in part_paths:
            p.unlink(missing_ok=True)

    # Fallback: generate silent MP3
    logger.warning("All TTS attempts failed, generating silent MP3 fallback")
    _write_silent_mp3(output_path)


def _write_silent_mp3(path: Path):
    """Generate a short silent MP3 file using ffmpeg."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                "anullsrc=r=24000:cl=mono", "-t", "0.5",
                "-c:a", "libmp3lame", "-b:a", "32k", str(path),
            ],
            capture_output=True,
            timeout=10,
        )
        if path.exists() and path.stat().st_size > 0:
            return
    except Exception as e:
        logger.warning("Silent MP3 generation failed: %s", e)

    # Last resort: write minimal silent WAV
    sr, dur = 16000, 0.5
    n = int(sr * dur)
    ds = n * 2
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + ds) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", ds) + b"\x00" * ds)
    logger.warning("Wrote silent WAV to %s (ffmpeg unavailable)", path)


# ─── Entry Point ───

if __name__ == "__main__":
    import uvicorn

    # Check for SSL certs
    certs_dir = Path(__file__).parent.parent / "certs"
    ssl_cert = os.environ.get("SSL_CERT", "")
    ssl_key = os.environ.get("SSL_KEY", "")

    # Auto-detect certs in certs/ directory
    if not ssl_cert and certs_dir.exists():
        for f in certs_dir.iterdir():
            if f.suffix == ".pem" and "-key" not in f.name:
                ssl_cert = str(f)
            elif f.suffix == ".pem" and "-key" in f.name:
                ssl_key = str(f)

    use_ssl = ssl_cert and ssl_key and Path(ssl_cert).exists() and Path(ssl_key).exists()
    proto = "https" if use_ssl else "http"

    print(f"🎥 {AGENT_NAME} Video Chat · {proto}://localhost:{PORT}")
    print(f"📡 OpenClaw API → {OPENCLAW_BASE}")
    print(f"🎤 STT → Groq Whisper")
    print(f"🔊 TTS → edge-tts")
    if use_ssl:
        print(f"🔒 SSL → {ssl_cert}")
    print()

    if use_ssl:
        uvicorn.run(app, host="0.0.0.0", port=PORT, ssl_certfile=ssl_cert, ssl_keyfile=ssl_key)
    else:
        uvicorn.run(app, host="0.0.0.0", port=PORT)
