#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
# ]
# ///
"""
Automatic Speech Recognition using SiliconFlow models.

Usage:
    uv run asr.py --audio "input.mp3" [--model MODEL]
    
Examples:
    uv run asr.py --audio "recording.mp3"
    uv run asr.py --audio "voice.m4a" --model teleai
"""

import argparse
import os
import sys
from pathlib import Path

import requests


SILICONFLOW_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"

MODELS = {
    "sensevoice": "FunAudioLLM/SenseVoiceSmall",
    "teleai": "TeleAI/TeleSpeechASR",
}


def get_api_key() -> str:
    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        print("Error: SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def transcribe(audio_path: str, model: str, api_key: str) -> str:
    model_id = MODELS.get(model, MODELS["sensevoice"])
    
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    
    files = {
        "file": (Path(audio_path).name, audio_data),
        "model": (None, model_id),
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    print(f"👂 Transcribing with {model_id}...")
    
    try:
        response = requests.post(SILICONFLOW_URL, files=files, headers=headers, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        
        if "text" in data:
            return data["text"]
        elif "results" in data:
            return " ".join(r.get("text", "") for r in data["results"])
        else:
            return str(data)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Speech recognition with SiliconFlow")
    parser.add_argument("--audio", "-a", required=True, help="Audio file path")
    parser.add_argument("--model", "-m", choices=list(MODELS.keys()), default="sensevoice",
                        help="ASR model (default: sensevoice)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"❌ Audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)
    
    api_key = get_api_key()
    
    result = transcribe(args.audio, args.model, api_key)
    
    if result:
        print(f"\n📝 Transcription:\n{result}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
