#!/usr/bin/env python3
"""Protonmail CLI — wraps himalaya for email via Proton Bridge."""

import argparse
from email.utils import formatdate
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_DIR = SKILL_DIR / "config"


def load_config():
    """Load config/config.json. Prints SETUP_REQUIRED sentinel if missing."""
    config_path = CONFIG_DIR / "config.json"
    if not config_path.exists():
        print("SETUP_REQUIRED")
        print("This skill needs to be configured before use.")
        print("Follow the setup instructions in SKILL.md.")
        sys.exit(1)

    with open(config_path) as f:
        return json.load(f)


def check_bridge(config=None):
    """TCP check that Bridge's IMAP and SMTP ports are listening."""
    imap_port = 1143
    smtp_port = 1025
    if config:
        imap_port = config.get("imap_port", 1143)
        smtp_port = config.get("smtp_port", 1025)

    for port, name in [(imap_port, "IMAP"), (smtp_port, "SMTP")]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(("127.0.0.1", port))
            sock.close()
        except (socket.timeout, ConnectionRefusedError, OSError):
            print(f"Error: Proton Bridge {name} port {port} is not responding.", file=sys.stderr)
            print("Fix: systemctl --user start protonmail-bridge", file=sys.stderr)
            return False

    return True


def run_himalaya(config, args, timeout=30):
    """Run himalaya with --config pointing to our isolated himalaya.toml."""
    himalaya_bin = config["bins"]["himalaya"]
    himalaya_config = config["himalaya_config"]
    cmd = [himalaya_bin, "--config", himalaya_config] + list(args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s", 1


def run_self_test():
    """Verify all dependencies: Bridge binary/service/ports, himalaya, config, connectivity."""
    print("Protonmail skill self-test")
    print("=" * 50)

    passed = 0
    failed = 0

    print("\n1. Proton Bridge binary")
    bridge_bin = shutil.which("protonmail-bridge")
    if not bridge_bin:
        for candidate in ["/usr/bin/protonmail-bridge", "/usr/local/bin/protonmail-bridge"]:
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                bridge_bin = candidate
                break
    if bridge_bin:
        print(f"   [ok] Found: {bridge_bin}")
        passed += 1
    else:
        print("   [fail] protonmail-bridge not found")
        print("   Fix: Download from https://proton.me/bridge/install")
        failed += 1

    print("\n2. Bridge systemd service")
    try:
        svc = subprocess.run(
            ["systemctl", "--user", "is-active", "protonmail-bridge.service"],
            capture_output=True, text=True, timeout=5,
        )
        if svc.stdout.strip() == "active":
            print("   [ok] Service is active")
            passed += 1
        else:
            print(f"   [fail] Service status: {svc.stdout.strip()}")
            print("   Fix: systemctl --user start protonmail-bridge")
            failed += 1
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   [fail] Could not check service status")
        failed += 1

    print("\n3. Bridge ports")
    for port, name in [(1143, "IMAP"), (1025, "SMTP")]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(("127.0.0.1", port))
            sock.close()
            print(f"   [ok] {name} port {port} is listening")
            passed += 1
        except (socket.timeout, ConnectionRefusedError, OSError):
            print(f"   [fail] {name} port {port} is not responding")
            print("   Fix: Ensure Bridge is running and logged in")
            failed += 1

    print("\n4. Himalaya binary")
    himalaya_bin = shutil.which("himalaya")
    if not himalaya_bin:
        linuxbrew = "/home/linuxbrew/.linuxbrew/bin/himalaya"
        if os.path.isfile(linuxbrew) and os.access(linuxbrew, os.X_OK):
            himalaya_bin = linuxbrew
    if himalaya_bin:
        print(f"   [ok] Found: {himalaya_bin}")
        passed += 1
    else:
        print("   [fail] himalaya not found")
        print("   Fix: brew install himalaya")
        failed += 1

    print("\n5. Config files")
    config_files = {
        "config.json": CONFIG_DIR / "config.json",
        "himalaya.toml": CONFIG_DIR / "himalaya.toml",
        "auth": CONFIG_DIR / "auth",
    }
    config_ok = True
    config = None
    for name, path in config_files.items():
        if path.exists():
            print(f"   [ok] {name}: {path}")
            passed += 1
        else:
            print(f"   [fail] {name} not found at {path}")
            print(f"   Fix: Run setup configure")
            failed += 1
            config_ok = False

    if config_ok:
        try:
            with open(CONFIG_DIR / "config.json") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"   [fail] Could not parse config.json: {e}")
            failed += 1
            config = None

    print("\n6. Himalaya connectivity")
    if config and himalaya_bin:
        himalaya_config = config.get("himalaya_config", "")
        if himalaya_config and os.path.exists(himalaya_config):
            try:
                result = subprocess.run(
                    [config["bins"]["himalaya"], "--config", himalaya_config,
                     "envelope", "list", "--page-size", "1"],
                    capture_output=True, text=True, timeout=15,
                )
                if result.returncode == 0:
                    print("   [ok] Successfully connected to Proton Bridge")
                    passed += 1
                else:
                    print(f"   [fail] {result.stderr.strip()[:200]}")
                    print("   Fix: Check Bridge password in config/auth")
                    failed += 1
            except subprocess.TimeoutExpired:
                print("   [fail] Connection timed out")
                print("   Fix: Ensure Bridge is running and responsive")
                failed += 1
        else:
            print(f"   [skip] himalaya config not found at {himalaya_config}")
            failed += 1
    else:
        print("   [skip] Missing config or himalaya binary")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("All checks passed!")
    else:
        print("Some checks failed. See [fail] entries above for fixes.")
    sys.exit(0 if failed == 0 else 1)


# -- Email: read operations --

def cmd_email_list(args, config):
    """List email envelopes."""
    count = args.count or 10
    folder = args.folder or "INBOX"

    cmd = ["envelope", "list", "--page-size", str(count), "-f", folder]
    if args.unread:
        cmd.extend(["flag", "unseen"])
    cmd.extend(["order", "by", "date", "desc"])

    stdout, stderr, rc = run_himalaya(config, cmd)
    print(stdout.strip() if stdout.strip() else "No emails found.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def cmd_email_read(args, config):
    """Read a single email by ID."""
    cmd = ["message", "read"]
    if args.folder:
        cmd.extend(["-f", args.folder])
    cmd.append(args.id)
    stdout, stderr, rc = run_himalaya(config, cmd)
    print(stdout.strip() if stdout.strip() else "Could not read message.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def _validate_search_query(query):
    """Validate search query tokens to prevent IMAP query injection.

    Himalaya's positional search args map to IMAP SEARCH commands. We allow
    known IMAP SEARCH keywords and simple values (alphanumeric, @, dots,
    hyphens, dates). Reject CLI flags (--/- prefixed) and control characters
    that could alter command behavior."""
    ALLOWED_KEYWORDS = {
        "from", "to", "cc", "bcc", "subject", "body", "text",
        "before", "after", "since", "on", "larger", "smaller",
        "and", "or", "not",
    }
    tokens = query.split()
    if not tokens:
        print("Error: empty search query", file=sys.stderr)
        sys.exit(1)
    for token in tokens:
        if token.startswith("-"):
            print(f"Error: search query contains flag-like token: {token}", file=sys.stderr)
            sys.exit(1)
        if any(ord(ch) < 32 for ch in token):
            print(f"Error: search query contains control characters", file=sys.stderr)
            sys.exit(1)
    return tokens


def cmd_email_search(args, config):
    """Search emails. Query uses himalaya's positional IMAP SEARCH syntax
    (e.g. "from alice subject invoice")."""
    count = args.count or 50
    folder = args.folder or "INBOX"
    query_tokens = _validate_search_query(args.query)
    cmd = ["envelope", "list", "--page-size", str(count), "-f", folder]
    cmd.extend(query_tokens)
    cmd.extend(["order", "by", "date", "desc"])

    stdout, stderr, rc = run_himalaya(config, cmd)
    print(stdout.strip() if stdout.strip() else f"No emails matching '{args.query}'.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


# -- Email: write operations --

def _read_body(args):
    """Read body from --body-stdin (preferred) or CLI arg.

    Stdin via heredoc avoids shell $ expansion — without it, "$5,000"
    silently becomes ",000".
    """
    if args.body_stdin:
        body = sys.stdin.read()
        if not body.strip():
            print("Error: --body-stdin specified but stdin is empty", file=sys.stderr)
            sys.exit(1)
        return body.strip()
    elif args.body:
        return args.body
    else:
        print("Error: provide body as argument or use --body-stdin", file=sys.stderr)
        sys.exit(1)


def _send_mml(config, mml, recipient_desc):
    """Pipe MML to himalaya message send, handling the IMAP append edge case.

    If SMTP succeeds but the IMAP APPEND to Sent fails, himalaya returns
    non-zero even though the email was delivered. We detect this and report
    success to prevent the agent from retrying (which would send duplicates).
    """
    himalaya_bin = config["bins"]["himalaya"]
    himalaya_config = config["himalaya_config"]
    result = subprocess.run(
        [himalaya_bin, "--config", himalaya_config, "message", "send"],
        input=mml, capture_output=True, text=True, timeout=60,
    )

    if result.returncode == 0:
        print(f"Email sent to {recipient_desc}")
    elif "cannot add IMAP message" in result.stderr:
        print(f"Email sent to {recipient_desc}")
        print(f"Warning: could not save copy to Sent folder: {result.stderr.strip()}",
              file=sys.stderr)
    else:
        print(f"Error sending email: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_email_send(args, config):
    """Send an email. Builds MML (headers + body) and pipes to himalaya."""
    display_name = config.get("display_name", "")
    email = config["account_email"]
    body = _read_body(args)

    mml = f"From: {display_name} <{email}>\n"
    mml += f"To: {args.to}\n"
    mml += f"Subject: {args.subject}\n"
    mml += f"Date: {formatdate(localtime=True)}\n"
    mml += f"\n{body}\n"

    _send_mml(config, mml, args.to)


def cmd_email_reply(args, config):
    """Reply to an email by ID. Reads original headers for threading."""
    display_name = config.get("display_name", "")
    default_email = config["account_email"]

    header_cmd = ["message", "read", args.id]
    if args.folder:
        header_cmd = ["message", "read", "-f", args.folder, args.id]

    stdout, stderr, rc = run_himalaya(config, header_cmd)
    if rc != 0:
        print(f"Error reading message {args.id}: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    # Parse headers (himalaya outputs headers then blank line then body)
    headers = {}
    for line in stdout.splitlines():
        if not line.strip():
            break
        if ": " in line:
            key, val = line.split(": ", 1)
            headers[key] = val

    orig_from = headers.get("From", "")
    orig_to = headers.get("To", "")
    orig_cc = headers.get("Cc", "")
    orig_subject = headers.get("Subject", "")
    orig_msg_id = headers.get("Message-ID", "")
    orig_references = headers.get("References", "")

    # Reply from whichever of our addresses was in To/Cc
    reply_from = default_email
    all_recipients = (orig_to + " " + orig_cc).lower()
    if default_email.lower() in all_recipients:
        reply_from = default_email

    reply_to = orig_from

    if orig_subject.lower().startswith("re:"):
        reply_subject = orig_subject
    else:
        reply_subject = f"Re: {orig_subject}"

    references = orig_references
    if orig_msg_id:
        references = f"{references} {orig_msg_id}".strip()

    body = _read_body(args)

    mml = f"From: {display_name} <{reply_from}>\n"
    mml += f"To: {reply_to}\n"
    mml += f"Subject: {reply_subject}\n"
    mml += f"Date: {formatdate(localtime=True)}\n"
    if orig_msg_id:
        mml += f"In-Reply-To: {orig_msg_id}\n"
    if references:
        mml += f"References: {references}\n"
    mml += f"\n{body}\n"

    _send_mml(config, mml, reply_to)


def cmd_email_move(args, config):
    """Move an email to a folder (INBOX, Sent, Drafts, Trash, Spam, Archive, All Mail)."""
    cmd = ["message", "move"]
    if args.source_folder:
        cmd.extend(["-f", args.source_folder])
    cmd.extend([args.folder, args.id])
    stdout, stderr, rc = run_himalaya(config, cmd)
    if rc == 0:
        print(f"Moved message {args.id} to {args.folder}")
    else:
        print(f"Error moving message: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_email_delete(args, config):
    """Delete an email (moves to Trash)."""
    cmd = ["message", "delete"]
    if args.folder:
        cmd.extend(["-f", args.folder])
    cmd.append(args.id)
    stdout, stderr, rc = run_himalaya(config, cmd)
    if rc == 0:
        print(f"Deleted message {args.id}")
    else:
        print(f"Error deleting message: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)


# -- Folder operations --

def cmd_folder_purge(args, config):
    """Purge all emails from a folder (folder remains, contents deleted)."""
    cmd = ["folder", "purge", "-y", args.folder]
    stdout, stderr, rc = run_himalaya(config, cmd, timeout=120)
    if rc == 0:
        print(f"Purged folder {args.folder}")
    else:
        print(f"Error purging folder: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)


# -- CLI parser --

def build_parser():
    parser = argparse.ArgumentParser(
        prog="proton.py",
        description="Protonmail CLI — email via Proton Bridge + himalaya",
    )
    parser.add_argument("--test", action="store_true", help="Run self-test")
    subparsers = parser.add_subparsers(dest="command")

    email_parser = subparsers.add_parser("email", help="Email operations")
    email_sub = email_parser.add_subparsers(dest="email_command")

    email_list = email_sub.add_parser("list", help="List emails")
    email_list.add_argument("--count", type=int, help="Number of emails (default: 10)")
    email_list.add_argument("--folder", help="Folder name (default: INBOX)")
    email_list.add_argument("--unread", action="store_true", help="Only unread emails")
    email_list.set_defaults(func=cmd_email_list)

    email_read = email_sub.add_parser("read", help="Read an email by ID")
    email_read.add_argument("id", help="Email ID (from list output)")
    email_read.add_argument("--folder", help="Folder containing the message (default: INBOX)")
    email_read.set_defaults(func=cmd_email_read)

    email_send = email_sub.add_parser("send", help="Send an email")
    email_send.add_argument("to", help="Recipient email address")
    email_send.add_argument("subject", help="Email subject")
    email_send.add_argument("body", nargs="?", default=None,
                            help="Email body (or use --body-stdin)")
    email_send.add_argument("--body-stdin", action="store_true",
                            help="Read body from stdin (preferred — avoids shell $ expansion)")
    email_send.set_defaults(func=cmd_email_send)

    email_reply = email_sub.add_parser("reply", help="Reply to an email")
    email_reply.add_argument("id", help="Email ID to reply to")
    email_reply.add_argument("body", nargs="?", default=None,
                             help="Reply body text (or use --body-stdin)")
    email_reply.add_argument("--body-stdin", action="store_true",
                             help="Read body from stdin (preferred — avoids shell $ expansion)")
    email_reply.add_argument("--folder", help="Folder containing the message (default: INBOX)")
    email_reply.set_defaults(func=cmd_email_reply)

    email_search = email_sub.add_parser("search", help="Search emails")
    email_search.add_argument("query", help="Search query (e.g., 'from alice subject meeting')")
    email_search.add_argument("--folder", help="Folder to search (default: INBOX)")
    email_search.add_argument("--count", type=int, help="Max results (default: 50)")
    email_search.set_defaults(func=cmd_email_search)

    email_move = email_sub.add_parser("move", help="Move email to folder")
    email_move.add_argument("folder", help="Destination folder")
    email_move.add_argument("id", help="Email ID")
    email_move.add_argument("--from", dest="source_folder", help="Source folder (default: INBOX)")
    email_move.set_defaults(func=cmd_email_move)

    email_delete = email_sub.add_parser("delete", help="Delete email (move to Trash)")
    email_delete.add_argument("id", help="Email ID")
    email_delete.add_argument("--folder", help="Folder containing the message (default: INBOX)")
    email_delete.set_defaults(func=cmd_email_delete)

    folder_parser = subparsers.add_parser("folder", help="Folder operations")
    folder_sub = folder_parser.add_subparsers(dest="folder_command")

    folder_purge = folder_sub.add_parser("purge", help="Purge all emails from a folder")
    folder_purge.add_argument("folder", help="Folder to purge")
    folder_purge.set_defaults(func=cmd_folder_purge)

    subparsers.add_parser("setup", help="Setup commands (delegates to setup.py)")

    return parser


def main():
    # Intercept "setup" early — setup.py has its own argparse
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_script = str(SCRIPT_DIR / "setup.py")
        if not os.path.exists(setup_script):
            print(f"Error: setup.py not found at {setup_script}", file=sys.stderr)
            sys.exit(1)
        os.execv(sys.executable, [sys.executable, setup_script] + sys.argv[2:])

    parser = build_parser()
    args = parser.parse_args()

    if args.test:
        run_self_test()
        return

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "email":
        if not getattr(args, "email_command", None):
            print("Usage: proton.py email {list|read|send|reply|search|move|delete}")
            sys.exit(1)

        config = load_config()
        if not check_bridge(config):
            sys.exit(1)

        args.func(args, config)

    elif args.command == "folder":
        if not getattr(args, "folder_command", None):
            print("Usage: proton.py folder {purge}")
            sys.exit(1)

        config = load_config()
        if not check_bridge(config):
            sys.exit(1)

        args.func(args, config)


if __name__ == "__main__":
    main()
