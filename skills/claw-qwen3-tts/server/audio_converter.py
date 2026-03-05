"""
audio_converter.py — Audio format conversion utilities.

Supports: WAV, MP3, OGG/Opus, FLAC
Uses ffmpeg for conversion and pydub for audio manipulation.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


SUPPORTED_FORMATS = {"wav", "mp3", "ogg", "flac"}

# ffmpeg codec mapping
CODEC_MAP = {
    "wav": {"codec": "pcm_s16le", "extra": []},
    "mp3": {"codec": "libmp3lame", "extra": ["-b:a", "192k"]},
    "ogg": {"codec": "libopus", "extra": ["-b:a", "64k", "-vbr", "on", "-application", "voip"]},
    "flac": {"codec": "flac", "extra": []},
}


def convert_audio(
    input_path: str,
    output_path: str,
    target_format: Optional[str] = None,
    sample_rate: int = 24000,
) -> str:
    """
    Convert an audio file to the specified format.

    Args:
        input_path: Path to the input audio file
        output_path: Path for the output file
        target_format: Target format (wav, mp3, ogg, flac). If None, inferred from output_path.
        sample_rate: Output sample rate (default 24000)

    Returns:
        Path to the output file

    Raises:
        ValueError: If the target format is unsupported
        FileNotFoundError: If the input file doesn't exist
        RuntimeError: If ffmpeg conversion fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if target_format is None:
        target_format = Path(output_path).suffix.lstrip(".")

    target_format = target_format.lower()
    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {target_format}. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    codec_info = CODEC_MAP[target_format]

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:a", codec_info["codec"],
        "-ar", str(sample_rate),
        *codec_info["extra"],
        output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    except FileNotFoundError:
        raise RuntimeError("ffmpeg is not installed or not in PATH")

    if not os.path.exists(output_path):
        raise RuntimeError("ffmpeg did not produce output file")

    return output_path


def convert_to_ogg_opus(
    input_path: str,
    output_path: Optional[str] = None,
    bitrate: str = "64k",
) -> str:
    """
    Convert any audio to OGG/Opus format for Telegram/WhatsApp PTT.

    Args:
        input_path: Path to input audio
        output_path: Path for output OGG. If None, uses input path with .ogg extension
        bitrate: Opus bitrate (default 64k)

    Returns:
        Path to the OGG/Opus file
    """
    if output_path is None:
        output_path = str(Path(input_path).with_suffix(".ogg"))

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:a", "libopus",
        "-b:a", bitrate,
        "-vbr", "on",
        "-compression_level", "10",
        "-frame_duration", "20",
        "-application", "voip",
        output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg OGG conversion failed: {result.stderr}")
    except FileNotFoundError:
        raise RuntimeError("ffmpeg is not installed or not in PATH")

    return output_path


def get_audio_duration(file_path: str) -> float:
    """Get duration of an audio file in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        return 0.0


def get_audio_info(file_path: str) -> dict:
    """Get audio file information (format, duration, sample rate)."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-show_entries", "format=duration,format_name,bit_rate:stream=sample_rate,channels,codec_name",
        "-of", "json",
        file_path,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        import json
        data = json.loads(result.stdout)
        return {
            "duration": float(data.get("format", {}).get("duration", 0)),
            "format": data.get("format", {}).get("format_name", "unknown"),
            "bit_rate": data.get("format", {}).get("bit_rate", "unknown"),
            "sample_rate": data.get("streams", [{}])[0].get("sample_rate", "unknown"),
            "channels": data.get("streams", [{}])[0].get("channels", 0),
            "codec": data.get("streams", [{}])[0].get("codec_name", "unknown"),
        }
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        return {"error": "Could not read audio info"}
