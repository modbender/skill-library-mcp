#!/usr/bin/env python3
"""Fetches Schlagzeilen von https://www.tageblatt.de/ und speichert sie lokal.

Der Parser ist bewusst simpel gehalten: Er sucht nach <h2 class="article-heading">…</h2>
Blöcken, entfernt HTML-Tags und gibt die gefundenen Überschriften (einmalig) aus.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from typing import List
from urllib import request

DEFAULT_URL = "https://www.tageblatt.de/"
HEADING_PATTERN = re.compile(r'<h2 class="article-heading">(.*?)</h2>', re.DOTALL)


def fetch_html(url: str, timeout: int) -> str:
    with request.urlopen(url, timeout=timeout) as response:  # noqa: S310 (trusted URL)
        return response.read().decode("utf-8", errors="ignore")


def extract_headlines(raw_html: str, limit: int | None = None) -> List[str]:
    headlines: List[str] = []
    for block in HEADING_PATTERN.findall(raw_html):
        text = re.sub(r"<[^>]+>", " ", block)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        text = re.sub(r"^T\s+", "", text)  # Entferne "T" vom Plus-Icon
        if text and text not in headlines:
            headlines.append(text)
        if limit and len(headlines) >= limit:
            break
    return headlines


def write_output(headlines: List[str], output: Path, fmt: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        payload = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": DEFAULT_URL,
            "headlines": headlines,
        }
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [f"TAGEBLATT Schlagzeilen ({timestamp})", "=" * 40]
        for idx, title in enumerate(headlines, start=1):
            lines.append(f"{idx}. {title}")
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download TAGEBLATT-Schlagzeilen")
    parser.add_argument("--url", default=DEFAULT_URL, help="Ziel-URL (Standard: %(default)s)")
    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="Maximale Anzahl Schlagzeilen (Standard: %(default)s)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Timeout für HTTP-Request in Sekunden (Standard: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default="output/tageblatt_headlines.txt",
        help="Pfad für Ausgabe-Datei (Standard: %(default)s)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Ausgabeformat (Standard: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        html_content = fetch_html(args.url, args.timeout)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Konnte {args.url} nicht abrufen: {exc}", file=sys.stderr)
        sys.exit(1)

    headlines = extract_headlines(html_content, args.limit)
    if not headlines:
        print("WARNUNG: Keine Schlagzeilen gefunden", file=sys.stderr)

    try:
        write_output(headlines, Path(args.output), args.format)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Konnte Ausgabe nicht schreiben: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(headlines, ensure_ascii=False, indent=2))
    else:
        for line in headlines:
            print(line)


if __name__ == "__main__":
    main()
