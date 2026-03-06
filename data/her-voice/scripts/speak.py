#!/usr/bin/env python3
"""Her Voice — Main TTS entry point. Streams speech to visualizer or speakers.

Author: Jackie & Matus
"""

import argparse
import atexit
import json
import os
import platform
import re as _re
import shutil
import socket
import struct
import subprocess
import sys
from typing import Any, BinaryIO, Union

MAX_STDIN_SIZE = 10 * 1024 * 1024  # 10MB
MAX_CHUNK_SIZE = 100 * 1024 * 1024  # 100MB — max reasonable audio chunk

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from config import load_config, resolve_voice, detect_engine, ensure_correct_python, LANG_MAP

# Track temp files for cleanup on unexpected exit
_temp_files: list[str] = []


def _cleanup_temp_files() -> None:
    for f in _temp_files:
        try:
            os.unlink(f)
        except FileNotFoundError:
            pass


atexit.register(_cleanup_temp_files)


def stream_via_daemon(text: str, voice: str, speed: float, lang: str,
                      socket_path: str, pipe_to: BinaryIO) -> None:
    """Send request to TTS daemon, pipe audio to output."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)

    request = json.dumps({"text": text, "voice": voice, "speed": speed, "lang": lang}).encode("utf-8")
    sock.sendall(struct.pack("!I", len(request)) + request)

    while True:
        header = b""
        while len(header) < 4:
            chunk = sock.recv(4 - len(header))
            if not chunk:
                sock.close()
                return
            header += chunk

        chunk_len = struct.unpack("!I", header)[0]
        if chunk_len == 0:
            break
        if chunk_len > MAX_CHUNK_SIZE:
            sock.close()
            return

        data = b""
        while len(data) < chunk_len:
            piece = sock.recv(min(chunk_len - len(data), 65536))
            if not piece:
                sock.close()
                return
            data += piece

        pipe_to.write(data)
        pipe_to.flush()

    sock.close()


def stream_direct_mlx(text: str, voice: str, speed: float, lang: str,
                      model_name: str, pipe_to: BinaryIO) -> None:
    """Load MLX model and stream directly (fallback when daemon not running)."""
    import numpy as np
    from mlx_audio.tts.utils import load_model

    model = load_model(model_path=model_name)

    for result in model.generate(
        text=text,
        voice=voice,
        speed=speed,
        lang_code=lang,
    ):
        audio_np = np.array(result.audio, dtype=np.float32)
        pipe_to.write(audio_np.tobytes())
        pipe_to.flush()


def resolve_pytorch_voice(config: dict[str, Any]) -> Union[str, Any]:
    """Resolve voice for PyTorch Kokoro — handle blending if configured."""
    blend = config.get("voice_blend", {})
    if blend and len(blend) > 1:
        try:
            import torch
            # Find voices directory from kokoro package
            import kokoro
            kokoro_dir = os.path.dirname(kokoro.__file__)
            voices_dir = os.path.join(kokoro_dir, "assets", "voices")
            if not os.path.isdir(voices_dir):
                # Fallback: check common locations
                for candidate in [
                    os.path.expanduser("~/.local/share/kokoro/voices"),
                    os.path.join(kokoro_dir, "voices"),
                ]:
                    if os.path.isdir(candidate):
                        voices_dir = candidate
                        break

            tensors = []
            weights = []
            for name, weight in blend.items():
                pt_path = os.path.join(voices_dir, f"{name}.pt")
                if os.path.exists(pt_path):
                    tensors.append(torch.load(pt_path, weights_only=True))
                    weights.append(weight)

            if len(tensors) >= 2:
                voice = sum(w * t for w, t in zip(weights, tensors))
                return voice
        except (ImportError, OSError, RuntimeError) as e:
            print(f"Warning: voice blending failed, using base voice: {e}", file=sys.stderr)

    return config["voice"]


def stream_direct_pytorch(text: str, voice: Union[str, Any], speed: float,
                          lang: str, pipe_to: BinaryIO) -> None:
    """Load PyTorch Kokoro and stream directly."""
    import numpy as np
    from kokoro import KPipeline

    pipeline = KPipeline(lang_code=lang)

    for result in pipeline(text, voice=voice, speed=speed):
        audio = result[2]
        if audio is not None:
            audio_np = audio.numpy().astype(np.float32)
            pipe_to.write(audio_np.tobytes())
            pipe_to.flush()


def save_audio(text: str, voice: Union[str, Any], speed: float, lang: str,
               model_name: str, save_path: str, socket_path: str, engine: str,
               config: dict[str, Any]) -> None:
    """Generate audio and save to file."""
    import numpy as np
    import wave

    all_audio = bytearray()

    class Collector:
        def write(self, data: bytes) -> None:
            all_audio.extend(data)
        def flush(self) -> None:
            pass

    w = Collector()
    daemon_voice = voice if isinstance(voice, str) else config["voice"]

    if os.path.exists(socket_path):
        try:
            stream_via_daemon(text, daemon_voice, speed, lang, socket_path, w)
        except (ConnectionRefusedError, FileNotFoundError):
            if engine == "mlx":
                stream_direct_mlx(text, voice, speed, lang, model_name, w)
            else:
                stream_direct_pytorch(text, voice, speed, lang, w)
    else:
        if engine == "mlx":
            stream_direct_mlx(text, voice, speed, lang, model_name, w)
        else:
            stream_direct_pytorch(text, voice, speed, lang, w)

    audio_np = np.frombuffer(bytes(all_audio), dtype=np.float32)
    int16_audio = (audio_np * 32767).astype(np.int16)

    with wave.open(save_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(int16_audio.tobytes())

    print(f"Saved: {save_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Her Voice — Speak text aloud")
    parser.add_argument("text", nargs="?", help="Text to speak (or pipe via stdin)")
    parser.add_argument("--no-viz", action="store_true", help="Skip visualizer")
    parser.add_argument("--persist", action="store_true", help="Keep visualizer open after playback")
    parser.add_argument("--save", metavar="PATH", help="Save audio to file instead of playing")
    parser.add_argument("--voice", help="Override voice")
    parser.add_argument("--speed", type=float, help="Override speed")
    parser.add_argument("--mode", choices=["v2", "classic"], help="Visualizer mode")
    args = parser.parse_args()

    text = args.text
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read(MAX_STDIN_SIZE).strip()
        if not text:
            print("Error: no text provided", file=sys.stderr)
            sys.exit(1)

    config = load_config()
    engine = detect_engine(config)

    # Ensure we're running with the correct venv Python
    ensure_correct_python(config, engine)

    if args.voice is not None:
        voice: Union[str, Any] = args.voice
    elif engine == "pytorch":
        voice = resolve_pytorch_voice(config)
    else:
        voice = resolve_voice(config, engine="mlx")

    speed = args.speed if args.speed is not None else config["speed"]
    lang = LANG_MAP.get(config["language"].lower(), "a")
    model_name = config["model"]
    socket_path = config["daemon"]["socket_path"]
    viz_enabled = config["visualizer"]["enabled"] and not args.no_viz
    viz_mode = args.mode or config["visualizer"]["mode"]
    viz_binary = config["paths"].get("visualizer_binary", "")

    # Save mode
    if args.save:
        save_audio(text, voice, speed, lang, model_name, args.save, socket_path, engine, config)
        return

    # Determine output target
    if viz_enabled and viz_binary and os.path.isfile(viz_binary):
        # Kill any existing streaming visualizer (avoid overlapping audio)
        import signal
        try:
            # Escape regex metacharacters in path for pgrep's POSIX ERE
            safe_pattern = _re.sub(r'([.+*?\[\](){}|^$\\])', r'\\\1', viz_binary)
            result = subprocess.run(["pgrep", "-f", safe_pattern + " --stream"], capture_output=True, text=True)
            for pid_str in result.stdout.strip().split('\n'):
                if pid_str:
                    try:
                        os.kill(int(pid_str), signal.SIGTERM)
                    except (ProcessLookupError, ValueError):
                        pass
        except (ProcessLookupError, ValueError):
            pass

        viz_cmd = [viz_binary, "--stream", "--sample-rate", "24000", "--mode", viz_mode]
        if args.persist:
            viz_cmd.append("--persist")
        viz_proc = subprocess.Popen(viz_cmd, stdin=subprocess.PIPE)
        pipe_to = viz_proc.stdin
    else:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".raw", delete=False)
        _temp_files.append(tmp.name)
        pipe_to = tmp
        viz_proc = None

    try:
        def do_stream(pipe_target: BinaryIO) -> None:
            if os.path.exists(socket_path):
                try:
                    daemon_voice = voice if isinstance(voice, str) else config["voice"]
                    stream_via_daemon(text, daemon_voice, speed, lang, socket_path, pipe_target)
                    return
                except (ConnectionRefusedError, FileNotFoundError):
                    pass

            if engine == "mlx":
                stream_direct_mlx(text, voice, speed, lang, model_name, pipe_target)
            else:
                stream_direct_pytorch(text, voice, speed, lang, pipe_target)

        do_stream(pipe_to)

        if viz_proc:
            pipe_to.close()
            viz_proc.wait()
        else:
            import numpy as np
            pipe_to.close()
            raw_path = pipe_to.name

            audio_np = np.fromfile(raw_path, dtype=np.float32)
            os.unlink(raw_path)
            if raw_path in _temp_files:
                _temp_files.remove(raw_path)

            if len(audio_np) == 0:
                print("Error: no audio generated", file=sys.stderr)
                sys.exit(1)

            import wave
            import tempfile
            wav_tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav_path = wav_tmp.name
            _temp_files.append(wav_path)
            wav_tmp.close()
            int16_audio = (audio_np * 32767).astype(np.int16)
            with wave.open(wav_path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(int16_audio.tobytes())

            if platform.system() == "Darwin":
                subprocess.run(["afplay", wav_path])
            elif shutil.which("aplay"):
                subprocess.run(["aplay", "-q", wav_path])
            elif shutil.which("paplay"):
                subprocess.run(["paplay", wav_path])
            elif shutil.which("ffplay"):
                subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", wav_path])
            else:
                print(f"No audio player found. Audio saved to: {wav_path}", file=sys.stderr)
                if wav_path in _temp_files:
                    _temp_files.remove(wav_path)
                return
            os.unlink(wav_path)
            if wav_path in _temp_files:
                _temp_files.remove(wav_path)

    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        if viz_proc:
            viz_proc.terminate()


if __name__ == "__main__":
    main()
