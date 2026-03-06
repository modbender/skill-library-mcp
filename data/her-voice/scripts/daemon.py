#!/usr/bin/env python3
"""Her Voice — TTS Daemon. Keeps Kokoro model warm in RAM, serves streaming audio over Unix socket."""

import json
import os
import signal
import socket
import struct
import sys
import time
from typing import Any, Callable, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
from config import load_config, resolve_voice, detect_engine, ensure_correct_python, LANG_MAP


def load_tts_model_mlx(model_name: str) -> Any:
    """Load the MLX TTS model."""
    t0 = time.time()
    from mlx_audio.tts.utils import load_model
    model = load_model(model_path=model_name)
    print(f"MLX model loaded in {(time.time()-t0)*1000:.0f}ms", file=sys.stderr)
    return model


def load_tts_model_pytorch(lang: str = "a") -> Any:
    """Load the PyTorch Kokoro pipeline."""
    t0 = time.time()
    from kokoro import KPipeline
    pipeline = KPipeline(lang_code=lang)
    print(f"PyTorch Kokoro pipeline loaded in {(time.time()-t0)*1000:.0f}ms", file=sys.stderr)
    return pipeline


MAX_MSG_SIZE = 1024 * 1024  # 1MB — longest reasonable TTS request
CLIENT_TIMEOUT = 30  # seconds — max time a single client can hold the connection


def _recv_request(conn: socket.socket) -> Optional[dict[str, Any]]:
    """Read a length-prefixed JSON request from the client. Returns parsed dict or None."""
    header = b""
    while len(header) < 4:
        chunk = conn.recv(4 - len(header))
        if not chunk:
            return None
        header += chunk

    msg_len = struct.unpack("!I", header)[0]
    if msg_len > MAX_MSG_SIZE:
        print(f"Rejecting oversized message: {msg_len} bytes (max {MAX_MSG_SIZE})", file=sys.stderr)
        return None

    data = b""
    while len(data) < msg_len:
        chunk = conn.recv(msg_len - len(data))
        if not chunk:
            return None
        data += chunk

    return json.loads(data.decode("utf-8"))


def handle_client_mlx(conn: socket.socket, model: Any, default_voice: str) -> None:
    """Handle a single TTS request (MLX engine)."""
    import numpy as np
    try:
        conn.settimeout(CLIENT_TIMEOUT)
        request = _recv_request(conn)
        if not request:
            return

        text = request.get("text", "")
        voice = request.get("voice", default_voice)
        speed = request.get("speed", 1.05)
        lang = request.get("lang", "a")

        if not text:
            return

        for result in model.generate(
            text=text,
            voice=voice,
            speed=speed,
            lang_code=lang,
        ):
            audio_np = np.array(result.audio, dtype=np.float32)
            pcm_bytes = audio_np.tobytes()
            conn.sendall(struct.pack("!I", len(pcm_bytes)) + pcm_bytes)

        conn.sendall(struct.pack("!I", 0))

    except (BrokenPipeError, ConnectionResetError, socket.timeout):
        pass
    except Exception as e:
        print(f"Error handling request: {e}", file=sys.stderr)
    finally:
        conn.close()


def handle_client_pytorch(conn: socket.socket, pipeline: Any, default_voice: str) -> None:
    """Handle a single TTS request (PyTorch engine)."""
    import numpy as np
    try:
        conn.settimeout(CLIENT_TIMEOUT)
        request = _recv_request(conn)
        if not request:
            return

        text = request.get("text", "")
        voice = request.get("voice", default_voice)
        speed = request.get("speed", 1.05)
        lang = request.get("lang", "a")

        if not text:
            return

        for result in pipeline(text, voice=voice, speed=speed):
            audio = result[2]
            if audio is not None:
                audio_np = audio.numpy().astype(np.float32)
                pcm_bytes = audio_np.tobytes()
                conn.sendall(struct.pack("!I", len(pcm_bytes)) + pcm_bytes)

        conn.sendall(struct.pack("!I", 0))

    except (BrokenPipeError, ConnectionResetError, socket.timeout):
        pass
    except Exception as e:
        print(f"Error handling request: {e}", file=sys.stderr)
    finally:
        conn.close()


def cleanup(socket_path: str, pid_file: str) -> None:
    """Remove socket and pid file."""
    for f in (socket_path, pid_file):
        try:
            os.unlink(f)
        except FileNotFoundError:
            pass


def _read_pid(pid_file: str) -> Optional[int]:
    """Read and parse PID from file. Returns None on any error."""
    try:
        with open(pid_file) as f:
            return int(f.read().strip())
    except (ValueError, OSError):
        return None


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("start", "stop", "status", "restart"):
        print("Usage: daemon.py <start|stop|status|restart>", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    socket_path = config["daemon"]["socket_path"]
    pid_file = config["daemon"]["pid_file"]
    action = sys.argv[1]

    if action == "stop":
        if os.path.exists(pid_file):
            pid = _read_pid(pid_file)
            if pid is None:
                print("Daemon not running (corrupt PID file)")
            else:
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"Stopped TTS daemon (PID {pid})")
                except ProcessLookupError:
                    print("Daemon not running (stale PID file)")
            cleanup(socket_path, pid_file)
        else:
            print("Daemon not running")
        return

    if action == "status":
        if os.path.exists(pid_file):
            pid = _read_pid(pid_file)
            if pid is None:
                print("Daemon not running (corrupt PID file)")
            else:
                try:
                    os.kill(pid, 0)
                    print(f"TTS daemon running (PID {pid})")
                except ProcessLookupError:
                    print("Daemon not running (stale PID file)")
        else:
            print("Daemon not running")
        return

    if action == "restart":
        if os.path.exists(pid_file):
            pid = _read_pid(pid_file)
            if pid is not None:
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)
                except ProcessLookupError:
                    pass
            cleanup(socket_path, pid_file)

    # Start
    engine = detect_engine(config)
    ensure_correct_python(config, engine)

    # Ensure socket/PID directory exists with restricted permissions
    socket_dir = os.path.dirname(socket_path)
    if socket_dir:
        os.makedirs(socket_dir, mode=0o700, exist_ok=True)

    # Remove stale socket (refuse to follow symlinks)
    if os.path.islink(socket_path):
        print(f"Error: socket path is a symlink — refusing to use it: {socket_path}", file=sys.stderr)
        sys.exit(1)
    if os.path.exists(socket_path):
        os.unlink(socket_path)

    def sig_handler(*args: Any) -> None:
        cleanup(socket_path, pid_file)
        sys.exit(0)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    lang = LANG_MAP.get(config.get("language", "en").lower(), "a")

    print(f"Loading TTS model ({engine} engine)...", file=sys.stderr)

    if engine == "mlx":
        model_name = config["model"]
        default_voice = resolve_voice(config, engine="mlx")
        model = load_tts_model_mlx(model_name)
        handle_fn: Callable[[socket.socket], None] = lambda conn: handle_client_mlx(conn, model, default_voice)
    else:
        default_voice = config["voice"]
        pipeline = load_tts_model_pytorch(lang)
        handle_fn = lambda conn: handle_client_pytorch(conn, pipeline, default_voice)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    os.chmod(socket_path, 0o600)
    server.listen(1)

    # Safe PID file creation — refuse to follow symlinks
    if os.path.islink(pid_file):
        print(f"Error: PID file is a symlink — refusing to use it: {pid_file}", file=sys.stderr)
        cleanup(socket_path, pid_file)
        sys.exit(1)
    fd = os.open(pid_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(str(os.getpid()))

    print(f"Ready! Engine: {engine}. Listening on {socket_path}", file=sys.stderr)

    while True:
        try:
            conn, _ = server.accept()
            handle_fn(conn)
        except KeyboardInterrupt:
            break

    cleanup(socket_path, pid_file)


if __name__ == "__main__":
    main()
