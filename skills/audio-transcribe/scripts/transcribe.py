#!/usr/bin/env python3
"""
Audio Transcription using faster-whisper
Local transcription, no API key needed
"""

import sys
import os
from pathlib import Path

# Add faster_whisper to path if needed
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster-whisper not installed")
    print("Run: pip install faster-whisper")
    sys.exit(1)

# Configuration
MODEL_SIZE = 'small'  # Options: tiny, base, small, medium, large-v3
DEVICE = 'cpu'
COMPUTE_TYPE = 'int8'  # int8 for CPU, float16 for GPU

def transcribe_file(audio_path: str) -> dict:
    """Transcribe an audio file"""
    
    if not Path(audio_path).exists():
        return {"error": f"File not found: {audio_path}"}
    
    try:
        # Load model (downloads on first run)
        model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        
        # Transcribe
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            best_of=5,
            condition_on_previous_text=True
        )
        
        # Collect text
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)
        
        full_text = ' '.join(text_parts).strip()
        
        return {
            "text": full_text,
            "language": info.language,
            "language_probability": info.language_probability,
            "model": MODEL_SIZE
        }
        
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file>")
        print("")
        print("Supported formats: wav, mp3, ogg, m4a, flac, opus")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    print(f"🎙️ Transcribing with '{MODEL_SIZE}' model...")
    print("")
    
    result = transcribe_file(audio_path)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    print(f"🌐 Language: {result['language']} (confidence: {result['language_probability']:.0%})")
    print("")
    print(result['text'])

if __name__ == "__main__":
    main()
