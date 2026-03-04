#!/usr/bin/env python3
"""
Voice Assistant Server for OpenClaw
====================================
Real-time voice pipeline: Browser Mic → STT → OpenClaw Gateway → TTS → Browser Speaker

Supports configurable STT (Deepgram / ElevenLabs) and TTS (Deepgram / ElevenLabs)
with full streaming at every stage for sub-2s time-to-first-audio.

Usage:
    uv run scripts/server.py
    # Then open http://localhost:7860
"""

import asyncio
import base64
import json
import logging
import os
import struct
import sys
import time
from pathlib import Path
from typing import AsyncGenerator, Optional

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).parent.parent / ".env")

GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://localhost:4141/v1")
GATEWAY_MODEL = os.getenv("OPENCLAW_MODEL", "claude-sonnet-4-5-20250929")
STT_PROVIDER = os.getenv("VOICE_STT_PROVIDER", "deepgram").lower()
TTS_PROVIDER = os.getenv("VOICE_TTS_PROVIDER", "elevenlabs").lower()
DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY", "")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY", "")
TTS_VOICE_EL = os.getenv("VOICE_TTS_VOICE", "rachel")
TTS_VOICE_DG = os.getenv("VOICE_TTS_VOICE_DG", "aura-2-theia-en")
VAD_SILENCE_MS = int(os.getenv("VOICE_VAD_SILENCE_MS", "400"))
SAMPLE_RATE = int(os.getenv("VOICE_SAMPLE_RATE", "16000"))
SERVER_PORT = int(os.getenv("VOICE_SERVER_PORT", "7860"))
SYSTEM_PROMPT = os.getenv(
    "VOICE_SYSTEM_PROMPT",
    "You are a helpful voice assistant. Keep responses concise and conversational — "
    "aim for 1-3 sentences unless the user asks for detail. "
    "Never use markdown formatting, bullet points, or code blocks in your responses "
    "since they will be spoken aloud.",
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("voice-assistant")

# ---------------------------------------------------------------------------
# STT Providers
# ---------------------------------------------------------------------------


class DeepgramSTT:
    """Streaming STT via Deepgram Nova-2 WebSocket API."""

    WS_URL = "wss://api.deepgram.com/v1/listen"

    def __init__(self):
        self._ws = None
        self._transcript_queue: asyncio.Queue[str] = asyncio.Queue()
        self._listener_task: Optional[asyncio.Task] = None

    async def connect(self):
        import websockets

        params = (
            f"?encoding=linear16&sample_rate={SAMPLE_RATE}&channels=1"
            f"&model=nova-2&punctuate=true&interim_results=false"
            f"&endpointing={VAD_SILENCE_MS}&smart_format=true"
            f"&vad_events=true"
        )
        headers = {"Authorization": f"Token {DEEPGRAM_KEY}"}
        self._ws = await websockets.connect(
            self.WS_URL + params, additional_headers=headers
        )
        self._listener_task = asyncio.create_task(self._listen())
        log.info("Deepgram STT connected")

    async def _listen(self):
        try:
            async for msg in self._ws:
                data = json.loads(msg)
                msg_type = data.get("type", "")

                if msg_type == "Results":
                    channel = data.get("channel", {})
                    alternatives = channel.get("alternatives", [{}])
                    transcript = alternatives[0].get("transcript", "").strip()
                    is_final = data.get("is_final", False)
                    speech_final = data.get("speech_final", False)

                    if transcript and (is_final or speech_final):
                        log.info(f"STT final: {transcript}")
                        await self._transcript_queue.put(transcript)

        except Exception as e:
            log.error(f"Deepgram listener error: {e}")

    async def send_audio(self, audio_bytes: bytes):
        if self._ws:
            await self._ws.send(audio_bytes)

    async def get_transcript(self) -> str:
        return await self._transcript_queue.get()

    async def close(self):
        if self._ws:
            try:
                await self._ws.send(json.dumps({"type": "CloseStream"}))
                await self._ws.close()
            except Exception:
                pass
        if self._listener_task:
            self._listener_task.cancel()


class ElevenLabsSTT:
    """STT via ElevenLabs Scribe API (REST-based, non-streaming)."""

    API_URL = "https://api.elevenlabs.io/v1/speech-to-text"

    def __init__(self):
        self._audio_buffer = bytearray()
        self._transcript_queue: asyncio.Queue[str] = asyncio.Queue()
        self._silence_counter = 0
        self._has_speech = False

    async def connect(self):
        self._audio_buffer.clear()
        self._silence_counter = 0
        self._has_speech = False
        log.info("ElevenLabs STT initialized")

    async def send_audio(self, audio_bytes: bytes):
        self._audio_buffer.extend(audio_bytes)

        # Simple energy-based VAD
        if len(audio_bytes) >= 2:
            samples = struct.unpack(f"<{len(audio_bytes)//2}h", audio_bytes)
            energy = sum(abs(s) for s in samples) / len(samples)

            if energy > 500:
                self._has_speech = True
                self._silence_counter = 0
            elif self._has_speech:
                self._silence_counter += len(audio_bytes) / (SAMPLE_RATE * 2) * 1000

                if self._silence_counter >= VAD_SILENCE_MS:
                    await self._transcribe()

    async def _transcribe(self):
        if len(self._audio_buffer) < SAMPLE_RATE:  # Less than 0.5s
            self._audio_buffer.clear()
            self._has_speech = False
            self._silence_counter = 0
            return

        # Build WAV in memory
        audio_data = bytes(self._audio_buffer)
        wav = self._build_wav(audio_data)

        self._audio_buffer.clear()
        self._has_speech = False
        self._silence_counter = 0

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    self.API_URL,
                    headers={"xi-api-key": ELEVENLABS_KEY},
                    files={"file": ("audio.wav", wav, "audio/wav")},
                    data={"model_id": "scribe_v1"},
                )
                resp.raise_for_status()
                result = resp.json()
                text = result.get("text", "").strip()
                if text:
                    log.info(f"STT final: {text}")
                    await self._transcript_queue.put(text)
        except Exception as e:
            log.error(f"ElevenLabs STT error: {e}")

    def _build_wav(self, pcm_data: bytes) -> bytes:
        """Build a minimal WAV header around raw PCM data."""
        data_size = len(pcm_data)
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + data_size, b"WAVE",
            b"fmt ", 16, 1, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16,
            b"data", data_size,
        )
        return header + pcm_data

    async def get_transcript(self) -> str:
        return await self._transcript_queue.get()

    async def close(self):
        self._audio_buffer.clear()


# ---------------------------------------------------------------------------
# TTS Providers
# ---------------------------------------------------------------------------


class ElevenLabsTTS:
    """Streaming TTS via ElevenLabs WebSocket API."""

    def __init__(self):
        self._voice_id: Optional[str] = None

    async def _resolve_voice_id(self):
        if self._voice_id:
            return
        # Try to resolve voice name to ID
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers={"xi-api-key": ELEVENLABS_KEY},
                )
                resp.raise_for_status()
                voices = resp.json().get("voices", [])
                for v in voices:
                    if v["name"].lower() == TTS_VOICE_EL.lower():
                        self._voice_id = v["voice_id"]
                        log.info(f"Resolved ElevenLabs voice '{TTS_VOICE_EL}' → {self._voice_id}")
                        return
                # If not found by name, assume it's already an ID
                self._voice_id = TTS_VOICE_EL
        except Exception as e:
            log.warning(f"Could not resolve voice, using as ID: {e}")
            self._voice_id = TTS_VOICE_EL

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Stream audio bytes from ElevenLabs for a given text chunk."""
        await self._resolve_voice_id()

        url = (
            f"https://api.elevenlabs.io/v1/text-to-speech/{self._voice_id}/stream"
            f"?output_format=pcm_16000"
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers={
                        "xi-api-key": ELEVENLABS_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                        },
                    },
                ) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes(chunk_size=4096):
                        yield chunk
        except Exception as e:
            log.error(f"ElevenLabs TTS error: {e}")


class DeepgramTTS:
    """Streaming TTS via Deepgram Aura REST API."""

    def __init__(self):
        pass

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Stream audio bytes from Deepgram Aura for a given text chunk."""
        url = f"https://api.deepgram.com/v1/speak?model={TTS_VOICE_DG}&encoding=linear16&sample_rate={SAMPLE_RATE}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    url,
                    headers={
                        "Authorization": f"Token {DEEPGRAM_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"text": text},
                ) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes(chunk_size=4096):
                        yield chunk
        except Exception as e:
            log.error(f"Deepgram TTS error: {e}")


# ---------------------------------------------------------------------------
# OpenClaw Gateway Client (OpenAI-compatible streaming)
# ---------------------------------------------------------------------------


async def stream_llm_response(
    messages: list[dict], http_client: httpx.AsyncClient
) -> AsyncGenerator[str, None]:
    """Stream text tokens from the OpenClaw gateway."""
    url = f"{GATEWAY_URL}/chat/completions"
    payload = {
        "model": GATEWAY_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 512,
    }

    try:
        async with http_client.stream(
            "POST",
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        log.error(f"LLM stream error: {e}")
        yield "Sorry, I had trouble processing that. Could you try again?"


# ---------------------------------------------------------------------------
# Sentence Chunker — accumulates tokens into speakable sentence chunks
# ---------------------------------------------------------------------------


class SentenceChunker:
    """Accumulates streaming tokens and yields sentence-sized chunks for TTS."""

    SENTENCE_ENDERS = {".", "!", "?", ":", ";"}

    def __init__(self):
        self._buffer = ""

    def add(self, token: str) -> Optional[str]:
        self._buffer += token
        # Check if we have a complete sentence
        for i in range(len(self._buffer) - 1, -1, -1):
            if self._buffer[i] in self.SENTENCE_ENDERS:
                chunk = self._buffer[: i + 1].strip()
                self._buffer = self._buffer[i + 1 :]
                if len(chunk) > 3:  # Skip very short fragments
                    return chunk
        # Flush if buffer gets long without punctuation
        if len(self._buffer) > 150:
            chunk = self._buffer.strip()
            self._buffer = ""
            return chunk if chunk else None
        return None

    def flush(self) -> Optional[str]:
        chunk = self._buffer.strip()
        self._buffer = ""
        return chunk if chunk else None


# ---------------------------------------------------------------------------
# Voice Session — manages one WebSocket connection's full pipeline
# ---------------------------------------------------------------------------


class VoiceSession:
    """Manages a single voice conversation session."""

    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.messages: list[dict] = []
        if SYSTEM_PROMPT:
            self.messages.append({"role": "system", "content": SYSTEM_PROMPT})

        self.stt = DeepgramSTT() if STT_PROVIDER == "deepgram" else ElevenLabsSTT()
        self.tts = ElevenLabsTTS() if TTS_PROVIDER == "elevenlabs" else DeepgramTTS()
        self.http_client = httpx.AsyncClient()
        self._cancelled = False
        self._speaking = False
        self._tasks: list[asyncio.Task] = []

    async def start(self):
        await self.stt.connect()
        log.info(f"Session started: STT={STT_PROVIDER}, TTS={TTS_PROVIDER}")

        # Run audio receiver and conversation loop concurrently
        recv_task = asyncio.create_task(self._receive_audio())
        conv_task = asyncio.create_task(self._conversation_loop())
        self._tasks = [recv_task, conv_task]

        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            pass
        finally:
            await self.cleanup()

    async def _receive_audio(self):
        """Receive audio from the browser WebSocket and forward to STT."""
        try:
            while True:
                data = await self.ws.receive()
                if data.get("type") == "websocket.disconnect":
                    break

                if "bytes" in data:
                    audio = data["bytes"]
                    # If agent is speaking and user starts talking, barge-in
                    if self._speaking:
                        if self._detect_speech(audio):
                            log.info("Barge-in detected, cancelling TTS")
                            self._cancelled = True
                    await self.stt.send_audio(audio)

                elif "text" in data:
                    msg = json.loads(data["text"])
                    if msg.get("type") == "stop":
                        break

        except WebSocketDisconnect:
            log.info("Client disconnected")
        except Exception as e:
            log.error(f"Receive error: {e}")

    def _detect_speech(self, audio_bytes: bytes) -> bool:
        """Simple energy-based speech detection for barge-in."""
        if len(audio_bytes) < 2:
            return False
        samples = struct.unpack(f"<{len(audio_bytes) // 2}h", audio_bytes)
        energy = sum(abs(s) for s in samples) / len(samples)
        return energy > 800

    async def _conversation_loop(self):
        """Main loop: wait for STT → call LLM → stream TTS."""
        try:
            while True:
                # Wait for user utterance
                transcript = await self.stt.get_transcript()
                if not transcript:
                    continue

                log.info(f"User: {transcript}")
                self.messages.append({"role": "user", "content": transcript})

                # Send transcript + status to browser
                await self._send_json({"type": "transcript", "role": "user", "text": transcript})
                await self._send_json({"type": "status", "status": "thinking"})

                # Stream LLM response and TTS
                self._cancelled = False
                self._speaking = True
                t0 = time.monotonic()
                full_response = ""

                chunker = SentenceChunker()
                first_audio = True

                async for token in stream_llm_response(self.messages, self.http_client):
                    if self._cancelled:
                        break

                    full_response += token
                    chunk = chunker.add(token)

                    if chunk:
                        if first_audio:
                            latency = (time.monotonic() - t0) * 1000
                            log.info(f"Time to first TTS chunk: {latency:.0f}ms")
                            first_audio = False
                        await self._speak_chunk(chunk)

                # Flush remaining text
                if not self._cancelled:
                    remaining = chunker.flush()
                    if remaining:
                        await self._speak_chunk(remaining)

                self._speaking = False
                self.messages.append({"role": "assistant", "content": full_response})

                # Send assistant transcript + status to browser
                if full_response.strip():
                    await self._send_json(
                        {"type": "transcript", "role": "assistant", "text": full_response}
                    )
                await self._send_json({"type": "status", "status": "listening"})
                log.info(f"Assistant: {full_response[:100]}...")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"Conversation loop error: {e}")

    async def _speak_chunk(self, text: str):
        """Convert a text chunk to audio and send to the browser."""
        try:
            async for audio_chunk in self.tts.synthesize_stream(text):
                if self._cancelled:
                    break
                b64 = base64.b64encode(audio_chunk).decode("ascii")
                await self._send_json({"type": "audio", "data": b64})
        except Exception as e:
            log.error(f"TTS streaming error: {e}")

    async def _send_json(self, data: dict):
        try:
            await self.ws.send_json(data)
        except Exception:
            pass

    async def cleanup(self):
        await self.stt.close()
        await self.http_client.aclose()
        for t in self._tasks:
            if not t.done():
                t.cancel()
        # Await cancelled tasks to ensure clean shutdown
        await asyncio.gather(*self._tasks, return_exceptions=True)
        log.info("Session cleaned up")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(title="OpenClaw Voice Assistant")

STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "stt_provider": STT_PROVIDER,
        "tts_provider": TTS_PROVIDER,
        "gateway": GATEWAY_URL,
    }


@app.websocket("/ws/voice")
async def voice_ws(ws: WebSocket):
    await ws.accept()
    session = VoiceSession(ws)
    await session.start()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Validate configuration
    errors = []
    if STT_PROVIDER == "deepgram" and not DEEPGRAM_KEY:
        errors.append("DEEPGRAM_API_KEY is required when VOICE_STT_PROVIDER=deepgram")
    if TTS_PROVIDER == "deepgram" and not DEEPGRAM_KEY:
        errors.append("DEEPGRAM_API_KEY is required when VOICE_TTS_PROVIDER=deepgram")
    if STT_PROVIDER == "elevenlabs" and not ELEVENLABS_KEY:
        errors.append("ELEVENLABS_API_KEY is required when VOICE_STT_PROVIDER=elevenlabs")
    if TTS_PROVIDER == "elevenlabs" and not ELEVENLABS_KEY:
        errors.append("ELEVENLABS_API_KEY is required when VOICE_TTS_PROVIDER=elevenlabs")

    if errors:
        for e in errors:
            log.error(f"Config error: {e}")
        sys.exit(1)

    log.info(f"Starting voice server on port {SERVER_PORT}")
    log.info(f"STT: {STT_PROVIDER} | TTS: {TTS_PROVIDER} | Gateway: {GATEWAY_URL}")

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT, log_level="info")
