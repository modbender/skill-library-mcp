#!/usr/bin/env python3
"""
ElevenLabs Instant Voice Cloning (IVC) API wrapper.

Usage (CLI):
    python3 voiceclone.py --name "MyVoice" --files audio1.mp3 audio2.mp3 --language de
    python3 voiceclone.py --name "MyVoice" --files *.m4a --description "German male voice"

Usage (Module):
    from voiceclone import clone_voice
    voice_id = clone_voice("MyVoice", ["audio1.mp3", "audio2.mp3"], language="de")
"""

import argparse
import os
import sys
import requests
from pathlib import Path

DEFAULT_SAMPLE_DIR = Path.home() / ".openclaw" / "elevenlabs" / "voiceclone-samples"
ALLOWED_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".webm"}
MAX_FILE_MB = 50


def _resolve_sample_path(file_path: str, *, sample_dir: Path) -> Path:
    p = Path(file_path)

    base = sample_dir.expanduser().resolve()
    # Interpret relative paths as relative to sample_dir (not CWD)
    resolved = (p.expanduser().resolve() if p.is_absolute() else (base / p).resolve())

    try:
        if not resolved.is_relative_to(base):
            raise ValueError(
                f"Refusing to read '{file_path}'. Put samples under {base}."
            )
    except AttributeError:
        # Python <3.9 fallback
        if str(resolved).startswith(str(base) + "/") is False and resolved != base:
            raise ValueError(
                f"Refusing to read '{file_path}'. Put samples under {base}."
            )

    return resolved


def clone_voice(
    name: str,
    files: list[str],
    api_key: str | None = None,
    description: str | None = None,
    labels: dict[str, str] | None = None,
    remove_background_noise: bool = False,
    sample_dir: str | None = None,
) -> dict:
    """
    Create an instant voice clone from audio samples.
    
    Args:
        name: Display name for the voice
        files: List of paths to audio files (mp3, m4a, wav, etc.)
        api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env)
        description: Optional description of the voice
        labels: Optional dict with keys like 'language', 'accent', 'gender', 'age'
        remove_background_noise: Whether to apply audio isolation
        
    Returns:
        dict with 'voice_id' and 'requires_verification'
    """
    api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set")

    url = "https://api.elevenlabs.io/v1/voices/add"
    
    headers = {
        "xi-api-key": api_key,
    }
    
    # Prepare multipart form data
    form_data = {
        "name": (None, name),
        "remove_background_noise": (None, str(remove_background_noise).lower()),
    }
    
    if description:
        form_data["description"] = (None, description)
    
    # Add labels as JSON string if provided
    if labels:
        import json
        form_data["labels"] = (None, json.dumps(labels))
    
    # Resolve sample directory and validate file paths.
    sample_base = Path(sample_dir).expanduser() if sample_dir else DEFAULT_SAMPLE_DIR
    sample_base.mkdir(parents=True, exist_ok=True)

    # Add audio files
    file_handles = []
    resolved_paths: list[Path] = []
    try:
        for file_path in files:
            path = _resolve_sample_path(
                file_path,
                sample_dir=sample_base,
            )
            if not path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")

            suffix = path.suffix.lower()
            if suffix not in ALLOWED_EXTENSIONS:
                raise ValueError(
                    f"Unsupported file type: {suffix}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                )

            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > MAX_FILE_MB:
                raise ValueError(f"File too large: {file_path} ({size_mb:.1f} MB > {MAX_FILE_MB} MB)")

            resolved_paths.append(path)

            # Determine MIME type
            mime_types = {
                ".mp3": "audio/mpeg",
                ".m4a": "audio/x-m4a",
                ".wav": "audio/wav",
                ".ogg": "audio/ogg",
                ".flac": "audio/flac",
                ".webm": "audio/webm",
            }
            mime_type = mime_types.get(suffix, "audio/mpeg")

            fh = open(path, "rb")
            file_handles.append(fh)
            form_data[f"files"] = (path.name, fh, mime_type)
        
        # Need to use files parameter for multiple files with same key
        # Rebuild as list of tuples for requests
        files_list = []
        for key, value in form_data.items():
            if key != "files":
                files_list.append((key, value))
        
        # Add all audio files with the same "files" key
        for i, path in enumerate(resolved_paths):
            suffix = path.suffix.lower()
            mime_types = {
                ".mp3": "audio/mpeg",
                ".m4a": "audio/x-m4a", 
                ".wav": "audio/wav",
                ".ogg": "audio/ogg",
                ".flac": "audio/flac",
                ".webm": "audio/webm",
            }
            mime_type = mime_types.get(suffix, "audio/mpeg")
            files_list.append(("files", (path.name, file_handles[i], mime_type)))
        
        response = requests.post(url, headers=headers, files=files_list)
        
    finally:
        for fh in file_handles:
            fh.close()
    
    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs API error {response.status_code}: {response.text}")
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Create an instant voice clone via ElevenLabs API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clone from multiple audio files
  python3 voiceclone.py --name "Andi" --files audio1.m4a audio2.m4a audio3.m4a

  # With language label
  python3 voiceclone.py --name "Andi" --files *.m4a --language de --gender male

  # With description and noise removal
  python3 voiceclone.py --name "Andi" --files *.m4a --description "German male voice" --denoise
""",
    )
    parser.add_argument("--name", "-n", required=True, help="Name for the cloned voice")
    parser.add_argument("--files", "-f", nargs="+", required=True, help="Audio file(s) for cloning")
    parser.add_argument("--description", "-d", help="Description of the voice")
    parser.add_argument("--language", "-l", help="Language label (e.g., 'de', 'en')")
    parser.add_argument("--accent", help="Accent label (e.g., 'german', 'british')")
    parser.add_argument("--gender", "-g", help="Gender label ('male' or 'female')")
    parser.add_argument("--age", help="Age label (e.g., 'young', 'middle_aged', 'old')")
    parser.add_argument("--denoise", action="store_true", help="Remove background noise from samples")
    parser.add_argument(
        "--sample-dir",
        help=(
            "Directory containing audio samples. Defaults to ~/.openclaw/elevenlabs/voiceclone-samples. "
            "Relative paths are resolved against this directory."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")

    args = parser.parse_args()

    # Build labels dict from provided options
    labels = {}
    if args.language:
        labels["language"] = args.language
    if args.accent:
        labels["accent"] = args.accent
    if args.gender:
        labels["gender"] = args.gender
    if args.age:
        labels["age"] = args.age

    try:
        result = clone_voice(
            name=args.name,
            files=args.files,
            description=args.description,
            labels=labels if labels else None,
            remove_background_noise=args.denoise,
            sample_dir=args.sample_dir,
        )
        
        if args.json:
            import json
            print(json.dumps(result, indent=2))
        else:
            print(f"✅ Voice cloned successfully!")
            print(f"   Name: {args.name}")
            print(f"   Voice ID: {result['voice_id']}")
            if result.get("requires_verification"):
                print("   ⚠️  Voice requires verification")
                
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
