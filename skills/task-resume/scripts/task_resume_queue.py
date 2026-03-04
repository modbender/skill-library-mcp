#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QUEUE_PATH = ROOT / "memory" / "task-resume-queue.json"
MAX_ITEMS = 30


def _json_print(payload):
    print(json.dumps(payload, ensure_ascii=False))


def load_queue():
    if not QUEUE_PATH.exists():
        return []
    try:
        data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_queue(q):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")


def norm(s):
    return " ".join((s or "").strip().lower().split())


def add_item(title, context, acceptance, source, session):
    now = int(time.time())
    q = load_queue()
    tnorm = norm(title)
    cnorm = norm(context)

    for item in q:
        if norm(item.get("title")) == tnorm and norm(item.get("context")) == cnorm:
            item["updated_at"] = now
            if source:
                item["source"] = source
            if session:
                item["session"] = session
            save_queue(q)
            _json_print({"status": "updated", "item": item})
            return

    item = {
        "id": f"tr_{now}_{len(q)+1}",
        "title": title,
        "context": context,
        "acceptance": acceptance,
        "source": source,
        "session": session,
        "created_at": now,
        "updated_at": now,
    }
    q.append(item)

    dropped = []
    if len(q) > MAX_ITEMS:
        dropped = q[:-MAX_ITEMS]
        q = q[-MAX_ITEMS:]

    save_queue(q)
    _json_print({"status": "added", "item": item, "dropped": dropped})


def pop_item():
    q = load_queue()
    if not q:
        _json_print({"status": "empty"})
        return
    item = q.pop(0)
    save_queue(q)
    _json_print({"status": "popped", "item": item})


def list_items():
    q = load_queue()
    _json_print({"status": "ok", "count": len(q), "items": q})


def status_items():
    q = load_queue()
    by_source = {}
    by_session = {}
    for item in q:
        src = item.get("source") or "unknown"
        ses = item.get("session") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1
        by_session[ses] = by_session.get(ses, 0) + 1
    _json_print(
        {
            "status": "ok",
            "count": len(q),
            "by_source": by_source,
            "by_session": by_session,
        }
    )


def clear_items():
    save_queue([])
    _json_print({"status": "cleared"})


def recover_from_session_log(log_path: str, title: str, acceptance: str, source: str, session: str):
    """
    Robust helper for task-resume recover flows.

    Soft-fail policy:
    - Missing .jsonl file (ENOENT): skip and return structured status instead of erroring.
    """
    path = Path(log_path).expanduser()
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _json_print(
            {
                "status": "skipped_missing_log",
                "reason": "ENOENT",
                "path": str(path),
                "message": "Session log missing; skipped recovery without alert.",
            }
        )
        return
    except Exception as e:
        _json_print(
            {
                "status": "error",
                "reason": type(e).__name__,
                "path": str(path),
                "message": str(e),
            }
        )
        return

    lines = [ln for ln in content.splitlines() if ln.strip()]
    tail = "\n".join(lines[-8:]) if lines else ""
    context = (
        "Recovered from session log tail.\n"
        f"Next step: resume last interrupted action from this context.\n{tail}"
    )
    add_item(title=title, context=context, acceptance=acceptance, source=source, session=session)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--context", required=True)
    p_add.add_argument("--acceptance", default="")
    p_add.add_argument("--source", default="")
    p_add.add_argument("--session", default="")

    sub.add_parser("pop")
    sub.add_parser("list")
    sub.add_parser("status")
    sub.add_parser("clear")

    p_recover = sub.add_parser("recover")
    p_recover.add_argument("--log", required=True, help="Path to session .jsonl log")
    p_recover.add_argument("--title", required=True)
    p_recover.add_argument("--acceptance", default="")
    p_recover.add_argument("--source", default="")
    p_recover.add_argument("--session", default="")

    args = p.parse_args()

    if args.cmd == "add":
        add_item(args.title, args.context, args.acceptance, args.source, args.session)
    elif args.cmd == "pop":
        pop_item()
    elif args.cmd == "list":
        list_items()
    elif args.cmd == "status":
        status_items()
    elif args.cmd == "clear":
        clear_items()
    elif args.cmd == "recover":
        recover_from_session_log(args.log, args.title, args.acceptance, args.source, args.session)
