#!/usr/bin/env python3
"""
scan.py - Score open PRs against a project's vision document and scoring rubric.

Usage:
    python3 scan.py <repo-url> <vision-doc-path> [--count N] [--output <file>]

Examples:
    python3 scan.py https://github.com/openclaw/openclaw ./triage-config/vision.md
    python3 scan.py https://github.com/user/repo ./vision.md --count 50 --output scores.json

The script fetches open PRs via `gh` CLI and outputs a JSON array of scored PRs.
Scoring is rule-based using the rubric; it does NOT call an LLM. The agent can
use the JSON output to apply additional reasoning if needed.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path


def run_gh(args: list[str], retries: int = 3) -> str:
    """Run a gh CLI command with retry for rate limiting."""
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                return result.stdout.strip()

            # Check for rate limiting
            if "rate limit" in result.stderr.lower() or "403" in result.stderr:
                wait = 2 ** attempt * 5
                print(f"Rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            print(f"gh error: {result.stderr[:200]}", file=sys.stderr)
            return ""
        except subprocess.TimeoutExpired:
            print(f"gh timeout on attempt {attempt + 1}", file=sys.stderr)
            continue
        except FileNotFoundError:
            print("Error: gh CLI not found. Install it: https://cli.github.com", file=sys.stderr)
            sys.exit(1)
    return ""


def parse_repo(url: str) -> str:
    """Extract owner/repo from a GitHub URL."""
    url = url.rstrip("/")
    if "github.com" in url:
        parts = url.split("github.com/")[-1]
    else:
        parts = url
    return parts.removesuffix(".git")


def fetch_prs(repo: str, count: int) -> list[dict]:
    """Fetch open PRs with metadata."""
    fields = "number,title,body,labels,additions,deletions,changedFiles,author,createdAt,files"
    raw = run_gh([
        "pr", "list", "--repo", repo,
        "--state", "open",
        "--limit", str(count),
        "--json", fields
    ])
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Error: Could not parse PR data from gh", file=sys.stderr)
        return []


def load_vision(path: str) -> dict:
    """Load and parse a vision document for scoring signals."""
    text = Path(path).read_text()

    vision = {
        "raw": text,
        "green_keywords": [],
        "red_keywords": [],
        "priority_areas": [],
    }

    # Extract green/red signal sections if they exist
    green_match = re.search(r"(?:GREEN|green|Align|align|Positive).*?\n((?:[-*].*\n)+)", text)
    if green_match:
        vision["green_keywords"] = [
            line.strip("- *").strip().lower()
            for line in green_match.group(1).strip().split("\n")
            if line.strip()
        ]

    red_match = re.search(r"(?:RED|red|Misalign|misalign|Negative).*?\n((?:[-*].*\n)+)", text)
    if red_match:
        vision["red_keywords"] = [
            line.strip("- *").strip().lower()
            for line in red_match.group(1).strip().split("\n")
            if line.strip()
        ]

    return vision


def strip_pr_template(body: str) -> str:
    """Remove common PR template boilerplate to avoid false keyword matches.

    PR templates often contain checklist items like '- [ ] Security review'
    or '## Testing' headers that trigger false positives. This strips those
    patterns while preserving the author's actual description."""
    if not body:
        return ""
    lines = body.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip empty checklist items (unchecked boxes with no custom text after)
        if re.match(r"^[-*]\s*\[[ x]\]\s*\S", stripped, re.IGNORECASE):
            # Only skip if it looks like a template item (short, generic)
            if len(stripped) < 80:
                continue
        # Skip markdown headers that are template sections
        if re.match(r"^#{1,4}\s*(description|testing|checklist|type of change|screenshots|notes|how has this been tested)", stripped, re.IGNORECASE):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def score_pr(pr: dict, vision: dict) -> dict:
    """Score a single PR using rule-based heuristics.

    Title keywords are treated as strong signals (author chose them deliberately).
    Body keywords are checked against cleaned text (template boilerplate stripped)
    and given lower weight to avoid false positives from PR templates."""
    score = 50
    modifiers = []
    title = (pr.get("title") or "").lower()
    raw_body = (pr.get("body") or "").lower()
    body = strip_pr_template(raw_body).lower()
    labels = [l.get("name", "").lower() for l in (pr.get("labels") or [])]
    additions = pr.get("additions", 0) or 0
    deletions = pr.get("deletions", 0) or 0
    changed_files = pr.get("changedFiles", 0) or 0
    files = pr.get("files", [])
    file_paths = [f.get("path", "") for f in files] if files else []

    # Helper: check title (strong signal) or body (weaker, cleaned)
    def in_title(keywords):
        return any(kw in title for kw in keywords)

    def in_body(keywords):
        return any(kw in body for kw in keywords)

    # -- Positive modifiers --

    # Security fix: title is strong signal, body alone is weaker
    security_kw = ["security", "cve-", "vulnerability", "injection", "redos", "xss", "csrf"]
    if in_title(security_kw):
        score += 20
        modifiers.append({"modifier": "security_fix", "points": 20})
    elif in_body(security_kw) and any(p for p in file_paths if "security" in p.lower() or "auth" in p.lower()):
        score += 12
        modifiers.append({"modifier": "security_fix_body_only", "points": 12})

    # Bug fix: require "fix" or "bug" in title (conventional commits use fix: prefix)
    bug_kw = ["fix", "bug", "patch", "crash", "deadlock"]
    if in_title(bug_kw):
        if in_title(["test", "spec"]) or in_body(["added test", "test case", "test coverage", "unit test"]):
            score += 10
            modifiers.append({"modifier": "bug_fix_with_tests", "points": 10})
        else:
            score += 5
            modifiers.append({"modifier": "bug_fix", "points": 5})

    # Documentation: check title or file paths
    doc_kw = ["docs", "documentation", "readme", "guide"]
    if in_title(doc_kw) or any(p for p in file_paths if p.startswith("docs/") or p.lower().endswith(".md")):
        score += 5
        modifiers.append({"modifier": "documentation", "points": 5})

    # Performance: title only (body mentions are too often incidental)
    perf_kw = ["perf", "performance", "speed", "optimize", "faster"]
    if in_title(perf_kw):
        score += 8
        modifiers.append({"modifier": "performance", "points": 8})

    # Tests: check file paths for test files (much more reliable than keyword matching)
    test_files = [p for p in file_paths if "test" in p.lower() or "spec" in p.lower()]
    if test_files and not any(m["modifier"].startswith("bug_fix") for m in modifiers):
        score += 5
        modifiers.append({"modifier": "has_tests", "points": 5})

    # Small focused diff
    total_changes = additions + deletions
    if total_changes < 200 and changed_files <= 5:
        score += 5
        modifiers.append({"modifier": "small_focused_diff", "points": 5})

    # Addresses an issue (check title and body)
    combined = f"{title} {body}"
    if re.search(r"(fix(es)?|close[sd]?|resolve[sd]?)\s+#\d+", combined):
        score += 3
        modifiers.append({"modifier": "addresses_issue", "points": 3})

    # Label signals
    if any("security" in l for l in labels):
        if not any(m["modifier"].startswith("security") for m in modifiers):
            score += 10
            modifiers.append({"modifier": "security_label", "points": 10})

    # -- Negative modifiers --

    # Large diff with no test files
    if total_changes > 500 and not test_files:
        score -= 15
        modifiers.append({"modifier": "large_diff_no_tests", "points": -15})

    # No description (check raw body, not cleaned)
    if not pr.get("body") or len(pr.get("body", "").strip()) < 20:
        score -= 5
        modifiers.append({"modifier": "no_description", "points": -5})

    # Spam or promotion
    spam_kw = ["promotion", "sponsor", "advertisement", "buy now", "check out my", "alibaba", "sponsored by"]
    if any(kw in combined for kw in spam_kw):
        score -= 30
        modifiers.append({"modifier": "spam_promotional", "points": -30})

    # Misleading: title says "fix" but zero code changes
    if in_title(["fix", "bug"]) and total_changes == 0:
        score -= 8
        modifiers.append({"modifier": "misleading_no_changes", "points": -8})

    # PR template unfilled (body is mostly template with no real content)
    if raw_body and len(strip_pr_template(raw_body).strip()) < 20 and len(raw_body) > 100:
        score -= 5
        modifiers.append({"modifier": "template_unfilled", "points": -5})

    # Scope creep signals
    if changed_files > 30:
        score -= 10
        modifiers.append({"modifier": "scope_creep_many_files", "points": -10})

    # Check against vision green keywords
    for kw in vision.get("green_keywords", []):
        if kw and kw in combined:
            score += 3
            modifiers.append({"modifier": f"vision_green:{kw[:30]}", "points": 3})
            break  # Only apply once

    # Check against vision red keywords
    for kw in vision.get("red_keywords", []):
        if kw and kw in combined:
            score -= 5
            modifiers.append({"modifier": f"vision_red:{kw[:30]}", "points": -5})
            break  # Only apply once

    # Clamp to 0-100
    score = max(0, min(100, score))

    # Determine action
    if score >= 80:
        action = "prioritize"
    elif score >= 50:
        action = "review"
    elif score >= 35:
        action = "request_changes"
    else:
        action = "close"

    return {
        "number": pr.get("number"),
        "title": pr.get("title"),
        "author": pr.get("author", {}).get("login", "unknown") if isinstance(pr.get("author"), dict) else "unknown",
        "created_at": pr.get("createdAt"),
        "score": score,
        "action": action,
        "modifiers": modifiers,
        "stats": {
            "additions": additions,
            "deletions": deletions,
            "changed_files": changed_files,
        },
        "labels": [l.get("name", "") for l in (pr.get("labels") or [])],
        "url": f"https://github.com/{parse_repo('')}" if not pr.get("number") else "",
    }


def find_duplicates(scored_prs: list[dict]) -> list[dict]:
    """Find PRs with very similar titles (potential duplicates)."""
    dupes = []
    titles = [(pr["number"], pr["title"].lower()) for pr in scored_prs]
    for i, (num_a, title_a) in enumerate(titles):
        for num_b, title_b in titles[i+1:]:
            # Simple word overlap check
            words_a = set(title_a.split())
            words_b = set(title_b.split())
            if len(words_a) > 2 and len(words_b) > 2:
                overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
                if overlap > 0.6:
                    dupes.append({"pr_a": num_a, "pr_b": num_b, "similarity": round(overlap, 2)})
    return dupes


def main():
    parser = argparse.ArgumentParser(description="Score open PRs against a vision document")
    parser.add_argument("repo_url", help="GitHub repo URL")
    parser.add_argument("vision_path", help="Path to vision document")
    parser.add_argument("--count", type=int, default=100, help="Number of PRs to fetch (default: 100)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    repo = parse_repo(args.repo_url)
    print(f"Scanning {repo} (up to {args.count} PRs)...", file=sys.stderr)

    # Load vision
    vision = load_vision(args.vision_path)

    # Fetch PRs
    prs = fetch_prs(repo, args.count)
    if not prs:
        print("No open PRs found or gh fetch failed.", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(prs)} PRs, scoring...", file=sys.stderr)

    # Score each PR
    scored = [score_pr(pr, vision) for pr in prs]

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Find duplicates
    dupes = find_duplicates(scored)

    output = {
        "repo": repo,
        "total_prs": len(scored),
        "scored_prs": scored,
        "potential_duplicates": dupes,
        "distribution": {
            "prioritize": len([p for p in scored if p["score"] >= 80]),
            "review": len([p for p in scored if 50 <= p["score"] < 80]),
            "close": len([p for p in scored if p["score"] < 50]),
        }
    }

    json_output = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).write_text(json_output)
        print(f"Scores written to: {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
