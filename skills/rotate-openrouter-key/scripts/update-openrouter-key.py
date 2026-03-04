#!/usr/bin/env python3
"""
Update or verify the OpenRouter API key in all OpenClaw config files.

Usage:
  python3 update-openrouter-key.py --key "sk-or-v1-NEW-KEY"
  python3 update-openrouter-key.py --key "sk-or-v1-NEW-KEY" --verify
  python3 update-openrouter-key.py --key "sk-or-v1-NEW-KEY" --dry-run
  python3 update-openrouter-key.py --find   # just list where keys are
"""

import argparse
import json
import os
import re
import shutil
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = os.environ.get("OPENCLAW_DIR", os.path.expanduser("~/.openclaw"))


def find_json_files_with_key(base_dir: str) -> list:
    """Find all JSON files under base_dir containing an openrouter apiKey."""
    results = []
    for root, dirs, files in os.walk(base_dir):
        # Skip node_modules, .git, etc.
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for f in files:
            if not f.endswith(".json"):
                continue
            path = os.path.join(root, f)
            try:
                with open(path) as fh:
                    content = fh.read()
                if "openrouter" not in content:
                    continue
                data = json.loads(content)
                # Check nested structures for openrouter apiKey
                for root_key in [data, data.get("models", {})]:
                    if not isinstance(root_key, dict):
                        continue
                    or_cfg = root_key.get("providers", {}).get("openrouter", {})
                    if or_cfg.get("apiKey"):
                        k = or_cfg["apiKey"]
                        results.append({
                            "path": path,
                            "current_key": k,
                            "key_preview": k[:8] + "..." + k[-4:] if len(k) > 12 else "***",
                        })
                        break
            except (OSError, json.JSONDecodeError):
                continue
    return results


def find_env_key(base_dir: str):
    """Check if .env has an active (uncommented) OPENROUTER_API_KEY."""
    env_path = os.path.join(base_dir, ".env")
    if not os.path.exists(env_path):
        return None
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return {
                            "path": env_path,
                            "current_key": key,
                            "key_preview": key[:8] + "..." + key[-4:] if len(key) > 12 else "***",
                        }
    except OSError:
        pass
    return None


def backup_file(filepath: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{filepath}.bak.{ts}"
    shutil.copy2(filepath, backup)
    return backup


def update_json_key(filepath: str, new_key: str, dry_run: bool) -> bool:
    """Update openrouter apiKey in a JSON config file. Returns True if changed."""
    with open(filepath) as f:
        data = json.load(f)

    changed = False
    for root_key in [data, data.get("models", {})]:
        if not isinstance(root_key, dict):
            continue
        or_cfg = root_key.get("providers", {}).get("openrouter", {})
        if or_cfg.get("apiKey") and or_cfg["apiKey"] != new_key:
            or_cfg["apiKey"] = new_key
            changed = True

    if changed and not dry_run:
        backup_file(filepath)
        tmp = filepath + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, filepath)

    return changed


def update_env_key(filepath: str, new_key: str, dry_run: bool) -> bool:
    """Update OPENROUTER_API_KEY in a .env file. Returns True if changed."""
    with open(filepath) as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("#") and stripped.startswith("OPENROUTER_API_KEY="):
            old_val = stripped.split("=", 1)[1].strip().strip('"').strip("'")
            if old_val != new_key:
                new_lines.append(f"OPENROUTER_API_KEY={new_key}\n")
                changed = True
                continue
        new_lines.append(line)

    if changed and not dry_run:
        backup_file(filepath)
        with open(filepath, "w") as f:
            f.writelines(new_lines)

    return changed


def verify_key(key: str) -> dict:
    """Verify an OpenRouter key against the API. Returns auth info or error."""
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            info = data.get("data", {})
            return {
                "valid": True,
                "label": info.get("label", ""),
                "limit": info.get("limit"),
                "remaining": info.get("limit_remaining"),
                "is_free_tier": info.get("is_free_tier"),
                "expires_at": info.get("expires_at"),
            }
    except urllib.error.HTTPError as e:
        return {"valid": False, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def main():
    p = argparse.ArgumentParser(description="Update OpenRouter API key in OpenClaw")
    p.add_argument("--key", help="New OpenRouter API key")
    p.add_argument("--find", action="store_true", help="Just list where keys are stored")
    p.add_argument("--verify", action="store_true", help="Verify the key against OpenRouter API")
    p.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    # Find all key locations
    json_files = find_json_files_with_key(OPENCLAW_DIR)
    env_entry = find_env_key(OPENCLAW_DIR)

    all_locations = []
    if env_entry:
        all_locations.append({"type": "env", **env_entry})
    for jf in json_files:
        all_locations.append({"type": "json", **jf})

    if args.find:
        if not all_locations:
            print("No OpenRouter keys found in", OPENCLAW_DIR, file=sys.stderr)
            sys.exit(1)
        print(f"Found {len(all_locations)} key location(s):", file=sys.stderr)
        for loc in all_locations:
            priority = "HIGH (overrides JSON)" if loc["type"] == "env" else "normal"
            print(f"  [{priority}] {loc['path']} — {loc['key_preview']}", file=sys.stderr)
        if args.json:
            print(json.dumps([{"path": l["path"], "type": l["type"]} for l in all_locations]))
        return

    if not args.key:
        print("ERROR: --key is required (or use --find to list locations).", file=sys.stderr)
        sys.exit(1)

    if not args.key.startswith("sk-or-"):
        print("WARNING: Key doesn't start with 'sk-or-'. Are you sure it's an OpenRouter key?", file=sys.stderr)

    # Verify key if requested
    if args.verify:
        print("Verifying key...", file=sys.stderr)
        result = verify_key(args.key)
        if result["valid"]:
            print(f"  VALID — label: {result['label']}, remaining: ${result['remaining']:.2f}, "
                  f"free_tier: {result['is_free_tier']}, expires: {result['expires_at']}", file=sys.stderr)
        else:
            print(f"  INVALID — {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(result))
        if not all_locations:
            return  # verify-only mode

    if not all_locations:
        print("No existing OpenRouter keys found to update.", file=sys.stderr)
        sys.exit(1)

    # Update each location
    tag = "[DRY RUN] " if args.dry_run else ""
    updated = []
    skipped = []

    for loc in all_locations:
        if loc["current_key"] == args.key:
            skipped.append(loc["path"])
            print(f"  SKIP {loc['path']} (already has new key)", file=sys.stderr)
            continue

        if loc["type"] == "env":
            changed = update_env_key(loc["path"], args.key, args.dry_run)
        else:
            changed = update_json_key(loc["path"], args.key, args.dry_run)

        if changed:
            updated.append(loc["path"])
            print(f"  {tag}UPDATED {loc['path']}", file=sys.stderr)
        else:
            skipped.append(loc["path"])

    print(f"\n{tag}Updated {len(updated)} file(s), skipped {len(skipped)}.", file=sys.stderr)

    # Auto-verify after update if --verify was passed
    if args.verify and updated and not args.dry_run:
        print("\nPost-update verification...", file=sys.stderr)
        result = verify_key(args.key)
        if result["valid"]:
            print(f"  VALID — label: {result['label']}, remaining: ${result['remaining']:.2f}", file=sys.stderr)
        else:
            print(f"  INVALID — {result['error']}", file=sys.stderr)
            print("WARNING: Key failed verification. Check the key and try again.", file=sys.stderr)

    if updated and not args.dry_run:
        print("\nRun: openclaw gateway restart", file=sys.stderr)

    if args.json:
        print(json.dumps({"updated": updated, "skipped": skipped, "dry_run": args.dry_run}))


if __name__ == "__main__":
    main()
