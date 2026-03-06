#!/usr/bin/env python3
"""Auto-review module for package updates (sys-updater extension).

Performs automatic review of npm and brew packages before upgrading.
Uses public GitHub/npm APIs to check for issues and changelogs.

Criteria for auto-approval:
- Patch versions (x.y.Z): automatically OK after 2 days
- Minor versions (x.Y.z): requires issue check on GitHub
- Major versions (X.y.z): always blocked, requires manual review

Criteria for auto-block:
- Critical/blocking issues in GitHub (last 3 days)
- Changelog contains "breaking", "regression", "rollback"
- 3+ failed upgrade attempts
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import sys
from urllib.parse import quote

# Setup logging
logger = logging.getLogger("auto_review")

# Rate limiting for GitHub API (60 req/hour for unauthenticated)
GITHUB_RATE_LIMIT = 60
_github_requests_made = 0
_last_github_request_time: Optional[datetime] = None

# Review delay in days (minimum time before auto-review)
REVIEW_DAYS = 2

def is_due_for_review(item: dict, days: int = REVIEW_DAYS) -> bool:
    """Check if package is due for review (firstSeenAt + days has passed)."""
    first_seen = item.get("firstSeenAt")
    if not first_seen:
        return False

    try:
        first_dt = datetime.fromisoformat(first_seen.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_passed = (now - first_dt).days
        return days_passed >= days
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse firstSeenAt '{first_seen}': {e}")
        return False


def is_due_for_auto_review(release_date: Optional[str], days: int = REVIEW_DAYS) -> bool:
    """Compatibility helper: check release-date based review maturity."""
    if not release_date:
        return False
    try:
        dt = datetime.fromisoformat(str(release_date).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt) >= timedelta(days=days)
    except (ValueError, TypeError):
        return False


# Danger keywords in changelogs.
# NOTE: keep this conservative but avoid noisy false positives.
STRONG_DANGER_KEYWORDS = [
    "breaking",
    "breaking change",
    "breaking changes",
    "regression",
    "rollback",
    "critical",
    "security vulnerability",
    "incompatible",
]

# "removed"/"deprecated" alone can be benign; treat as risky only with context.
WEAK_DANGER_KEYWORDS = [
    "deprecated",
    "removed",
]


class ReviewResult(Enum):
    """Result of package review."""
    OK = "ok"
    BLOCKED = "blocked"
    PENDING = "pending"
    ERROR = "error"


class VersionType(Enum):
    """Type of version change."""
    PATCH = "patch"  # x.y.Z -> x.y.W
    MINOR = "minor"  # x.Y.z -> x.W.z
    MAJOR = "major"  # X.y.z -> W.y.z


@dataclass
class PackageMeta:
    """Package metadata for review."""
    name: str
    current_version: str
    latest_version: str
    manager: str  # "npm" or "brew"
    first_seen_at: Optional[str] = None
    release_date: Optional[str] = None
    auto_review_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    review_result: Optional[str] = None
    failed_attempts: int = 0
    last_attempt_at: Optional[str] = None
    issues: list = field(default_factory=list)
    changelog_content: Optional[str] = None
    type: str = "package"  # "package" or "formula"


def now_iso() -> str:
    """Return current time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse version string to (major, minor, patch) tuple.
    
    Handles:
    - 1.2.3 -> (1, 2, 3)
    - 1.2.3-alpha -> (1, 2, 3)
    - v1.2.3 -> (1, 2, 3)
    """
    # Remove leading 'v' and trailing pre-release/build/packager suffixes
    clean = version_str.lstrip("vV").split("-")[0].split("+")[0].split("_")[0]
    parts = clean.split(".")
    
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        # Fallback for non-numeric versions
        return (0, 0, 0)


def get_version_type(current: str, latest: str) -> VersionType:
    """Determine version change type.
    
    Returns:
        VersionType.MAJOR for X.y.z -> W.y.z (X != W)
        VersionType.MINOR for x.Y.z -> x.W.z (Y != W)
        VersionType.PATCH for x.y.Z -> x.y.W (Z != W)
    """
    cur = parse_version(current)
    lat = parse_version(latest)
    
    if lat[0] != cur[0]:
        return VersionType.MAJOR
    elif lat[1] != cur[1]:
        return VersionType.MINOR
    else:
        return VersionType.PATCH


def github_api_request(url: str) -> Optional[dict]:
    """Make GitHub API request with rate limiting.
    
    Returns parsed JSON or None on error.
    """
    global _github_requests_made, _last_github_request_time
    
    # Rate limit: max 60 requests per hour for unauthenticated
    if _github_requests_made >= GITHUB_RATE_LIMIT - 5:  # Keep 5 req buffer
        logger.warning(f"GitHub API rate limit approaching ({_github_requests_made}/{GITHUB_RATE_LIMIT})")
        # Check if we should wait
        if _last_github_request_time:
            elapsed = datetime.now() - _last_github_request_time
            if elapsed < timedelta(hours=1):
                logger.error("GitHub API rate limit exceeded, skipping request")
                return None
        # Reset counter if hour passed
        _github_requests_made = 0
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "sys-updater-auto-review/1.0",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            _github_requests_made += 1
            _last_github_request_time = datetime.now()
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            logger.warning(f"GitHub API rate limited: {url}")
        elif e.code == 404:
            logger.debug(f"GitHub resource not found: {url}")
        else:
            logger.error(f"GitHub API error {e.code}: {url}")
        return None
    except Exception as e:
        logger.error(f"GitHub API request failed: {url} - {e}")
        return None


def get_npm_package_info(package_name: str) -> Optional[dict]:
    """Fetch package info from npm registry."""
    try:
        url = f"https://registry.npmjs.org/{quote(package_name, safe='')}/latest"
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.debug(f"Failed to fetch npm info for {package_name}: {e}")
        return None


def get_github_repo_from_npm(package_name: str) -> Optional[str]:
    """Extract GitHub repo URL from npm package metadata."""
    info = get_npm_package_info(package_name)
    if not info:
        return None
    
    # Check repository field
    repo = info.get("repository", {})
    if isinstance(repo, dict):
        url = repo.get("url", "")
    elif isinstance(repo, str):
        url = repo
    else:
        url = ""
    
    # Extract owner/repo from GitHub URL
    if "github.com" in url:
        # Handle git+https://github.com/owner/repo.git
        match = re.search(r"github\.com/([^/]+)/([^/\.]+)", url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    
    # Check homepage as fallback
    homepage = info.get("homepage", "")
    if "github.com" in homepage:
        match = re.search(r"github\.com/([^/]+)/([^/\.]+)", homepage)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    
    return None


def get_github_repo_from_brew(formula_name: str) -> Optional[str]:
    """Extract GitHub repo from brew formula.
    
    Uses `brew info --json=v2` to get formula metadata.
    """
    try:
        result = subprocess.run(
            ["brew", "info", "--json=v2", formula_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.debug(f"brew info failed for {formula_name}: {result.stderr[:200]}")
            return None
        
        data = json.loads(result.stdout)
        # Formula is in data["formulas"][0]
        formulas = data.get("formulas", [])
        if not formulas:
            return None
        
        formula = formulas[0]
        homepage = formula.get("homepage", "")
        
        # Extract GitHub repo from homepage
        if "github.com" in homepage:
            match = re.search(r"github\.com/([^/]+)/([^/\.]+)", homepage)
            if match:
                return f"{match.group(1)}/{match.group(2)}"
        
        # Check head URL (source repo)
        head = formula.get("head", "")
        if "github.com" in head:
            match = re.search(r"github\.com/([^/]+)/([^/\.]+)", head)
            if match:
                return f"{match.group(1)}/{match.group(2)}"
        
        return None
    except Exception as e:
        logger.debug(f"Failed to get brew info for {formula_name}: {e}")
        return None


def check_npm_package(package_name: str) -> dict[str, Any]:
    """Compatibility wrapper for tests/legacy callers."""
    repo = get_github_repo_from_npm(package_name)
    issues = fetch_github_issues(repo) if repo else []
    return {
        "release_date": None,
        "github_repo": repo,
        "issues": issues,
        "changelog_url": f"https://github.com/{repo}" if repo else None,
    }


def check_brew_formula(formula_name: str) -> dict[str, Any]:
    """Compatibility wrapper for tests/legacy callers."""
    repo = get_github_repo_from_brew(formula_name)
    issues = fetch_github_issues(repo) if repo else []
    return {
        "release_date": None,
        "github_repo": repo,
        "issues": issues,
        "changelog_url": f"https://github.com/{repo}" if repo else None,
    }


def fetch_github_issues(repo: str, days: int = 3) -> list[dict]:
    """Fetch recent issues from GitHub repository.
    
    Args:
        repo: Owner/repo format (e.g., "facebook/react")
        days: How many days back to check
        
    Returns:
        List of issue dicts with title, labels, created_at
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    url = f"https://api.github.com/repos/{repo}/issues?state=all&since={since}&per_page=30"
    
    data = github_api_request(url)
    if not data:
        return []
    
    issues = []
    for item in data:
        # Skip pull requests (GitHub returns PRs as issues too)
        if "pull_request" in item:
            continue
        
        issues.append({
            "title": item.get("title", ""),
            "labels": [l.get("name", "") for l in item.get("labels", [])],
            "state": item.get("state", "open"),
            "created_at": item.get("created_at", ""),
            "body": item.get("body", "")[:500],  # First 500 chars
        })
    
    return issues


def analyze_issues(issues: list[dict]) -> dict:
    """Analyze GitHub issues for critical/blocking problems.
    
    Returns:
        Dict with:
        - has_critical_issues: bool
        - blocking_issues: list of issue titles
    """
    critical_keywords = [
        "critical",
        "security",
        "vulnerability",
        "cve",
        "crash",
        "data loss",
        "breaking",
        "regression",
        "rollback",
    ]
    
    blocking_issues = []
    
    for issue in issues:
        title_lower = issue["title"].lower()
        body_lower = issue.get("body", "").lower()
        labels = [l.lower() for l in issue["labels"]]
        
        # Check for critical keywords in title or body
        is_critical = any(kw in title_lower or kw in body_lower for kw in critical_keywords)
        
        # Check for critical labels
        has_critical_label = any(
            l in ["critical", "security", "bug", "regression", "breaking"]
            for l in labels
        )
        
        # Only count open issues as blocking
        if issue["state"] == "open" and (is_critical or has_critical_label):
            blocking_issues.append(issue["title"])
    
    return {
        "has_critical_issues": len(blocking_issues) > 0,
        "critical_count": len(blocking_issues),
        "blocking_issues": blocking_issues[:5],  # Max 5
        "total_issues_checked": len(issues),
    }


def fetch_changelog(repo: str, version: str) -> Optional[str]:
    """Try to fetch changelog from common locations.
    
    Checks:
    - CHANGELOG.md
    - CHANGELOG
    - HISTORY.md
    - releases/tag/v{version}
    """
    paths = [
        f"https://raw.githubusercontent.com/{repo}/main/CHANGELOG.md",
        f"https://raw.githubusercontent.com/{repo}/master/CHANGELOG.md",
        f"https://raw.githubusercontent.com/{repo}/main/CHANGELOG",
        f"https://raw.githubusercontent.com/{repo}/master/CHANGELOG",
        f"https://raw.githubusercontent.com/{repo}/main/HISTORY.md",
        f"https://raw.githubusercontent.com/{repo}/master/HISTORY.md",
    ]
    
    for url in paths:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                # Return first 5000 chars (should cover recent changes)
                return content[:5000]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue  # Try next path
            break
        except Exception:
            break
    
    return None


def analyze_changelog(content: Optional[str], current_ver: str, latest_ver: str) -> dict:
    """Analyze changelog for danger keywords with reduced false positives.

    Priority:
    1) Analyze latest version section when available.
    2) Fallback to the first chunk of changelog text.
    """
    if not content:
        return {
            "has_danger_keywords": False,
            "danger_matches": [],
            "changelog_length": 0,
            "version_section": None,
        }

    # Best-effort extraction for latest version section.
    version_section = None
    latest_patterns = [
        rf"^##\s*\[?v?{re.escape(latest_ver)}\]?[^\n]*$",
        rf"^#\s*\[?v?{re.escape(latest_ver)}\]?[^\n]*$",
    ]
    lines = content.splitlines()
    start = None
    for i, line in enumerate(lines):
        if any(re.match(p, line.strip(), flags=re.IGNORECASE) for p in latest_patterns):
            start = i
            break
    if start is not None:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if re.match(r"^##\s+", lines[j].strip()):
                end = j
                break
        version_section = "\n".join(lines[start:end]).strip() or None

    # Prefer latest section; fallback to first part of full changelog.
    analysis_text = (version_section or content[:2500]).lower()

    found_keywords: list[str] = []

    # Strong keywords: direct block signals.
    for keyword in STRONG_DANGER_KEYWORDS:
        if keyword in analysis_text:
            found_keywords.append(keyword)

    # Weak keywords are too noisy for hard-blocking by themselves.
    # Keep them for future scoring/telemetry, but do not block on them now.
    _weak_hits = [k for k in WEAK_DANGER_KEYWORDS if k in analysis_text]

    return {
        "has_danger_keywords": len(found_keywords) > 0,
        "danger_matches": sorted(set(found_keywords)),
        "changelog_length": len(content),
        "version_section": version_section,
    }


def auto_review_package(meta: PackageMeta) -> tuple[ReviewResult, str]:
    """Perform automatic review of a package."""
    # Hard stop for repeated failures.
    if (meta.failed_attempts or 0) >= 3:
        return ReviewResult.BLOCKED, "Auto-blocked due to failed upgrade attempts"

    # Determine version type
    version_type = get_version_type(meta.current_version, meta.latest_version)

    # Major versions: always blocked (requires manual review)
    if version_type == VersionType.MAJOR:
        return ReviewResult.BLOCKED, f"Major version bump ({meta.current_version} -> {meta.latest_version}), requires manual review"

    # Collect package metadata via compatibility wrappers (easy to mock in tests)
    if meta.manager in ("npm", "pnpm"):
        info = check_npm_package(meta.name)
    else:
        info = check_brew_formula(meta.name)

    release_date = info.get("release_date") or meta.release_date
    if release_date and not is_due_for_auto_review(release_date, days=REVIEW_DAYS):
        return ReviewResult.PENDING, "Release is too fresh for auto-review"

    repo = info.get("github_repo")

    # If no repo found: conservative behavior.
    if not repo:
        if version_type == VersionType.PATCH:
            return ReviewResult.OK, "Patch version, no GitHub repo found (conservative approval)"
        return ReviewResult.PENDING, "No GitHub repository found for issue check, manual review recommended"

    logger.debug(f"Found GitHub repo for {meta.name}: {repo}")

    # Use prefetched issues when available.
    meta.issues = info.get("issues") or fetch_github_issues(repo)

    # Fetch and analyze changelog.
    meta.changelog_content = fetch_changelog(repo, meta.latest_version)
    changelog_analysis = analyze_changelog(meta.changelog_content, meta.current_version, meta.latest_version)
    if changelog_analysis["has_danger_keywords"]:
        keywords = ", ".join(changelog_analysis["danger_matches"])
        return ReviewResult.BLOCKED, f"Changelog contains danger keywords: {keywords}"

    # Patch versions are low risk if no danger indicators.
    if version_type == VersionType.PATCH:
        return ReviewResult.OK, "Patch version with no danger indicators"

    # Minor versions: check GitHub issues.
    if version_type == VersionType.MINOR:
        issue_analysis = analyze_issues(meta.issues)
        if issue_analysis["has_critical_issues"]:
            issues_str = "; ".join(issue_analysis["blocking_issues"][:3])
            return ReviewResult.BLOCKED, f"Critical issues found: {issues_str}"
        return ReviewResult.OK, "Minor version, no critical issues found"

    return ReviewResult.ERROR, "Unknown review state"


def _is_due_for_blocked_recheck(meta: dict, days: int = REVIEW_DAYS) -> bool:
    """Check if a blocked package is due for periodic re-check.

    For auto-blocked packages we re-check every `days` since the last
    auto review (fallback: reviewedAt/firstSeenAt).
    """
    anchor = meta.get("autoReviewAt") or meta.get("reviewedAt") or meta.get("firstSeenAt")
    if not anchor:
        return False
    try:
        anchor_dt = datetime.fromisoformat(str(anchor).replace("Z", "+00:00"))
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse recheck anchor '{anchor}': {e}")
        return False
    return datetime.now(timezone.utc) >= anchor_dt + timedelta(days=days)


def _is_auto_block(meta: dict) -> bool:
    """True for packages auto-blocked by the review system.

    Any auto-blocked package should be periodically re-checked. Restricting
    re-checks only to notes containing specific keywords (e.g. "regression")
    can leave packages permanently blocked after fixes are released.
    """
    return (
        meta.get("reviewResult") == "blocked"
        and meta.get("blocked") is True
        and meta.get("reviewedBy") == "auto"
    )


def review_single_package(
    name: str,
    meta: dict,
    manager: str
) -> dict:
    """Review a single package and return updated metadata.
    
    Only processes packages that are due for review (firstSeenAt + 2 days).
    Skips packages that are not yet due to save API calls.
    
    Args:
        name: Package name
        meta: Current metadata dict from tracked.json
        manager: "npm" or "brew"
        
    Returns:
        Updated metadata dict with review fields
    """
    auto_block = _is_auto_block(meta)

    # Check if package is due for review.
    # - regular packages: firstSeenAt + REVIEW_DAYS
    # - auto-blocked packages: periodic re-check every REVIEW_DAYS
    if auto_block:
        if not _is_due_for_blocked_recheck(meta, days=REVIEW_DAYS):
            logger.debug(
                "Skipping %s: auto-blocked, not yet due for re-check "
                "(autoReviewAt=%s)",
                name,
                meta.get("autoReviewAt") or meta.get("reviewedAt") or meta.get("firstSeenAt"),
            )
            return meta
    elif not is_due_for_review(meta, days=REVIEW_DAYS):
        logger.debug(f"Skipping {name}: not yet due for review (firstSeenAt={meta.get('firstSeenAt')})")
        return meta  # Return unchanged

    # Skip if already reviewed manually
    if meta.get("reviewedBy") == "manual":
        logger.debug(f"Skipping {name}: already manually reviewed")
        return meta

    # Skip if already blocked unless:
    # - failed attempts increased, or
    # - this is a periodic re-check of an auto-blocked package
    if (
        meta.get("reviewResult") == "blocked"
        and not auto_block
        and not meta.get("failedAttempts", 0) > meta.get("_prev_failedAttempts", 0)
    ):
        logger.debug(f"Skipping {name}: already blocked")
        return meta

    # Skip if already planned (already approved)
    if meta.get("planned") and meta.get("reviewResult") == "ok":
        logger.debug(f"Skipping {name}: already planned for upgrade")
        return meta
    
    # Create PackageMeta from stored data
    pkg = PackageMeta(
        name=name,
        current_version=meta.get("currentVersion", "?"),
        latest_version=meta.get("latestVersion", "?"),
        manager=manager,
        first_seen_at=meta.get("firstSeenAt"),
        release_date=meta.get("releaseDate"),
        auto_review_at=meta.get("autoReviewAt"),
        reviewed_by=meta.get("reviewedBy"),
        review_result=meta.get("reviewResult"),
        failed_attempts=meta.get("failedAttempts", 0),
        last_attempt_at=meta.get("lastAttemptAt"),
        type=meta.get("type", "package"),
    )
    
    # Perform auto-review
    result, reason = auto_review_package(pkg)
    
    # Update metadata
    updated = meta.copy()
    updated["reviewResult"] = result.value
    updated["reviewedBy"] = "auto" if result != ReviewResult.PENDING else None
    updated["autoReviewAt"] = now_iso()
    
    if result == ReviewResult.OK:
        updated["planned"] = True
        updated["blocked"] = False
        updated["note"] = f"Auto-approved: {reason}"
        logger.info(f"✅ {manager}/{name}: {reason}")
    elif result == ReviewResult.BLOCKED:
        updated["blocked"] = True
        updated["planned"] = False
        updated["note"] = f"Auto-blocked: {reason}"
        logger.info(f"🚫 {manager}/{name}: {reason}")
    elif result == ReviewResult.PENDING:
        updated["planned"] = False
        updated["blocked"] = False
        updated["note"] = f"Pending: {reason}"
        logger.debug(f"⏳ {manager}/{name}: {reason}")
    else:
        updated["note"] = f"Review error: {reason}"
        logger.warning(f"⚠️ {manager}/{name}: {reason}")
    
    return updated


def run_auto_review(
    npm_tracked_path: Path,
    brew_tracked_path: Path,
    pnpm_tracked_path: Path | None = None,
    dry_run: bool = False
) -> dict[str, Any]:
    """Run auto-review on all tracked packages.

    Only processes packages that are due for review (firstSeenAt + 2 days).
    """
    summary = {
        "npm": {"reviewed": 0, "approved": 0, "blocked": 0, "pending": 0, "errors": 0, "skipped_not_due": 0},
        "brew": {"reviewed": 0, "approved": 0, "blocked": 0, "pending": 0, "errors": 0, "skipped_not_due": 0},
        "pnpm": {"reviewed": 0, "approved": 0, "blocked": 0, "pending": 0, "errors": 0, "skipped_not_due": 0},
        "details": [],
    }

    def load(path: Path | None, label: str) -> dict[str, Any]:
        if not path or not path.exists():
            return {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load {label}: {e}")
            return {}

    npm_data = load(npm_tracked_path, "npm_tracked.json")
    brew_data = load(brew_tracked_path, "brew_tracked.json")
    pnpm_data = load(pnpm_tracked_path, "pnpm_tracked.json")

    npm_items = npm_data.get("items", {})
    brew_items = brew_data.get("items", {})
    pnpm_items = pnpm_data.get("items", {})

    def _is_due_item(m: dict) -> bool:
        if _is_auto_block(m):
            return _is_due_for_blocked_recheck(m)
        return is_due_for_review(m)

    npm_due = sum(1 for m in npm_items.values() if _is_due_item(m))
    brew_due = sum(1 for m in brew_items.values() if _is_due_item(m))
    pnpm_due = sum(1 for m in pnpm_items.values() if _is_due_item(m))

    logger.info(
        "Starting auto-review: %d npm (%d due), %d brew (%d due), %d pnpm (%d due) packages",
        len(npm_items), npm_due, len(brew_items), brew_due, len(pnpm_items), pnpm_due,
    )

    def process(manager: str, items: dict[str, Any]) -> None:
        for name, meta in items.items():
            updated = review_single_package(name, meta, manager)
            items[name] = updated

            if updated.get("reviewedBy") == "auto":
                result = updated.get("reviewResult")
                summary[manager]["reviewed"] += 1
                if result == "ok":
                    summary[manager]["approved"] += 1
                elif result == "blocked":
                    summary[manager]["blocked"] += 1
                elif result == "pending":
                    summary[manager]["pending"] += 1
                else:
                    summary[manager]["errors"] += 1

                summary["details"].append({
                    "name": name,
                    "manager": manager,
                    "result": result,
                    "reason": updated.get("note", ""),
                })
            elif updated == meta:
                summary[manager]["skipped_not_due"] += 1

    process("npm", npm_items)
    process("brew", brew_items)
    process("pnpm", pnpm_items)

    if not dry_run:
        now = now_iso()
        npm_data["items"] = npm_items
        brew_data["items"] = brew_items
        npm_data["lastAutoReview"] = now
        brew_data["lastAutoReview"] = now

        if pnpm_tracked_path:
            pnpm_data["items"] = pnpm_items
            pnpm_data["lastAutoReview"] = now

        for path, data, label in [
            (npm_tracked_path, npm_data, "npm_tracked.json"),
            (brew_tracked_path, brew_data, "brew_tracked.json"),
            (pnpm_tracked_path, pnpm_data, "pnpm_tracked.json") if pnpm_tracked_path else (None, None, None),
        ]:
            if not path:
                continue
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved {label}")
            except IOError as e:
                logger.error(f"Failed to save {label}: {e}")

    total_reviewed = summary["npm"]["reviewed"] + summary["brew"]["reviewed"] + summary["pnpm"]["reviewed"]
    total_skipped = summary["npm"]["skipped_not_due"] + summary["brew"]["skipped_not_due"] + summary["pnpm"]["skipped_not_due"]
    total_approved = summary["npm"]["approved"] + summary["brew"]["approved"] + summary["pnpm"]["approved"]
    total_blocked = summary["npm"]["blocked"] + summary["brew"]["blocked"] + summary["pnpm"]["blocked"]

    logger.info(
        "Auto-review complete: %d reviewed (%d approved, %d blocked), %d skipped (not yet due)",
        total_reviewed, total_approved, total_blocked, total_skipped,
    )

    return summary


def main():
    """CLI entry point for manual auto-review runs."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-review npm/pnpm/brew packages")
    parser.add_argument("--npm-path", type=Path, default=Path("/home/moltuser/clawd/sys-updater/state/apt/npm_tracked.json"))
    parser.add_argument("--brew-path", type=Path, default=Path("/home/moltuser/clawd/sys-updater/state/apt/brew_tracked.json"))
    parser.add_argument("--pnpm-path", type=Path, default=Path("/home/moltuser/clawd/sys-updater/state/apt/pnpm_tracked.json"))
    parser.add_argument("--dry-run", action="store_true", help="Don't save changes")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    
    # Run auto-review
    summary = run_auto_review(args.npm_path, args.brew_path, args.pnpm_path, args.dry_run)
    
    # Print summary as JSON
    print(json.dumps(summary, indent=2))
    
    # Exit with error if any errors occurred
    total_errors = summary["npm"]["errors"] + summary["brew"]["errors"] + summary["pnpm"]["errors"]
    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
