#!/usr/bin/env python3
"""Guardian Security Scanner CLI for text, files, directories, and session reports."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CORE_DIR = SKILL_ROOT / "core"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from settings import definitions_dir, load_config, resolve_scan_paths, severity_min_score

CHANNEL_MULTIPLIERS = {
    "telegram_dm": 0.8,
    "telegram": 0.9,
    "signal_dm": 0.8,
    "discord": 1.1,
    "discord_group": 1.3,
    "email": 1.2,
    "cron": 0.7,
    "webchat": 1.2,
    "unknown": 1.0,
    "file": 1.0,
}

TRUST_INTERNAL = 0   # cron, workspace files, system prompts — log only, never block
TRUST_OWNER = 1      # owner Telegram — flag only, never block
TRUST_SEMI = 2       # web_fetch, email — block at high threshold score>=70
TRUST_EXTERNAL = 3   # webhooks, unknown — block at lower threshold score>=50

CHANNEL_TRUST: Dict[str, int] = {
    "cron": 0, "system": 0, "file": 0, "workspace": 0,
    "telegram": 1,
    "email": 2, "unknown": 2,
    "webhook": 3,
}

ROLE_TRUST_ADJUST: Dict[str, int] = {
    "system": -1, "assistant": 0, "user": 0, "tool": 1,
}

META_WORDS = re.compile(r'(?:detects?|blocks?|example|signature|pattern for)\s', re.IGNORECASE)


def _load_json(path: Path) -> Dict[str, Any]:
    """Read and parse JSON object from path."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_definitions(config_path: str | None = None) -> Dict[str, List[Dict[str, Any]]]:
    """Load signature definition files configured for this skill."""
    config = load_config(config_path)
    defs = {}
    defs_dir = definitions_dir(config)

    for file_path in defs_dir.glob("*.json"):
        if file_path.name == "manifest.json":
            continue
        try:
            data = _load_json(file_path)
        except (json.JSONDecodeError, OSError):
            continue

        category = data.get("category", file_path.stem)
        sigs = data.get("signatures", data.get("checks", []))
        if isinstance(sigs, list):
            defs[category] = sigs

    return defs


def scan_text(text: str, definitions: Dict[str, List[Dict[str, Any]]], channel: str = "unknown", role: str = "unknown") -> Dict[str, Any]:
    """Scan text against loaded definitions and return scored threats."""
    # Load config to check for false positive suppression
    config = load_config()
    suppress_config = config.get("false_positive_suppression", {})
    suppress_assistant_numbers = suppress_config.get("suppress_assistant_number_matches", True)
    is_assistant = role in ("assistant", "model", "bot")
    number_sensitive_patterns = {"EXF-008", "EXF-009", "EXF-011"}
    
    threats: List[Dict[str, Any]] = []
    for category, signatures in definitions.items():
        if category == "openclaw_hardening":
            continue
        for sig in signatures:
            pattern = sig.get("pattern", "")
            if not pattern:
                continue

            flags = 0
            flag_str = sig.get("flags", "")
            if "i" in flag_str:
                flags |= re.IGNORECASE
            if "s" in flag_str:
                flags |= re.DOTALL

            try:
                match = re.search(pattern, text, flags)
            except re.error:
                continue

            if not match:
                continue

            sig_id = sig.get("id", "unknown")
            
            # Skip number-sensitive patterns in assistant messages if suppression is enabled
            if (suppress_assistant_numbers and 
                is_assistant and 
                sig_id in number_sensitive_patterns):
                # Check if the match has financial context keywords nearby
                match_start = max(0, match.start() - 50)
                match_end = min(len(text), match.end() + 50)
                context = text[match_start:match_end].lower()
                
                financial_keywords = [
                    "bsb", "tfn", "tax file", "account", "banking", "transfer",
                    "payment", "balance", "deposit", "withdrawal", "medicare",
                    "abn", "financial", "bank"
                ]
                
                has_financial_context = any(keyword in context for keyword in financial_keywords)
                if not has_financial_context:
                    continue  # Skip this match - likely a false positive

            threats.append(
                {
                    "id": sig_id,
                    "category": category,
                    "severity": sig.get("severity", "medium"),
                    "description": sig.get("description", ""),
                    "score": int(sig.get("score", 50)),
                    "evidence": match.group(0)[:80],
                    "position": match.start(),
                }
            )

    # Compute effective trust level
    effective_trust = max(0, min(3, CHANNEL_TRUST.get(channel, 2) + ROLE_TRUST_ADJUST.get(role, 0)))
    trust_name = ["internal", "owner", "semi_trusted", "external"][effective_trust]

    # Apply context-based score adjustments to each hit
    for threat in threats:
        pos = threat["position"]
        ev_len = len(threat["evidence"])
        before_ctx = text[max(0, pos - 100):pos]
        after_ctx = text[pos + ev_len:min(len(text), pos + ev_len + 100)]
        if "`" in before_ctx and "`" in after_ctx:
            threat["score"] = max(0, threat["score"] - 20)
        pre_ctx = text[max(0, pos - 80):pos]
        if META_WORDS.search(pre_ctx):
            threat["score"] = max(0, threat["score"] - 15)

    if not threats:
        return {
            "score": 0,
            "threats": [],
            "action": "allow",
            "channel": channel,
            "blocked": False,
            "trust_level": effective_trust,
            "trust_name": trust_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    threats.sort(key=lambda threat: threat["score"], reverse=True)
    max_score = threats[0]["score"]
    additional = sum(threat["score"] * 0.1 for threat in threats[1:])
    raw_score = min(100, max_score + additional)

    multiplier = CHANNEL_MULTIPLIERS.get(channel, 1.0)
    final_score = min(100, int(raw_score * multiplier))

    if final_score >= 80:
        action = "block"
    elif final_score >= 50:
        action = "flag"
    else:
        action = "allow"

    # Trust-based blocking decision
    block_reason: Any = None
    if effective_trust == 0:
        blocked = False
        block_reason = "trust_internal_no_block"
    elif effective_trust == 1:
        blocked = False
        block_reason = "trust_owner_flag_only"
    elif effective_trust == 2:
        blocked = final_score >= 70
    else:
        blocked = final_score >= 50

    result: Dict[str, Any] = {
        "score": final_score,
        "threats": threats,
        "action": action,
        "channel": channel,
        "blocked": blocked,
        "trust_level": effective_trust,
        "trust_name": trust_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if block_reason is not None:
        result["block_reason"] = block_reason
    return result


def _iter_jsonl_files(search_roots: Iterable[Path]) -> List[Path]:
    """Collect JSONL files recursively from one or more roots."""
    collected: List[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for pattern in ("*.jsonl", "**/*.jsonl"):
            collected.extend(root.glob(pattern))

    deduped: List[Path] = []
    seen = set()
    for file_path in collected:
        key = str(file_path.resolve())
        if key not in seen:
            seen.add(key)
            deduped.append(file_path)
    return deduped


def _extract_text(entry: Dict[str, Any]) -> str:
    """Extract text payload from common JSONL message record variants."""
    text = entry.get("content", "") or entry.get("message", "") or entry.get("text", "")
    if isinstance(text, list):
        return " ".join(str(part) for part in text)
    return text if isinstance(text, str) else (str(text) if text else "")


def _iter_file_chunks(file_path: Path) -> List[Tuple[int, str]]:
    """Return text chunks for any file format Guardian can scan."""
    chunks: List[Tuple[int, str]] = []
    if file_path.suffix.lower() == ".jsonl":
        try:
            with file_path.open(encoding="utf-8") as handle:
                for line_num, line in enumerate(handle, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        obj = json.loads(stripped)
                    except json.JSONDecodeError:
                        chunks.append((line_num, stripped))
                        continue
                    if isinstance(obj, dict):
                        text = _extract_text(obj)
                        if text:
                            chunks.append((line_num, text))
                    else:
                        chunks.append((line_num, str(obj)))
            return chunks
        except OSError:
            return chunks

    try:
        with file_path.open(encoding="utf-8") as handle:
            for line_num, line in enumerate(handle, 1):
                text = line.strip()
                if text:
                    chunks.append((line_num, text))
    except (OSError, UnicodeDecodeError):
        return []

    return chunks


def scan_file(file_path: str, definitions: Dict[str, List[Dict[str, Any]]], channel: str = "file") -> Dict[str, Any]:
    """Scan an arbitrary file by evaluating each text line/chunk."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        return {"error": f"File not found: {path}", "threats": [], "files_scanned": 0, "chunks_scanned": 0}

    threats: List[Dict[str, Any]] = []
    chunks = _iter_file_chunks(path)
    for line_num, chunk in chunks:
        result = scan_text(chunk, definitions, channel=channel)
        for threat in result.get("threats", []):
            threat["file"] = str(path)
            threat["line"] = line_num
            threats.append(threat)

    return {
        "path": str(path),
        "files_scanned": 1,
        "chunks_scanned": len(chunks),
        "threats": threats,
        "unique_detections": len({(t["id"], t.get("evidence", "")) for t in threats}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def scan_directory(directory: str, definitions: Dict[str, List[Dict[str, Any]]], channel: str = "file") -> Dict[str, Any]:
    """Recursively scan all regular files in a directory."""
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return {"error": f"Directory not found: {root}", "threats": [], "files_scanned": 0, "chunks_scanned": 0}

    all_threats: List[Dict[str, Any]] = []
    files_scanned = 0
    chunks_scanned = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        result = scan_file(str(path), definitions, channel=channel)
        files_scanned += int(result.get("files_scanned", 0))
        chunks_scanned += int(result.get("chunks_scanned", 0))
        all_threats.extend(result.get("threats", []))

    return {
        "path": str(root),
        "files_scanned": files_scanned,
        "chunks_scanned": chunks_scanned,
        "threats": all_threats,
        "unique_detections": len({(t["id"], t.get("evidence", "")) for t in all_threats}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def watch_directory(
    directory: str,
    definitions: Dict[str, List[Dict[str, Any]]],
    interval: int = 30,
    channel: str = "file",
    once: bool = False,
) -> Dict[str, Any]:
    """Poll directory for changed files and scan changed content."""
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return {"error": f"Directory not found: {root}", "scans": 0, "threats": []}

    seen_mtime: Dict[str, float] = {}
    scans = 0
    collected: List[Dict[str, Any]] = []

    while True:
        scans += 1
        cycle_threats: List[Dict[str, Any]] = []
        files_changed = 0
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            key = str(path)
            if seen_mtime.get(key) == mtime:
                continue
            seen_mtime[key] = mtime
            files_changed += 1
            cycle = scan_file(str(path), definitions, channel=channel)
            cycle_threats.extend(cycle.get("threats", []))

        payload = {
            "scan": scans,
            "files_changed": files_changed,
            "threats": cycle_threats,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        collected.append(payload)
        print(json.dumps(payload))

        if once:
            return {"path": str(root), "scans": scans, "threats": [t for c in collected for t in c["threats"]]}

        time.sleep(max(1, int(interval)))


def scan_sessions(
    sessions_dir: str,
    definitions: Dict[str, List[Dict[str, Any]]],
    hours: int = 24,
) -> Dict[str, Any]:
    """Scan JSONL sessions under a directory for threats."""
    return scan_sessions_multi([Path(sessions_dir)], definitions, hours)


def scan_sessions_multi(
    search_roots: List[Path],
    definitions: Dict[str, List[Dict[str, Any]]],
    hours: int = 24,
) -> Dict[str, Any]:
    """Scan JSONL sessions under multiple roots for recent threats."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results: List[Dict[str, Any]] = []
    jsonl_files = _iter_jsonl_files(search_roots)

    if not jsonl_files:
        return {"threats": [], "files_scanned": 0, "message": "No JSONL files found"}

    files_scanned = 0
    for file_path in jsonl_files:
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                continue
        except OSError:
            continue

        files_scanned += 1
        try:
            with file_path.open(encoding="utf-8") as handle:
                for line_num, line in enumerate(handle, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        entry = json.loads(stripped)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(entry, dict):
                        continue

                    text = _extract_text(entry)
                    if len(text) < 5:
                        continue

                    channel = str(entry.get("channel", "unknown"))
                    role = str(entry.get("role", "unknown"))
                    result = scan_text(text, definitions, channel=channel, role=role)
                    if not result["threats"]:
                        continue

                    for threat in result["threats"]:
                        threat["file"] = file_path.name
                        threat["line"] = line_num
                    results.extend(result["threats"])
        except OSError:
            continue

    seen = set()
    unique: List[Dict[str, Any]] = []
    for threat in results:
        key = (threat["id"], threat.get("evidence", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(threat)

    return {
        "threats": unique[:100],
        "files_scanned": files_scanned,
        "total_detections": len(results),
        "unique_detections": len(unique),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def audit_config(config_path: str, definitions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Audit OpenClaw config JSON against hardening checks."""
    try:
        config = _load_json(Path(config_path))
    except (json.JSONDecodeError, OSError) as exc:
        return {"error": str(exc), "warnings": [], "passed": []}

    hardening = definitions.get("openclaw_hardening", [])
    warnings: List[Dict[str, Any]] = []
    passed: List[str] = []

    def get_nested(obj: Dict[str, Any], path: str) -> Any:
        current: Any = obj
        for part in path.split("."):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    for check in hardening:
        path = check.get("path", "")
        condition = check.get("condition", "")
        val = get_nested(config, path)

        failed = False
        if condition == "missing_or_empty":
            failed = val is None or val == {} or val == [] or val == ""
        elif condition == "missing":
            failed = val is None
        elif condition == "missing_or_false":
            failed = val is None or val is False
        elif condition == "truthy":
            failed = bool(val)
        elif condition == "false":
            failed = val is False
        elif condition.startswith("equals_"):
            target = condition[7:]
            failed = val == "*" if target == "wildcard" else str(val) == target
        elif condition == "has_default_token":
            failed = False

        if failed:
            warnings.append(
                {
                    "id": check.get("id", "unknown"),
                    "severity": check.get("severity", "medium"),
                    "description": check.get("description", ""),
                    "path": path,
                    "severity_score": int(check.get("score", 10)),
                }
            )
        else:
            passed.append(str(check.get("id", "unknown")))

    return {
        "config_path": str(config_path),
        "warnings": warnings,
        "passed": passed,
        "score": max(0, 100 - sum(w.get("severity_score", 10) for w in warnings)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    """CLI entrypoint for Guardian scan, audit, and report commands."""
    parser = argparse.ArgumentParser(description="Guardian Security Scanner")
    parser.add_argument("--scan", type=str, help="Text to scan for threats")
    parser.add_argument("--file", type=str, help="Scan any single file")
    parser.add_argument("--dir", dest="directory", type=str, help="Scan all files recursively in directory")
    parser.add_argument("--watch", type=str, help="Watch a directory for changed files")
    parser.add_argument("--interval", type=int, default=30, help="Watch poll interval in seconds")
    parser.add_argument("--channel", type=str, default="unknown", help="Channel context")
    parser.add_argument("--audit", type=str, help="Path to OpenClaw config JSON to audit")
    parser.add_argument("--report", type=str, help="Path to sessions directory to scan")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back for report mode")
    parser.add_argument("--config", type=str, help="Path to Guardian config.json")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    if not any([args.scan, args.file, args.directory, args.watch, args.audit, args.report]):
        parser.print_help()
        return 1

    definitions = load_definitions(config_path=args.config)
    indent = 2 if args.pretty else None

    if args.scan:
        result = scan_text(args.scan, definitions, args.channel)
        config = load_config(args.config)
        min_score = severity_min_score(config.get("severity_threshold", "medium"))
        if result.get("score", 0) < min_score:
            result["action"] = "allow"
        print(json.dumps(result, indent=indent))
        return 0

    if args.file:
        result = scan_file(args.file, definitions, channel=args.channel or "file")
        print(json.dumps(result, indent=indent))
        return 0

    if args.directory:
        result = scan_directory(args.directory, definitions, channel=args.channel or "file")
        print(json.dumps(result, indent=indent))
        return 0

    if args.watch:
        try:
            watch_directory(args.watch, definitions, interval=args.interval, channel=args.channel or "file")
            return 0
        except KeyboardInterrupt:
            return 0

    if args.audit:
        result = audit_config(args.audit, definitions)
        print(json.dumps(result, indent=indent))
        return 0

    config = load_config(args.config)
    if args.report:
        result = scan_sessions(args.report, definitions, args.hours)
    else:
        scan_roots = resolve_scan_paths(config)
        result = scan_sessions_multi(scan_roots, definitions, args.hours)

    min_score = severity_min_score(config.get("severity_threshold", "medium"))
    filtered = [t for t in result.get("threats", []) if int(t.get("score", 0)) >= min_score]
    result["threats"] = filtered
    result["unique_detections"] = len(filtered)
    print(json.dumps(result, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
