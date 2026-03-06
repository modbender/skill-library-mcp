#!/usr/bin/env python3
"""
Gemini Assistant - General purpose AI assistant using Gemini API
Supports text and voice interactions
"""

import asyncio
import os
import subprocess
import tempfile
import json
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import soundfile as sf
from google import genai
from google.genai import types

# Load .env file manually if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, val = line.strip().split('=', 1)
                if not os.environ.get(key):
                    os.environ[key] = val.strip().strip("'").strip('"')

# Configuration
MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
SYSTEM_INSTRUCTION = """You are a helpful, friendly AI assistant. You can:
- Answer questions on any topic
- Help with explanations and clarifications
- Assist with general tasks and problem-solving
- Have natural conversations

Keep responses concise but informative. If the user speaks in Arabic, respond in Arabic. If English, respond in English."""

SAMPLE_RATE_IN = 16000
SAMPLE_RATE_OUT = 24000
FFMPEG = "/usr/bin/ffmpeg"


async def _process_with_gemini(audio_path: str = None, text_input: str = None, system_instruction: str = None) -> dict:
    """
    Process input using Gemini Live API.
    Returns both audio and text response.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": system_instruction or SYSTEM_INSTRUCTION,
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": "Puck"}
            }
        }
    }

    chunks = []

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        # Send input
        if text_input:
            await session.send_client_content(turns={"parts": [{"text": text_input}]})
        elif audio_path:
            # Convert audio to PCM and send
            import librosa
            y, sr = librosa.load(audio_path, sr=SAMPLE_RATE_IN)
            
            # Send as realtime audio input
            await session.send_realtime_input(
                audio=types.Blob(
                    data=y.tobytes(),
                    mime_type=f"audio/pcm;rate={SAMPLE_RATE_IN}"
                )
            )
        else:
            raise ValueError("Either text_input or audio_path must be provided")

        # Receive responses
        async for response in session.receive():
            if response.data is not None:
                chunks.append(response.data)
            elif response.server_content and response.server_content.turn_complete:
                break

    raw_pcm = b"".join(chunks) if chunks else b""
    
    return {
        "raw_pcm": raw_pcm
    }


def _pcm_to_ogg_opus(raw_pcm: bytes, output_path: str) -> str:
    """Convert raw PCM to OGG Opus."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    audio_np = np.frombuffer(raw_pcm, dtype=np.int16)
    sf.write(wav_path, audio_np, SAMPLE_RATE_OUT, format="WAV", subtype="PCM_16")

    try:
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "/usr/lib/x86_64-linux-gnu"
        result = subprocess.run(
            [
                FFMPEG, "-i", wav_path,
                "-c:a", "libopus",
                "-b:a", "32k",
                "-ar", "48000",
                "-ac", "1",
                output_path, "-y"
            ],
            capture_output=True,
            timeout=30,
            env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()[-300:]}")
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)

    size = os.path.getsize(output_path)
    if size == 0:
        raise RuntimeError("ffmpeg produced an empty OGG file")

    print(f"[gemini-assistant] OGG Opus written: {output_path} ({size} bytes)")
    return output_path


def handle_request(request_data: dict) -> dict:
    """Main entry point for Gemini Assistant."""
    chat_id = request_data.get("chat_id", "unknown")
    text_input = request_data.get("text")
    audio_path = request_data.get("audio_path")
    system_instruction = request_data.get("system_instruction")
    
    safe_id = str(chat_id).replace("@", "_").replace("+", "").replace(".", "_")
    voice_output_path = f"/tmp/gemini_voice_{safe_id}.ogg"
    
    try:
        # Process with Gemini
        result = asyncio.run(_process_with_gemini(
            audio_path=audio_path,
            text_input=text_input,
            system_instruction=system_instruction
        ))
        
        raw_pcm = result.get("raw_pcm", b"")
        
        response = {}
        
        # Convert voice to OGG if we have audio
        if raw_pcm:
            _pcm_to_ogg_opus(raw_pcm, voice_output_path)
            response["message"] = f"[[audio_as_voice]]\nMEDIA:{voice_output_path}"
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        print(f"[gemini-assistant] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        
        return {
            "message": f"Sorry, an error occurred: {str(e)}"
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Gemini Assistant")
    parser.add_argument("input_text", nargs="?", help="Text input to send to Gemini")
    parser.add_argument("--audio", "-a", help="Path to audio file for voice input")
    parser.add_argument("--system", "-s", help="Custom system instruction")
    
    args = parser.parse_args()
    
    request_data = {
        "chat_id": "cli",
        "text": args.input_text,
        "audio_path": args.audio,
        "system_instruction": args.system
    }
    
    result = handle_request(request_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
