#!/usr/bin/env python3
"""clawhub_sync.py — Sync ClawHub skill catalog and check for security issues.

Fetches all skills from ClawHub, compares against local installs,
checks blocklist, detects version drift, and pushes results to dashboard.

Usage:
    python3 clawhub_sync.py [--full-scan] [--blocklist-only] [--json]

Environment:
    CLAWGUARD_API_KEY           Dashboard API key
    CLAWGUARD_DASHBOARD_URL     Dashboard URL
    CRUSTY_DATA_DIR             Data directory (default: /tmp/crusty_data)
"""

import json
import os
import sys
import subprocess
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(os.environ.get("CLAWGUARD_DATA_DIR", "/tmp/crusty_data"))
BLOCKLIST_FILE = DATA_DIR / "blocklist.json"
CATALOG_FILE = DATA_DIR / "catalog.json"
INSTALLED_CACHE = DATA_DIR / "installed_skills.json"
DASHBOARD_URL = os.environ.get("CRUSTY_DASHBOARD_URL", os.environ.get("CLAWGUARD_DASHBOARD_URL", "https://crustysecurity.com"))
API_KEY = os.environ.get("CRUSTY_API_KEY", os.environ.get("CLAWGUARD_API_KEY", ""))

# Known malicious patterns in skill owners/slugs (seed blocklist)
SEED_BLOCKLIST = {
    "patterns": [
        # Add known bad patterns here as they're discovered
    ],
    "slugs": [
        # Add specific banned skill slugs here
    ],
    "owners": [
        # Add banned owner handles here
    ]
}


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_clawhub(*args):
    """Run clawhub CLI command and return parsed JSON output."""
    cmd = ["clawhub"] + list(args) + ["--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout
        # ClawHub sometimes prefixes with non-JSON text
        idx = output.find("{")
        if idx < 0:
            idx = output.find("[")
        if idx >= 0:
            return json.loads(output[idx:])
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error running clawhub {' '.join(args)}: {e}", file=sys.stderr)
        return None


def fetch_full_catalog():
    """Fetch all skills from ClawHub registry."""
    all_skills = []
    # Fetch by different sort orders to maximize coverage
    for sort in ["newest", "downloads", "installs"]:
        data = run_clawhub("explore", "--limit", "200", "--sort", sort)
        if data and "items" in data:
            for item in data["items"]:
                slug = item.get("slug")
                if slug and not any(s["slug"] == slug for s in all_skills):
                    all_skills.append(item)

    print(f"Fetched {len(all_skills)} skills from ClawHub", file=sys.stderr)
    return all_skills


def get_installed_skills():
    """Get locally installed skills with file hashes."""
    installed = []

    # Method 1: clawhub list (lockfile-based)
    data = run_clawhub("list")
    if data and isinstance(data, list):
        for skill in data:
            installed.append({
                "slug": skill.get("slug", ""),
                "version": skill.get("version", "unknown"),
                "source": "clawhub",
            })

    # Method 2: Scan skills directories
    skill_dirs = [
        Path("/data/workspace/skills"),
        Path("/openclaw/skills"),
        Path.home() / ".openclaw" / "skills",
        Path.home() / "clawd" / "skills",
    ]

    for skills_root in skill_dirs:
        if not skills_root.exists():
            continue
        for skill_dir in skills_root.iterdir():
            if not skill_dir.is_dir():
                continue
            slug = skill_dir.name
            if any(s["slug"] == slug for s in installed):
                continue

            # Read version from _meta.json (ClawHub), SKILL.md frontmatter, or fallback
            version = ""
            meta_json = skill_dir / "_meta.json"
            if meta_json.exists():
                try:
                    with open(meta_json) as f:
                        meta = json.load(f)
                        version = meta.get("version", "")
                except Exception:
                    pass

            if not version:
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    with open(skill_md) as f:
                        content = f.read()
                        if "version:" in content:
                            for line in content.split("\n"):
                                if line.strip().startswith("version:"):
                                    version = line.split(":", 1)[1].strip().strip("\"'")
                                    break

            if not version:
                # Bundled OpenClaw skills have no version — managed by OpenClaw itself
                version = "bundled" if str(skills_root) == "/openclaw/skills" else "local"

            # Hash all files for integrity checking
            file_hashes = {}
            for fpath in sorted(skill_dir.rglob("*")):
                if fpath.is_file() and not fpath.name.startswith("."):
                    try:
                        h = hashlib.sha256(fpath.read_bytes()).hexdigest()
                        file_hashes[str(fpath.relative_to(skill_dir))] = h
                    except Exception:
                        pass

            installed.append({
                "slug": slug,
                "version": version,
                "source": str(skills_root),
                "path": str(skill_dir),
                "file_count": len(file_hashes),
                "files_hash": hashlib.sha256(
                    json.dumps(file_hashes, sort_keys=True).encode()
                ).hexdigest()[:16],
            })

    return installed


def load_blocklist():
    """Load blocklist from file, merging with seed."""
    blocklist = dict(SEED_BLOCKLIST)
    if BLOCKLIST_FILE.exists():
        try:
            with open(BLOCKLIST_FILE) as f:
                saved = json.load(f)
                blocklist["slugs"] = list(set(blocklist["slugs"] + saved.get("slugs", [])))
                blocklist["owners"] = list(set(blocklist["owners"] + saved.get("owners", [])))
                blocklist["patterns"] = list(set(blocklist["patterns"] + saved.get("patterns", [])))
        except Exception:
            pass
    return blocklist


def save_blocklist(blocklist):
    """Save blocklist to file."""
    ensure_dirs()
    with open(BLOCKLIST_FILE, "w") as f:
        json.dump(blocklist, f, indent=2)


def check_skill_security(skill, catalog, blocklist, installed_hashes):
    """Check a single installed skill against security criteria."""
    issues = []
    slug = skill["slug"]

    # Check blocklist
    if slug in blocklist.get("slugs", []):
        issues.append({
            "severity": "critical",
            "type": "blocklisted",
            "message": f"Skill '{slug}' is on the blocklist"
        })

    # Check if from ClawHub
    catalog_entry = next((c for c in catalog if c.get("slug") == slug), None)

    if catalog_entry:
        owner = catalog_entry.get("owner", {}).get("handle", "")
        if owner in blocklist.get("owners", []):
            issues.append({
                "severity": "critical",
                "type": "banned_owner",
                "message": f"Skill owner '{owner}' is banned"
            })

        # Check for low reputation (very new, no downloads, no stars)
        stats = catalog_entry.get("stats", {})
        if stats.get("downloads", 0) < 5 and stats.get("stars", 0) == 0:
            issues.append({
                "severity": "low",
                "type": "low_reputation",
                "message": f"Low reputation: {stats.get('downloads', 0)} downloads, 0 stars"
            })

        # Check version drift (skip bundled/local — no meaningful version to compare)
        latest_version = catalog_entry.get("tags", {}).get("latest", "")
        if latest_version and skill.get("version") and skill["version"] not in ("local", "bundled", latest_version):
            issues.append({
                "severity": "medium",
                "type": "version_drift",
                "message": f"Installed {skill['version']}, latest is {latest_version}"
            })
    else:
        # Not on ClawHub — could be custom or removed
        if skill.get("source") != "/openclaw/skills":  # OpenClaw built-ins are fine
            issues.append({
                "severity": "info",
                "type": "not_on_clawhub",
                "message": "Skill not found on ClawHub registry"
            })

    # Check pattern blocklist
    for pattern in blocklist.get("patterns", []):
        if pattern.lower() in slug.lower():
            issues.append({
                "severity": "high",
                "type": "pattern_match",
                "message": f"Skill matches blocked pattern: {pattern}"
            })

    return issues


def push_to_dashboard(scan_type, target, status, results, severity=None):
    """Push scan result to dashboard API."""
    if not API_KEY:
        return

    import urllib.request
    import ssl

    severity_val = "null" if not severity else f'"{severity}"'
    payload = json.dumps({
        "scan_type": scan_type,
        "target": target,
        "status": status,
        "engine": "Crusty Security ClawHub Sync",
        "severity": severity,
        "results": results,
    }).encode()

    try:
        req = urllib.request.Request(
            f"{DASHBOARD_URL}/api/v1/scan",
            data=payload,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        urllib.request.urlopen(req, timeout=10, context=ssl.create_default_context())
    except Exception as e:
        print(f"Dashboard push failed: {e}", file=sys.stderr)


def main():
    ensure_dirs()
    full_scan = "--full-scan" in sys.argv
    blocklist_only = "--blocklist-only" in sys.argv
    output_json = "--json" in sys.argv

    timestamp = datetime.now(timezone.utc).isoformat()

    # Load blocklist
    blocklist = load_blocklist()

    # Fetch catalog (unless blocklist-only)
    catalog = []
    if not blocklist_only:
        catalog = fetch_full_catalog()
        # Save catalog
        with open(CATALOG_FILE, "w") as f:
            json.dump({"fetched_at": timestamp, "skills": catalog}, f, indent=2)

    # Get installed skills
    installed = get_installed_skills()

    # Save installed cache
    with open(INSTALLED_CACHE, "w") as f:
        json.dump({"scanned_at": timestamp, "skills": installed}, f, indent=2)

    # Check each installed skill
    results = []
    for skill in installed:
        issues = check_skill_security(skill, catalog, blocklist, {})
        worst_severity = "none"
        for issue in issues:
            sev = issue["severity"]
            if sev == "critical":
                worst_severity = "critical"
            elif sev == "high" and worst_severity not in ("critical",):
                worst_severity = "high"
            elif sev == "medium" and worst_severity not in ("critical", "high"):
                worst_severity = "medium"
            elif sev == "low" and worst_severity == "none":
                worst_severity = "low"

        # Look up ClawHub data
        catalog_entry = next((c for c in catalog if c.get("slug") == skill["slug"]), None)

        skill_result = {
            "slug": skill["slug"],
            "version": skill.get("version", "unknown"),
            "source": skill.get("source", "unknown"),
            "path": skill.get("path", ""),
            "file_count": skill.get("file_count", 0),
            "files_hash": skill.get("files_hash", ""),
            "clawhub_found": catalog_entry is not None,
            "clawhub_latest": catalog_entry.get("tags", {}).get("latest", "") if catalog_entry else "",
            "clawhub_downloads": catalog_entry.get("stats", {}).get("downloads", 0) if catalog_entry else 0,
            "clawhub_stars": catalog_entry.get("stats", {}).get("stars", 0) if catalog_entry else 0,
            "clawhub_owner": catalog_entry.get("owner", {}).get("handle", "") if catalog_entry else "",
            "issues": issues,
            "severity": worst_severity,
            "scanned_at": timestamp,
        }
        results.append(skill_result)

        # Push critical/high issues to dashboard
        if worst_severity in ("critical", "high"):
            status = "malicious" if worst_severity == "critical" else "suspicious"
            push_to_dashboard(
                "clawhub_check",
                skill["slug"],
                status,
                skill_result,
                severity=worst_severity,
            )

    # Push overall sync result
    clean_count = sum(1 for r in results if r["severity"] == "none")
    issue_count = len(results) - clean_count
    overall_status = "clean" if issue_count == 0 else "suspicious"
    push_to_dashboard(
        "clawhub_sync",
        f"{len(results)} skills checked",
        overall_status,
        {
            "total_skills": len(results),
            "clean": clean_count,
            "with_issues": issue_count,
            "catalog_size": len(catalog),
            "blocklist_size": len(blocklist.get("slugs", [])),
        },
        severity="info" if issue_count == 0 else "medium",
    )

    # Push skills_detail to agent metadata via heartbeat endpoint
    if API_KEY and DASHBOARD_URL:
        import urllib.request, ssl
        try:
            payload = json.dumps({
                "metadata": {
                    "skills_detail": results,
                    "skills_synced_at": timestamp,
                }
            }).encode()
            req = urllib.request.Request(
                f"{DASHBOARD_URL}/api/v1/heartbeat",
                data=payload,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=10, context=ssl.create_default_context())
            print("   ✅ Skills detail pushed to dashboard", file=sys.stderr)
        except Exception as e:
            print(f"   ⚠️ Skills detail push failed: {e}", file=sys.stderr)

    # Output
    output = {
        "timestamp": timestamp,
        "catalog_size": len(catalog),
        "installed_count": len(installed),
        "clean": clean_count,
        "with_issues": issue_count,
        "skills": results,
    }

    if output_json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n🛡️  ClawHub Security Sync — {timestamp}")
        print(f"   Catalog: {len(catalog)} skills indexed")
        print(f"   Installed: {len(installed)} skills found")
        print(f"   Clean: {clean_count} | Issues: {issue_count}")
        print()
        for r in results:
            icon = "✅" if r["severity"] == "none" else "⚠️" if r["severity"] in ("low", "medium", "info") else "🚨"
            hub = f"ClawHub: v{r['clawhub_latest']}, {r['clawhub_downloads']} downloads" if r["clawhub_found"] else "Not on ClawHub"
            print(f"   {icon} {r['slug']} (v{r['version']}) — {hub}")
            for issue in r["issues"]:
                print(f"      └─ [{issue['severity'].upper()}] {issue['message']}")
        print()


if __name__ == "__main__":
    main()
