#!/usr/bin/env python3

import argparse
import json
import os
import signal
import socket
import sys
from pathlib import Path
from typing import Any


def _find_workspace_root() -> Path:
    """Walk up from script location to find workspace root (parent of 'skills/')."""
    # Use $PWD (preserves symlinks) instead of Path.cwd() (resolves them).
    pwd_env = os.environ.get("PWD")
    cwd = Path(pwd_env) if pwd_env else Path.cwd()
    d = cwd
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        parent = d.parent
        if parent == d:
            break
        d = parent

    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        d = d.parent
    return Path.cwd()


def _default_root_dir() -> Path:
    """Default intranet root directory."""
    return _find_workspace_root() / "intranet"


def _root_dir() -> Path:
    """Root directory is always workspace/intranet."""
    return _default_root_dir()


def _pid_file() -> Path:
    """PID file location (workspace/intranet/.pid)."""
    return _default_root_dir() / ".pid"


def _config_file() -> Path:
    """Runtime config file (workspace/intranet/.conf)."""
    return _default_root_dir() / ".conf"


def _read_pid() -> int | None:
    """Read PID from file if it exists."""
    pid_file = _pid_file()
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text().strip())
    except (ValueError, OSError):
        return None


def _write_pid(pid: int) -> None:
    """Write PID to file."""
    _pid_file().write_text(str(pid) + "\n")


def _clear_pid() -> None:
    """Remove PID file."""
    try:
        _pid_file().unlink()
    except FileNotFoundError:
        pass


def _persistent_config_file() -> Path:
    """Persistent config file (workspace/intranet/config.json)."""
    return _default_root_dir() / "config.json"


def _load_persistent_config() -> dict[str, Any]:
    """Load persistent config from workspace/intranet/config.json."""
    cf = _persistent_config_file()
    if not cf.exists():
        return {}
    try:
        return json.loads(cf.read_text())
    except (ValueError, OSError):
        return {}


def _read_config() -> dict[str, Any]:
    """Read server configuration."""
    config_file = _config_file()
    if not config_file.exists():
        return {}
    try:
        return json.loads(config_file.read_text())
    except (ValueError, OSError):
        return {}


def _write_config(config: dict[str, Any]) -> None:
    """Write server configuration."""
    _config_file().write_text(json.dumps(config, indent=2) + "\n")


def _clear_config() -> None:
    """Remove config file."""
    try:
        _config_file().unlink()
    except FileNotFoundError:
        pass


def _is_process_running(pid: int) -> bool:
    """Check if a process is running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _get_display_url(host: str, port: int) -> str:
    """Get a user-friendly URL for accessing the server."""
    # If bound to all interfaces, use the local hostname
    if host in ("0.0.0.0", "::"):
        hostname = socket.gethostname()
        # Append .local for mDNS if not already present
        if "." not in hostname:
            hostname = f"{hostname}.local"
        return f"http://{hostname}:{port}/"
    return f"http://{host}:{port}/"


def cmd_start(args) -> int:
    """Start the intranet server."""
    # Check if already running
    pid = _read_pid()
    if pid and _is_process_running(pid):
        print(f"[intranet] Server already running (PID {pid})")
        config = _read_config()
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8080)
        print(f"[intranet] Access at {_get_display_url(host, port)}")
        return 0

    # Resolve directory
    root_dir = _root_dir()
    if not root_dir.exists():
        root_dir.mkdir(parents=True, exist_ok=True)
        print(f"[intranet] Created root directory: {root_dir}")

    # Load persistent config (workspace/intranet/config.json)
    persistent_config = _load_persistent_config()

    host = args.host
    port = args.port
    token = args.token or persistent_config.get("token") or None
    allowed_hosts = persistent_config.get("allowed_hosts", [])

    # Non-loopback binding requires auth + allowed_hosts
    if host not in ("127.0.0.1", "localhost", "::1"):
        missing = []
        if not token:
            missing.append("token auth (--token or token in config.json)")
        if not allowed_hosts:
            missing.append("allowed_hosts in config.json")
        if missing:
            print(f"[intranet] ERROR: Binding to {host} requires: {' and '.join(missing)}")
            print("[intranet] Use --host localhost for local-only access, or configure auth + allowed_hosts first.")
            return 1

    # Save configuration
    config = {
        "host": host,
        "port": port,
    }
    if token:
        config["token"] = token
    _write_config(config)

    # Fork to background
    pid = os.fork()
    if pid > 0:
        # Parent process
        _write_pid(pid)
        print(f"[intranet] Server started (PID {pid})")
        print(f"[intranet] Serving {root_dir}")
        print(f"[intranet] Access at {_get_display_url(host, port)}")
        if token:
            print("[intranet] Auth: token enabled")
        return 0

    # Child process - start the server
    # Detach from terminal
    os.setsid()

    # Redirect stdout/stderr to /dev/null (daemon mode)
    devnull = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull, sys.stdout.fileno())
    os.dup2(devnull, sys.stderr.fileno())
    os.close(devnull)

    # Import and run the server (always load fresh from file to avoid stale cache)
    import importlib.util
    p = Path(__file__).with_name("intranet_web.py")
    spec = importlib.util.spec_from_file_location("intranet_web", p)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        run_server = getattr(mod, "run_server")

    run_server(host=host, port=port, token=token)
    return 0


def cmd_status(args) -> int:
    """Check server status."""
    pid = _read_pid()
    if not pid:
        print("[intranet] Server is not running")
        return 1

    if _is_process_running(pid):
        config = _read_config()
        host = config.get("host", "127.0.0.1")
        port = config.get("port", 8080)
        root_dir = config.get("root_dir", str(_default_root_dir()))
        has_token = bool(config.get("token"))
        print(f"[intranet] Server is running (PID {pid})")
        print(f"[intranet] Serving {root_dir}")
        print(f"[intranet] Access at {_get_display_url(host, port)}")
        print(f"[intranet] Auth: {'token enabled' if has_token else 'none (open)'}")
        return 0
    else:
        print(f"[intranet] Server not running (stale PID {pid})")
        _clear_pid()
        return 1


def cmd_stop(args) -> int:
    """Stop the intranet server."""
    pid = _read_pid()
    if not pid:
        print("[intranet] Server is not running")
        return 1

    if not _is_process_running(pid):
        print(f"[intranet] Server not running (stale PID {pid})")
        _clear_pid()
        _clear_config()
        return 1

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"[intranet] Server stopped (PID {pid})")
        _clear_pid()
        _clear_config()
        return 0
    except OSError as e:
        print(f"[intranet] ERROR: Failed to stop server (PID {pid}): {e}")
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="intranet.py",
        description="Simple web server for local file serving"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # Start command
    start = sub.add_parser("start", help="Start the intranet server")
    start.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1; 0.0.0.0 requires token + allowed_hosts)")
    start.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    start.add_argument("--token", default=None, help="Bearer token for authentication (or set in config.json)")
    start.set_defaults(func=cmd_start)

    # Status command
    status = sub.add_parser("status", help="Check server status")
    status.set_defaults(func=cmd_status)

    # Stop command
    stop = sub.add_parser("stop", help="Stop the intranet server")
    stop.set_defaults(func=cmd_stop)

    args = ap.parse_args()
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
