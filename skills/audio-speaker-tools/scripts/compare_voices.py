#!/usr/bin/env python3
"""Compare two audio files using Resemblyzer d-vector cosine similarity.

Computes speaker embeddings for two audio files and reports:
- Cosine similarity score
- Pass/fail verdict (based on configurable threshold)

Example:
  python compare_voices.py --audio1 sample1.wav --audio2 sample2.wav --threshold 0.75

Scoring guide:
  < 0.75 = Different speakers
  0.75-0.84 = Likely same speaker
  0.85+ = Excellent match (same speaker)

Notes:
- Works best with clean, short audio samples (5-30s)
- Resemblyzer uses CPU by default
- Audio format: any format supported by librosa (wav, mp3, flac, etc.)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav


def compute_embedding(audio_path: str, encoder: VoiceEncoder) -> np.ndarray:
    """Load audio and compute d-vector embedding."""
    wav = preprocess_wav(Path(audio_path))
    embed = encoder.embed_utterance(wav)
    return embed


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare two voice samples using Resemblyzer")
    ap.add_argument("--audio1", required=True, help="First audio file")
    ap.add_argument("--audio2", required=True, help="Second audio file")
    ap.add_argument("--threshold", type=float, default=0.75, help="Similarity threshold for pass/fail (default: 0.75)")
    ap.add_argument("--json", action="store_true", help="Output JSON format")
    args = ap.parse_args()

    if not Path(args.audio1).exists():
        print(f"Error: {args.audio1} does not exist", file=sys.stderr)
        sys.exit(1)
    if not Path(args.audio2).exists():
        print(f"Error: {args.audio2} does not exist", file=sys.stderr)
        sys.exit(1)

    # Initialize encoder (CPU)
    encoder = VoiceEncoder()

    # Compute embeddings
    embed1 = compute_embedding(args.audio1, encoder)
    embed2 = compute_embedding(args.audio2, encoder)

    # Compute similarity
    similarity = cosine_similarity(embed1, embed2)

    # Determine verdict
    if similarity >= 0.85:
        verdict = "EXCELLENT_MATCH"
        verdict_text = "Excellent match (same speaker)"
    elif similarity >= args.threshold:
        verdict = "LIKELY_SAME"
        verdict_text = "Likely same speaker"
    else:
        verdict = "DIFFERENT"
        verdict_text = "Different speakers"

    # Output
    if args.json:
        import json

        result = {
            "audio1": args.audio1,
            "audio2": args.audio2,
            "similarity": round(similarity, 4),
            "threshold": args.threshold,
            "verdict": verdict,
            "verdict_text": verdict_text,
            "pass": similarity >= args.threshold,
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Audio 1: {args.audio1}")
        print(f"Audio 2: {args.audio2}")
        print(f"Similarity: {similarity:.4f}")
        print(f"Threshold: {args.threshold:.2f}")
        print(f"Verdict: {verdict_text}")
        print(f"Pass: {'YES' if similarity >= args.threshold else 'NO'}")

    # Exit code based on pass/fail
    sys.exit(0 if similarity >= args.threshold else 1)


if __name__ == "__main__":
    main()
