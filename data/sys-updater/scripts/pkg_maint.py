#!/usr/bin/env python3
"""Package manager maintenance helper for OpenClaw host (sys-updater extension).

Extends apt_maint.py to support npm and brew package managers with
the same conservative workflow: track -> review after 2 days -> upgrade.

Modes:
- check: Update tracked state (run during run_6am)
- review: Review packages for bugs/risks (manual or cron after 2 days)
- upgrade: Apply planned upgrades (manual or auto after review)

Conservative by design:
- Non-security upgrades are tracked for 2 days before auto-upgrade
- User can block packages with known bugs
- Security updates (not typical for npm/brew) would need manual handling
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable

from managers.adapters import build_manager_registry

# === Directories (same as apt_maint.py) ===
BASE_DIR = Path(os.getenv("SYS_UPDATER_BASE_DIR", "/home/moltuser/clawd/sys-updater"))
STATE_DIR = Path(os.getenv("SYS_UPDATER_STATE_DIR", BASE_DIR / "state" / "apt"))
LOG_DIR = Path(os.getenv("SYS_UPDATER_LOG_DIR", BASE_DIR / "state" / "logs"))

NPM_TRACK_PATH = STATE_DIR / "npm_tracked.json"
PNPM_TRACK_PATH = STATE_DIR / "pnpm_tracked.json"
BREW_TRACK_PATH = STATE_DIR / "brew_tracked.json"

REVIEW_DAYS = 2  # Same as apt policy
AUTO_PLAN_PENDING_AFTER_DAYS = 4  # Escalate long-pending items to planned

# ClawHub / OpenClaw skills - update immediately without quarantine
SKILLS_WORKDIR = Path(os.getenv("CLAWHUB_WORKDIR", "/home/moltuser/clawd"))
SKILLS_DIR = SKILLS_WORKDIR / "skills"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("pkg_maint")


def sh(cmd: list[str], check: bool = False, timeout: int = 60) -> tuple[int, str, str]:
    """Run command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, text=True, capture_output=True, check=check, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def check_npm() -> dict[str, Any]:
    """Check for outdated npm global packages."""
    result = {"installed": False, "outdated": []}
    
    rc, _, _ = sh(["npm", "--version"])
    if rc != 0:
        return result
    
    result["installed"] = True
    rc, stdout, stderr = sh(["npm", "outdated", "-g", "--json", "--depth=0"], timeout=30)
    
    if rc not in (0, 1):
        log.warning("npm outdated failed: %s", stderr)
        return result
    
    try:
        data = json.loads(stdout) if stdout else {}
        for pkg, info in data.items():
            result["outdated"].append({
                "name": pkg,
                "current": info.get("current", "?"),
                "wanted": info.get("wanted", "?"),
                "latest": info.get("latest", "?"),
                "location": info.get("location", "global"),
            })
    except json.JSONDecodeError:
        log.warning("Failed to parse npm outdated output")
    
    return result


def check_pnpm() -> dict[str, Any]:
    """Check for outdated pnpm global packages."""
    result = {"installed": False, "outdated": []}

    rc, _, _ = sh(["pnpm", "--version"])
    if rc != 0:
        return result

    result["installed"] = True
    rc, stdout, stderr = sh(["pnpm", "outdated", "-g", "--json"], timeout=30)
    if rc == 1 and "ERR_PNPM_NO_IMPORTER_MANIFEST_FOUND" in ((stderr or "") + (stdout or "")):
        # No pnpm global store initialized yet; treat as no outdated packages.
        return result
    if rc not in (0, 1):
        log.warning("pnpm outdated failed: %s", stderr)
        return result

    try:
        data = json.loads(stdout) if stdout else {}
        if isinstance(data, dict):
            iterable = data.items()
            for pkg, info in iterable:
                if not isinstance(info, dict):
                    continue
                result["outdated"].append({
                    "name": pkg,
                    "current": info.get("current", "?"),
                    "wanted": info.get("wanted", "?"),
                    "latest": info.get("latest", "?"),
                    "location": info.get("location", "global"),
                })
        elif isinstance(data, list):
            # Fallback shape used by some pnpm versions
            for info in data:
                if not isinstance(info, dict):
                    continue
                name = info.get("name")
                if not name:
                    continue
                result["outdated"].append({
                    "name": name,
                    "current": info.get("current", "?"),
                    "wanted": info.get("wanted", "?"),
                    "latest": info.get("latest", "?"),
                    "location": "global",
                })
    except json.JSONDecodeError:
        log.warning("Failed to parse pnpm outdated output")

    return result


def check_brew() -> dict[str, Any]:
    """Check for outdated brew packages."""
    result = {"installed": False, "outdated": []}
    
    rc, _, _ = sh(["brew", "--version"])
    if rc != 0:
        return result
    
    result["installed"] = True
    rc, stdout, stderr = sh(["brew", "outdated", "--json"], timeout=30)
    
    if rc != 0:
        log.warning("brew outdated failed: %s", stderr)
        return result
    
    try:
        data = json.loads(stdout) if stdout else {}
        for pkg in data.get("formulae", []):
            result["outdated"].append({
                "name": pkg.get("name"),
                "current": pkg.get("installed_versions", ["?"])[0],
                "latest": pkg.get("current_version", "?"),
                "type": "formula",
            })
        for pkg in data.get("casks", []):
            result["outdated"].append({
                "name": pkg.get("name"),
                "current": pkg.get("installed_versions", ["?"])[0],
                "latest": pkg.get("current_version", "?"),
                "type": "cask",
            })
    except json.JSONDecodeError:
        log.warning("Failed to parse brew outdated output")
    
    return result


def check_skills() -> dict[str, Any]:
    """Check for outdated ClawHub/OpenClaw skills and update immediately."""
    result = {"installed": False, "checked": [], "updated": [], "failed": []}
    
    # Check clawhub is available
    rc, _, _ = sh(["clawhub", "--version"])
    if rc != 0:
        log.debug("clawhub not available")
        return result
    
    result["installed"] = True
    
    # Get list of installed skills
    rc, stdout, stderr = sh(["clawhub", "list", "--json"], timeout=30)
    if rc != 0:
        log.warning("clawhub list failed: %s", stderr)
        return result
    
    try:
        skills = json.loads(stdout) if stdout else []
    except json.JSONDecodeError:
        log.warning("Failed to parse clawhub list output")
        return result
    
    if not skills:
        log.info("No skills installed")
        return result
    
    # Check each skill for updates
    for skill in skills:
        slug = skill.get("slug") or skill.get("name")
        if not slug:
            continue
        
        result["checked"].append(slug)
        current_version = skill.get("version", "?")
        
        log.info("Checking skill: %s (current: %s)", slug, current_version)
        
        # Try to update (clawhub update will skip if already latest)
        rc, stdout, stderr = sh(["clawhub", "update", slug], timeout=120)
        
        if rc == 0:
            # Check if actually updated by looking for upgrade message
            if "upgraded" in stdout.lower() or "updated" in stdout.lower():
                log.info("Updated skill: %s", slug)
                result["updated"].append({
                    "name": slug,
                    "previous": current_version,
                    "status": "updated"
                })
            else:
                log.debug("Skill %s already up to date", slug)
        else:
            log.error("Failed to update skill %s: %s", slug, stderr[:200])
            result["failed"].append({"name": slug, "error": stderr[:200]})
    
    return result


def upgrade_skills(dry_run: bool = False) -> str:
    """Upgrade all skills immediately (no quarantine for skills)."""
    log.info("=== SKILLS UPGRADE START (dry_run=%s) ===", dry_run)
    
    if dry_run:
        # clawhub doesn't support --dry-run, just list skills
        rc, stdout, stderr = sh(["clawhub", "list"], timeout=60)
        if rc != 0:
            return f"❌ clawhub list failed: {stderr[:200]}"
        
        lines = ["🔍 Skills (dry-run not supported by clawhub):"]
        lines.append("Will check and update all installed skills")
        lines.append("\nInstalled skills:")
        lines.append(stdout if stdout else "No skills found")
        return "\n".join(lines)
    
    # Real update
    result = check_skills()
    
    lines = ["📦 Обновление скиллов OpenClaw:"]
    
    if result["updated"]:
        lines.append(f"✅ Обновлено: {len(result['updated'])}")
        for skill in result["updated"]:
            lines.append(f"   - {skill['name']}")
    
    if result["failed"]:
        lines.append(f"❌ Ошибки: {len(result['failed'])}")
        for skill in result["failed"]:
            lines.append(f"   - {skill['name']}: {skill['error'][:80]}")
    
    if not result["updated"] and not result["failed"]:
        lines.append("✓ Все скиллы актуальны")
    
    log.info("Skills: checked=%d, updated=%d, failed=%d",
             len(result["checked"]), len(result["updated"]), len(result["failed"]))
    log.info("=== SKILLS UPGRADE END ===")
    return "\n".join(lines)


def load_tracked(path: Path) -> dict:
    """Load tracked packages state."""
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Failed to load %s: %s", path, e)
    return {"items": {}, "lastCheck": None, "createdAt": now_iso()}


def save_tracked(path: Path, data: dict) -> None:
    """Save tracked packages state."""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error("Failed to save %s: %s", path, e)


def update_tracked(
    tracked: dict,
    current_outdated: list[dict],
    manager: str
) -> tuple[dict, int, int]:
    """Update tracked packages with current state. Returns (tracked, new_count, removed_count)."""
    items = tracked.get("items", {})
    now = now_iso()
    new_count = 0
    
    # Mark packages no longer outdated
    # NOTE: Keep packages that are still outdated to preserve firstSeenAt timer
    current_names = {p["name"] for p in current_outdated}
    to_remove = []
    for name in list(items.keys()):
        if name not in current_names:
            # Only remove if no longer outdated AND no user decision made
            if not items[name].get("blocked") and not items[name].get("planned"):
                to_remove.append(name)
        # If name IS in current_names (still outdated), keep it to preserve timer
    
    for name in to_remove:
        del items[name]
        log.info("Removed %s from tracking (no longer outdated)", name)
    
    # Add/update outdated packages
    for pkg in current_outdated:
        name = pkg["name"]
        if name not in items:
            new_count += 1
            items[name] = {
                "firstSeenAt": now,
                "reviewedAt": None,
                "planned": False,
                "blocked": False,
                "note": None,
            }
            log.info("Added %s to tracking (first seen)", name)
        
        items[name]["currentVersion"] = pkg.get("current", "?")
        items[name]["latestVersion"] = pkg.get("latest", pkg.get("wanted", "?"))
        items[name]["type"] = pkg.get("type", "package")
        items[name]["manager"] = manager
    
    tracked["items"] = items
    tracked["lastCheck"] = now
    return tracked, new_count, len(to_remove)


def is_due_for_review(item: dict, days: int = REVIEW_DAYS) -> bool:
    """Check if package is due for review (firstSeenAt + days has passed)."""
    first_seen = item.get("firstSeenAt")
    if not first_seen:
        return False

    try:
        first_dt = parse_iso(first_seen)
        cutoff = first_dt + timedelta(days=days)
        return now_utc() >= cutoff
    except (ValueError, TypeError):
        return False


def auto_plan_long_pending(tracked: dict, manager: str, days: int = AUTO_PLAN_PENDING_AFTER_DAYS) -> int:
    """Escalate long-pending items to planned upgrades.

    Policy:
    - only items with reviewResult == "pending"
    - not blocked
    - not already planned
    - older than `days` since firstSeenAt
    """
    changed = 0
    items = tracked.get("items", {})
    now = now_utc()

    for name, meta in items.items():
        if meta.get("blocked") or meta.get("planned"):
            continue
        if meta.get("reviewResult") != "pending":
            continue

        first_seen = meta.get("firstSeenAt")
        if not first_seen:
            continue

        try:
            first_dt = parse_iso(first_seen)
        except (ValueError, TypeError):
            continue

        if (now - first_dt) < timedelta(days=days):
            continue

        meta["planned"] = True
        note = meta.get("note") or ""
        suffix = f"Auto-planned after pending>{days}d"
        meta["note"] = f"{note}; {suffix}" if note else suffix
        meta["reviewedBy"] = meta.get("reviewedBy") or "auto"
        changed += 1
        log.info("Auto-planned long-pending %s/%s (firstSeenAt=%s)", manager, name, first_seen)

    return changed


MANAGER_ADAPTERS = build_manager_registry(
    npm_path=NPM_TRACK_PATH,
    pnpm_path=PNPM_TRACK_PATH,
    brew_path=BREW_TRACK_PATH,
    check_npm=check_npm,
    check_pnpm=check_pnpm,
    check_brew=check_brew,
)
MANAGER_ORDER = [m.name for m in MANAGER_ADAPTERS]
MANAGER_TRACK_PATHS: dict[str, Path] = {m.name: m.track_path for m in MANAGER_ADAPTERS}
MANAGER_CHECKERS: dict[str, Callable[[], dict[str, Any]]] = {m.name: m.check_fn for m in MANAGER_ADAPTERS}
MANAGER_TITLES: dict[str, str] = {m.name: m.title for m in MANAGER_ADAPTERS}


def _manager_title(manager: str) -> str:
    return MANAGER_TITLES.get(manager, manager.upper())


def _load_all_tracked() -> dict[str, dict[str, Any]]:
    return {m: load_tracked(MANAGER_TRACK_PATHS[m]) for m in MANAGER_ORDER}


def _save_all_tracked(tracked_by_manager: dict[str, dict[str, Any]]) -> None:
    for manager in MANAGER_ORDER:
        save_tracked(MANAGER_TRACK_PATHS[manager], tracked_by_manager[manager])


def _count_flag(tracked_by_manager: dict[str, dict[str, Any]], flag: str) -> int:
    total = 0
    for manager in MANAGER_ORDER:
        total += sum(1 for v in tracked_by_manager[manager].get("items", {}).values() if v.get(flag))
    return total


def check_mode() -> None:
    """Run check mode: update tracked state for all managers."""
    log.info("=== CHECK MODE START ===")
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    tracked_by_manager = _load_all_tracked()

    for manager in MANAGER_ORDER:
        log.info("Checking %s packages...", manager)
        result = MANAGER_CHECKERS[manager]()
        tracked = tracked_by_manager[manager]
        tracked, new_count, removed_count = update_tracked(tracked, result["outdated"], manager)
        tracked_by_manager[manager] = tracked
        save_tracked(MANAGER_TRACK_PATHS[manager], tracked)
        log.info(
            "%s: %d outdated (%d new, %d removed)",
            _manager_title(manager),
            len(result["outdated"]),
            new_count,
            removed_count,
        )

    planned_count = _count_flag(tracked_by_manager, "planned")
    blocked_count = _count_flag(tracked_by_manager, "blocked")
    log.info("Summary: planned=%d, blocked=%d", planned_count, blocked_count)

    # Update skills immediately (no quarantine for skills)
    log.info("Updating OpenClaw skills...")
    skills_result = check_skills()
    if skills_result["installed"]:
        log.info("Skills: checked=%d, updated=%d, failed=%d",
                 len(skills_result["checked"]), len(skills_result["updated"]), len(skills_result["failed"]))
    else:
        log.info("clawhub not available, skipping skills")

    log.info("=== CHECK MODE END ===")


def review_mode() -> str:
    """Review packages due for review (2+ days old)."""
    log.info("=== REVIEW MODE START ===")

    tracked_by_manager = _load_all_tracked()
    review_list: list[dict[str, Any]] = []

    for manager in MANAGER_ORDER:
        for name, meta in tracked_by_manager[manager].get("items", {}).items():
            if meta.get("reviewedAt") or meta.get("blocked") or meta.get("planned"):
                continue
            if not is_due_for_review(meta):
                continue
            review_list.append({
                "name": name,
                "manager": manager,
                "current": meta.get("currentVersion", "?"),
                "latest": meta.get("latestVersion", "?"),
                "firstSeen": meta.get("firstSeenAt"),
                "type": meta.get("type", "package"),
            })

    if not review_list:
        log.info("No packages due for review")
        return "Нет пакетов для ревью (все новые, не прошло 2 дня, или уже обработаны)."

    lines = ["📋 Пакеты для ревью (прошло 2+ дней):"]
    for pkg in review_list:
        lines.append(f"  - {pkg['name']} ({pkg['manager']}): {pkg['current']} → {pkg['latest']}")

    lines.append("")
    lines.append("🔍 Рекомендация: проверь эти пакеты на наличие багов/регрессий")
    lines.append("   перед автоматическим обновлением.")
    lines.append("")
    lines.append("Действия:")
    lines.append("  1. Поискать 'package_name latest version bug regression' в Google")
    lines.append("  2. Если найдены серьезные проблемы → заблокировать")
    lines.append("  3. Если всё чисто → пометить planned=True для обновления")

    log.info("Found %d packages for review", len(review_list))
    return "\n".join(lines)


def _upgrade_node_manager(
    manager: str,
    tracked: dict[str, Any],
    dry_run: bool,
    upgraded: list[str],
    failed: list[tuple[str, str, str]],
) -> None:
    """Upgrade planned npm/pnpm packages with shared logic."""
    cmd_prefix = [manager, "update", "-g"]

    for name, meta in tracked.get("items", {}).items():
        if not meta.get("planned") or meta.get("blocked"):
            continue

        log.info("Upgrading %s package: %s", manager, name)
        if dry_run:
            log.info("[DRY-RUN] Would run: %s", " ".join([*cmd_prefix, name]))
            upgraded.append(name)
            continue

        rc, stdout, stderr = sh([*cmd_prefix, name], timeout=120)
        if rc == 0:
            log.info("Successfully upgraded %s", name)
            upgraded.append(name)
            meta["planned"] = False
            meta["failedAttempts"] = 0
            meta["lastAttemptAt"] = now_iso()
            continue

        err = (stderr or stdout or f"{manager} update failed").strip()
        meta["failedAttempts"] = int(meta.get("failedAttempts", 0)) + 1
        meta["lastAttemptAt"] = now_iso()
        log.error("Failed to upgrade %s: %s", name, err[:200])
        failed.append((name, manager, err[:200]))


def upgrade_mode(dry_run: bool = False) -> str:
    """Apply planned upgrades. Same as apt workflow.

    Enhancements:
    - Auto-plan long-pending review items (pending > AUTO_PLAN_PENDING_AFTER_DAYS)
    - Brew link-error recovery retry
    - Post-upgrade recheck to sync tracked state with actual outdated lists
    """
    log.info("=== UPGRADE MODE START (dry_run=%s) ===", dry_run)

    tracked_by_manager = _load_all_tracked()

    # Escalate long-pending items to planned so they don't stall forever.
    auto_planned_by_manager: dict[str, int] = {
        manager: auto_plan_long_pending(tracked_by_manager[manager], manager)
        for manager in MANAGER_ORDER
    }

    npm_upgraded: list[str] = []
    pnpm_upgraded: list[str] = []
    brew_upgraded: list[str] = []
    failed: list[tuple[str, str, str]] = []

    _upgrade_node_manager("npm", tracked_by_manager["npm"], dry_run, npm_upgraded, failed)
    _upgrade_node_manager("pnpm", tracked_by_manager["pnpm"], dry_run, pnpm_upgraded, failed)

    brew_tracked = tracked_by_manager["brew"]

    # Upgrade brew packages marked as planned
    for name, meta in brew_tracked.get("items", {}).items():
        if not meta.get("planned") or meta.get("blocked"):
            continue

        log.info("Upgrading brew package: %s", name)
        if dry_run:
            log.info("[DRY-RUN] Would run: brew upgrade %s", name)
            brew_upgraded.append(name)
            continue

        rc, stdout, stderr = sh(["brew", "upgrade", name], timeout=120)
        if rc == 0:
            log.info("Successfully upgraded %s", name)
            brew_upgraded.append(name)
            meta["planned"] = False
            meta["failedAttempts"] = 0
            meta["lastAttemptAt"] = now_iso()
            continue

        combined_err = (stderr or "") + "\n" + (stdout or "")
        link_retry_ok = False
        if "brew link" in combined_err.lower() or "link step did not complete" in combined_err.lower():
            log.warning("Detected brew link failure for %s, retrying link", name)
            rc_link, out_link, err_link = sh(["brew", "link", "--overwrite", name], timeout=90)
            if rc_link == 0:
                log.info("brew link recovery succeeded for %s", name)
                link_retry_ok = True
            else:
                # second conservative attempt for keg-only edge cases
                rc_link2, out_link2, err_link2 = sh(["brew", "link", "--overwrite", "--force", name], timeout=90)
                if rc_link2 == 0:
                    log.info("brew link --force recovery succeeded for %s", name)
                    link_retry_ok = True
                else:
                    combined_err += f"\nlink-retry: {(err_link or out_link or '').strip()} {(err_link2 or out_link2 or '').strip()}"

        if link_retry_ok:
            brew_upgraded.append(name)
            meta["planned"] = False
            meta["failedAttempts"] = 0
            meta["lastAttemptAt"] = now_iso()
            meta["note"] = "Recovered via brew link retry"
            continue

        err = combined_err.strip() or "brew upgrade failed"
        meta["failedAttempts"] = int(meta.get("failedAttempts", 0)) + 1
        meta["lastAttemptAt"] = now_iso()
        log.error("Failed to upgrade %s: %s", name, err[:200])
        failed.append((name, "brew", err[:200]))

    # Post-upgrade recheck to keep tracked state fresh and avoid stale reporting.
    if not dry_run:
        for manager in MANAGER_ORDER:
            result = MANAGER_CHECKERS[manager]()
            tracked, _, _ = update_tracked(tracked_by_manager[manager], result["outdated"], manager)
            tracked_by_manager[manager] = tracked

    # Save updated state
    _save_all_tracked(tracked_by_manager)

    # Build report
    lines = ["🚀 Результат обновления:"]

    if any(auto_planned_by_manager.values()):
        lines.append(
            "📝 Auto-planned pending: "
            f"npm={auto_planned_by_manager['npm']}, "
            f"pnpm={auto_planned_by_manager['pnpm']}, "
            f"brew={auto_planned_by_manager['brew']} "
            f"(>{AUTO_PLAN_PENDING_AFTER_DAYS}d pending)"
        )

    if npm_upgraded:
        lines.append(f"✅ npm: {', '.join(npm_upgraded)}")
    if pnpm_upgraded:
        lines.append(f"✅ pnpm: {', '.join(pnpm_upgraded)}")
    if brew_upgraded:
        lines.append(f"✅ brew: {', '.join(brew_upgraded)}")
    if failed:
        lines.append(f"❌ Ошибки: {len(failed)}")
        for name, manager, err in failed:
            lines.append(f"   - {name} ({manager}): {err[:100]}")

    if not npm_upgraded and not pnpm_upgraded and not brew_upgraded and not failed and not any(auto_planned_by_manager.values()):
        lines.append("Нет запланированных пакетов для обновления.")

    log.info("=== UPGRADE MODE END ===")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Package manager maintenance for npm/pnpm/brew/skills (like apt workflow).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  check    - Update tracked state + auto-update skills (run daily in run_6am)
  review   - Show packages due for bug review (after 2 days)
  upgrade  - Apply planned npm/pnpm/brew upgrades
  skills   - Update OpenClaw skills immediately (no quarantine)

Examples:
  python3 pkg_maint.py check              # Daily check + auto skills update
  python3 pkg_maint.py review             # Review packages after 2 days
  python3 pkg_maint.py upgrade --dry-run  # Simulate npm/pnpm/brew upgrade
  python3 pkg_maint.py upgrade            # Apply npm/pnpm/brew upgrades
  python3 pkg_maint.py skills --dry-run   # Check skill updates
""",
    )
    ap.add_argument("mode", choices=["check", "review", "upgrade", "skills"], help="Operation mode")
    ap.add_argument("--dry-run", "-n", action="store_true", help="Don't actually upgrade")
    args = ap.parse_args()
    
    if args.mode == "check":
        check_mode()
    elif args.mode == "review":
        print(review_mode())
    elif args.mode == "upgrade":
        print(upgrade_mode(dry_run=args.dry_run))
    elif args.mode == "skills":
        print(upgrade_skills(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
