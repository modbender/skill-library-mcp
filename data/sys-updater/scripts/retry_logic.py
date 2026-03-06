#!/usr/bin/env python3
"""Retry logic module for package upgrades with fallback handling.

Handles failed upgrade attempts and implements exponential backoff.
After 3 failed attempts, packages are automatically blocked.
"""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("retry_logic")

# Maximum retry attempts before auto-block
MAX_RETRY_ATTEMPTS = 3
# Days to wait between retry attempts
RETRY_DELAY_DAYS = 1


def now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def can_retry(item: dict) -> bool:
    """Check if package is eligible for retry.

    Args:
        item: Package metadata dict

    Returns:
        True if retry should be attempted
    """
    failed_attempts = item.get("failedAttempts", 0)

    # Max attempts reached
    if failed_attempts >= MAX_RETRY_ATTEMPTS:
        logger.debug(f"Max attempts ({MAX_RETRY_ATTEMPTS}) reached, blocking")
        return False

    # Check if enough time passed since last attempt
    last_attempt = item.get("lastAttemptAt")
    if last_attempt:
        try:
            last_dt = parse_iso(last_attempt)
            cutoff = last_dt + timedelta(days=RETRY_DELAY_DAYS)
            if datetime.now(timezone.utc) < cutoff:
                logger.debug(f"Too soon to retry, next attempt after {cutoff.isoformat()}")
                return False
        except (ValueError, TypeError):
            pass  # Invalid timestamp, allow retry

    return True


def run_command(cmd: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Run a shell command and return success status.

    Args:
        cmd: Command and arguments
        timeout: Timeout in seconds

    Returns:
        (success, error_message)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode == 0:
            return True, ""
        else:
            error = result.stderr.strip() if result.stderr else result.stdout.strip()
            # Truncate long errors
            if len(error) > 500:
                error = error[:500] + "..."
            return False, error

    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def upgrade_npm_package(name: str, dry_run: bool = False) -> tuple[bool, str]:
    """Attempt to upgrade an npm package."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would run: npm update -g {name}")
        return True, ""

    logger.info(f"Upgrading npm package: {name}")
    return run_command(["npm", "update", "-g", name], timeout=120)


def upgrade_brew_package(name: str, dry_run: bool = False) -> tuple[bool, str]:
    """Attempt to upgrade a brew package."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would run: brew upgrade {name}")
        return True, ""

    logger.info(f"Upgrading brew package: {name}")
    return run_command(["brew", "upgrade", name], timeout=120)


def upgrade_pnpm_package(name: str, dry_run: bool = False) -> tuple[bool, str]:
    """Attempt to upgrade a pnpm global package."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would run: pnpm update -g {name}")
        return True, ""

    logger.info(f"Upgrading pnpm package: {name}")
    return run_command(["pnpm", "update", "-g", name], timeout=120)


def retry_upgrade(
    name: str,
    manager: str,
    meta: dict,
    dry_run: bool = False
) -> dict:
    """Attempt to upgrade a package with retry tracking."""
    updated = meta.copy()

    # Check if we should retry
    if not can_retry(meta):
        failed_attempts = meta.get("failedAttempts", 0)
        if failed_attempts >= MAX_RETRY_ATTEMPTS:
            updated["blocked"] = True
            updated["reviewResult"] = "blocked"
            updated["reviewedBy"] = "auto"
            updated["note"] = f"Auto-blocked after {MAX_RETRY_ATTEMPTS} failed upgrade attempts"
            logger.warning(f"🚫 {manager}/{name}: Auto-blocked after {MAX_RETRY_ATTEMPTS} failures")
        return updated

    # Attempt upgrade
    if manager == "npm":
        success, error = upgrade_npm_package(name, dry_run=dry_run)
    elif manager == "brew":
        success, error = upgrade_brew_package(name, dry_run=dry_run)
    elif manager == "pnpm":
        success, error = upgrade_pnpm_package(name, dry_run=dry_run)
    else:
        logger.error(f"Unknown manager: {manager}")
        return updated

    # Update metadata based on result
    updated["lastAttemptAt"] = now_iso()

    if success:
        # Success: reset counters and mark as upgraded
        updated["failedAttempts"] = 0
        updated["planned"] = False
        updated["reviewResult"] = "ok"
        updated["reviewedBy"] = "auto"
        updated["note"] = "Successfully upgraded"
        logger.info(f"✅ {manager}/{name}: Upgrade successful")
    else:
        # Failure: increment counter
        failed_attempts = updated.get("failedAttempts", 0) + 1
        updated["failedAttempts"] = failed_attempts
        updated["note"] = f"Upgrade failed (attempt {failed_attempts}/{MAX_RETRY_ATTEMPTS}): {error[:200]}"
        logger.warning(f"❌ {manager}/{name}: Upgrade failed (attempt {failed_attempts}/{MAX_RETRY_ATTEMPTS}): {error[:100]}")

        # Auto-block if max attempts reached
        if failed_attempts >= MAX_RETRY_ATTEMPTS:
            updated["blocked"] = True
            updated["planned"] = False
            updated["reviewResult"] = "blocked"
            updated["reviewedBy"] = "auto"
            updated["note"] = f"Auto-blocked after {MAX_RETRY_ATTEMPTS} failed attempts. Last error: {error[:200]}"
            logger.error(f"🚫 {manager}/{name}: Auto-blocked after {MAX_RETRY_ATTEMPTS} failures")

    return updated


def process_retries(
    npm_tracked_path: Path,
    brew_tracked_path: Path,
    pnpm_tracked_path: Path | None = None,
    dry_run: bool = False
) -> dict[str, Any]:
    """Process pending retries for npm/brew/pnpm."""
    summary = {
        "npm": {"attempted": 0, "succeeded": 0, "failed": 0, "blocked": 0},
        "brew": {"attempted": 0, "succeeded": 0, "failed": 0, "blocked": 0},
        "pnpm": {"attempted": 0, "succeeded": 0, "failed": 0, "blocked": 0},
        "details": [],
    }

    def load(path: Path, label: str) -> dict[str, Any]:
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
    pnpm_data = load(pnpm_tracked_path, "pnpm_tracked.json") if pnpm_tracked_path else {}

    npm_items = npm_data.get("items", {})
    brew_items = brew_data.get("items", {})
    pnpm_items = pnpm_data.get("items", {})

    def queue(items: dict[str, Any]):
        return [
            (name, meta) for name, meta in items.items()
            if meta.get("planned") and meta.get("failedAttempts", 0) > 0 and not meta.get("blocked")
        ]

    npm_retries = queue(npm_items)
    brew_retries = queue(brew_items)
    pnpm_retries = queue(pnpm_items)

    logger.info(
        "Retry queue: %d npm, %d brew, %d pnpm packages",
        len(npm_retries), len(brew_retries), len(pnpm_retries)
    )

    def process(manager: str, retries: list[tuple[str, dict]], items: dict[str, Any]) -> None:
        for name, meta in retries:
            summary[manager]["attempted"] += 1
            updated = retry_upgrade(name, manager, meta, dry_run=dry_run)
            items[name] = updated

            if not updated.get("failedAttempts"):
                summary[manager]["succeeded"] += 1
                summary["details"].append({"name": name, "manager": manager, "result": "success"})
            elif updated.get("blocked"):
                summary[manager]["blocked"] += 1
                summary["details"].append({
                    "name": name,
                    "manager": manager,
                    "result": "blocked",
                    "reason": updated.get("note", ""),
                })
            else:
                summary[manager]["failed"] += 1
                summary["details"].append({
                    "name": name,
                    "manager": manager,
                    "result": "failed",
                    "attempt": updated.get("failedAttempts", 0),
                })

    process("npm", npm_retries, npm_items)
    process("brew", brew_retries, brew_items)
    process("pnpm", pnpm_retries, pnpm_items)

    if not dry_run:
        now = now_iso()
        npm_data["items"] = npm_items
        brew_data["items"] = brew_items
        npm_data["lastRetryRun"] = now
        brew_data["lastRetryRun"] = now
        if pnpm_tracked_path:
            pnpm_data["items"] = pnpm_items
            pnpm_data["lastRetryRun"] = now

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

    total_attempted = summary["npm"]["attempted"] + summary["brew"]["attempted"] + summary["pnpm"]["attempted"]
    total_succeeded = summary["npm"]["succeeded"] + summary["brew"]["succeeded"] + summary["pnpm"]["succeeded"]
    total_failed = summary["npm"]["failed"] + summary["brew"]["failed"] + summary["pnpm"]["failed"]
    total_blocked = summary["npm"]["blocked"] + summary["brew"]["blocked"] + summary["pnpm"]["blocked"]

    logger.info(
        "Retry processing complete: %d attempted, %d succeeded, %d failed, %d blocked",
        total_attempted, total_succeeded, total_failed, total_blocked
    )

    return summary


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Retry failed package upgrades")
    ap.add_argument("--npm-path", type=Path, default=Path("/home/moltuser/clawd/sys-updater/state/apt/npm_tracked.json"))
    ap.add_argument("--brew-path", type=Path, default=Path("/home/moltuser/clawd/sys-updater/state/apt/brew_tracked.json"))
    ap.add_argument("--pnpm-path", type=Path, default=Path("/home/moltuser/clawd/sys-updater/state/apt/pnpm_tracked.json"))
    ap.add_argument("--dry-run", "-n", action="store_true", help="Don't actually upgrade")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    result = process_retries(args.npm_path, args.brew_path, args.pnpm_path, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
