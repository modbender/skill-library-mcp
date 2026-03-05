#!/usr/bin/env python3
"""Parse showing intake text into normalized JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PHONE_RE = re.compile(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LISTING_RE = re.compile(r"(?:mls|listing)\s*#?:?\s*([A-Za-z0-9-]+)", re.IGNORECASE)


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return f"+1{digits}" if len(digits) == 10 else raw.strip()


def parse_listings(text: str) -> list[dict]:
    listings = []
    for line in text.splitlines():
        raw = line.strip()
        stripped = line.strip(" -\t")
        if not stripped:
            continue
        is_listing_hint = raw.startswith("-") or "mls" in stripped.lower() or "office phone" in stripped.lower()
        if not is_listing_hint:
            continue
        phone_match = PHONE_RE.search(stripped)
        listing_match = LISTING_RE.search(stripped)
        listings.append(
            {
                "raw_line": stripped,
                "address": stripped.split("|")[0].strip() if "|" in stripped else stripped,
                "listing_id": listing_match.group(1) if listing_match else None,
                "office_phone": normalize_phone(phone_match.group(0)) if phone_match else None,
            }
        )
    return listings


def parse_request(text: str) -> dict:
    client_match = re.search(r"(?:client|buyer)\s*:\s*(.+)", text, re.IGNORECASE)
    timezone_match = re.search(r"(?:timezone|tz)\s*:\s*([A-Za-z0-9_/\-+]+)", text, re.IGNORECASE)

    return {
        "client_name": client_match.group(1).strip() if client_match else "Unknown Client",
        "timezone": timezone_match.group(1).strip() if timezone_match else "America/Toronto",
        "preferred_windows_text": text,
        "listings": parse_listings(text),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse showing intake into normalized JSON.")
    parser.add_argument("--input-file", help="Path to raw intake text file.")
    parser.add_argument("--input-text", help="Inline intake text.")
    parser.add_argument("--output", required=True, help="Output JSON path.")
    args = parser.parse_args()

    if not args.input_file and not args.input_text:
        raise SystemExit("Provide --input-file or --input-text.")

    if args.input_file:
        text = Path(args.input_file).read_text()
    else:
        text = args.input_text or ""

    result = parse_request(text)
    out = Path(args.output)
    out.write_text(json.dumps(result, indent=2))
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
