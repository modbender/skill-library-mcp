#!/usr/bin/env python3
"""
Transcribe and align lyrics using stable-ts.
Produces word-level timestamps for precise subtitle timing.
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Align lyrics with stable-ts")
    parser.add_argument("--audio", required=True, help="Path to audio file (WAV/MP3)")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--model", default="large-v3", help="Whisper model size")
    parser.add_argument("--language", default="ja", help="Language code")
    parser.add_argument("--device", default="cpu", help="Device (cpu/cuda/mps)")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"❌ Audio file not found: {args.audio}")
        sys.exit(1)

    # Import inside main to allow checking args before heavy import
    try:
        import stable_whisper
    except ImportError:
        print("❌ stable-ts not installed. Run:")
        print("   source ~/.openclaw/workspace/.venv/bin/activate")
        print("   pip install stable-ts")
        sys.exit(1)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    print(f"🎤 Loading model: {args.model} (device: {args.device})", flush=True)
    model = stable_whisper.load_model(args.model, device=args.device)

    print(f"🎵 Transcribing: {args.audio}", flush=True)
    result = model.transcribe(
        args.audio,
        language=args.language,
        word_timestamps=True
    )

    result.save_as_json(args.output)
    print(f"✅ Saved aligned JSON: {args.output}", flush=True)

    # Summary
    segments = result.segments
    total_words = sum(len(s.words) for s in segments)
    print(f"   📊 {len(segments)} segments, {total_words} words")

if __name__ == "__main__":
    main()
