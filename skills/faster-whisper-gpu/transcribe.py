#!/usr/bin/env python3
"""
Faster Whisper GPU - Local Speech-to-Text Transcription

High-performance audio transcription using NVIDIA GPU acceleration.
100% local - no data sent to external services.

Usage:
    python transcribe.py audio.mp3
    python transcribe.py audio.mp3 --language pt --format srt
    python transcribe.py audio.mp3 --model large-v3 --vad_filter
"""

import argparse
import sys
import json
import warnings
from pathlib import Path
from typing import Optional, List

try:
    from faster_whisper import WhisperModel
    import torch
except ImportError as e:
    print(f"Error: Required package not installed: {e}", file=sys.stderr)
    print("\nInstall with: pip install faster-whisper torch", file=sys.stderr)
    sys.exit(1)


# Suppress future warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def format_timestamp(seconds: float) -> str:
    """Format seconds as SRT timestamp (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds as VTT timestamp (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
    device: str = "cuda",
    compute_type: str = "float16",
    task: str = "transcribe",
    vad_filter: bool = False,
    vad_parameters: Optional[dict] = None,
    condition_on_previous_text: bool = True,
    initial_prompt: Optional[str] = None,
    word_timestamps: bool = False,
    hotwords: Optional[str] = None,
) -> tuple:
    """
    Transcribe audio file using Faster Whisper.
    
    Args:
        audio_path: Path to audio file
        model_size: Model size (tiny, base, small, medium, large-v1, large-v2, large-v3)
        language: Language code (e.g., 'pt', 'en') or None for auto-detect
        device: Device to use ('cuda' or 'cpu')
        compute_type: Computation type (int8, int8_float16, int16, float16, float32)
        task: Task type ('transcribe' or 'translate')
        vad_filter: Enable voice activity detection
        vad_parameters: VAD parameters dict
        condition_on_previous_text: Condition on previous text
        initial_prompt: Initial prompt for transcription
        word_timestamps: Include word-level timestamps
        hotwords: Comma-separated hotwords to boost
        
    Returns:
        Tuple of (segments generator, transcription info)
    """
    # Check CUDA availability
    if device == "cuda" and not torch.cuda.is_available():
        print("Warning: CUDA not available, falling back to CPU", file=sys.stderr)
        device = "cpu"
        compute_type = "int8"  # Use int8 for CPU
    
    # Load model
    print(f"Loading model '{model_size}' on {device} ({compute_type})...", file=sys.stderr)
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    # Prepare transcription options
    options = {
        "task": task,
        "vad_filter": vad_filter,
        "condition_on_previous_text": condition_on_previous_text,
        "word_timestamps": word_timestamps,
    }
    
    if language:
        options["language"] = language
    
    if vad_parameters:
        options["vad_parameters"] = vad_parameters
    
    if initial_prompt:
        options["initial_prompt"] = initial_prompt
    
    if hotwords:
        options["hotwords"] = hotwords
    
    # Transcribe
    print(f"Transcribing: {audio_path}", file=sys.stderr)
    segments, info = model.transcribe(audio_path, **options)
    
    return segments, info


def output_txt(segments, output_file: Optional[str] = None):
    """Output as plain text"""
    full_text = []
    for segment in segments:
        full_text.append(segment.text.strip())
    
    text = " ".join(full_text)
    
    if output_file:
        Path(output_file).write_text(text, encoding="utf-8")
        print(f"Transcription saved to: {output_file}", file=sys.stderr)
    else:
        print(text)


def output_srt(segments, output_file: Optional[str] = None, word_timestamps: bool = False):
    """Output as SRT subtitles"""
    lines = []
    subtitle_index = 1
    
    for segment in segments:
        if word_timestamps and segment.words:
            # Word-level timestamps
            for word in segment.words:
                lines.append(f"{subtitle_index}")
                lines.append(f"{format_timestamp(word.start)} --> {format_timestamp(word.end)}")
                lines.append(word.word.strip())
                lines.append("")
                subtitle_index += 1
        else:
            # Segment-level timestamps
            lines.append(f"{subtitle_index}")
            lines.append(f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}")
            lines.append(segment.text.strip())
            lines.append("")
            subtitle_index += 1
    
    srt_content = "\n".join(lines)
    
    if output_file:
        Path(output_file).write_text(srt_content, encoding="utf-8")
        print(f"Subtitles saved to: {output_file}", file=sys.stderr)
    else:
        print(srt_content)


def output_vtt(segments, output_file: Optional[str] = None, word_timestamps: bool = False):
    """Output as WebVTT"""
    lines = ["WEBVTT", ""]
    
    for segment in segments:
        if word_timestamps and segment.words:
            for word in segment.words:
                lines.append(f"{format_timestamp_vtt(word.start)} --> {format_timestamp_vtt(word.end)}")
                lines.append(word.word.strip())
                lines.append("")
        else:
            lines.append(f"{format_timestamp_vtt(segment.start)} --> {format_timestamp_vtt(segment.end)}")
            lines.append(segment.text.strip())
            lines.append("")
    
    vtt_content = "\n".join(lines)
    
    if output_file:
        Path(output_file).write_text(vtt_content, encoding="utf-8")
        print(f"WebVTT saved to: {output_file}", file=sys.stderr)
    else:
        print(vtt_content)


def output_json(segments, info, output_file: Optional[str] = None, word_timestamps: bool = False):
    """Output as JSON"""
    result = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": []
    }
    
    for segment in segments:
        seg_data = {
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip(),
        }
        
        if word_timestamps and segment.words:
            seg_data["words"] = [
                {
                    "word": word.word.strip(),
                    "start": word.start,
                    "end": word.end,
                    "probability": word.probability
                }
                for word in segment.words
            ]
        
        result["segments"].append(seg_data)
    
    json_content = json.dumps(result, indent=2, ensure_ascii=False)
    
    if output_file:
        Path(output_file).write_text(json_content, encoding="utf-8")
        print(f"JSON saved to: {output_file}", file=sys.stderr)
    else:
        print(json_content)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio using Faster Whisper with GPU acceleration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.mp3
  %(prog)s audio.mp3 --language pt --format srt
  %(prog)s audio.mp3 --model large-v3 --vad_filter
  %(prog)s audio.mp3 --task translate --format json
        """
    )
    
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument(
        "--model",
        choices=["tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3"],
        default="base",
        help="Model size to use (default: base)"
    )
    parser.add_argument(
        "--language",
        help="Language code (e.g., 'pt', 'en'). Auto-detect if not specified."
    )
    parser.add_argument(
        "--format",
        choices=["txt", "srt", "json", "vtt"],
        default="txt",
        help="Output format (default: txt)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--device",
        choices=["cuda", "cpu"],
        default="cuda",
        help="Device to use (default: cuda if available)"
    )
    parser.add_argument(
        "--compute_type",
        choices=["int8", "int8_float16", "int16", "float16", "float32"],
        default="float16",
        help="Computation precision (default: float16)"
    )
    parser.add_argument(
        "--task",
        choices=["transcribe", "translate"],
        default="transcribe",
        help="Task: transcribe or translate to English (default: transcribe)"
    )
    parser.add_argument(
        "--vad_filter",
        action="store_true",
        help="Enable voice activity detection filter"
    )
    parser.add_argument(
        "--condition_on_previous_text",
        action="store_true",
        default=True,
        help="Condition on previous text (default: True)"
    )
    parser.add_argument(
        "--initial_prompt",
        help="Initial prompt to guide transcription"
    )
    parser.add_argument(
        "--word_timestamps",
        action="store_true",
        help="Include word-level timestamps (for SRT/JSON)"
    )
    parser.add_argument(
        "--hotwords",
        help="Comma-separated hotwords to boost recognition"
    )
    
    args = parser.parse_args()
    
    # Validate audio file
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # Transcribe
    try:
        segments, info = transcribe_audio(
            audio_path=str(audio_path),
            model_size=args.model,
            language=args.language,
            device=args.device,
            compute_type=args.compute_type,
            task=args.task,
            vad_filter=args.vad_filter,
            condition_on_previous_text=args.condition_on_previous_text,
            initial_prompt=args.initial_prompt,
            word_timestamps=args.word_timestamps,
            hotwords=args.hotwords,
        )
        
        # Print language info
        print(
            f"Detected language: {info.language} "
            f"(probability: {info.language_probability:.2f})",
            file=sys.stderr
        )
        print(f"Duration: {info.duration:.2f}s", file=sys.stderr)
        
        # Output in requested format
        if args.format == "txt":
            output_txt(segments, args.output)
        elif args.format == "srt":
            output_srt(segments, args.output, args.word_timestamps)
        elif args.format == "vtt":
            output_vtt(segments, args.output, args.word_timestamps)
        elif args.format == "json":
            output_json(segments, info, args.output, args.word_timestamps)
            
    except KeyboardInterrupt:
        print("\nTranscription interrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()