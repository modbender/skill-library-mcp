#!/usr/bin/env python3
"""Agent GitOps — deployment, rollback, and version management for agent skills.

Tracks skill versions using git, enables fast rollback, and optionally
integrates with arc-skill-scanner for pre-deploy security checks.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = os.path.expanduser("~/.openclaw/gitops")
MANIFEST_PATH = os.path.join(DATA_DIR, "manifest.json")


import re


def _sanitize_tag(tag):
    """Validate tag name contains only safe characters."""
    if not re.match(r'^[a-zA-Z0-9._-]+$', tag):
        print(f"Error: Invalid tag name: {tag!r} — only alphanumeric, dot, dash, underscore allowed", file=sys.stderr)
        sys.exit(1)
    if '..' in tag:
        print(f"Error: Tag name cannot contain '..': {tag!r}", file=sys.stderr)
        sys.exit(1)
    return tag


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_manifest():
    ensure_data_dir()
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"skills": {}}


def save_manifest(manifest):
    ensure_data_dir()
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def git(skill_path, *args):
    """Run a git command in the skill directory."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=skill_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


def resolve_skill_path(path):
    """Resolve and validate skill path."""
    resolved = os.path.realpath(os.path.expanduser(path))
    if not os.path.isdir(resolved):
        print(f"Error: {resolved} is not a directory", file=sys.stderr)
        sys.exit(1)
    skill_md = os.path.join(resolved, "SKILL.md")
    if not os.path.exists(skill_md):
        print(f"Warning: No SKILL.md found in {resolved} — may not be an OpenClaw skill", file=sys.stderr)
    return resolved


def skill_name(path):
    """Extract skill name from path."""
    return os.path.basename(path)


def cmd_init(args):
    """Initialize gitops tracking for a skill."""
    path = resolve_skill_path(args.skill)
    name = skill_name(path)

    # Initialize git repo if not already one
    git_dir = os.path.join(path, ".git")
    if not os.path.isdir(git_dir):
        result = git(path, "init")
        if result.returncode != 0:
            print(f"Error initializing git: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        # Create .gitignore for common noise
        gitignore = os.path.join(path, ".gitignore")
        if not os.path.exists(gitignore):
            with open(gitignore, "w") as f:
                f.write("__pycache__/\n*.pyc\n.DS_Store\n")
        # Initial commit
        git(path, "add", "-A")
        git(path, "commit", "-m", "Initial snapshot (gitops init)")
        print(f"Initialized git repo in {path}")
    else:
        print(f"Git repo already exists in {path}")

    # Add to manifest
    manifest = load_manifest()
    manifest["skills"][name] = {
        "path": path,
        "initialized_at": datetime.now(timezone.utc).isoformat(),
        "snapshots": [],
    }
    save_manifest(manifest)
    print(f"Tracking {name} at {path}")


def cmd_snapshot(args):
    """Take a snapshot of the current skill state."""
    path = resolve_skill_path(args.skill)
    name = skill_name(path)
    tag = _sanitize_tag(args.tag) if args.tag else f"snap-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    # Ensure git repo exists
    if not os.path.isdir(os.path.join(path, ".git")):
        print(f"Error: {path} is not initialized. Run 'gitops init' first.", file=sys.stderr)
        sys.exit(1)

    # Stage and commit
    git(path, "add", "-A")
    result = git(path, "commit", "-m", f"Snapshot: {tag}")
    if result.returncode != 0 and "nothing to commit" in result.stdout:
        print(f"No changes to snapshot for {name}")
        # Still create the tag for reference
    else:
        print(f"Committed changes for {name}")

    # Create git tag
    git(path, "tag", "-f", tag)
    print(f"Tagged as '{tag}'")

    # Update manifest
    manifest = load_manifest()
    if name in manifest["skills"]:
        manifest["skills"][name]["snapshots"].append({
            "tag": tag,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        save_manifest(manifest)


def cmd_deploy(args):
    """Deploy a skill update with automatic pre-snapshot."""
    path = resolve_skill_path(args.skill)
    name = skill_name(path)
    tag = _sanitize_tag(args.tag) if args.tag else f"deploy-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    # Pre-deploy snapshot
    pre_tag = f"pre-{tag}"
    print(f"Taking pre-deploy snapshot as '{pre_tag}'...")
    git(path, "add", "-A")
    result = git(path, "commit", "-m", f"Pre-deploy snapshot: {pre_tag}")
    git(path, "tag", "-f", pre_tag)

    # Run pre-deploy checks if requested
    if not args.skip_check:
        scanner_path = os.path.expanduser("~/.openclaw/skills/skill-scanner/scripts/scanner.py")
        if os.path.exists(scanner_path):
            print("Running pre-deploy security scan...")
            scan_result = subprocess.run(
                ["python3", scanner_path, "scan", "--path", path, "--format", "json"],
                capture_output=True, text=True, timeout=60,
            )
            if scan_result.returncode == 0:
                try:
                    scan_data = json.loads(scan_result.stdout)
                    severity = scan_data.get("severity", "UNKNOWN")
                    if severity == "CRITICAL":
                        print(f"BLOCKED: Critical security findings. Fix before deploying.", file=sys.stderr)
                        print(f"Scan output: {scan_result.stdout}")
                        sys.exit(1)
                    elif severity in ("HIGH", "MEDIUM"):
                        print(f"Warning: {severity} severity findings detected. Review recommended.")
                    else:
                        print(f"Security scan: {severity}")
                except json.JSONDecodeError:
                    print(f"Scanner output: {scan_result.stdout[:200]}")
            else:
                print(f"Scanner failed (non-blocking): {scan_result.stderr[:200]}")
        else:
            print("arc-skill-scanner not found — skipping security check")

    # Commit the deploy
    git(path, "add", "-A")
    result = git(path, "commit", "-m", f"Deploy: {tag}")
    git(path, "tag", "-f", tag)

    # Update manifest
    manifest = load_manifest()
    if name in manifest["skills"]:
        manifest["skills"][name]["snapshots"].append({
            "tag": tag,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "deploy",
        })
        manifest["skills"][name]["current_tag"] = tag
        save_manifest(manifest)

    print(f"Deployed {name} as '{tag}'")


def cmd_rollback(args):
    """Roll back to a previous snapshot."""
    path = resolve_skill_path(args.skill)
    name = skill_name(path)
    tag = _sanitize_tag(args.tag) if args.tag else None

    if not tag:
        print("Error: --tag is required for rollback", file=sys.stderr)
        sys.exit(1)

    # Check tag exists
    result = git(path, "tag", "-l", tag)
    if tag not in result.stdout:
        print(f"Error: Tag '{tag}' not found", file=sys.stderr)
        # Show available tags
        all_tags = git(path, "tag", "-l")
        if all_tags.stdout.strip():
            print(f"Available tags: {all_tags.stdout.strip()}")
        sys.exit(1)

    # Snapshot current state before rollback
    rollback_pre_tag = f"pre-rollback-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    git(path, "add", "-A")
    git(path, "commit", "-m", f"Pre-rollback snapshot: {rollback_pre_tag}")
    git(path, "tag", "-f", rollback_pre_tag)

    # Perform rollback
    result = git(path, "checkout", tag, "--", ".")
    if result.returncode != 0:
        print(f"Error during rollback: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    git(path, "add", "-A")
    git(path, "commit", "-m", f"Rollback to: {tag}")

    # Update manifest
    manifest = load_manifest()
    if name in manifest["skills"]:
        manifest["skills"][name]["snapshots"].append({
            "tag": f"rollback-to-{tag}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "rollback",
            "target": tag,
        })
        manifest["skills"][name]["current_tag"] = tag
        save_manifest(manifest)

    print(f"Rolled back {name} to '{tag}'")
    print(f"Pre-rollback state saved as '{rollback_pre_tag}'")


def cmd_history(args):
    """Show snapshot history for a skill."""
    path = resolve_skill_path(args.skill)
    name = skill_name(path)

    manifest = load_manifest()
    skill_data = manifest.get("skills", {}).get(name)
    if not skill_data:
        print(f"No tracking data for {name}. Run 'gitops init' first.")
        return

    snapshots = skill_data.get("snapshots", [])
    current = skill_data.get("current_tag", "unknown")

    print(f"Skill: {name}")
    print(f"Path: {skill_data['path']}")
    print(f"Current: {current}")
    print(f"Snapshots ({len(snapshots)}):")

    for snap in reversed(snapshots[-20:]):
        marker = " <-- current" if snap["tag"] == current else ""
        snap_type = snap.get("type", "snapshot")
        print(f"  [{snap_type}] {snap['tag']} — {snap['timestamp']}{marker}")


def cmd_status(args):
    """Show status of all tracked skills."""
    manifest = load_manifest()
    skills = manifest.get("skills", {})

    if not skills:
        print("No skills tracked. Use 'gitops init --skill <path>' to start tracking.")
        return

    print(f"Tracked skills: {len(skills)}")
    print()

    for name, data in skills.items():
        path = data["path"]
        exists = os.path.isdir(path)
        current = data.get("current_tag", "initial")
        snap_count = len(data.get("snapshots", []))

        status_icon = "OK" if exists else "MISSING"
        # Check for uncommitted changes
        if exists and os.path.isdir(os.path.join(path, ".git")):
            diff = git(path, "status", "--porcelain")
            if diff.stdout.strip():
                status_icon = "MODIFIED"

        print(f"  [{status_icon}] {name}")
        print(f"    Path: {path}")
        print(f"    Version: {current} | Snapshots: {snap_count}")
        print()


def cmd_check(args):
    """Run pre-deploy checks on a skill."""
    path = resolve_skill_path(args.skill)
    name = skill_name(path)

    scanner_path = os.path.expanduser("~/.openclaw/skills/skill-scanner/scripts/scanner.py")
    if not os.path.exists(scanner_path):
        print("arc-skill-scanner not installed. Install it from ClawHub for security checks.")
        print("Manual review recommended before deploying.")
        return

    print(f"Scanning {name}...")
    result = subprocess.run(
        ["python3", scanner_path, "scan", "--path", path],
        capture_output=True, text=True, timeout=60,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent GitOps — deployment and rollback for agent skills"
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    p_init = subparsers.add_parser("init", help="Initialize tracking for a skill")
    p_init.add_argument("--skill", required=True, help="Path to skill directory")

    # snapshot
    p_snap = subparsers.add_parser("snapshot", help="Snapshot current state")
    p_snap.add_argument("--skill", required=True, help="Path to skill directory")
    p_snap.add_argument("--tag", help="Tag name for this snapshot")

    # deploy
    p_deploy = subparsers.add_parser("deploy", help="Deploy with auto-snapshot")
    p_deploy.add_argument("--skill", required=True, help="Path to skill directory")
    p_deploy.add_argument("--tag", help="Tag name for this deploy")
    p_deploy.add_argument("--skip-check", action="store_true", help="Skip security scan")

    # rollback
    p_roll = subparsers.add_parser("rollback", help="Roll back to a snapshot")
    p_roll.add_argument("--skill", required=True, help="Path to skill directory")
    p_roll.add_argument("--tag", required=True, help="Tag to roll back to")

    # history
    p_hist = subparsers.add_parser("history", help="Show snapshot history")
    p_hist.add_argument("--skill", required=True, help="Path to skill directory")

    # status
    p_status = subparsers.add_parser("status", help="Status of all tracked skills")

    # check
    p_check = subparsers.add_parser("check", help="Run pre-deploy security check")
    p_check.add_argument("--skill", required=True, help="Path to skill directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "snapshot": cmd_snapshot,
        "deploy": cmd_deploy,
        "rollback": cmd_rollback,
        "history": cmd_history,
        "status": cmd_status,
        "check": cmd_check,
    }

    commands[args.command](args)
