#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-TTS MLX CLI runner
Optimized for Apple Silicon (M1/M2/M3/M4)

Dependencies:
    pip install mlx-audio soundfile

Examples:
    # CustomVoice
    python run_tts.py custom-voice --text "Hello" --voice Vivian --lang_code English

    # VoiceDesign
    python run_tts.py voice-design --text "Hello" --instruct "warm, youthful female voice"

    # VoiceClone
    python run_tts.py voice-clone --text "Hello" --ref_audio ref.wav --ref_text "Reference transcript"
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Suppress noisy warnings before importing mlx_audio
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

from mlx_audio.tts.generate import generate_audio


DEFAULT_MODELS = {
    "custom-voice": "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-4bit",
    "voice-design": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-5bit",
    "voice-clone": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit",
}

# Supported voices (case-insensitive in the model)
VOICES = [
    "Vivian",      # Chinese female, bright/young
    "Serena",      # Chinese female, gentle/soft
    "Uncle_Fu",    # Chinese male, news/narration
    "Dylan",       # Chinese male (Beijing dialect)
    "Eric",        # Chinese male (Sichuan dialect)
    "Ryan",        # English male, energetic
    "Aiden",       # English male, clear/neutral
    "Ono_Anna",    # Japanese female
    "Sohee",       # Korean female
]

# Supported languages
LANGUAGES = [
    "auto",       # Auto-detect (default)
    "Chinese",
    "English",
    "Japanese",
    "Korean",
    "French",
    "German",
    "Italian",
    "Spanish",
    "Portuguese",
    "Russian",
]


def get_output_components(output: str | None, out_dir: str, prefix: str):
    """Resolve output directory, prefix, and format.

    If output is specified:
      - Absolute path: use its directory
      - Relative path with directory: use that directory
      - Filename only: use current directory
    """
    if output:
        output_path = Path(output).expanduser()
        if output_path.is_absolute():
            out_dir_path = output_path.parent
            out_dir_path.mkdir(parents=True, exist_ok=True)
        elif output_path.parent != Path("."):
            out_dir_path = output_path.parent
            out_dir_path.mkdir(parents=True, exist_ok=True)
        else:
            out_dir_path = Path(".")

        stem = output_path.stem
        ext = output_path.suffix.lstrip(".") or "wav"
        return str(out_dir_path), stem, ext, True

    out_dir_path = Path(out_dir).expanduser()
    out_dir_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(out_dir_path), f"{prefix}_{timestamp}", "wav", False


def run_custom_voice(args):
    """CustomVoice: built-in voices with optional style control."""
    model = args.model or DEFAULT_MODELS["custom-voice"]
    out_dir, prefix, audio_format, join_audio = get_output_components(
        args.output, args.out_dir, "custom_voice"
    )

    generate_audio(
        text=args.text,
        model=model,
        voice=args.voice,
        instruct=args.instruct,
        speed=args.speed or 1.0,
        lang_code=args.lang_code.lower() if args.lang_code != "auto" else "auto",
        temperature=args.temperature,
        output_path=out_dir,
        file_prefix=prefix,
        audio_format=audio_format,
        join_audio=join_audio,
        play=False,
        verbose=True,
    )


def run_voice_design(args):
    """VoiceDesign: describe a new voice in natural language."""
    model = args.model or DEFAULT_MODELS["voice-design"]
    out_dir, prefix, audio_format, join_audio = get_output_components(
        args.output, args.out_dir, "voice_design"
    )

    generate_audio(
        text=args.text,
        model=model,
        voice=None,
        instruct=args.instruct,
        speed=args.speed or 1.0,
        lang_code=args.lang_code.lower() if args.lang_code != "auto" else "auto",
        temperature=args.temperature,
        output_path=out_dir,
        file_prefix=prefix,
        audio_format=audio_format,
        join_audio=join_audio,
        play=False,
        verbose=True,
    )


def run_voice_clone(args):
    """VoiceClone: clone a voice from reference audio."""
    model = args.model or DEFAULT_MODELS["voice-clone"]
    out_dir, prefix, audio_format, join_audio = get_output_components(
        args.output, args.out_dir, "voice_clone"
    )

    generate_audio(
        text=args.text,
        model=model,
        voice=None,
        ref_audio=args.ref_audio,
        ref_text=args.ref_text,
        speed=args.speed or 1.0,
        lang_code=args.lang_code.lower() if args.lang_code != "auto" else "auto",
        temperature=args.temperature,
        output_path=out_dir,
        file_prefix=prefix,
        audio_format=audio_format,
        join_audio=join_audio,
        play=False,
        verbose=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Qwen3-TTS MLX speech synthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CustomVoice (built-in voices)
  python run_tts.py custom-voice --text "Hello world" --voice Ryan --lang_code English

  # CustomVoice with style control
  python run_tts.py custom-voice --text "Breaking news today." --voice Uncle_Fu \\
    --lang_code Chinese --instruct "news anchor, calm and authoritative"

  # VoiceDesign (create voice from description)
  python run_tts.py voice-design --text "Welcome back." --lang_code English \\
    --instruct "warm, mature male narrator with low pitch and gentle tone"

  # VoiceClone (clone from reference audio)
  python run_tts.py voice-clone --text "Your new line here." \\
    --ref_audio reference.wav --ref_text "Transcript of the reference audio"
        """,
    )

    subparsers = parser.add_subparsers(dest="mode", help="TTS mode")

    # CustomVoice subcommand
    cv_parser = subparsers.add_parser("custom-voice", help="Generate with built-in voices")
    cv_parser.add_argument("--text", required=True, help="Text to synthesize")
    cv_parser.add_argument(
        "--voice",
        default="Vivian",
        choices=VOICES,
        help="Voice name (default: Vivian)",
    )
    cv_parser.add_argument(
        "--lang_code",
        default="auto",
        choices=LANGUAGES,
        help="Language (default: auto-detect)",
    )
    cv_parser.add_argument(
        "--instruct",
        help="Style instruction (e.g., 'calm and warm', 'excited and energetic')",
    )
    cv_parser.add_argument("--model", help="Model name (default: 0.6B-CustomVoice-4bit)")
    cv_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    cv_parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    cv_parser.add_argument("--output", help="Output file path (e.g., output.wav)")
    cv_parser.add_argument("--out-dir", default="./outputs", help="Output directory when --output not specified")

    # VoiceDesign subcommand
    vd_parser = subparsers.add_parser("voice-design", help="Create a voice from text description")
    vd_parser.add_argument("--text", required=True, help="Text to synthesize")
    vd_parser.add_argument(
        "--instruct",
        required=True,
        help="Voice description (e.g., 'warm, mature male narrator with low pitch')",
    )
    vd_parser.add_argument(
        "--lang_code",
        default="auto",
        choices=LANGUAGES,
        help="Language (default: auto-detect)",
    )
    vd_parser.add_argument("--model", help="Model name (default: 1.7B-VoiceDesign-5bit)")
    vd_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    vd_parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    vd_parser.add_argument("--output", help="Output file path")
    vd_parser.add_argument("--out-dir", default="./outputs", help="Output directory when --output not specified")

    # VoiceClone subcommand
    vc_parser = subparsers.add_parser("voice-clone", help="Clone voice from reference audio")
    vc_parser.add_argument("--text", required=True, help="Text to synthesize")
    vc_parser.add_argument("--ref_audio", required=True, help="Reference audio file (5-10s recommended)")
    vc_parser.add_argument("--ref_text", required=True, help="Transcript of the reference audio")
    vc_parser.add_argument(
        "--lang_code",
        default="auto",
        choices=LANGUAGES,
        help="Language (default: auto-detect)",
    )
    vc_parser.add_argument("--model", help="Model name (default: 0.6B-Base-4bit)")
    vc_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    vc_parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    vc_parser.add_argument("--output", help="Output file path")
    vc_parser.add_argument("--out-dir", default="./outputs", help="Output directory when --output not specified")

    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        sys.exit(1)

    if args.mode == "custom-voice":
        run_custom_voice(args)
    elif args.mode == "voice-design":
        run_voice_design(args)
    elif args.mode == "voice-clone":
        run_voice_clone(args)


if __name__ == "__main__":
    main()
