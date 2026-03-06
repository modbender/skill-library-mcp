#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import requests

API_URL = "https://api.sarvam.ai/text-to-speech/stream"


def stream_tts(
    text: str,
    output_path: Path,
    speaker: str = "rupali",
    pace: float = 1.3,
    temperature: float = 0.6,
    sample_rate: int = 22050,
    codec: str = "mp3",
    target_language_code: str = "en-IN",
    enable_preprocessing: bool = True,
):
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise SystemExit("Missing SARVAM_API_KEY env var")

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "target_language_code": target_language_code,
        "speaker": speaker,
        "model": "bulbul:v3",
        "pace": pace,
        "speech_sample_rate": sample_rate,
        "temperature": temperature,
        "output_audio_codec": codec,
        "enable_preprocessing": enable_preprocessing,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)



def main():
    parser = argparse.ArgumentParser(description="Sarvam Bulbul v3 TTS (streaming) to file")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--out", default="output.mp3", help="Output file path")
    parser.add_argument("--speaker", default="rupali")
    parser.add_argument("--pace", type=float, default=1.3)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--sample-rate", type=int, default=22050)
    parser.add_argument("--codec", default="mp3")
    parser.add_argument("--lang", default="en-IN")
    parser.add_argument("--no-preprocess", action="store_true")

    args = parser.parse_args()

    stream_tts(
        text=args.text,
        output_path=Path(args.out),
        speaker=args.speaker,
        pace=args.pace,
        temperature=args.temperature,
        sample_rate=args.sample_rate,
        codec=args.codec,
        target_language_code=args.lang,
        enable_preprocessing=not args.no_preprocess,
    )


if __name__ == "__main__":
    main()
