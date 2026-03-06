#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path


def resolve_mud_dir(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise FileNotFoundError(f"mud_dir_not_found: {p}")
        return p

    candidates = [
        Path(r"C:\Users\openclaw\.openclaw\workspace-mud-dm\mud-agent"),
        Path(r"C:\Users\openclaw\.openclaw\workspace\mud-agent"),
    ]
    for c in candidates:
        if (c / "mud_agent.py").exists():
            return c
    raise FileNotFoundError("mud_agent.py not found in known locations")


def is_legacy_engine(mud_file: Path) -> bool:
    try:
        text = mud_file.read_text(encoding="utf-8", errors="ignore")
        return "class MudAgent" in text and "class Context" in text
    except Exception:
        return False


def run_legacy(mud_dir: Path, db_path: Path, command: str, campaign_key: str, user_id: str, username: str, message_id: str):
    sys.path.insert(0, str(mud_dir))
    from mud_agent import MudAgent, Context  # type: ignore

    agent = MudAgent(str(db_path))
    ctx = Context(
        campaign_key=campaign_key,
        user_id=user_id,
        username=username,
        message_id=message_id,
        text=command,
    )
    result = agent.handle(ctx)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def run_cli(mud_dir: Path, db_path: Path, command: str):
    py = sys.executable or "python"
    cmd = [py, str(mud_dir / "mud_agent.py"), "--db", str(db_path)] + shlex.split(command)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr.strip(), file=sys.stderr)
        raise SystemExit(proc.returncode)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run one MUD engine command and print JSON response.")
    ap.add_argument("command", help="Legacy slash command OR CLI args (e.g. 'list-races' or 'new-character --campaign demo --player u1 --name Rook --char-class rogue')")
    ap.add_argument("--mud-dir", default=None, help="Directory containing mud_agent.py")
    ap.add_argument("--db-path", default=None, help="SQLite DB path (default: auto per engine)")
    ap.add_argument("--campaign-key", default="telegram:group:demo")
    ap.add_argument("--user-id", default="ops-user")
    ap.add_argument("--username", default="ops")
    ap.add_argument("--message-id", default=None)
    args = ap.parse_args()

    mud_dir = resolve_mud_dir(args.mud_dir)
    mud_file = mud_dir / "mud_agent.py"

    default_db = mud_dir / ("mud_agent.db" if is_legacy_engine(mud_file) else "mud_state.db")
    db_path = Path(args.db_path) if args.db_path else default_db
    msg_id = args.message_id or f"ops-{int(time.time() * 1000)}"

    if is_legacy_engine(mud_file):
        run_legacy(mud_dir, db_path, args.command, args.campaign_key, args.user_id, args.username, msg_id)
    else:
        run_cli(mud_dir, db_path, args.command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
