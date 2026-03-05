#!/usr/bin/env python3
"""Create short-lived ngrok preview links for local artifacts.

Usage examples:
  python3 scripts/ngrok_preview.py up --title "image search" --source ./outputs/result.png
  python3 scripts/ngrok_preview.py up --session-id task-123 --ttl-minutes 60 --source ./out
  python3 scripts/ngrok_preview.py down --session-id task-123
  python3 scripts/ngrok_preview.py status
"""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STATE_ROOT = Path.home() / ".cache" / "openclaw-ngrok-preview"
SESSIONS_DIR = STATE_ROOT / "sessions"
STATE_DIR = STATE_ROOT / "state"
LOG_DIR = STATE_ROOT / "logs"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".bmp"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v", ".mkv", ".avi"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
TEXT_EXT = {
    ".txt",
    ".md",
    ".json",
    ".csv",
    ".log",
    ".yaml",
    ".yml",
    ".html",
    ".xml",
}


def ensure_dirs() -> None:
    for path in (SESSIONS_DIR, STATE_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    chars: list[str] = []
    for c in value.lower().strip():
        if c.isalnum():
            chars.append(c)
        elif c in {" ", "-", "_"}:
            if not chars or chars[-1] != "-":
                chars.append("-")
    slug = "".join(chars).strip("-")
    return slug[:48] if slug else "preview"


def unique_name(base_name: str, used: set[str]) -> str:
    candidate = base_name
    idx = 2
    while candidate in used:
        stem, suffix = os.path.splitext(base_name)
        candidate = f"{stem}-{idx}{suffix}"
        idx += 1
    used.add(candidate)
    return candidate


def pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def run(cmd: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
    )


def ensure_ngrok_ready(auth_token: str | None) -> None:
    if shutil.which("ngrok") is None:
        raise RuntimeError(
            "ngrok command not found. Install ngrok first: https://ngrok.com/download"
        )

    if auth_token:
        run(["ngrok", "config", "add-authtoken", auth_token], check=True, capture=True)

    probe = run(["ngrok", "config", "check"], check=False, capture=True)
    if probe.returncode != 0:
        raise RuntimeError(
            "ngrok auth token is required. Run: ngrok config add-authtoken <TOKEN>\n"
            "Or pass --auth-token / set NGROK_AUTHTOKEN for this command."
        )


def classify(path: Path) -> str:
    if path.is_dir():
        return "dir"
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXT:
        return "image"
    if suffix in VIDEO_EXT:
        return "video"
    if suffix in AUDIO_EXT:
        return "audio"
    if suffix in TEXT_EXT:
        return "text"
    return "file"


def copy_sources(sources: list[Path], data_dir: Path) -> list[dict[str, Any]]:
    data_dir.mkdir(parents=True, exist_ok=True)
    used_names: set[str] = set()
    manifest: list[dict[str, Any]] = []

    for src in sources:
        src = src.expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(f"Source path does not exist: {src}")

        name = unique_name(src.name or "item", used_names)
        dest = data_dir / name

        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)

        manifest.append(
            {
                "name": name,
                "path": f"data/{name}",
                "kind": classify(dest),
                "bytes": dest.stat().st_size if dest.is_file() else None,
            }
        )

    return manifest


def render_index_html(
    *,
    title: str,
    session_id: str,
    created_at: str,
    expires_at: str,
    manifest: list[dict[str, Any]],
) -> str:
    cards: list[str] = []

    for item in manifest:
        name = html.escape(item["name"])
        rel = html.escape(item["path"])
        kind = item["kind"]

        if kind == "image":
            body = f'<a href="{rel}" target="_blank"><img src="{rel}" alt="{name}" loading="lazy"/></a>'
        elif kind == "video":
            body = (
                f'<video controls preload="metadata">'
                f'<source src="{rel}"></video>'
                f'<p><a href="{rel}" target="_blank">Open video</a></p>'
            )
        elif kind == "audio":
            body = (
                f'<audio controls preload="metadata">'
                f'<source src="{rel}"></audio>'
                f'<p><a href="{rel}" target="_blank">Open audio</a></p>'
            )
        elif kind == "dir":
            body = f'<p><a href="{rel}/" target="_blank">Open folder</a></p>'
        else:
            body = f'<p><a href="{rel}" target="_blank">Open file</a></p>'

        cards.append(
            "\n".join(
                [
                    '<article class="card">',
                    f"<h3>{name}</h3>",
                    body,
                    "</article>",
                ]
            )
        )

    cards_html = "\n".join(cards) if cards else "<p>No files were added.</p>"

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0b1020;
      color: #e7ecff;
      line-height: 1.4;
    }}
    header {{
      position: sticky;
      top: 0;
      padding: 14px 16px;
      background: rgba(11,16,32,0.92);
      border-bottom: 1px solid #27355f;
      backdrop-filter: blur(4px);
      z-index: 5;
    }}
    header h1 {{ margin: 0 0 6px; font-size: 18px; }}
    header p {{ margin: 2px 0; font-size: 12px; color: #9fb1eb; word-break: break-all; }}
    main {{ padding: 14px; display: grid; gap: 12px; }}
    .card {{
      border: 1px solid #2b3f75;
      border-radius: 12px;
      padding: 10px;
      background: #121a34;
    }}
    .card h3 {{ margin: 0 0 10px; font-size: 14px; word-break: break-all; }}
    .card img, .card video {{ width: 100%; border-radius: 10px; background: #050814; }}
    a {{ color: #8dc6ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>Session: {html.escape(session_id)}</p>
    <p>Created: {html.escape(created_at)} • Expires: {html.escape(expires_at)}</p>
  </header>
  <main>
    {cards_html}
  </main>
</body>
</html>
"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def stop_pid(pid: int | None) -> None:
    if not pid:
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        return

    for _ in range(20):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def find_tunnel_url(port: int, timeout_seconds: int) -> str:
    deadline = time.time() + timeout_seconds
    target_addrs = {
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}",
        f"127.0.0.1:{port}",
        f"localhost:{port}",
    }

    while time.time() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=1.2) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            time.sleep(0.35)
            continue

        tunnels = payload.get("tunnels", [])
        for tunnel in tunnels:
            public_url = tunnel.get("public_url", "")
            cfg = tunnel.get("config", {}) or {}
            addr = cfg.get("addr")
            if not public_url:
                continue
            if public_url.startswith("https://") and (
                not addr or str(addr) in target_addrs
            ):
                return public_url

        time.sleep(0.35)

    raise TimeoutError("Timed out waiting for ngrok tunnel URL")


def cmd_up(args: argparse.Namespace) -> int:
    ensure_dirs()

    auth_token = args.auth_token or os.environ.get("NGROK_AUTHTOKEN")
    ensure_ngrok_ready(auth_token)

    session_id = args.session_id
    if not session_id:
        stamp = utc_now().strftime("%Y%m%d-%H%M%S")
        session_id = f"{slugify(args.title)}-{stamp}"

    session_dir = SESSIONS_DIR / session_id
    if session_dir.exists():
        raise RuntimeError(f"Session already exists: {session_id}")

    created_at = utc_now()
    expires_at = created_at + timedelta(minutes=args.ttl_minutes)

    data_dir = session_dir / "data"
    session_dir.mkdir(parents=True, exist_ok=False)

    sources = [Path(src) for src in args.source]
    manifest = copy_sources(sources, data_dir)

    index_html = render_index_html(
        title=args.title,
        session_id=session_id,
        created_at=iso_z(created_at),
        expires_at=iso_z(expires_at),
        manifest=manifest,
    )
    (session_dir / "index.html").write_text(index_html)

    port = pick_free_port()
    http_log = (LOG_DIR / f"{session_id}-http.log").open("a", encoding="utf-8")
    ngrok_log = (LOG_DIR / f"{session_id}-ngrok.log").open("a", encoding="utf-8")

    http_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "http.server",
            str(port),
            "--bind",
            "127.0.0.1",
            "--directory",
            str(session_dir),
        ],
        stdout=http_log,
        stderr=subprocess.STDOUT,
    )

    ngrok_proc = subprocess.Popen(
        [
            "ngrok",
            "http",
            f"127.0.0.1:{port}",
            "--log=stdout",
            "--log-format=json",
        ],
        stdout=ngrok_log,
        stderr=subprocess.STDOUT,
    )

    try:
        public_url = find_tunnel_url(port, timeout_seconds=args.ngrok_timeout_seconds)
    except Exception:
        stop_pid(ngrok_proc.pid)
        stop_pid(http_proc.pid)
        raise
    finally:
        ngrok_log.flush()
        http_log.flush()
        ngrok_log.close()
        http_log.close()

    state = {
        "session_id": session_id,
        "title": args.title,
        "created_at": iso_z(created_at),
        "expires_at": iso_z(expires_at),
        "status": "running",
        "public_url": public_url,
        "local_port": port,
        "sources": [str(Path(src).expanduser().resolve()) for src in args.source],
        "workspace_dir": str(session_dir),
        "http_pid": http_proc.pid,
        "ngrok_pid": ngrok_proc.pid,
        "manifest": manifest,
    }

    write_json(STATE_DIR / f"{session_id}.json", state)

    result = {
        "session_id": session_id,
        "public_url": public_url,
        "expires_at": state["expires_at"],
        "stop_command": f"python3 scripts/ngrok_preview.py down --session-id {session_id}",
        "status_command": "python3 scripts/ngrok_preview.py status",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def load_state_by_id(session_id: str) -> tuple[Path, dict[str, Any]]:
    path = STATE_DIR / f"{session_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No session state found for: {session_id}")
    return path, read_json(path)


def choose_latest_state() -> tuple[Path, dict[str, Any]]:
    items = sorted(STATE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not items:
        raise FileNotFoundError("No session states found")
    path = items[0]
    return path, read_json(path)


def cmd_down(args: argparse.Namespace) -> int:
    ensure_dirs()

    if args.session_id:
        path, state = load_state_by_id(args.session_id)
    else:
        path, state = choose_latest_state()

    stop_pid(state.get("ngrok_pid"))
    stop_pid(state.get("http_pid"))

    state["status"] = "stopped"
    state["stopped_at"] = iso_z(utc_now())
    write_json(path, state)

    if args.delete_session_dir:
        session_dir = Path(state.get("workspace_dir", ""))
        if session_dir.exists() and str(session_dir).startswith(str(SESSIONS_DIR)):
            shutil.rmtree(session_dir)

    print(
        json.dumps(
            {
                "session_id": state.get("session_id"),
                "status": state.get("status"),
                "stopped_at": state.get("stopped_at"),
                "deleted_files": bool(args.delete_session_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    ensure_dirs()
    rows = []

    for path in sorted(STATE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        state = read_json(path)
        rows.append(
            {
                "session_id": state.get("session_id"),
                "status": state.get("status", "unknown"),
                "created_at": state.get("created_at"),
                "expires_at": state.get("expires_at"),
                "public_url": state.get("public_url"),
            }
        )

    print(json.dumps({"sessions": rows}, ensure_ascii=False, indent=2))
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    ensure_dirs()
    now = utc_now()
    removed: list[str] = []

    for path in sorted(STATE_DIR.glob("*.json")):
        state = read_json(path)
        session_id = state.get("session_id")

        try:
            expires_at = datetime.fromisoformat(state.get("expires_at", "").replace("Z", "+00:00"))
        except ValueError:
            expires_at = now

        should_remove = expires_at <= now
        if args.force:
            should_remove = True

        if not should_remove:
            continue

        stop_pid(state.get("ngrok_pid"))
        stop_pid(state.get("http_pid"))

        session_dir = Path(state.get("workspace_dir", ""))
        if session_dir.exists() and str(session_dir).startswith(str(SESSIONS_DIR)):
            shutil.rmtree(session_dir)

        log_glob = f"{session_id}-*.log"
        for log_file in LOG_DIR.glob(log_glob):
            log_file.unlink(missing_ok=True)

        path.unlink(missing_ok=True)
        removed.append(str(session_id))

    print(json.dumps({"removed_sessions": removed}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage short-lived ngrok preview sessions")
    sub = parser.add_subparsers(dest="command", required=True)

    up = sub.add_parser("up", help="Create a temporary preview and return a public URL")
    up.add_argument("--title", required=True, help="Preview title shown on the landing page")
    up.add_argument(
        "--source",
        action="append",
        required=True,
        help="File or directory to include in preview (repeatable)",
    )
    up.add_argument("--session-id", help="Custom session id for traceability")
    up.add_argument("--ttl-minutes", type=int, default=120, help="Auto-expire window")
    up.add_argument("--auth-token", help="ngrok auth token (optional if already configured)")
    up.add_argument(
        "--ngrok-timeout-seconds",
        type=int,
        default=20,
        help="Wait timeout for ngrok tunnel URL",
    )
    up.set_defaults(func=cmd_up)

    down = sub.add_parser("down", help="Stop a running preview session")
    down.add_argument("--session-id", help="Session id to stop (default: latest)")
    down.add_argument(
        "--delete-session-dir",
        action="store_true",
        help="Delete copied preview files after stopping",
    )
    down.set_defaults(func=cmd_down)

    status = sub.add_parser("status", help="List known preview sessions")
    status.set_defaults(func=cmd_status)

    cleanup = sub.add_parser("cleanup", help="Remove expired sessions and files")
    cleanup.add_argument("--force", action="store_true", help="Remove all sessions")
    cleanup.set_defaults(func=cmd_cleanup)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
