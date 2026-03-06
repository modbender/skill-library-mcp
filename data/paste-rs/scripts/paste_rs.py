#!/usr/bin/env python3
"""Upload text/markdown/html to https://paste.rs and print the resulting URL.

Usage examples:
  echo "hello" | ./paste_rs.py
  ./paste_rs.py --text "# Title\ncontent"
  ./paste_rs.py --file README.md

Notes:
- paste.rs stores raw text; markdown/html are treated as plain text.
- On success, paste.rs returns the URL in the response body.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PASTE_URL = "https://paste.rs"


def redact(text: str) -> str:
    """Best-effort redaction for common secret patterns.

    Goal: avoid accidentally pasting tokens/keys/passwords from logs/config.
    This is heuristic and not perfect.
    """

    # JSON/YAML-ish key-value secrets (quoted)
    quoted_keys = [
        "botToken",
        "apiKey",
        "token",
        "access_token",
        "refresh_token",
        "password",
    ]

    for key in quoted_keys:
        text = re.sub(
            rf"({re.escape(key)}\"?\s*[:=]\s*\")([^\"]+)(\")",
            r"\1[REDACTED]\3",
            text,
        )

    # Unquoted values (YAML)
    text = re.sub(
        r"(?im)^(\s*(?:botToken|apiKey|token|access_token|refresh_token|password)\s*[:=]\s*)(.+)$",
        r"\1[REDACTED]",
        text,
    )

    # Authorization headers / bearer tokens
    text = re.sub(
        r"(?im)^(\s*authorization\s*:\s*)(bearer\s+)?(.+)$",
        r"\1\2[REDACTED]",
        text,
    )

    # Telegram bot token pattern: 9-12 digits:AA... (common)
    text = re.sub(r"\b\d{6,12}:[A-Za-z0-9_-]{20,}\b", "[REDACTED_TELEGRAM_BOT_TOKEN]", text)

    # Generic long tokens (very heuristic): long base64/url-safe strings
    text = re.sub(r"\b[A-Za-z0-9_-]{32,}\b", "[REDACTED_TOKEN]", text)

    return text


def _read_all_stdin() -> str:
    data = sys.stdin.buffer.read()
    return data.decode("utf-8", errors="replace")


def _write_markdown_file(text: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"paste-rs-{ts}.md"
    path.write_text(text, encoding="utf-8", errors="replace")
    return path


def upload(text: str, timeout: int = 30, out_dir: str | None = None) -> tuple[str, Path]:
    """Write to a local .md file first, then upload its contents to paste.rs.

    Returns: (url, saved_path)
    """
    if not text:
        raise ValueError("Refusing to upload empty content")

    saved_path = _write_markdown_file(text, Path(out_dir or "/tmp"))

    req = urllib.request.Request(
        PASTE_URL,
        data=saved_path.read_bytes(),
        method="POST",
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": "openclaw-paste-rs-skill/1.1",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace").strip()

    if not body.startswith("http"):
        raise RuntimeError(f"Unexpected response from paste.rs: {body!r}")

    # Make the URL reflect markdown extension for convenience.
    # paste.rs serves the same content for /id and /id.md.
    url = body
    if not re.search(r"\.[A-Za-z0-9]+$", url):
        url = url + ".md"

    return url, saved_path


def main() -> int:
    p = argparse.ArgumentParser(description="Paste text to paste.rs and print URL")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--text", help="Text to paste (UTF-8)")
    g.add_argument("--file", help="Path to file to paste")
    p.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds")
    p.add_argument(
        "--outdir",
        default="/tmp",
        help="Directory to save the .md file before uploading (default: /tmp)",
    )
    p.add_argument(
        "--no-redact",
        action="store_true",
        help="Disable redaction (NOT recommended; content may contain secrets)",
    )
    args = p.parse_args()

    if args.text is not None:
        text = args.text
    elif args.file is not None:
        with open(args.file, "rb") as f:
            text = f.read().decode("utf-8", errors="replace")
    else:
        if sys.stdin.isatty():
            p.error("Provide --text, --file, or pipe stdin")
        text = _read_all_stdin()

    if not args.no_redact:
        text = redact(text)

    url, saved_path = upload(text, timeout=args.timeout, out_dir=args.outdir)
    sys.stdout.write(url + "\n")
    # Helpful for auditing/debugging; goes to stderr so URL stays machine-friendly.
    sys.stderr.write(f"saved: {saved_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
