import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentmail import AgentMail
from dotenv import load_dotenv


def build_parser(desc: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--env-file", default=None, help="Optional .env path")
    p.add_argument("--inbox", default=None, help="Inbox id/email")
    p.add_argument("--json", action="store_true", help="Force JSON output")
    return p


def load_env(env_file: str | None) -> None:
    if env_file:
        load_dotenv(env_file, override=False)
        return

    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env, override=False)


def get_client_and_inbox(args: argparse.Namespace) -> tuple[AgentMail, str]:
    load_env(args.env_file)
    api_key = os.getenv("AGENTMAIL_API_KEY")
    inbox = args.inbox or os.getenv("AGENTMAIL_INBOX")
    if not api_key:
        raise SystemExit("Missing AGENTMAIL_API_KEY")
    if not inbox:
        raise SystemExit("Missing inbox (use --inbox or AGENTMAIL_INBOX)")
    return AgentMail(api_key=api_key), inbox


def emit(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def get_allowed_senders() -> list[str]:
    raw = os.getenv("AGENTMAIL_ALLOWED_SENDERS", "").strip()
    if not raw:
        return []
    return [x.strip().lower() for x in raw.split(",") if x.strip()]


def sender_matches(sender: str, allowed_senders: list[str]) -> bool:
    s = sender.lower()
    return any(a in s for a in allowed_senders)


def log_action(action: str, **fields: Any) -> None:
    log_path = Path(__file__).resolve().parents[1] / "inbox_ops.log"
    ts = datetime.now(timezone.utc).isoformat()
    line = {"ts": ts, "action": action, **fields}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False, default=str) + "\n")
