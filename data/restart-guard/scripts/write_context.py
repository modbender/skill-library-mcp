#!/usr/bin/env python3
"""
restart-guard: write_context.py
Generate and update restart context files with robust YAML/frontmatter handling.
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

DEFAULT_CONTEXT = "~/.openclaw/custom/work/restart-context.md"

DEFAULT_BODY = """# Restart Context

## Reason

{reason_text}

## Pre-Restart State

<!-- Auto-generated; agent may append details -->

## Notes

{notes}
"""


def validate_host_port(host, port):
    """
    Validate host and port values for URL construction.
    Rejects dangerous characters that could break URL parsing or enable injection.
    Returns sanitized (host, port) tuple or raises ValueError.
    """
    if not host or not isinstance(host, str):
        raise ValueError("Host must be a non-empty string")
    host = host.strip()
    # Check for dangerous characters that could break URL parsing or enable injection
    dangerous_chars = ('\x00', '\n', '\r', ' ', '\t', '<', '>', '"', '{', '}', '|', '\\', '^', '`')
    for char in dangerous_chars:
        if char in host:
            raise ValueError(f"Host contains invalid character: {repr(char)}")
    # Validate port
    try:
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            raise ValueError(f"Port must be between 1-65535, got: {port_num}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid port value: {port}") from e
    return host, str(port)


def main():
    parser = argparse.ArgumentParser(description="Write restart context file")
    parser.add_argument("--config", required=True, help="Path to restart-guard.yaml")
    parser.add_argument("--reason", required=True, help="Why restart is needed")
    parser.add_argument(
        "--verify",
        nargs=2,
        action="append",
        metavar=("CMD", "EXPECT"),
        help="Verification command and expected output (repeatable)",
    )
    parser.add_argument(
        "--resume",
        action="append",
        metavar="STEP",
        help="Post-restart resume step (repeatable)",
    )
    parser.add_argument("--note", default="", help="Additional notes")
    parser.add_argument("--triggered-by", default="agent", help="Who triggered (agent/user/cron)")
    args = parser.parse_args()

    config = load_config(args.config)
    context_path = os.path.expanduser(
        (config.get("paths", {}) or {}).get("context_file", DEFAULT_CONTEXT)
    )
    backup_dir = os.path.expanduser((config.get("paths", {}) or {}).get("backup_dir", ""))

    verify_list = []
    if args.verify:
        for cmd, expect in args.verify:
            verify_list.append({"command": cmd, "expect": expect})
    else:
        verify_list.append({"command": "openclaw health --json", "expect": "ok"})

    resume_list = list(args.resume or ["向用户汇报重启结果"])
    now = datetime.now(timezone.utc).astimezone().isoformat()

    frontmatter = {
        "reason": args.reason,
        "triggered_at": now,
        "triggered_by": args.triggered_by,
        "verify": verify_list,
        "resume": resume_list,
        "rollback": {
            "config_backup": os.path.join(backup_dir, "openclaw.json") if backup_dir else "",
        },
        # Reserved keys for restart.py to fill/update.
        "restart_id": "",
        "origin_session_key": "",
        "notify_mode": "origin",
        "channel_selection": {},
        "effective_notify_plan": {},
        "state_timestamps": {},
        "diagnostics_file": "",
        "delivery_status": "",
    }

    body = DEFAULT_BODY.format(
        reason_text=args.reason,
        notes=args.note or "<!-- none -->",
    )
    write_markdown_frontmatter(context_path, frontmatter, body)
    print(f"Context written to {context_path}")


def load_config(path):
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        print(f"Warning: config not found at {expanded}, using defaults", file=sys.stderr)
        return {}
    with open(expanded, "r", encoding="utf-8") as f:
        raw = f.read()

    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, ValueError):
        pass

    parsed = load_yaml_text(raw)
    if isinstance(parsed, dict):
        return parsed
    return {}


def load_yaml_text(raw):
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(raw)
        return parsed if parsed is not None else {}
    except Exception:
        return _parse_simple_yaml_text(raw)


def dump_yaml_text(data):
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip()
    except Exception:
        return _dump_simple_yaml(data).strip()


def parse_markdown_frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if not m:
        return {}, content

    fm_raw = m.group(1)
    body = m.group(2)
    data = load_yaml_text(fm_raw)
    if not isinstance(data, dict):
        data = {}
    return data, body


def write_markdown_frontmatter(path, frontmatter, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fm_text = dump_yaml_text(frontmatter)
    payload = f"---\n{fm_text}\n---\n\n{body.lstrip()}"
    atomic_write(path, payload)


def upsert_markdown_frontmatter(path, updates, default_body=""):
    if os.path.exists(path):
        current, body = parse_markdown_frontmatter(path)
    else:
        current, body = {}, default_body
    current.update(updates or {})
    write_markdown_frontmatter(path, current, body or default_body)


def atomic_write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".restart-guard-", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass


def _strip_inline_comment(line):
    in_single = False
    in_double = False
    out = []
    for ch in line:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_simple_yaml_text(raw):
    lines = []
    for raw_line in raw.splitlines():
        cleaned = _strip_inline_comment(raw_line.rstrip("\n"))
        if not cleaned.strip():
            continue
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        lines.append((indent, cleaned.strip()))

    if not lines:
        return {}
    value, _ = _parse_block(lines, 0, lines[0][0])
    return value


def _parse_block(lines, idx, indent):
    if idx >= len(lines):
        return {}, idx

    is_list = lines[idx][1].startswith("- ")
    if is_list:
        result = []
        while idx < len(lines):
            line_indent, text = lines[idx]
            if line_indent < indent:
                break
            if line_indent != indent or not text.startswith("- "):
                break
            item_text = text[2:].strip()
            idx += 1

            if not item_text:
                if idx < len(lines) and lines[idx][0] > indent:
                    item, idx = _parse_block(lines, idx, lines[idx][0])
                else:
                    item = None
                result.append(item)
                continue

            if ":" in item_text and not _looks_like_quoted(item_text):
                key, val = item_text.split(":", 1)
                key = key.strip()
                val = val.strip()
                item = {}
                if val:
                    item[key] = _parse_scalar(val)
                else:
                    if idx < len(lines) and lines[idx][0] > indent:
                        nested, idx = _parse_block(lines, idx, lines[idx][0])
                    else:
                        nested = {}
                    item[key] = nested

                while idx < len(lines) and lines[idx][0] > indent:
                    child_indent, child_text = lines[idx]
                    if child_text.startswith("- "):
                        break
                    if ":" not in child_text:
                        idx += 1
                        continue
                    ckey, cval = child_text.split(":", 1)
                    ckey = ckey.strip()
                    cval = cval.strip()
                    idx += 1
                    if cval:
                        item[ckey] = _parse_scalar(cval)
                    else:
                        if idx < len(lines) and lines[idx][0] > child_indent:
                            nested, idx = _parse_block(lines, idx, lines[idx][0])
                        else:
                            nested = {}
                        item[ckey] = nested
                result.append(item)
                continue

            result.append(_parse_scalar(item_text))
        return result, idx

    result = {}
    while idx < len(lines):
        line_indent, text = lines[idx]
        if line_indent < indent:
            break
        if line_indent != indent or text.startswith("- "):
            break
        if ":" not in text:
            idx += 1
            continue

        key, val = text.split(":", 1)
        key = key.strip()
        val = val.strip()
        idx += 1
        if val:
            result[key] = _parse_scalar(val)
            continue
        if idx < len(lines) and lines[idx][0] > line_indent:
            nested, idx = _parse_block(lines, idx, lines[idx][0])
        else:
            nested = {}
        result[key] = nested
    return result, idx


def _looks_like_quoted(text):
    return (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    )


def _parse_scalar(value):
    raw = value.strip()
    if raw == "":
        return ""
    if _looks_like_quoted(raw):
        return raw[1:-1]
    lower = raw.lower()
    if lower in {"true", "yes"}:
        return True
    if lower in {"false", "no"}:
        return False
    if lower in {"null", "~"}:
        return None
    if raw == "[]":
        return []
    if raw == "{}":
        return {}
    if re.fullmatch(r"-?\d+", raw):
        try:
            return int(raw)
        except ValueError:
            return raw
    if re.fullmatch(r"-?\d+\.\d+", raw):
        try:
            return float(raw)
        except ValueError:
            return raw
    return raw


def _dump_simple_yaml(value, indent=0):
    space = " " * indent
    if isinstance(value, dict):
        lines = []
        for key, val in value.items():
            if isinstance(val, (dict, list)):
                lines.append(f"{space}{key}:")
                lines.append(_dump_simple_yaml(val, indent + 2))
            else:
                lines.append(f"{space}{key}: {_dump_scalar(val)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{space}-")
                lines.append(_dump_simple_yaml(item, indent + 2))
            else:
                lines.append(f"{space}- {_dump_scalar(item)}")
        return "\n".join(lines)
    return f"{space}{_dump_scalar(value)}"


def _dump_scalar(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "":
        return '""'
    if re.search(r'[\s:#\-\{\}\[\],&\*\?]|^["\']', text):
        return json.dumps(text, ensure_ascii=False)
    return text


if __name__ == "__main__":
    main()
