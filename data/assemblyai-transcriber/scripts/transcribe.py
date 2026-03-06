#!/usr/bin/env python3
"""
AssemblyAI Transcriber with Speaker Diarization
Usage: python3 transcribe.py <audio_file_or_url> [--no-diarization] [--json]
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Config locations
CONFIG_PATHS = [
    Path.home() / ".assemblyai_config.json",
    Path.cwd() / ".assemblyai_config.json",
    Path(__file__).parent.parent.parent.parent / ".assemblyai_config.json",
]

BASE_URL = "https://api.assemblyai.com/v2"


def load_api_key():
    """Load API key from config file."""
    for config_path in CONFIG_PATHS:
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get("api_key")
    
    # Check environment variable
    if os.environ.get("ASSEMBLYAI_API_KEY"):
        return os.environ["ASSEMBLYAI_API_KEY"]
    
    raise ValueError(
        "No API key found. Create ~/.assemblyai_config.json with: "
        '{"api_key": "YOUR_KEY"}'
    )


def api_request(endpoint, method="GET", data=None, api_key=None):
    """Make API request to AssemblyAI."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    
    if data:
        data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"API Error {e.code}: {error_body}")


def upload_file(file_path, api_key):
    """Upload local file to AssemblyAI."""
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/octet-stream",
    }
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    req = urllib.request.Request(
        f"{BASE_URL}/upload",
        data=file_data,
        headers=headers,
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["upload_url"]


def transcribe(audio_source, speaker_labels=True, api_key=None):
    """
    Transcribe audio with optional speaker diarization.
    
    Args:
        audio_source: URL or local file path
        speaker_labels: Enable speaker diarization
        api_key: AssemblyAI API key
    
    Returns:
        dict with transcript data
    """
    if not api_key:
        api_key = load_api_key()
    
    # Check if local file or URL
    if os.path.exists(audio_source):
        print(f"📤 Uploading file: {audio_source}", file=sys.stderr)
        audio_url = upload_file(audio_source, api_key)
    else:
        audio_url = audio_source
    
    # Start transcription
    print("🎙️ Starting transcription...", file=sys.stderr)
    
    transcript_request = {
        "audio_url": audio_url,
        "speaker_labels": speaker_labels,
        "language_detection": True,
        "speech_models": ["universal-2"],
    }
    
    response = api_request("transcript", method="POST", data=transcript_request, api_key=api_key)
    transcript_id = response["id"]
    
    # Poll for completion
    while True:
        result = api_request(f"transcript/{transcript_id}", api_key=api_key)
        status = result["status"]
        
        if status == "completed":
            print("✅ Transcription complete!", file=sys.stderr)
            return result
        elif status == "error":
            raise Exception(f"Transcription failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"⏳ Status: {status}...", file=sys.stderr)
            time.sleep(2)


def format_timestamp(ms):
    """Convert milliseconds to MM:SS format."""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def format_transcript(result, include_timestamps=True):
    """Format transcript result as readable markdown."""
    output = []
    output.append("## Transkript\n")
    
    # Add metadata
    if result.get("language_code"):
        lang = result["language_code"].upper()
        output.append(f"*Sprache: {lang}*\n")
    
    duration_ms = result.get("audio_duration", 0) * 1000
    if duration_ms:
        output.append(f"*Dauer: {format_timestamp(int(duration_ms))}*\n")
    
    output.append("")
    
    # Format utterances with speaker labels
    if result.get("utterances"):
        for utterance in result["utterances"]:
            speaker = utterance.get("speaker", "?")
            text = utterance.get("text", "")
            start = utterance.get("start", 0)
            
            if include_timestamps:
                ts = format_timestamp(start)
                output.append(f"**Speaker {speaker}** [{ts}]: {text}\n")
            else:
                output.append(f"**Speaker {speaker}**: {text}\n")
    else:
        # No speaker labels, just plain text
        output.append(result.get("text", ""))
    
    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe.py <audio_file_or_url> [--no-diarization] [--json]")
        print("\nExamples:")
        print("  python3 transcribe.py meeting.mp3")
        print("  python3 transcribe.py https://example.com/audio.mp3")
        print("  python3 transcribe.py recording.wav --json")
        sys.exit(1)
    
    audio_source = sys.argv[1]
    speaker_labels = "--no-diarization" not in sys.argv
    output_json = "--json" in sys.argv
    
    try:
        result = transcribe(audio_source, speaker_labels=speaker_labels)
        
        if output_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_transcript(result))
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
