#!/usr/bin/env python3
"""
Voice to Text transcription using Vosk (offline speech recognition)
"""

import sys
import os
import json
import subprocess
import wave
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    try:
        import vosk
    except ImportError:
        missing.append("vosk (pip install vosk)")

    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append("ffmpeg (brew install ffmpeg)")

    return missing

def get_model_path():
    """Get the Vosk model path."""
    # Check environment variable first
    env_path = os.environ.get("VOSK_MODEL_PATH")
    if env_path:
        expanded = os.path.expanduser(env_path)
        if os.path.exists(expanded):
            return expanded

    # Check default model directory
    models_dir = Path.home() / ".vosk" / "models"
    if models_dir.exists():
        # Prefer Chinese model, then English
        for model_name in [
            "vosk-model-small-cn-0.22",
            "vosk-model-cn-0.22",
            "vosk-model-small-en-us-0.15",
            "vosk-model-en-us-0.22"
        ]:
            model_path = models_dir / model_name
            if model_path.exists():
                return str(model_path)

    return None

def convert_to_wav(input_file, output_file):
    """Convert audio file to WAV format suitable for Vosk."""
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",      # Mono
        "-f", "wav",
        output_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")
    return output_file

def transcribe(audio_file, model_path):
    """Transcribe audio file using Vosk."""
    from vosk import Model, KaldiRecognizer

    # Convert to WAV if needed
    temp_wav = None
    audio_path = os.path.expanduser(audio_file)

    if not audio_path.lower().endswith('.wav'):
        temp_wav = "/tmp/vosk_temp_audio.wav"
        convert_to_wav(audio_path, temp_wav)
        audio_path = temp_wav

    # Load model
    print(f"Loading model: {model_path}", file=sys.stderr)
    model = Model(model_path)

    # Open audio file
    wf = wave.open(audio_path, "rb")

    # Verify audio format - need mono 16-bit PCM
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
        wf.close()
        if temp_wav is None:
            temp_wav = "/tmp/vosk_temp_audio.wav"
        convert_to_wav(audio_file, temp_wav)
        wf = wave.open(temp_wav, "rb")

    # Create recognizer
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    # Process audio
    results = []
    print("Transcribing...", file=sys.stderr)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if result.get("text"):
                results.append(result["text"])

    # Get final result
    final = json.loads(rec.FinalResult())
    if final.get("text"):
        results.append(final["text"])

    wf.close()

    # Clean up temp file
    if temp_wav and os.path.exists(temp_wav):
        os.remove(temp_wav)

    return " ".join(results)

def main():
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file>", file=sys.stderr)
        print("\nSupported formats: MP3, WAV, M4A, OGG, FLAC, AAC, WEBM", file=sys.stderr)
        print("\nEnvironment variables:", file=sys.stderr)
        print("  VOSK_MODEL_PATH - Path to Vosk model directory", file=sys.stderr)
        sys.exit(1)

    audio_file = sys.argv[1]
    audio_path = os.path.expanduser(audio_file)

    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_file}", file=sys.stderr)
        sys.exit(1)

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print("Missing dependencies:", file=sys.stderr)
        for dep in missing:
            print(f"  - {dep}", file=sys.stderr)
        sys.exit(1)

    # Get model path
    model_path = get_model_path()
    if not model_path:
        print("Error: No Vosk model found.", file=sys.stderr)
        print("\nPlease download a model:", file=sys.stderr)
        print("  mkdir -p ~/.vosk/models && cd ~/.vosk/models", file=sys.stderr)
        print("  # Chinese model:", file=sys.stderr)
        print("  curl -LO https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip", file=sys.stderr)
        print("  unzip vosk-model-small-cn-0.22.zip", file=sys.stderr)
        print("  # English model:", file=sys.stderr)
        print("  curl -LO https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", file=sys.stderr)
        print("  unzip vosk-model-small-en-us-0.15.zip", file=sys.stderr)
        sys.exit(1)

    # Transcribe
    try:
        text = transcribe(audio_path, model_path)
        if text.strip():
            print(text)
        else:
            print("(No speech detected)", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
