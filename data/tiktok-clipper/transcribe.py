#!/usr/bin/env python3
"""Transcribe video/audio using OpenAI Whisper API with word-level timestamps."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def extract_audio(video_path: str, audio_path: str):
    """Extract audio from video as mp3 for Whisper."""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", "-q:a", "4",
        "-y", audio_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"Audio extracted: {audio_path}")

def transcribe(audio_path: str) -> dict:
    """Transcribe audio using OpenAI Whisper API."""
    try:
        from openai import OpenAI
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "openai"], check=True)
        from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    file_size = os.path.getsize(audio_path)
    max_size = 24 * 1024 * 1024  # 24MB to be safe
    
    if file_size > max_size:
        # Split into chunks
        print(f"File too large ({file_size/1024/1024:.1f}MB), splitting...")
        return transcribe_chunked(audio_path, client)
    
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            language="es"
        )
    
    result = {
        "text": response.text,
        "segments": [{"start": s.start, "end": s.end, "text": s.text} for s in (response.segments or [])],
        "words": [{"start": w.start, "end": w.end, "word": w.word} for w in (response.words or [])]
    }
    return result

def transcribe_chunked(audio_path: str, client) -> dict:
    """Split audio into chunks and transcribe each."""
    # Get duration
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", audio_path],
        capture_output=True, text=True
    )
    duration = float(json.loads(probe.stdout)["format"]["duration"])
    
    chunk_duration = 600  # 10 minutes per chunk
    chunks = []
    offset = 0
    
    temp_dir = Path("/tmp/whisper_chunks")
    temp_dir.mkdir(exist_ok=True)
    
    all_segments = []
    all_words = []
    all_text = []
    
    i = 0
    while offset < duration:
        chunk_path = str(temp_dir / f"chunk_{i}.mp3")
        end = min(offset + chunk_duration, duration)
        
        subprocess.run([
            "ffmpeg", "-i", audio_path,
            "-ss", str(offset), "-to", str(end),
            "-acodec", "libmp3lame", "-q:a", "4",
            "-y", chunk_path
        ], capture_output=True, check=True)
        
        print(f"Transcribing chunk {i+1} ({offset/60:.0f}m - {end/60:.0f}m)...")
        
        with open(chunk_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language="es"
            )
        
        # Adjust timestamps with offset
        for s in (response.segments or []):
            all_segments.append({"start": s.start + offset, "end": s.end + offset, "text": s.text})
        for w in (response.words or []):
            all_words.append({"start": w.start + offset, "end": w.end + offset, "word": w.word})
        all_text.append(response.text)
        
        os.remove(chunk_path)
        offset = end
        i += 1
    
    return {
        "text": " ".join(all_text),
        "segments": all_segments,
        "words": all_words
    }

def main():
    parser = argparse.ArgumentParser(description="Transcribe video/audio with Whisper")
    parser.add_argument("--input", "-i", required=True, help="Input video/audio file")
    parser.add_argument("--output", "-o", required=True, help="Output JSON transcript")
    parser.add_argument("--audio-only", action="store_true", help="Input is already audio")
    args = parser.parse_args()
    
    if args.audio_only:
        audio_path = args.input
    else:
        audio_path = "/tmp/whisper_extract.mp3"
        extract_audio(args.input, audio_path)
    
    print("Transcribing with Whisper...")
    result = transcribe(audio_path)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Transcript saved: {args.output}")
    print(f"Segments: {len(result['segments'])}, Words: {len(result['words'])}")
    print(f"Duration: {result['segments'][-1]['end']/60:.1f} minutes" if result['segments'] else "")

if __name__ == "__main__":
    main()
