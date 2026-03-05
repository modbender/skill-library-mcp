#!/usr/bin/env python3
"""
outgoing-message-filter: Filter outgoing messages for sensitive information.

Usage:
  filter_message.py --message "text" [--channel CHANNEL_ID] [--config PATH]
  echo "text" | filter_message.py [--channel CHANNEL_ID] [--config PATH]

Output (JSON):
  {
    "blocked": false,
    "message": "filtered text or original",
    "detections": [{"name": "...", "action": "mask|block|warn", "snippet": "..."}],
    "warnings": ["..."]
  }

Exit codes:
  0 - OK (send the 'message' field)
  1 - BLOCKED (do not send, see 'detections' for reason)
  2 - Error (see stderr)
"""

import argparse
import json
import re
import sys
import os
import datetime
from pathlib import Path

# ── Default configuration ──────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "mode": "mask",           # global default action: mask | block | warn
    "mask_char": "*",
    "show_prefix": 3,         # reveal first N chars of matched value
    "show_suffix": 0,         # reveal last N chars of matched value
    "log_detections": False,
    "log_path": "~/.openclaw/outgoing-filter.jsonl",
    "allow_channels": [],     # channel IDs exempt from filtering
    "allow_patterns": [],     # regex patterns; matching messages are passed through
    "patterns": []            # user-defined patterns (merged with built-ins below)
}

# ── Built-in patterns ──────────────────────────────────────────────────────────

BUILTIN_PATTERNS = [
    {
        "name": "private_key_block",
        "regex": r"-----BEGIN\s+(?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----",
        "action": "block",
        "description": "PEM private key header"
    },
    {
        "name": "aws_access_key",
        "regex": r"\b(AKIA[0-9A-Z]{16})\b",
        "action": "block",
        "description": "AWS access key ID"
    },
    {
        "name": "aws_secret_key",
        "regex": r"(?i)aws[_\-\s]?secret[_\-\s]?(?:access[_\-\s]?)?key\s*[=:\"'`\s]\s*([A-Za-z0-9/+=]{40})\b",
        "capture_group": 1,
        "action": "block",
        "description": "AWS secret access key"
    },
    {
        "name": "jwt_token",
        "regex": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "action": "block",
        "description": "JSON Web Token (JWT)"
    },
    {
        "name": "generic_api_key",
        "regex": r"(?i)(?:api[_\-]?key|apikey|api[_\-]?secret|app[_\-]?secret|client[_\-]?secret)\s*[=:\"'`\s]\s*([A-Za-z0-9_\-]{20,})",
        "capture_group": 1,
        "action": "mask",
        "description": "Generic API key / secret"
    },
    {
        "name": "bearer_token",
        "regex": r"(?i)bearer\s+([A-Za-z0-9_\-\.~+/]{20,})",
        "capture_group": 1,
        "action": "mask",
        "description": "HTTP Bearer token"
    },
    {
        "name": "password_assignment",
        "regex": r"(?i)(?:password|passwd|pass|pwd)\s*[=:\"'`\s]\s*(\S{6,})",
        "capture_group": 1,
        "action": "mask",
        "description": "Password in key=value form"
    },
    {
        "name": "database_url",
        "regex": r"(?i)(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql|oracle)\://[^:@\s]+:([^@\s]+)@",
        "capture_group": 1,
        "action": "mask",
        "description": "Database connection string password"
    },
    {
        "name": "github_token",
        "regex": r"\b(gh[pousr]_[A-Za-z0-9_]{36,})\b",
        "action": "block",
        "description": "GitHub personal/OAuth/app token"
    },
    {
        "name": "slack_token",
        "regex": r"\b(xox[baprs]-[0-9A-Za-z\-]{10,})\b",
        "action": "block",
        "description": "Slack API token"
    },
    {
        "name": "stripe_key",
        "regex": r"\b(sk_(?:live|test)_[0-9a-zA-Z]{24,})\b",
        "action": "block",
        "description": "Stripe secret key"
    },
    {
        "name": "credit_card",
        "regex": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b",
        "action": "mask",
        "description": "Credit card number (Visa/MC/Amex/Discover)"
    },
    {
        "name": "ssn_us",
        "regex": r"\b\d{3}-\d{2}-\d{4}\b",
        "action": "block",
        "description": "US Social Security Number"
    },
    {
        "name": "private_ip_range",
        "regex": r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})\b",
        "action": "warn",
        "description": "Private IP address (RFC1918)"
    },
    {
        "name": "env_file_line",
        "regex": r"(?m)^[A-Z_]{3,}=[^\s]{8,}$",
        "action": "mask",
        "description": ".env file variable assignment"
    },
    {
        "name": "sendgrid_key",
        "regex": r"\bSG\.[A-Za-z0-9_\-]{22,}\.[A-Za-z0-9_\-]{43,}\b",
        "action": "block",
        "description": "SendGrid API key"
    },
    {
        "name": "twilio_token",
        "regex": r"\b(SK[0-9a-fA-F]{32})\b",
        "action": "block",
        "description": "Twilio auth token"
    },
    {
        "name": "openai_key",
        "regex": r"\b(sk-[A-Za-z0-9]{20,})\b",
        "action": "block",
        "description": "OpenAI API key"
    },
    {
        "name": "anthropic_key",
        "regex": r"\b(sk-ant-[A-Za-z0-9\-_]{40,})\b",
        "action": "block",
        "description": "Anthropic API key"
    },
    {
        "name": "google_api_key",
        "regex": r"\b(AIza[0-9A-Za-z\-_]{35})\b",
        "action": "block",
        "description": "Google API key"
    },
    {
        "name": "ssh_connection_with_password",
        "regex": r"(?i)sshpass\s+-p\s+(\S+)",
        "capture_group": 1,
        "action": "block",
        "description": "sshpass inline password"
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_config(config_path: str | None) -> dict:
    """Load YAML or JSON config, falling back to defaults."""
    if config_path is None:
        candidates = [
            Path("~/.openclaw/outgoing-filter-config.yaml").expanduser(),
            Path("~/.openclaw/outgoing-filter-config.yml").expanduser(),
            Path("~/.openclaw/outgoing-filter-config.json").expanduser(),
        ]
        config_path = next((str(p) for p in candidates if p.exists()), None)

    cfg = dict(DEFAULT_CONFIG)

    if config_path:
        p = Path(config_path).expanduser()
        if not p.exists():
            print(f"[filter_message] WARNING: config not found at {p}", file=sys.stderr)
            return cfg
        raw = p.read_text()
        ext = p.suffix.lower()
        try:
            if ext in (".yaml", ".yml"):
                try:
                    import yaml
                    loaded = yaml.safe_load(raw)
                except ImportError:
                    # Fallback: minimal YAML parser not available; try json
                    print("[filter_message] WARNING: pyyaml not installed, falling back to json parser", file=sys.stderr)
                    loaded = json.loads(raw)
            else:
                loaded = json.loads(raw)
            cfg.update(loaded)
        except Exception as e:
            print(f"[filter_message] WARNING: failed to parse config ({e}), using defaults", file=sys.stderr)

    return cfg


def mask_value(value: str, mask_char: str, show_prefix: int, show_suffix: int) -> str:
    """Mask a sensitive value, optionally preserving prefix/suffix chars."""
    n = len(value)
    prefix = value[:show_prefix] if show_prefix and n > show_prefix else ""
    suffix = value[-show_suffix:] if show_suffix and n > show_suffix else ""
    middle_len = max(n - len(prefix) - len(suffix), 3)
    return prefix + (mask_char * middle_len) + suffix


def apply_pattern(message: str, pattern: dict, global_mode: str, mask_char: str,
                  show_prefix: int, show_suffix: int) -> tuple[str, list[dict]]:
    """
    Apply one pattern to the message.
    Returns (modified_message, list_of_detections).
    """
    regex = pattern["regex"]
    action = pattern.get("action", global_mode)
    capture_group = pattern.get("capture_group", 0)
    name = pattern["name"]
    detections = []

    try:
        compiled = re.compile(regex, re.MULTILINE)
    except re.error as e:
        print(f"[filter_message] WARNING: bad regex for pattern '{name}': {e}", file=sys.stderr)
        return message, detections

    if capture_group:
        # Only mask the capture group, not the full match
        def replacer(m):
            try:
                sensitive = m.group(capture_group)
            except IndexError:
                sensitive = m.group(0)
            detections.append({
                "name": name,
                "action": action,
                "snippet": sensitive[:6] + "…" if len(sensitive) > 6 else sensitive,
                "description": pattern.get("description", "")
            })
            if action in ("block", "warn"):
                return m.group(0)  # Keep original; block/warn caller handles it
            masked = mask_value(sensitive, mask_char, show_prefix, show_suffix)
            return m.group(0).replace(sensitive, masked, 1)

        new_message = compiled.sub(replacer, message)
    else:
        def replacer(m):
            sensitive = m.group(0)
            detections.append({
                "name": name,
                "action": action,
                "snippet": sensitive[:6] + "…" if len(sensitive) > 6 else sensitive,
                "description": pattern.get("description", "")
            })
            if action in ("block", "warn"):
                return sensitive  # Keep original; block/warn caller handles it
            return mask_value(sensitive, mask_char, show_prefix, show_suffix)

        new_message = compiled.sub(replacer, message)

    return new_message, detections


def log_detection(log_path: str, channel: str | None, detections: list[dict], blocked: bool):
    """Append detection event to JSONL log."""
    path = Path(log_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "channel": channel,
        "blocked": blocked,
        "detections": detections
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def filter_message(message: str, channel: str | None = None, config_path: str | None = None) -> dict:
    """
    Core filtering function.
    Returns result dict with keys: blocked, message, detections, warnings.
    """
    cfg = load_config(config_path)
    global_mode = cfg.get("mode", "mask")
    mask_char = cfg.get("mask_char", "*")
    show_prefix = int(cfg.get("show_prefix", 3))
    show_suffix = int(cfg.get("show_suffix", 0))
    allow_channels = cfg.get("allow_channels", [])
    allow_patterns = cfg.get("allow_patterns", [])

    warnings = []
    all_detections = []

    # ── Allow-list checks ──────────────────────────────────────────────────────
    if channel and channel in allow_channels:
        return {"blocked": False, "message": message, "detections": [], "warnings": []}

    for ap in allow_patterns:
        try:
            if re.search(ap, message):
                return {"blocked": False, "message": message, "detections": [], "warnings": []}
        except re.error as e:
            warnings.append(f"Bad allow_pattern regex: {ap!r} ({e})")

    # ── Merge pattern lists (built-ins first, then user overrides) ─────────────
    user_patterns = cfg.get("patterns", [])
    user_names = {p["name"] for p in user_patterns}
    effective_patterns = [p for p in BUILTIN_PATTERNS if p["name"] not in user_names] + user_patterns

    # Honour disabled flag
    effective_patterns = [p for p in effective_patterns if not p.get("disabled", False)]

    # ── Apply each pattern ─────────────────────────────────────────────────────
    filtered = message
    for pattern in effective_patterns:
        filtered, detections = apply_pattern(
            filtered, pattern, global_mode, mask_char, show_prefix, show_suffix
        )
        all_detections.extend(detections)

    # ── Decide blocked vs masked ───────────────────────────────────────────────
    block_names = [d for d in all_detections if d["action"] == "block"]
    warn_names  = [d for d in all_detections if d["action"] == "warn"]
    blocked = len(block_names) > 0

    if warn_names:
        warnings.extend([
            f"⚠️  Sensitive pattern detected ({d['name']}): {d.get('description','')}"
            for d in warn_names
        ])

    result = {
        "blocked": blocked,
        "message": message if blocked else filtered,  # blocked = send nothing
        "detections": all_detections,
        "warnings": warnings
    }

    # ── Logging ────────────────────────────────────────────────────────────────
    if cfg.get("log_detections") and all_detections:
        try:
            log_detection(cfg["log_path"], channel, all_detections, blocked)
        except Exception as e:
            warnings.append(f"Log write failed: {e}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Filter outgoing messages for sensitive information."
    )
    parser.add_argument("--message", "-m", help="Message text to filter (or pass via stdin)")
    parser.add_argument("--channel", "-c", help="Channel ID (for allow-list checks)")
    parser.add_argument("--config", help="Path to config file (YAML or JSON)")
    parser.add_argument("--json", action="store_true", default=True, help="Output JSON (default)")
    args = parser.parse_args()

    if args.message:
        text = args.message
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(2)

    result = filter_message(text.rstrip("\n"), channel=args.channel, config_path=args.config)

    print(json.dumps(result, indent=2))
    sys.exit(1 if result["blocked"] else 0)


if __name__ == "__main__":
    main()
