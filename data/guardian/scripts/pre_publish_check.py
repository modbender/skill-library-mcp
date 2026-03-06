#!/usr/bin/env python3
"""
Pre-publish safety gate for Guardian ClawHub packaging.

Usage: python3 scripts/pre_publish_check.py [--path /path/to/skill]

Scans all files that would be included in a clawhub publish and checks for:
  - Hex/token-like strings >= 40 chars (pure hex, no underscores)
  - Known secret values from ~/.openclaw/openclaw.json (>16 chars, no underscores)
  - Files in audit_exports/ directory
  - .db files
  - gateway_token assignment patterns (actual value assignments, not mentions)
"""

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

# Directories always excluded from publish regardless of .clawhubignore
ALWAYS_EXCLUDE_DIRS = {".git", "__pycache__", ".venv", ".pytest_cache", ".clawhub"}

# Files whose token-like content is known-safe ClawHub metadata
SKIP_TOKEN_SCAN = {"_meta.json"}

# --------------------------------------------------------------------------- #
# Ignore-file parsing
# --------------------------------------------------------------------------- #

def load_ignore_patterns(skill_root: Path) -> list[str]:
    """Read .clawhubignore and return list of patterns."""
    ignore_file = skill_root / ".clawhubignore"
    patterns = []
    if ignore_file.exists():
        for line in ignore_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def is_ignored(rel_path: str, patterns: list[str]) -> bool:
    """Return True if rel_path matches any ignore pattern."""
    parts = Path(rel_path).parts
    for pattern in patterns:
        pat = pattern.rstrip("/")
        if fnmatch.fnmatch(rel_path, pat):
            return True
        if fnmatch.fnmatch(Path(rel_path).name, pat):
            return True
        for part in parts:
            if fnmatch.fnmatch(part, pat):
                return True
        if pat.startswith("**/"):
            sub = pat[3:]
            if fnmatch.fnmatch(rel_path, sub) or fnmatch.fnmatch(Path(rel_path).name, sub):
                return True
        if pattern.endswith("/") and (rel_path.startswith(pat + "/") or rel_path == pat):
            return True
    return False


def collect_included_files(skill_root: Path, patterns: list[str]) -> list[Path]:
    """Walk skill_root, return files not excluded by ignore patterns or ALWAYS_EXCLUDE_DIRS."""
    included = []
    for dirpath, dirnames, filenames in os.walk(skill_root):
        rel_dir = Path(dirpath).relative_to(skill_root)

        # Prune always-excluded dirs first
        dirnames[:] = [
            d for d in dirnames
            if d not in ALWAYS_EXCLUDE_DIRS
        ]
        # Then prune by .clawhubignore patterns
        dirnames[:] = [
            d for d in dirnames
            if not is_ignored(str(rel_dir / d), patterns)
            and not is_ignored(str(rel_dir / d) + "/", patterns)
        ]

        for fname in filenames:
            rel = str(rel_dir / fname) if str(rel_dir) != "." else fname
            if not is_ignored(rel, patterns):
                included.append(skill_root / rel)

    return sorted(included)


# --------------------------------------------------------------------------- #
# Secret value extraction from openclaw.json
# --------------------------------------------------------------------------- #

def _looks_like_secret(value: str) -> bool:
    """Return True if value looks like a real secret (not a config key or identifier)."""
    # Skip snake_case identifiers (config options, not secrets)
    if "_" in value:
        return False
    # Must contain at least one digit (real tokens usually do)
    if not any(c.isdigit() for c in value):
        return False
    # Must contain at least one letter
    if not any(c.isalpha() for c in value):
        return False
    return True


def load_env_values(min_len: int = 16) -> list[str]:
    """
    Read ~/.openclaw/openclaw.json and return string values > min_len
    that look like actual secrets (not config keys or identifiers).
    """
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists():
        return []
    try:
        data = json.loads(config_path.read_text())
    except Exception:
        return []

    values = []

    def _extract(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                _extract(v)
        elif isinstance(obj, list):
            for item in obj:
                _extract(item)
        elif isinstance(obj, str) and len(obj) > min_len and _looks_like_secret(obj):
            values.append(obj)

    _extract(data)
    return values


# --------------------------------------------------------------------------- #
# Scanning helpers
# --------------------------------------------------------------------------- #

# Token-like patterns for real secrets:
#   1. Pure lowercase hex >= 40 chars (SHA hashes, hex tokens)
#   2. Mixed-case alphanumeric >= 32 chars WITHOUT underscores (API keys, IDs)
#      — underscores indicate Python identifiers, not secrets
TOKEN_PATTERNS = [
    re.compile(r"\b[a-f0-9]{40,}\b"),           # long lowercase hex
    re.compile(r"\b[a-zA-Z0-9-]{32,}\b"),       # base62 without underscores (real tokens)
]

# Gateway token: only flag actual value assignments, not mentions/searches/comments
# Matches: gateway_token = "value" or GATEWAY_TOKEN = value (not SQL LIKE or regex)
GATEWAY_ASSIGN_PATTERN = re.compile(
    r"""(?i)\bgateway_token\s*=\s*['"]?[a-zA-Z0-9_\-]{8,}"""
)


def is_binary(path: Path) -> bool:
    """Heuristic: read first 1024 bytes and check for null bytes."""
    try:
        chunk = path.read_bytes()[:1024]
        return b"\x00" in chunk
    except Exception:
        return True


def _is_safe_token_context(line: str, match_str: str) -> bool:
    """Return True if the token match is a known-safe false positive context."""
    stripped = line.strip()
    # Skip Python comments
    if stripped.startswith("#"):
        return True
    # Skip lines with regex/pattern definitions
    if any(kw in line for kw in ["re.compile", "pattern", "regex", "PATTERN", "signature", "r\""]):
        return True
    # Skip JSON schema / field names (surrounded by quotes with : nearby)
    # e.g.  "suppress_assistant_number_matches": true
    if re.search(r'"[^"]*' + re.escape(match_str) + r'[^"]*"\s*:', line):
        return True
    # Skip lines that look like function/variable definitions (snake_case already excluded
    # by regex, but handle edge cases)
    return False


def scan_file(path: Path, env_values: list[str], skill_root: Path) -> list[dict]:
    """Scan a single file and return list of issue dicts."""
    issues = []
    rel_path = str(path.relative_to(skill_root))

    # Hard-coded path checks (always CRITICAL regardless of ignore rules)
    if "audit_exports" in rel_path.split("/"):
        issues.append({
            "severity": "CRITICAL",
            "type": "audit_export_file",
            "detail": "File is inside audit_exports/ directory — must never be published",
            "file": rel_path,
        })

    suffix = path.suffix.lower()
    if suffix in (".db", ".db-shm", ".db-wal"):
        issues.append({
            "severity": "CRITICAL",
            "type": "database_file",
            "detail": f"SQLite database file ({suffix}) must never be shipped",
            "file": rel_path,
        })

    if is_binary(path):
        return issues

    try:
        content = path.read_text(errors="replace")
    except Exception:
        return issues

    lines = content.splitlines()
    fname = path.name

    # Gateway token assignment (not just mentions)
    # Skip this file itself — it defines the pattern
    if fname != "pre_publish_check.py":
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip comment lines and SQL LIKE patterns
            if stripped.startswith("#") or "LIKE '%" in line or "LIKE \"%" in line:
                continue
            # Skip lines in test files that are searching for the pattern
            if "evidence" in line.lower() and "LIKE" in line:
                continue
            if GATEWAY_ASSIGN_PATTERN.search(line):
                issues.append({
                    "severity": "CRITICAL",
                    "type": "gateway_token_assignment",
                    "detail": f"Line {i}: gateway_token assignment: {stripped[:120]}",
                    "file": rel_path,
                })

    # Token-like strings — skip ClawHub metadata files
    if fname not in SKIP_TOKEN_SCAN:
        for i, line in enumerate(lines, 1):
            for pat in TOKEN_PATTERNS:
                for m in pat.finditer(line):
                    token = m.group(0)
                    if len(token) < 24:
                        continue
                    if _is_safe_token_context(line, token):
                        continue
                    issues.append({
                        "severity": "CRITICAL",
                        "type": "token_like_string",
                        "detail": (
                            f"Line {i}: token-like string ({len(token)} chars): "
                            f"{token[:40]}{'...' if len(token) > 40 else ''}"
                        ),
                        "file": rel_path,
                    })

    # Known env var secret values
    for secret in env_values:
        if secret in content:
            issues.append({
                "severity": "CRITICAL",
                "type": "env_value_leak",
                "detail": f"File contains a secret value from ~/.openclaw/openclaw.json (len={len(secret)})",
                "file": rel_path,
            })

    return issues


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="Pre-publish safety check for Guardian")
    parser.add_argument("--path", default=None, help="Path to skill root (default: auto-detect)")
    args = parser.parse_args()

    if args.path:
        skill_root = Path(args.path).resolve()
    else:
        skill_root = Path(__file__).resolve().parent.parent

    if not skill_root.exists():
        print(f"ERROR: skill root not found: {skill_root}")
        sys.exit(1)

    print(f"PRE-PUBLISH CHECK")
    print(f"Skill root: {skill_root}")
    print("=" * 60)

    patterns = load_ignore_patterns(skill_root)
    included = collect_included_files(skill_root, patterns)

    print(f"Files that would be included in publish: {len(included)}")
    for f in included:
        print(f"  {f.relative_to(skill_root)}")
    print()

    env_values = load_env_values()
    if env_values:
        print(f"Loaded {len(env_values)} secret values from ~/.openclaw/openclaw.json to check")
    else:
        print("No secret values found in ~/.openclaw/openclaw.json (or file absent)")
    print()

    # Scan all included files
    all_issues: list[dict] = []
    for f in included:
        all_issues.extend(scan_file(f, env_values, skill_root))

    # Also warn about audit_exports/ or .db files that exist on disk but are excluded
    for dirpath, _dirs, filenames in os.walk(skill_root):
        rel_dir = Path(dirpath).relative_to(skill_root)
        for fname in filenames:
            rel = str(rel_dir / fname) if str(rel_dir) != "." else fname
            full = skill_root / rel
            if "audit_exports" in rel.split("/") and full not in included:
                all_issues.append({
                    "severity": "WARNING",
                    "type": "audit_export_exists",
                    "detail": "audit_exports/ file present on disk (excluded by .clawhubignore — good)",
                    "file": rel,
                })
            if Path(fname).suffix in (".db", ".db-shm", ".db-wal") and full not in included:
                all_issues.append({
                    "severity": "WARNING",
                    "type": "db_file_exists",
                    "detail": ".db file present on disk (excluded by .clawhubignore — good)",
                    "file": rel,
                })

    # Deduplicate
    seen: set = set()
    deduped = []
    for issue in all_issues:
        key = (issue["type"], issue["file"], issue.get("detail", "")[:80])
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    all_issues = deduped

    critical_issues = [i for i in all_issues if i["severity"] == "CRITICAL"]
    warning_issues = [i for i in all_issues if i["severity"] == "WARNING"]

    if all_issues:
        print("ISSUES FOUND:")
        for issue in all_issues:
            badge = "CRITICAL" if issue["severity"] == "CRITICAL" else "WARNING "
            print(f"  [{badge}] {issue['type']}")
            print(f"           File:   {issue['file']}")
            print(f"           Detail: {issue['detail']}")
        print()

    print("=" * 60)
    if critical_issues:
        print(f"PRE-PUBLISH CHECK: FAILED ({len(critical_issues)} issues)")
        sys.exit(1)
    else:
        if warning_issues:
            print(f"PRE-PUBLISH CHECK: PASSED (with {len(warning_issues)} warnings — .db/.audit files present but excluded)")
        else:
            print("PRE-PUBLISH CHECK: PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
