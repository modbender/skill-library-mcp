#!/usr/bin/env python3
"""AgenticLetters CLI — send physical letters via the AgenticLetters API.

Designed as an OpenClaw agent skill tool. All errors go to stderr with
structured context so the calling AI can distinguish local from server errors.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import NoReturn


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = "https://agentic-letters.com/api"
ENV_FILE = os.path.expanduser("~/.openclaw/secrets/agentic_letters.env")
ENV_VAR = "AGENTIC_LETTERS_API_KEY"
RECORDS_DIR = os.path.expanduser("~/.openclaw/workspace/skills/agentic-letters/records")


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class ErrorOrigin(Enum):
    LOCAL = "local"
    SERVER = "server"
    NETWORK = "network"


@dataclass
class CLIError:
    origin: ErrorOrigin
    message: str
    code: str | None = None
    detail: str | None = None
    field: str | None = None
    http_status: int | None = None

    def format(self) -> str:
        parts = [f"[{self.origin.value}] {self.message}"]
        if self.code:
            parts.append(f"  code: {self.code}")
        if self.http_status:
            parts.append(f"  http_status: {self.http_status}")
        if self.detail:
            parts.append(f"  detail: {self.detail}")
        if self.field:
            parts.append(f"  field: {self.field}")
        return "\n".join(parts)


def die(err: CLIError) -> NoReturn:
    print(err.format(), file=sys.stderr)
    sys.exit(1)


def die_local(message: str, *, detail: str | None = None) -> NoReturn:
    die(CLIError(origin=ErrorOrigin.LOCAL, message=message, detail=detail))


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------

class AgenticLettersClient:
    """Thin HTTP client for the AgenticLetters API (stdlib only)."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": "agentic-letters-skill/1.0",
        }

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{API_BASE}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read())
            except Exception:
                die(CLIError(
                    origin=ErrorOrigin.SERVER,
                    message=f"HTTP {e.code} with non-JSON response",
                    http_status=e.code,
                    detail=str(e.reason),
                ))
            die(CLIError(
                origin=ErrorOrigin.SERVER,
                message=error_body.get("error", f"HTTP {e.code}"),
                code=error_body.get("code"),
                http_status=e.code,
                detail=error_body.get("detail"),
                field=error_body.get("field"),
            ))
        except urllib.error.URLError as e:
            die(CLIError(
                origin=ErrorOrigin.NETWORK,
                message="Could not reach the API",
                detail=str(e.reason),
            ))
        except TimeoutError:
            die(CLIError(
                origin=ErrorOrigin.NETWORK,
                message="Request timed out after 60 seconds",
            ))

    # -- Public methods --

    def send_letter(
        self,
        pdf_path: str,
        name: str,
        street: str,
        zip_code: str,
        city: str,
        *,
        country: str = "DE",
        letter_type: str = "standard",
        label: str | None = None,
    ) -> dict:
        path = Path(pdf_path)
        if not path.exists():
            die_local(f"File not found: {pdf_path}")
        if not path.is_file():
            die_local(f"Not a file: {pdf_path}")

        try:
            pdf_bytes = path.read_bytes()
        except PermissionError:
            die_local(f"Permission denied: {pdf_path}")
        except OSError as e:
            die_local(f"Cannot read file: {pdf_path}", detail=str(e))

        pdf_b64 = base64.b64encode(pdf_bytes).decode()

        payload: dict = {
            "pdf": pdf_b64,
            "recipient": {
                "name": name,
                "street": street,
                "zip": zip_code,
                "city": city,
                "country": country,
            },
            "type": letter_type,
        }
        if label:
            payload["label"] = label

        return self._request("POST", "/letters", payload)

    def get_letter(self, letter_id: str) -> dict:
        return self._request("GET", f"/letters/{letter_id}")

    def list_letters(self) -> dict:
        return self._request("GET", "/letters")

    def get_credits(self) -> dict:
        return self._request("GET", "/credits")


# ---------------------------------------------------------------------------
# Local letter records
# ---------------------------------------------------------------------------

def _ensure_records_dir() -> Path:
    p = Path(RECORDS_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_record(send_result: dict, recipient: dict, label: str | None) -> Path:
    """Save a letter record after successful send."""
    records = _ensure_records_dir()
    letter_id = send_result["id"]
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    record = {
        "id": letter_id,
        "status": send_result.get("status", "queued"),
        "type": send_result.get("type", "standard"),
        "label": label,
        "recipient": recipient,
        "created_at": send_result.get("created_at", datetime.now(timezone.utc).isoformat()),
        "credits_remaining": send_result.get("credits_remaining"),
        "last_checked": None,
    }
    path = records / f"{date}_{letter_id[:8]}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    return path


def update_record_status(letter_id: str, status_result: dict) -> None:
    """Update an existing record with fresh status from the API."""
    records = _ensure_records_dir()
    # Find record by ID prefix
    for f in sorted(records.iterdir(), reverse=True):
        if not f.name.endswith(".json"):
            continue
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if data.get("id", "").startswith(letter_id) or letter_id.startswith(data.get("id", "")[:8]):
            data["status"] = status_result.get("status", data["status"])
            data["last_checked"] = datetime.now(timezone.utc).isoformat()
            f.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            return


# ---------------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    """Load API key from environment or secrets file."""
    key = os.environ.get(ENV_VAR)
    if key:
        return key.strip()

    env_path = Path(ENV_FILE)
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith(f"{ENV_VAR}="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val

    die_local(
        "No API key found",
        detail=f"Set {ENV_VAR} in environment or in {ENV_FILE}. Get a key at https://agentic-letters.com/buy",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic_letters",
        description="Send physical letters via the AgenticLetters API.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # send
    send_p = sub.add_parser("send", help="Send a letter")
    send_p.add_argument("--pdf", required=True, help="Path to the PDF file")
    send_p.add_argument("--name", required=True, help="Recipient full name")
    send_p.add_argument("--street", required=True, help="Recipient street + number")
    send_p.add_argument("--zip", required=True, help="Recipient postal code (5-digit German PLZ)")
    send_p.add_argument("--city", required=True, help="Recipient city")
    send_p.add_argument("--country", default="DE", help="Recipient country code (default: DE)")
    send_p.add_argument("--type", default="standard", dest="letter_type", help="Letter type (default: standard)")
    send_p.add_argument("--label", help="Optional label for your reference")

    # status
    status_p = sub.add_parser("status", help="Check letter status")
    status_p.add_argument("id", help="Letter UUID")

    # list
    sub.add_parser("list", help="List all letters")

    # credits
    sub.add_parser("credits", help="Check remaining credits")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    api_key = load_api_key()
    client = AgenticLettersClient(api_key)

    if args.command == "send":
        result = client.send_letter(
            pdf_path=args.pdf,
            name=args.name,
            street=args.street,
            zip_code=args.zip,
            city=args.city,
            country=args.country,
            letter_type=args.letter_type,
            label=args.label,
        )
        # Save local record
        recipient = {
            "name": args.name,
            "street": args.street,
            "zip": args.zip,
            "city": args.city,
            "country": args.country,
        }
        save_record(result, recipient, args.label)
    elif args.command == "status":
        result = client.get_letter(args.id)
        update_record_status(args.id, result)
    elif args.command == "list":
        result = client.list_letters()
    elif args.command == "credits":
        result = client.get_credits()
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
