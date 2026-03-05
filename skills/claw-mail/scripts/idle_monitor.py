#!/usr/bin/env python3
"""Monitor an IMAP mailbox for new messages using IDLE (push).

Uses IMAP IDLE (RFC 2177) to wait for new-mail events instead of polling.
When a new message arrives the script fetches and prints it, then re-enters
IDLE mode.

Usage:
    python3 scripts/idle_monitor.py --config config.yaml
    python3 scripts/idle_monitor.py --config config.yaml --account work --folder INBOX
    python3 scripts/idle_monitor.py --config config.yaml --timeout 60 --max-events 10
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient


_running = True


def _handle_signal(signum, frame):
    global _running
    _running = False


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor mailbox via IMAP IDLE")
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--account", default="", help="Account profile name")
    parser.add_argument("--folder", default="INBOX", help="Folder to monitor")
    parser.add_argument(
        "--timeout", type=int, default=29 * 60,
        help="IDLE timeout in seconds (default: 29 min per RFC 2177)",
    )
    parser.add_argument(
        "--poll-interval", type=float, default=30.0,
        help="Seconds between idle_check polls (default: 30)",
    )
    parser.add_argument(
        "--max-events", type=int, default=0,
        help="Stop after N new-mail events (0 = run forever)",
    )
    parser.add_argument("--format", choices=["json", "cli"], default="json")

    # Direct IMAP flags
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Build client
    client: IMAPClient | None = None
    acct_name = args.account

    if args.imap_host:
        client = IMAPClient(
            host=args.imap_host, port=args.imap_port,
            username=args.imap_user, password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
        acct_name = acct_name or "direct"
    elif args.config:
        try:
            mgr = AccountManager.from_yaml(args.config)
        except Exception as exc:
            _error(f"Failed to load config: {exc}")
            return
        acct_name = acct_name or mgr.default_account
        client = mgr.get_imap_client(acct_name)
    else:
        _error("Either --config or --imap-host is required.")
        return

    event_count = 0

    try:
        client.connect()
        _log(f"Connected to {client.host}, monitoring {args.folder}", args.format)

        while _running:
            try:
                client.idle_start(args.folder, timeout=args.timeout)
                _log("IDLE started, waiting for events...", args.format)

                idle_start = time.monotonic()
                while _running:
                    responses = client.idle_check(timeout=args.poll_interval)

                    new_exists = any(
                        resp == b"EXISTS" for _, resp in responses
                    )

                    if new_exists:
                        client.idle_done()
                        event_count += 1

                        # Fetch the newest unread messages
                        messages = client.fetch_unread(
                            mailbox=args.folder, limit=10,
                        )

                        event = {
                            "event": "new_mail",
                            "account": acct_name,
                            "folder": args.folder,
                            "event_number": event_count,
                            "new_messages": len(messages),
                            "messages": [
                                {
                                    "message_id": m.message_id,
                                    "subject": m.subject,
                                    "sender": str(m.sender) if m.sender else "",
                                    "date": m.date.isoformat() if m.date else "",
                                }
                                for m in messages
                            ],
                        }

                        if args.format == "cli":
                            print(f"\n--- New mail ({len(messages)} message(s)) ---")
                            for m in messages:
                                sender = str(m.sender) if m.sender else "(unknown)"
                                print(f"  From: {sender}")
                                print(f"  Subject: {m.subject}")
                                print()
                        else:
                            json.dump(event, sys.stdout)
                            print()
                            sys.stdout.flush()

                        if args.max_events and event_count >= args.max_events:
                            _log(f"Reached max events ({args.max_events})", args.format)
                            return

                        # Re-enter IDLE
                        break

                    # Re-issue IDLE every timeout seconds
                    elapsed = time.monotonic() - idle_start
                    if elapsed >= args.timeout - 60:
                        client.idle_done()
                        _log("Re-issuing IDLE (timeout approaching)", args.format)
                        break

            except (OSError, RuntimeError) as exc:
                _log(f"IDLE error: {exc}, reconnecting in 5s...", args.format)
                try:
                    client.disconnect()
                except Exception:
                    pass
                time.sleep(5)
                client.connect()

    except Exception as exc:
        _error(f"Fatal: {exc}")
    finally:
        _log("Stopping IDLE monitor", args.format)
        try:
            client.disconnect()
        except Exception:
            pass


def _log(msg: str, fmt: str) -> None:
    if fmt == "cli":
        print(f"[idle] {msg}", file=sys.stderr)
    else:
        json.dump({"log": msg}, sys.stderr)
        print(file=sys.stderr)


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
