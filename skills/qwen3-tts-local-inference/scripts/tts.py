#!/usr/bin/env python3
"""
Qwen3-TTS Local Inference — CLI Entry Point

Generate speech directly from the command line, no server needed.

Usage:
    python tts.py "Hello world"
    python tts.py "Hello world" --speaker Aiden --language English
    python tts.py "Hello world" --mode voice-design --instruct "Warm female voice"
    python tts.py "Hello world" --mode voice-clone --ref-audio ref.wav --ref-text "Hi"
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).resolve().parent.as_posix())

from config import MODEL_SIZE_LABEL, OUTPUT_DIR, SPEAKER_NAMES, SUPPORTED_LANGUAGES


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate speech from text using Qwen3-TTS (direct inference).",
    )
    p.add_argument("text", help="Text to synthesise")
    p.add_argument(
        "--mode",
        choices=["custom-voice", "voice-design", "voice-clone"],
        default="custom-voice",
        help="TTS mode (default: custom-voice)",
    )
    p.add_argument("--speaker", default="Ryan", help=f"Speaker name (default: Ryan). Options: {', '.join(SPEAKER_NAMES)}")
    p.add_argument("--language", default="Auto", help=f"Language (default: Auto). Options: {', '.join(SUPPORTED_LANGUAGES)}")
    p.add_argument("--instruct", default="", help="Style/emotion instruction or voice description")
    p.add_argument("--ref-audio", default="", help="Reference audio path/URL for voice-clone mode")
    p.add_argument("--ref-text", default="", help="Transcript of reference audio for voice-clone mode")
    p.add_argument("--output-dir", default=None, help=f"Output directory (default: {OUTPUT_DIR})")
    p.add_argument("--model-dir", default=None, help="Custom model directory (overrides QWEN_TTS_MODEL_DIR)")
    p.add_argument("-o", "--output", default=None, help="Exact output file path (overrides auto-naming)")
    p.add_argument("--json", action="store_true", help="Output result as JSON")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    return p


def main() -> None:
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(name)-24s  %(levelname)-5s  %(message)s",
    )
    logger = logging.getLogger("qwen3-tts.cli")

    from inference import TTSInferenceEngine

    engine = TTSInferenceEngine(
        model_dir=args.model_dir,
        output_dir=args.output_dir,
    )

    logger.info("Model size: %s | Mode: %s", MODEL_SIZE_LABEL, args.mode)

    if args.mode == "custom-voice":
        result = engine.generate_custom_voice(
            text=args.text,
            language=args.language,
            speaker=args.speaker,
            instruct=args.instruct,
        )
    elif args.mode == "voice-design":
        if not args.instruct:
            logger.error("--instruct is required for voice-design mode")
            sys.exit(1)
        result = engine.generate_voice_design(
            text=args.text,
            language=args.language,
            instruct=args.instruct,
        )
    elif args.mode == "voice-clone":
        if not args.ref_audio:
            logger.error("--ref-audio is required for voice-clone mode")
            sys.exit(1)
        result = engine.generate_voice_clone(
            text=args.text,
            language=args.language,
            ref_audio=args.ref_audio,
            ref_text=args.ref_text,
        )
    else:
        logger.error("Unknown mode: %s", args.mode)
        sys.exit(1)

    if args.output:
        import shutil
        shutil.move(result["file"], args.output)
        result["file"] = args.output

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Output:    {result['file']}")
        print(f"Duration:  {result['duration_s']}s")
        print(f"Inference: {result['inference_s']}s")


if __name__ == "__main__":
    main()
