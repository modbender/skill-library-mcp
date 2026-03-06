#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiliconFlow TTS Generation Script
Compatible with OpenClaw Agent Skills
"""

import os
import sys
import json
import argparse
import subprocess

# API Configuration
API_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "FunAudioLLM/CosyVoice2-0.5B"
DEFAULT_VOICE = "alex"

# Available voices
VOICES = {
    "alex": "沉稳男声",
    "benjamin": "低沉男声",
    "charles": "磁性男声",
    "david": "欢快男声",
    "anna": "沉稳女声",
    "bella": "激情女声",
    "claire": "温柔女声",
    "diana": "欢快女声"
}

def get_api_key():
    """Get API key from environment or OpenClaw config"""
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if api_key:
        return api_key
    
    try:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        providers = config.get("models", {}).get("providers", {})
        siliconflow = providers.get("siliconflow", {})
        api_key = siliconflow.get("apiKey")
        if api_key and api_key != "ollama":
            return api_key
    except Exception:
        pass
    
    return None

def generate_speech(text, voice=None, model=None, output_path=None, speed=1.0, response_format="mp3"):
    """Generate speech using SiliconFlow TTS API"""
    api_key = get_api_key()
    if not api_key:
        print(json.dumps({
            "success": False,
            "error": "SILICONFLOW_API_KEY not found. Please set SILICONFLOW_API_KEY environment variable."
        }))
        sys.exit(1)
    
    model = model or DEFAULT_MODEL
    voice = voice or DEFAULT_VOICE
    
    # Prepare request data
    # voice format: "FunAudioLLM/CosyVoice2-0.5B:alex" for system voices
    full_voice = f"{model}:{voice}"
    
    data = {
        "model": model,
        "voice": full_voice,
        "input": text,
        "speed": speed,
        "response_format": response_format
    }
    
    # Determine output file
    if not output_path:
        output_path = f"output.{response_format}"
    
    headers = [
        f"Authorization: Bearer {api_key}",
        "Content-Type: application/json"
    ]
    
    try:
        # Use curl to make request and save directly to file
        curl_cmd = [
            "curl", "-s", "-X", "POST",
            f"{API_BASE_URL}/audio/speech",
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(data),
            "--max-time", "60",
            "-o", output_path
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True)
        
        if result.returncode != 0:
            print(json.dumps({
                "success": False,
                "error": f"API request failed: {result.stderr.decode('utf-8', errors='ignore')}"
            }))
            sys.exit(1)
        
        # Check if file was created and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size = os.path.getsize(output_path)
            print(json.dumps({
                "success": True,
                "text": text,
                "model": model,
                "voice": voice,
                "voice_name": VOICES.get(voice, voice),
                "speed": speed,
                "format": response_format,
                "output_path": output_path,
                "file_size_bytes": file_size
            }, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({
                "success": False,
                "error": "Output file is empty or not created"
            }))
            sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)

def list_voices():
    """List available voices"""
    print(json.dumps({
        "voices": [
            {"id": k, "name": v, "gender": "男" if k in ["alex", "benjamin", "charles", "david"] else "女"}
            for k, v in VOICES.items()
        ]
    }, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(
        description="Generate speech using SiliconFlow TTS API (CosyVoice2)",
        epilog="Examples:\n"
               "  %(prog)s \"你好，世界\"\n"
               "  %(prog)s \"Hello World\" --voice bella\n"
               "  %(prog)s \"你好\" --voice claire --speed 0.9 --output hello.mp3\n"
               "  %(prog)s --list-voices",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("--voice", "-v", help="Voice to use (default: alex)", default=DEFAULT_VOICE)
    parser.add_argument("--model", "-m", help="Model to use", default=DEFAULT_MODEL)
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--speed", "-s", help="Speech speed (0.25-4.0)", type=float, default=1.0)
    parser.add_argument("--format", "-f", help="Output format (mp3, opus, wav, pcm)", default="mp3")
    parser.add_argument("--list-voices", "-l", action="store_true", help="List available voices")
    
    args = parser.parse_args()
    
    if args.list_voices:
        list_voices()
    elif args.text:
        generate_speech(args.text, args.voice, args.model, args.output, args.speed, args.format)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
