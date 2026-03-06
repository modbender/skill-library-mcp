#!/usr/bin/env python3
"""
speakturbo CLI - Ultra-fast text-to-speech

Usage:
    speakturbo "Hello world"              # Play audio
    speakturbo "Hello" -o output.wav      # Save to file
    speakturbo "Hello" -v marius          # Use different voice
    speakturbo --list-voices              # List available voices
    echo "Hello" | speakturbo             # Read from stdin
"""

import argparse
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

__version__ = "0.1.0"

# Daemon configuration
DAEMON_HOST = "127.0.0.1"
DAEMON_PORT = 7125
DAEMON_URL = f"http://{DAEMON_HOST}:{DAEMON_PORT}"
PID_FILE = Path.home() / ".speakturbo" / "daemon.pid"

VOICES = ["alba", "marius", "javert", "jean", "fantine", "cosette", "eponine", "azelma"]

# Default directories where -o output is allowed without --allow-dir
DEFAULT_ALLOWED_DIRS = [
    "/tmp",
    "/var/tmp",
    tempfile.gettempdir(),
]


def is_daemon_running() -> bool:
    """Check if daemon is running."""
    try:
        response = requests.get(f"{DAEMON_URL}/health", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def start_daemon():
    """Start the daemon in background."""
    if is_daemon_running():
        return True
    
    print("Starting speakturbo daemon...", file=sys.stderr)
    
    # Start streaming daemon as subprocess
    daemon_script = Path(__file__).parent / "daemon_streaming.py"
    
    # Create log directory
    log_dir = Path("/tmp")
    log_file = log_dir / "speakturbo.log"
    
    with open(log_file, "a") as log:
        process = subprocess.Popen(
            [sys.executable, str(daemon_script)],
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
    
    # Save PID
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(process.pid))
    
    # Wait for daemon to be ready (can take 2-5s for model loading)
    for _ in range(100):  # 10 seconds max
        if is_daemon_running():
            print("Daemon ready.", file=sys.stderr)
            return True
        time.sleep(0.1)
    
    print("Warning: Daemon may not have started correctly.", file=sys.stderr)
    return False


def stop_daemon():
    """Stop the daemon."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, signal.SIGTERM)
            PID_FILE.unlink()
            print("Daemon stopped.")
        except (ValueError, ProcessLookupError):
            PID_FILE.unlink()
            print("Daemon was not running.")
    else:
        print("Daemon is not running.")


def daemon_status():
    """Check daemon status."""
    if is_daemon_running():
        try:
            response = requests.get(f"{DAEMON_URL}/health", timeout=1)
            data = response.json()
            print(f"Daemon: running")
            print(f"Voices: {', '.join(data.get('voices', []))}")
        except Exception as e:
            print(f"Daemon: running (but health check failed: {e})")
    else:
        print("Daemon: not running")


def list_voices():
    """List available voices."""
    print("Available voices:")
    for voice in VOICES:
        print(f"  - {voice}")


def load_allowed_dirs() -> list[str]:
    """Load user-configured allowed directories from ~/.speakturbo/config."""
    config_file = Path.home() / ".speakturbo" / "config"
    custom_dirs = []
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                expanded = os.path.expanduser(line)
                if os.path.isabs(expanded):
                    custom_dirs.append(expanded)
    return custom_dirs


def validate_output_path(output: str, extra_allowed: list[str] | None = None) -> str:
    """Validate output path is within allowed directories.

    Returns the resolved absolute path if allowed.
    Exits with a clear error message if not.
    """
    resolved = os.path.realpath(os.path.expanduser(output))

    allowed = list(DEFAULT_ALLOWED_DIRS)
    allowed.append(os.getcwd())
    allowed.append(str(Path.home() / ".speakturbo"))
    allowed.extend(load_allowed_dirs())
    if extra_allowed:
        allowed.extend(extra_allowed)

    # Normalize ALL paths once (realpath resolves symlinks + makes absolute)
    allowed = [os.path.realpath(os.path.expanduser(d)) for d in allowed]

    for allowed_dir in allowed:
        if resolved.startswith(allowed_dir + os.sep) or resolved == allowed_dir:
            return resolved

    # Build error message that tells the agent exactly what to do
    allowed_display = "\n".join(f"    {d}" for d in sorted(set(allowed)))
    parent_dir = os.path.dirname(resolved)
    print(
        f"Error: Output path is outside allowed directories.\n"
        f"\n"
        f"  Path: {resolved}\n"
        f"\n"
        f"Allowed directories:\n"
        f"{allowed_display}\n"
        f"\n"
        f"To allow this directory for this command:\n"
        f"  speakturbo \"text\" -o {output} --allow-dir {parent_dir}\n"
        f"\n"
        f"To allow it permanently, add to ~/.speakturbo/config:\n"
        f"  mkdir -p ~/.speakturbo && echo \"{parent_dir}\" >> ~/.speakturbo/config",
        file=sys.stderr,
    )
    sys.exit(1)


def generate_speech(text: str, voice: str = "alba", output: str = None,
                    play: bool = True, allowed_dirs: list[str] | None = None):
    """Generate speech from text."""
    # Ensure daemon is running
    if not is_daemon_running():
        if not start_daemon():
            print("Error: Could not start daemon.", file=sys.stderr)
            sys.exit(1)
    
    # Validate voice
    if voice not in VOICES:
        print(f"Error: Invalid voice '{voice}'. Available: {', '.join(VOICES)}", file=sys.stderr)
        sys.exit(1)
    
    # Validate text
    if not text or not text.strip():
        print("Error: Text cannot be empty.", file=sys.stderr)
        sys.exit(1)
    
    # Validate output path BEFORE HTTP request (fail fast)
    if output:
        output = validate_output_path(output, extra_allowed=allowed_dirs)
    
    # Generate audio
    try:
        response = requests.get(
            f"{DAEMON_URL}/tts",
            params={"text": text.strip(), "voice": voice},
            stream=True,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}", file=sys.stderr)
        if response.status_code == 400:
            try:
                detail = response.json().get("detail", "Unknown error")
                print(f"  {detail}", file=sys.stderr)
            except:
                pass
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to daemon: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle output
    if output:
        # Save to file
        with open(output, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)
        print(f"Saved to {output}", file=sys.stderr)
    elif play:
        # Play audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)
        
        try:
            # Use afplay on macOS
            subprocess.run(["afplay", temp_path], check=True)
        except FileNotFoundError:
            # Try aplay on Linux
            try:
                subprocess.run(["aplay", temp_path], check=True)
            except FileNotFoundError:
                print(f"Audio saved to: {temp_path}", file=sys.stderr)
                print("Install afplay (macOS) or aplay (Linux) to play audio.", file=sys.stderr)
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description="speakturbo - Ultra-fast text-to-speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  speakturbo "Hello world"              # Play audio
  speakturbo "Hello" -o output.wav      # Save to file
  speakturbo "Hello" -v marius          # Use different voice
  speakturbo --list-voices              # List available voices
  echo "Hello" | speakturbo             # Read from stdin
""",
    )
    
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("-v", "--voice", default="alba", help="Voice to use (default: alba)")
    parser.add_argument("-o", "--output", help="Output WAV file (default: play audio)")
    parser.add_argument("--allow-dir", action="append", default=None,
                        help="Allow output to this directory (repeatable)")
    parser.add_argument("--no-play", action="store_true", help="Don't play audio (only with -o)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--version", action="version", version=f"speakturbo {__version__}")
    
    # Daemon management
    parser.add_argument("--daemon-start", action="store_true", help="Start daemon")
    parser.add_argument("--daemon-stop", action="store_true", help="Stop daemon")
    parser.add_argument("--daemon-status", action="store_true", help="Check daemon status")
    
    args = parser.parse_args()
    
    # Handle daemon commands
    if args.daemon_start:
        start_daemon()
        return
    
    if args.daemon_stop:
        stop_daemon()
        return
    
    if args.daemon_status:
        daemon_status()
        return
    
    if args.list_voices:
        list_voices()
        return
    
    # Get text from argument or stdin
    text = args.text
    if text is None:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)
    
    # Generate speech
    generate_speech(
        text=text,
        voice=args.voice,
        output=args.output,
        play=not args.no_play,
        allowed_dirs=args.allow_dir,
    )


if __name__ == "__main__":
    main()
