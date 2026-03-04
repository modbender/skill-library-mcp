#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
# ]
# ///
"""
Text-to-Speech using SiliconFlow models.

Usage:
    uv run tts.py --text "要合成的文字" --filename "output.mp3" [--model MODEL]
    
Examples:
    uv run tts.py --text "你好世界" --filename "hello.mp3"
    uv run tts.py --text "Hello world" --filename "hello.mp3" --model cosyvoice
"""

import argparse
import os
import sys
from pathlib import Path

import requests


SILICONFLOW_URL = "https://api.siliconflow.cn/v1/audio/speech"

MODELS = {
    "fish-speech": "fishaudio/fish-speech-1.5",
    "cosyvoice": "FunAudioLLM/CosyVoice2-0.5B",
    "indextts": "IndexTeam/IndexTTS-2",
    "moss": "fnlp/MOSS-TTSD-v0.5",
}

DEFAULT_VOICES = {
    "fishaudio/fish-speech-1.5": "fishaudio/fish-speech-1.5:anna",
    "FunAudioLLM/CosyVoice2-0.5B": "FunAudioLLM/CosyVoice2-0.5B:alex",
    "IndexTeam/IndexTTS-2": "IndexTeam/IndexTTS-2:default",
    "fnlp/MOSS-TTSD-v0.5": "fnlp/MOSS-TTSD-v0.5:default",
}


def get_api_key() -> str:
    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        print("Error: SILICONFLOW_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def text_to_speech(text: str, output_path: Path, model: str, api_key: str) -> bool:
    model_id = MODELS.get(model, MODELS["fish-speech"])
    voice = DEFAULT_VOICES.get(model_id, f"{model_id}:default")
    
    payload = {
        "model": model_id,
        "input": text,
        "voice": voice,
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🎤 Synthesizing speech with {model_id}...")
    
    try:
        response = requests.post(SILICONFLOW_URL, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Audio saved: {output_path.resolve()}")
        print(f"MEDIA: {output_path.resolve()}")
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech with SiliconFlow")
    parser.add_argument("--text", "-t", required=True, help="Text to synthesize")
    parser.add_argument("--filename", "-f", required=True, help="Output filename (e.g., output.mp3)")
    parser.add_argument("--model", "-m", choices=list(MODELS.keys()), default="fish-speech",
                        help="TTS model (default: fish-speech)")
    
    args = parser.parse_args()
    
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    api_key = get_api_key()
    
    if not text_to_speech(args.text, output_path, args.model, api_key):
        sys.exit(1)


if __name__ == "__main__":
    main()
