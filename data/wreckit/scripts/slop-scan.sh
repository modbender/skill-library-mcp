#!/usr/bin/env bash
# wreckit — semantic slop scan (categorized, context-aware)
# Usage: ./slop-scan.sh [project-path]
# Exit 0 = clean, Exit 1 = slop found

set -euo pipefail

PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

python3 - "$PROJECT" <<'PYEOF'
import json
import os
import re
import sys

project = sys.argv[1]
project_norm = project.replace(os.sep, "/")
disable_fixture_noise = "/tests/fixtures/" in project_norm

threshold_raw = os.getenv("WRECKIT_SLOP_PER_KLOC", "5")
try:
    threshold_per_kloc = float(threshold_raw)
except Exception:
    threshold_per_kloc = 5.0
if threshold_per_kloc <= 0:
    threshold_per_kloc = 5.0

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".wreckit",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
    # Vendored / third-party
    "vendor",
    "third_party",
    ".bundle",
}

# Lock files and generated files to skip entirely
SKIP_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "Cargo.lock",
    "poetry.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "composer.lock",
    "Gemfile.lock",
}

# Generated file patterns (basename regex)
GENERATED_FILE_RE = re.compile(
    r"\.(generated\.ts|generated\.tsx|gen\.go|pb\.go|pb_grpc\.go)$"
    r"|_generated\.(py|ts|js)$"
    r"|\.generated\.(js|jsx|ts|tsx)$",
    re.IGNORECASE,
)

EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".sh", ".swift",
    ".java", ".rb", ".php", ".mjs", ".cjs", ".json", ".yml", ".yaml", ".md"
}

TEST_FILE_RE = re.compile(r"\.(test|spec)\.(ts|tsx|js|jsx|py|rb|go)$", re.IGNORECASE)

TEMPLATE_RE = re.compile(r"example\.com|YOUR_API_KEY|INSERT_HERE|lorem ipsum", re.IGNORECASE)
EMPTY_CATCH_RE = re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}")
EMPTY_EXCEPT_RE = re.compile(r"^\s*except\b[^:]*:\s*pass\s*$", re.IGNORECASE)
HARDCODED_RE_LIST = [
    re.compile(r"\bconst\b.*=.*[\"']sk-[A-Za-z0-9_-]+[\"']", re.IGNORECASE),
    re.compile(r"\bpassword\b\s*[:=]\s*[\"'][^\"']+[\"']", re.IGNORECASE),
    re.compile(r"\b(api[_-]?key|apikey|secret|token)\b\s*[:=]\s*[\"'][A-Za-z0-9_\-+/]{8,}[\"']", re.IGNORECASE),
]

# ── Tracked TODO / FIXME / HACK patterns ────────────────────────────────────
# Matches patterns like:
#   // TODO(JIRA-123)      // TODO(GH-45)     // TODO(#123)   // TODO(@user)
#   # TODO: https://github.com/...
#   // FIXME(#123)         # FIXME(PROJ-99)
#   # HACK: see issue ...  // HACK(#42)
#   // TODO: auto-generated   # TODO: auto-generated
TODO_TRACKED_RE = re.compile(
    r"(?://|#)\s*(?:TODO|FIXME|HACK)\s*"
    r"(?:"
        # Parenthesised ticket/user reference: (JIRA-123), (GH-45), (#123), (@user)
        r"\([^)]+\)"
        r"|"
        # URL reference: TODO: https://...
        r":\s*https?://"
        r"|"
        # Named issue ref: "see issue", ": issue #"
        r":\s*(?:see\s+)?issue\b"
        r"|"
        # Auto-generated marker
        r":\s*auto[- ]?gen(?:erated)?"
    r")",
    re.IGNORECASE,
)

# Untracked TODO/FIXME/HACK — has content but no ticket/URL/issue ref
# Match # TODO: or // TODO: with trailing text (language-aware: // and #)
TODO_BASE_RE = re.compile(r"(?://|#)\s*(?:TODO|FIXME|HACK)\b", re.IGNORECASE)
TODO_UNTRACKED_RE = re.compile(r"(?://|#)\s*(?:TODO|FIXME|HACK)\s*:\s+\S", re.IGNORECASE)


categories = {
    "untracked_todos": 0,
    "tracked_debt": 0,
    "empty_catch_blocks": 0,
    "hardcoded_values": 0,
    "template_artifacts": 0,
    "test_fixture_stubs": 0,
}

# Severity mapping per category (used in output metadata)
SEVERITY = {
    "hardcoded_values": "high",
    "empty_catch_blocks": "medium",
    "template_artifacts": "medium",
    "untracked_todos": "low",
    "tracked_debt": "info",
    "test_fixture_stubs": "info",
}

total_loc = 0
md_todo_threshold = 20  # .md files tolerate up to this many untracked TODOs before counting


def is_generated_file(filename: str) -> bool:
    if filename in SKIP_FILENAMES:
        return True
    if GENERATED_FILE_RE.search(filename):
        return True
    return False


def is_noise_path(path: str) -> bool:
    p = path.replace(os.sep, "/")
    if "/__tests__/" in p:
        return True
    if "/fixtures/" in p and not disable_fixture_noise:
        return True
    if "/examples/" in p:
        return True
    # Vendored paths (belt-and-suspenders beyond EXCLUDE_DIRS)
    for seg in ("/vendor/", "/third_party/", "/.bundle/"):
        if seg in p:
            return True
    if TEST_FILE_RE.search(p):
        return True
    return False


def is_doc_file(path: str) -> bool:
    """Markdown / RST files have natural TODOs — apply much higher tolerance."""
    return path.endswith(".md") or path.endswith(".rst")


def record_noise(matches: int) -> None:
    if matches > 0:
        categories["test_fixture_stubs"] += matches


for root, dirs, files in os.walk(project):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for filename in files:
        _, ext = os.path.splitext(filename)
        if ext.lower() not in EXTS:
            continue
        if is_generated_file(filename):
            continue

        path = os.path.join(root, filename)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            continue

        total_loc += len(lines)
        noise_path = is_noise_path(path)
        doc_file = is_doc_file(path)

        # For doc files, accumulate TODOs locally and only flag if over threshold
        doc_untracked_count = 0

        for line in lines:
            line_matches = 0

            # ── TODO / FIXME / HACK detection ───────────────────────────────
            if TODO_BASE_RE.search(line):
                if TODO_TRACKED_RE.search(line):
                    # Tracked debt (ticket / URL / issue ref / auto-gen)
                    if noise_path:
                        line_matches += 1
                    else:
                        categories["tracked_debt"] += 1
                elif TODO_UNTRACKED_RE.search(line):
                    if noise_path:
                        line_matches += 1
                    elif doc_file:
                        doc_untracked_count += 1  # deferred
                    else:
                        categories["untracked_todos"] += 1

            if TEMPLATE_RE.search(line):
                if noise_path:
                    line_matches += 1
                else:
                    categories["template_artifacts"] += 1

            if EMPTY_CATCH_RE.search(line) or EMPTY_EXCEPT_RE.search(line):
                if noise_path:
                    line_matches += 1
                else:
                    categories["empty_catch_blocks"] += 1

            if any(r.search(line) for r in HARDCODED_RE_LIST):
                if noise_path:
                    line_matches += 1
                else:
                    categories["hardcoded_values"] += 1

            if noise_path and line_matches > 0:
                record_noise(line_matches)

        # Apply doc-file tolerance: only count excess over threshold
        if doc_untracked_count > md_todo_threshold:
            categories["untracked_todos"] += doc_untracked_count - md_todo_threshold


actionable_findings = (
    categories["untracked_todos"]
    + categories["template_artifacts"]
    + categories["empty_catch_blocks"]
    + categories["hardcoded_values"]
)
noise_findings = categories["tracked_debt"] + categories["test_fixture_stubs"]

kloc = total_loc / 1000.0 if total_loc > 0 else 0.0
density_per_kloc = (actionable_findings / kloc) if kloc > 0 else 0.0

if actionable_findings == 0:
    status = "PASS"
elif density_per_kloc > threshold_per_kloc:
    status = "FAIL"
else:
    status = "WARN"

if actionable_findings == 0:
    confidence = 0.0
else:
    confidence = 0.6
    if categories["hardcoded_values"] > 0:
        confidence = 0.9
    elif categories["empty_catch_blocks"] > 0:
        confidence = 0.7
    confidence = min(1.0, confidence + min(0.1, (density_per_kloc / threshold_per_kloc) * 0.1 if threshold_per_kloc > 0 else 0.0))

report = {
    "status": status,
    "confidence": round(confidence, 4),
    "categories": categories,
    "severity": SEVERITY,
    "actionable_findings": actionable_findings,
    "noise_findings": noise_findings,
    "density_per_kloc": round(density_per_kloc, 4),
    "threshold_per_kloc": threshold_per_kloc,
}

print(json.dumps(report))
sys.exit(0)
PYEOF
