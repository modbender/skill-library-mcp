#!/usr/bin/env python3
"""CLI tool to post/rotate Discord webhook promos with a JSONL anti-spam ledger.

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from typing import List, Optional

from ledger import DEFAULT_LEDGER_PATH, Ledger, LedgerEntry, today_local_yyyy_mm_dd
from post_webhook import post_discord_webhook, redact_webhook_url


def eprint(msg: str) -> None:
    sys.stderr.write(msg + "\n")


def sha256_hex(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def read_messages_file(path: str) -> List[str]:
    out: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            out.append(line)
    return out


def choose_next_message(messages: List[str], last_hash: Optional[str]) -> str:
    if not messages:
        raise ValueError("messages list is empty")
    if last_hash is None:
        return messages[0]

    hashes = [sha256_hex(m) for m in messages]
    try:
        idx = hashes.index(last_hash)
    except ValueError:
        return messages[0]
    return messages[(idx + 1) % len(messages)]


def validate_no_url_print(_: str) -> str:
    return "<redacted>"


def cmd_post(args: argparse.Namespace) -> int:
    ledger = Ledger(args.ledger_path)
    today = today_local_yyyy_mm_dd()

    if ledger.already_posted_today(args.channel, today=today):
        eprint(f"Refusing to post: already posted today for channel={args.channel} date={today}")
        return 3

    message = args.message
    msg_hash = sha256_hex(message)

    ledger.append(LedgerEntry(date=today, channel=args.channel, status="reserved", hash=msg_hash))

    if getattr(args, "dry_run", False):
        ledger.append(LedgerEntry(date=today, channel=args.channel, status="dry-run", hash=msg_hash))
        eprint(
            f"Dry-run (not sent): channel={args.channel} date={today} hash={msg_hash[:12]}... url={validate_no_url_print(args.webhook_url)}"
        )
        return 0

    ok, info = post_discord_webhook(
        args.webhook_url,
        message,
        username=args.username,
        timeout_seconds=args.timeout,
    )

    if ok:
        ledger.append(LedgerEntry(date=today, channel=args.channel, status="posted", hash=msg_hash))
        eprint(
            f"Posted: channel={args.channel} date={today} hash={msg_hash[:12]}... ({info}) url={validate_no_url_print(args.webhook_url)}"
        )
        return 0

    ledger.append(LedgerEntry(date=today, channel=args.channel, status="error", hash=msg_hash))
    eprint(
        f"Post failed: channel={args.channel} date={today} hash={msg_hash[:12]}... ({redact_webhook_url(info)}) url={validate_no_url_print(args.webhook_url)}"
    )
    return 2


def cmd_rotate(args: argparse.Namespace) -> int:
    ledger = Ledger(args.ledger_path)
    today = today_local_yyyy_mm_dd()

    if ledger.already_posted_today(args.channel, today=today):
        eprint(f"Skipping rotate: already posted today for channel={args.channel} date={today}")
        return 0

    messages = read_messages_file(args.messages_file)
    if not messages:
        eprint("No messages found (after filtering blanks/#comments).")
        return 2

    last_hash = ledger.last_posted_hash(args.channel)
    msg = choose_next_message(messages, last_hash)

    post_args = argparse.Namespace(
        webhook_url=args.webhook_url,
        channel=args.channel,
        message=msg,
        ledger_path=args.ledger_path,
        username=args.username,
        timeout=args.timeout,
        dry_run=args.dry_run,
    )
    return cmd_post(post_args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="promo_scheduler.py",
        description="Post/rotate Discord webhook promos with a JSONL anti-spam ledger (stdlib only).",
    )
    p.add_argument(
        "--ledger-path",
        default=DEFAULT_LEDGER_PATH,
        help=f"JSONL ledger path (default: {DEFAULT_LEDGER_PATH})",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_post = sub.add_parser("post", help="One-shot post (max 1/day/channel)")
    p_post.add_argument("--webhook-url", required=True, help="Discord webhook URL (never printed)")
    p_post.add_argument("--channel", required=True, help="Logical channel name for ledger enforcement")
    p_post.add_argument("--message", required=True, help="Message content to send")
    p_post.add_argument("--username", default=None, help="Optional Discord webhook username override")
    p_post.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds (default: 15)")
    p_post.add_argument("--dry-run", action="store_true", help="Do not send; only write to ledger and print a dry-run log")
    p_post.set_defaults(func=cmd_post)

    p_rot = sub.add_parser("rotate", help="Rotate through a messages file (max 1/day/channel)")
    p_rot.add_argument("--webhook-url", required=True, help="Discord webhook URL (never printed)")
    p_rot.add_argument("--channel", required=True, help="Logical channel name for ledger enforcement")
    p_rot.add_argument("--messages-file", required=True, help="Text file with one message per line")
    p_rot.add_argument("--username", default=None, help="Optional Discord webhook username override")
    p_rot.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds (default: 15)")
    p_rot.add_argument("--dry-run", action="store_true", help="Do not send; only write to ledger and print a dry-run log")
    p_rot.set_defaults(func=cmd_rotate)

    return p


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
