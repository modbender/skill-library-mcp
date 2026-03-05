# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Text-to-Speech

Convert text to speech using Venice's /audio/speech endpoint.
Returns binary audio directly.
API docs: https://docs.venice.ai
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

# Voice IDs from swagger - Venice supports many voices
AVAILABLE_VOICES = [
    # American Female
    "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jadzia",
    "af_jessica", "af_kore", "af_nicole", "af_nova", "af_river",
    "af_sarah", "af_sky",
    # American Male
    "am_adam", "am_echo", "am_eric",
    # British Female
    "bf_emma", "bf_isabella", "bf_alice",
    # British Male
    "bm_george", "bm_lewis", "bm_daniel",
]

AVAILABLE_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def text_to_speech(
    text: str,  # This is the 'input' parameter in the API
    output: str | None = None,
    voice: str = "af_nicole",
    model: str = "tts-kokoro",
    speed: float = 1.0,
    response_format: str = "mp3",
    streaming: bool = False,
) -> Path:
    """Convert text to speech using Venice AI.
    
    Returns binary audio directly.
    """
    api_key = get_api_key()

    # Validate parameters
    if not 0.25 <= speed <= 4.0:
        print(f"Warning: Speed {speed} out of range (0.25-4.0). Using 1.0.", file=sys.stderr)
        speed = 1.0
    
    if len(text) > 4096:
        print(f"Warning: Text exceeds 4096 chars, truncating.", file=sys.stderr)
        text = text[:4096]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # API uses 'input' not 'text'
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "speed": speed,
        "response_format": response_format,
        "streaming": streaming,
    }

    print(f"Generating speech with voice '{voice}'...", file=sys.stderr)
    print(f"Text: {text[:80]}{'...' if len(text) > 80 else ''}", file=sys.stderr)

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/audio/speech",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Response is binary audio
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output = f"speech-{timestamp}.{response_format}"
            
            output_path = Path(output).resolve()
            output_path.write_bytes(response.content)
            
            print(f"Audio saved to: {output_path}", file=sys.stderr)
            print(f"MEDIA:{output_path}")
            
            return output_path

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert text to speech using Venice AI"
    )
    parser.add_argument(
        "--text", "-t",
        required=True,
        help="Text to convert to speech (max 4096 characters)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: speech-{timestamp}.{format})"
    )
    parser.add_argument(
        "--voice", "-v",
        default="af_nicole",
        help=f"Voice ID (default: af_nicole). Options: {', '.join(AVAILABLE_VOICES[:8])}..."
    )
    parser.add_argument(
        "--model", "-m",
        default="tts-kokoro",
        help="TTS model (default: tts-kokoro)"
    )
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=1.0,
        help="Speed multiplier 0.25-4.0 (default: 1.0)"
    )
    parser.add_argument(
        "--format", "-f",
        dest="response_format",
        choices=AVAILABLE_FORMATS,
        default="mp3",
        help="Audio format (default: mp3)"
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Stream audio sentence by sentence"
    )

    args = parser.parse_args()
    
    text_to_speech(
        text=args.text,
        output=args.output,
        voice=args.voice,
        model=args.model,
        speed=args.speed,
        response_format=args.response_format,
        streaming=args.streaming,
    )


if __name__ == "__main__":
    main()
