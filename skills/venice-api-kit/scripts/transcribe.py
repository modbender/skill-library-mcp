# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Audio Transcription

Transcribe audio files to text using Whisper-based speech recognition.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

SUPPORTED_EXTENSIONS = [".wav", ".wave", ".mp3", ".flac", ".m4a", ".aac", ".mp4"]

MIME_TYPES = {
    ".wav": "audio/wav",
    ".wave": "audio/wav",
    ".mp3": "audio/mpeg",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".mp4": "audio/mp4",
}


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def transcribe_audio(
    file_path: str,
    output: str | None = None,
    model: str = "openai/whisper-large-v3",
    response_format: str = "json",
    timestamps: bool = False,
    language: str | None = None,
) -> dict | str:
    """Transcribe an audio file to text."""
    api_key = get_api_key()

    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"Error: Unsupported format '{ext}'", file=sys.stderr)
        print(f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}", file=sys.stderr)
        sys.exit(1)

    mime_type = MIME_TYPES.get(ext, "audio/mpeg")

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    files = {
        "file": (path.name, path.read_bytes(), mime_type),
    }
    
    data: dict = {
        "model": model,
        "response_format": response_format,
        "timestamps": str(timestamps).lower(),
    }
    
    if language:
        data["language"] = language

    file_size_mb = path.stat().st_size / (1024 * 1024)
    print(f"Transcribing: {path.name} ({file_size_mb:.1f} MB)", file=sys.stderr)
    print(f"Model: {model}", file=sys.stderr)

    try:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            
            if response_format == "text":
                result = response.text
                print(f"\nTranscription complete!", file=sys.stderr)
                
                if output:
                    output_path = Path(output).resolve()
                    output_path.write_text(result)
                    print(f"Saved to: {output_path}", file=sys.stderr)
                else:
                    print(result)
                
                return result
            else:
                result = response.json()
                
                text = result.get("text", "")
                duration = result.get("duration")
                
                print(f"\nTranscription complete!", file=sys.stderr)
                if duration:
                    print(f"Audio duration: {duration:.1f}s", file=sys.stderr)
                print(f"Text length: {len(text)} characters", file=sys.stderr)
                
                if output:
                    output_path = Path(output).resolve()
                    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                    print(f"Saved to: {output_path}", file=sys.stderr)
                else:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                
                return result

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
        description="Transcribe audio files using Venice AI"
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Audio file to transcribe (WAV, MP3, FLAC, M4A, AAC)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save transcription to file (default: print to stdout)"
    )
    parser.add_argument(
        "--model", "-m",
        default="openai/whisper-large-v3",
        help="ASR model (default: openai/whisper-large-v3)"
    )
    parser.add_argument(
        "--format",
        dest="response_format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--timestamps", "-t",
        action="store_true",
        help="Include word/segment timestamps"
    )
    parser.add_argument(
        "--language", "-l",
        help="Language hint (ISO 639-1: en, es, fr, etc.)"
    )

    args = parser.parse_args()
    
    transcribe_audio(
        file_path=args.file,
        output=args.output,
        model=args.model,
        response_format=args.response_format,
        timestamps=args.timestamps,
        language=args.language,
    )


if __name__ == "__main__":
    main()
