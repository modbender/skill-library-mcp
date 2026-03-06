#!/usr/bin/env python3
"""
Whisper STT Transcription Script
Supports local Whisper model for free speech-to-text
"""

import argparse
import os
import sys
import json
import warnings

def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    try:
        import whisper
    except ImportError:
        missing.append("openai-whisper")
    try:
        import torch
    except ImportError:
        missing.append("torch")
    
    if missing:
        print(f"Error: Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print("Install with: pip install " + " ".join(missing), file=sys.stderr)
        sys.exit(1)

def transcribe(audio_path, model_size="base", language=None, output_format="json"):
    """
    Transcribe audio file using Whisper
    
    Args:
        audio_path: Path to audio file
        model_size: tiny, base, small, medium, large, large-v2, large-v3
        language: Language code (e.g., 'zh', 'en', 'ja'), auto-detect if None
        output_format: json, txt, srt, vtt
    
    Returns:
        Transcription result dict
    """
    import whisper
    
    # Load model
    print(f"Loading Whisper model: {model_size}", file=sys.stderr)
    model = whisper.load_model(model_size)
    
    # Transcribe
    print(f"Transcribing: {audio_path}", file=sys.stderr)
    
    decode_options = {}
    if language:
        decode_options["language"] = language
    
    result = model.transcribe(audio_path, **decode_options)
    
    # Format output
    output = {
        "text": result["text"].strip(),
        "language": result.get("language", "unknown"),
        "segments": []
    }
    
    for seg in result.get("segments", []):
        output["segments"].append({
            "id": seg["id"],
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
    
    return output

def format_output(result, fmt):
    """Format result to specified output format"""
    if fmt == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    elif fmt == "txt":
        return result["text"]
    elif fmt == "srt":
        lines = []
        for seg in result["segments"]:
            start = format_timestamp(seg["start"], srt=True)
            end = format_timestamp(seg["end"], srt=True)
            lines.append(f"{seg['id'] + 1}\n{start} --> {end}\n{seg['text']}\n")
        return "\n".join(lines)
    elif fmt == "vtt":
        lines = ["WEBVTT\n"]
        for seg in result["segments"]:
            start = format_timestamp(seg["start"], srt=False)
            end = format_timestamp(seg["end"], srt=False)
            lines.append(f"{start} --> {end}\n{seg['text']}\n")
        return "\n".join(lines)
    else:
        return result["text"]

def format_timestamp(seconds, srt=False):
    """Format seconds to timestamp"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    if srt:
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def main():
    parser = argparse.ArgumentParser(description="Whisper STT Transcription")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--model", default="base", 
                       choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "large-v3-turbo"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--language", "-l", default=None,
                       help="Language code (e.g., zh, en, ja). Auto-detect if not specified.")
    parser.add_argument("--output", "-o", default="json",
                       choices=["json", "txt", "srt", "vtt"],
                       help="Output format (default: json)")
    
    args = parser.parse_args()
    
    # Check file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: File not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # Check dependencies
    check_dependencies()
    
    # Transcribe
    try:
        result = transcribe(args.audio_file, args.model, args.language, args.output)
        output = format_output(result, args.output)
        print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
