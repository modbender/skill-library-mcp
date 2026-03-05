#!/usr/bin/env python3
"""Redact an OpenClaw config file for safe sharing.

OpenClaw config (`~/.openclaw/openclaw.json`) is JSON5 (comments + trailing commas
allowed). This script tries to parse JSON5 when possible, but it also has a
best-effort text fallback so it can still help even if JSON5 parsing isn't
available.

Redaction rules (best-effort):
- Any key containing token/password/secret/key/etc. (case-insensitive) is masked.
- Any string value that looks like a long secret is partially masked.
- Query-string secrets in URLs are masked (e.g. ?token=...).

Usage:
  python3 scripts/redact_openclaw_config.py ~/.openclaw/openclaw.json > openclaw.json5.redacted

Notes:
- The JSON output (when parsing succeeds) is regular JSON (not JSON5) to make it
  easy to share and read.
- Always review the output before sharing.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any, Callable, Optional

SENSITIVE_KEY_RE = re.compile(
    r"(token|password|secret|apikey|api_key|clientsecret|privatekey|private_key|key)\b",
    re.IGNORECASE,
)

# crude heuristic for "likely secret" strings (tokens, keys, hashes)
LIKELY_SECRET_RE = re.compile(r"^[A-Za-z0-9_\-]{24,}$")

# URL query-string secret patterns
URL_QS_SECRET_RE = re.compile(
    r"(?P<prefix>[?&](?:token|password|apikey|api_key|key)=)(?P<val>[^&\s#]+)",
    re.IGNORECASE,
)


def mask(s: str) -> str:
    if len(s) <= 8:
        return "***"
    return s[:4] + "…" + s[-4:]


def redact_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if SENSITIVE_KEY_RE.search(str(k)):
                if isinstance(v, str):
                    out[str(k)] = mask(v)
                else:
                    out[str(k)] = "***"
            else:
                out[str(k)] = redact_obj(v)
        return out
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj]
    if isinstance(obj, str):
        s = obj
        if LIKELY_SECRET_RE.match(s):
            return mask(s)
        # redact common URL query-string secrets
        s = URL_QS_SECRET_RE.sub(lambda m: m.group("prefix") + mask(m.group("val")), s)
        return s
    return obj


def try_json5_parser() -> Optional[Callable[[str], Any]]:
    """Return a loads(text) function if json5 parsing is available."""
    try:
        import json5  # type: ignore

        return json5.loads  # type: ignore
    except Exception:
        return None


def text_fallback_redact(raw: str) -> str:
    """Heuristic redaction for JSON5-like text.

    This does not guarantee valid JSON/JSON5 output. It's designed for human
    review/sharing when parsing isn't possible.
    """

    # Redact URL query-string secrets first
    redacted = URL_QS_SECRET_RE.sub(lambda m: m.group("prefix") + mask(m.group("val")), raw)

    # Redact key: "value" and key: 'value' patterns
    # Example: token: "abc"  OR  password: 'abc'
    key_val_re = re.compile(
        r"(?P<key>\b\w*(?:token|password|secret|apikey|api_key|clientsecret|privatekey|private_key|key)\w*\b)"
        r"(?P<ws>\s*:\s*)"
        r"(?P<val>(?:\"[^\"]*\"|'[^']*'))",
        re.IGNORECASE,
    )

    def repl_kv(m: re.Match[str]) -> str:
        key = m.group("key")
        ws = m.group("ws")
        val = m.group("val")
        # keep quote type
        if val.startswith('"'):
            inner = val[1:-1]
            masked = mask(inner)
            return f"{key}{ws}\"{masked}\""
        if val.startswith("'"):
            inner = val[1:-1]
            masked = mask(inner)
            return f"{key}{ws}'{masked}'"
        return f"{key}{ws}***"

    redacted = key_val_re.sub(repl_kv, redacted)

    # Redact bare long secrets assigned to known keys (token: abcdef...)
    bare_re = re.compile(
        r"(?P<key>\b\w*(?:token|password|secret|apikey|api_key|clientsecret|privatekey|private_key|key)\w*\b)"
        r"(?P<ws>\s*:\s*)"
        r"(?P<val>[A-Za-z0-9_\-]{24,})",
        re.IGNORECASE,
    )
    redacted = bare_re.sub(lambda m: m.group("key") + m.group("ws") + mask(m.group("val")), redacted)

    return redacted


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: redact_openclaw_config.py <path-to-openclaw.json>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    raw = open(path, "r", encoding="utf-8", errors="replace").read()

    # Try strict JSON first
    obj: Any
    parsed: bool = False
    try:
        obj = json.loads(raw)
        parsed = True
    except Exception:
        obj = None

    if not parsed:
        json5_loads = try_json5_parser()
        if json5_loads is not None:
            try:
                obj = json5_loads(raw)
                parsed = True
            except Exception:
                parsed = False

    if parsed:
        redacted_obj = redact_obj(obj)
        json.dump(redacted_obj, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        # Best-effort textual redaction
        sys.stdout.write(text_fallback_redact(raw))
        if not raw.endswith("\n"):
            sys.stdout.write("\n")


if __name__ == "__main__":
    main()
