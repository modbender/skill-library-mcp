"""
Shared audio processing functions for super-transcribe backends.
Includes: preprocessing (denoise/normalize), channel extraction,
subtitle burn-in, URL download, audio conversion, probing,
and dependency auto-installation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency auto-install
# ---------------------------------------------------------------------------


def auto_install_package(
    package_name: str, import_name: str | None = None, quiet: bool = False
) -> bool:
    """Auto-install a Python package into the current interpreter's environment.

    Uses uv (preferred) or pip as fallback. Works in venvs and system Python.
    Returns True if the package is now importable, False otherwise.

    Args:
        package_name: pip/uv package name (e.g. "pyannote.audio")
        import_name: Python import name if different from package (e.g. "pyannote.audio")
        quiet: suppress progress output
    """
    if import_name is None:
        import_name = package_name

    # Check if already importable
    try:
        __import__(import_name.split(".")[0])
        return True
    except ImportError:
        pass

    if not quiet:
        print(
            f"📦 {package_name} not found — installing automatically (one-time setup)...",
            file=sys.stderr,
        )

    python_exe = sys.executable

    try:
        if shutil.which("uv"):
            cmd = ["uv", "pip", "install", "--python", python_exe, package_name]
        else:
            cmd = [python_exe, "-m", "pip", "install", package_name]

        subprocess.run(cmd, check=True, capture_output=quiet, text=True, timeout=300)

        if not quiet:
            print(f"✅ {package_name} installed successfully", file=sys.stderr)
        return True

    except subprocess.TimeoutExpired:
        print(
            f"Error: Installation of {package_name} timed out after 5 minutes.", file=sys.stderr
        )
        return False
    except subprocess.CalledProcessError as e:
        stderr_text = e.stderr if hasattr(e, "stderr") and e.stderr else str(e)
        print(f"Error: Failed to install {package_name}: {stderr_text}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: Unexpected failure installing {package_name}: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Duration
# ---------------------------------------------------------------------------


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe or soundfile."""
    if shutil.which("ffprobe"):
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "quiet",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    audio_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError, OSError):
            pass

    try:
        import soundfile as sf

        info = sf.info(audio_path)
        return info.duration
    except (ImportError, OSError):
        pass

    return 0.0


# ---------------------------------------------------------------------------
# Probe — quick audio metadata without transcription
# ---------------------------------------------------------------------------


def probe_audio(audio_path: str) -> dict[str, object]:
    """Get audio metadata without transcribing. Returns dict with duration,
    format, channels, sample_rate, bitrate, size_mb. Uses ffprobe if available,
    falls back to soundfile for basic info.
    """
    result = {
        "file": os.path.basename(audio_path),
        "path": os.path.abspath(audio_path),
        "duration": 0.0,
        "format": Path(audio_path).suffix.lstrip(".").lower(),
        "channels": None,
        "sample_rate": None,
        "bitrate": None,
        "size_mb": round(os.path.getsize(audio_path) / (1024 * 1024), 2)
        if os.path.isfile(audio_path)
        else None,
    }

    if shutil.which("ffprobe"):
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                audio_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(proc.stdout)

            fmt = info.get("format", {})
            result["duration"] = round(float(fmt.get("duration", 0)), 2)
            result["bitrate"] = int(fmt.get("bit_rate", 0)) if fmt.get("bit_rate") else None
            result["format"] = fmt.get("format_name", result["format"])

            # Find the audio stream
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "audio":
                    result["channels"] = int(stream.get("channels", 0)) or None
                    result["sample_rate"] = int(stream.get("sample_rate", 0)) or None
                    break
        except (subprocess.CalledProcessError, ValueError, OSError, json.JSONDecodeError):
            # Fall through to soundfile fallback
            pass

    # Fallback: try soundfile for basic info
    if result["duration"] == 0.0:
        try:
            import soundfile as sf

            sfinfo = sf.info(audio_path)
            result["duration"] = round(sfinfo.duration, 2)
            result["channels"] = sfinfo.channels
            result["sample_rate"] = sfinfo.samplerate
        except (ImportError, OSError):
            pass

    # Human-readable duration
    dur = result["duration"]
    if dur > 0:
        mins, secs = divmod(int(dur), 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            result["duration_human"] = f"{hrs}h {mins}m {secs}s"
        elif mins > 0:
            result["duration_human"] = f"{mins}m {secs}s"
        else:
            result["duration_human"] = f"{secs}s"
    else:
        result["duration_human"] = "unknown"

    return result


# ---------------------------------------------------------------------------
# Audio preprocessing
# ---------------------------------------------------------------------------


def preprocess_audio(
    audio_path: str, normalize: bool = False, denoise: bool = False, quiet: bool = False
) -> tuple[str, str | None]:
    """Preprocess audio with ffmpeg filters (normalize volume, reduce noise).
    Returns (processed_path, tmp_path_to_cleanup_or_None).
    """
    if not normalize and not denoise:
        return audio_path, None

    if not shutil.which("ffmpeg"):
        if not quiet:
            import sys

            print("⚠️  ffmpeg not found — skipping preprocessing", file=sys.stderr)
        return audio_path, None

    filters = []
    if denoise:
        filters.append("highpass=f=200")
        filters.append("afftdn=nf=-25")
    if normalize:
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

    tmp_path = audio_path + ".preprocessed.wav"
    filter_str = ",".join(filters)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        audio_path,
        "-af",
        filter_str,
        "-ar",
        "16000",
        "-ac",
        "1",
        tmp_path,
    ]

    if not quiet:
        import sys

        labels = []
        if normalize:
            labels.append("normalizing")
        if denoise:
            labels.append("denoising")
        print(f"🔧 Preprocessing: {' + '.join(labels)}...", file=sys.stderr)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return tmp_path, tmp_path
    except subprocess.CalledProcessError:
        if not quiet:
            import sys

            print("⚠️  Preprocessing failed, using original audio", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return audio_path, None


# ---------------------------------------------------------------------------
# Channel extraction
# ---------------------------------------------------------------------------


def extract_channel(
    audio_path: str, channel: str, quiet: bool = False
) -> tuple[str, str | None]:
    """Extract a stereo channel from audio using ffmpeg.
    channel: 'left' (c0), 'right' (c1), or 'mix' (no-op).
    Returns (output_path, tmp_path_to_cleanup_or_None).
    """
    if channel == "mix":
        return audio_path, None

    if not shutil.which("ffmpeg"):
        if not quiet:
            import sys

            print(
                "⚠️  ffmpeg not found — cannot extract channel; using full mix", file=sys.stderr
            )
        return audio_path, None

    pan = "c0" if channel == "left" else "c1"
    tmp_path = audio_path + f".{channel}.wav"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        audio_path,
        "-af",
        f"pan=mono|c0={pan}",
        "-ar",
        "16000",
        tmp_path,
    ]
    if not quiet:
        import sys

        print(f"🎚️  Extracting {channel} channel...", file=sys.stderr)
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return tmp_path, tmp_path
    except subprocess.CalledProcessError:
        if not quiet:
            import sys

            print("⚠️  Channel extraction failed; using full mix", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return audio_path, None


# ---------------------------------------------------------------------------
# Subtitle burn-in
# ---------------------------------------------------------------------------


def burn_subtitles(
    video_path: str, srt_content: str, output_path: str, quiet: bool = False
) -> None:
    """Burn SRT subtitles into a video file using ffmpeg."""
    import sys

    tmp_srt = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".srt", delete=False, encoding="utf-8"
        ) as f:
            f.write(srt_content)
            tmp_srt = f.name

        escaped = tmp_srt.replace("\\", "/").replace(":", "\\:")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-vf",
            f"subtitles={escaped}",
            "-c:a",
            "copy",
            output_path,
        ]
        if not quiet:
            print(f"🎬 Burning subtitles into {output_path}...", file=sys.stderr)
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd, check=True, capture_output=True)
        if not quiet:
            print(f"✅ Burned: {output_path}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Burn-in failed: {e}", file=sys.stderr)
    finally:
        if tmp_srt and os.path.exists(tmp_srt):
            os.unlink(tmp_srt)


# ---------------------------------------------------------------------------
# URL download
# ---------------------------------------------------------------------------


def is_url(path: str) -> bool:
    """Check if the input looks like a URL."""
    return path.startswith(("http://", "https://", "www."))


def download_url(url: str, audio_format: str = "wav", quiet: bool = False) -> tuple[str, str]:
    """Download audio from URL using yt-dlp. Returns (audio_path, tmpdir)."""
    import sys

    from .exitcodes import EXIT_BAD_INPUT, EXIT_MISSING_DEP

    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        pipx_path = Path.home() / ".local/share/pipx/venvs/yt-dlp/bin/yt-dlp"
        if pipx_path.exists():
            ytdlp = str(pipx_path)
        else:
            print("Error: yt-dlp not found. Install with: pipx install yt-dlp", file=sys.stderr)
            sys.exit(EXIT_MISSING_DEP)

    tmpdir = tempfile.mkdtemp(prefix="super-transcribe-")
    out_tmpl = os.path.join(tmpdir, "audio.%(ext)s")

    cmd = [ytdlp, "-x", "--audio-format", audio_format, "-o", out_tmpl, "--no-playlist"]
    if quiet:
        cmd.append("-q")
    cmd.append(url)

    if not quiet:
        print("⬇️  Downloading audio from URL...", file=sys.stderr)

    try:
        subprocess.run(cmd, check=True, capture_output=quiet)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading URL: {e}", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(EXIT_BAD_INPUT)

    files = list(Path(tmpdir).glob("audio.*"))
    if not files:
        print("Error: No audio file downloaded", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(EXIT_BAD_INPUT)

    return str(files[0]), tmpdir


# ---------------------------------------------------------------------------
# Audio format conversion (for NeMo: prefers .wav 16kHz mono)
# ---------------------------------------------------------------------------

NATIVE_EXTS = {".wav", ".flac"}
CONVERTIBLE_EXTS = {
    ".mp3",
    ".m4a",
    ".mp4",
    ".mkv",
    ".avi",
    ".wma",
    ".aac",
    ".ogg",
    ".webm",
    ".opus",
}
AUDIO_EXTS = NATIVE_EXTS | CONVERTIBLE_EXTS


def resolve_inputs(inputs: list[str]) -> list[str]:
    """Expand globs, directories, and URLs into a flat list of audio paths.
    Shared across all backends to avoid duplication.
    """
    import glob as _glob

    files = []
    for inp in inputs:
        if is_url(inp):
            files.append(inp)
            continue
        expanded = sorted(_glob.glob(inp, recursive=True)) or [inp]
        for p_str in expanded:
            p = Path(p_str)
            if p.is_dir():
                files.extend(
                    str(f)
                    for f in sorted(p.iterdir())
                    if f.is_file() and f.suffix.lower() in AUDIO_EXTS
                )
            elif p.is_file():
                if p.suffix.lower() not in AUDIO_EXTS:
                    import sys

                    print(
                        f"Warning: skipping non-audio file: {p} "
                        f"(supported: {', '.join(sorted(AUDIO_EXTS))})",
                        file=sys.stderr,
                    )
                    continue
                files.append(str(p))
            else:
                import sys

                print(f"Warning: not found: {inp}", file=sys.stderr)
    return files


def convert_to_wav(audio_path: str, quiet: bool = False) -> tuple[str, str | None]:
    """Convert non-wav/flac audio to 16kHz mono WAV using ffmpeg.
    Returns (wav_path, tmp_path_to_cleanup_or_None).
    """
    ext = Path(audio_path).suffix.lower()
    if ext in NATIVE_EXTS:
        return audio_path, None

    if not shutil.which("ffmpeg"):
        import sys

        print(
            f"⚠️  ffmpeg not found — cannot convert {ext} to WAV.",
            file=sys.stderr,
        )
        return audio_path, None

    tmp_path = audio_path + ".converted.wav"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        audio_path,
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        tmp_path,
    ]
    if not quiet:
        import sys

        print(f"🔄 Converting {ext} → WAV (16kHz mono)...", file=sys.stderr)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return tmp_path, tmp_path
    except subprocess.CalledProcessError as e:
        if not quiet:
            import sys

            print(f"⚠️  Conversion failed: {e}. Trying original file.", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return audio_path, None
