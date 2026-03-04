#!/usr/bin/env python3
"""Apt maintenance helper for the OpenClaw host (sys-updater).

Modes:
- run_6am: sudo apt-get update; sudo unattended-upgrade; sudo apt-get -s upgrade; snapshot upgradable pkgs.
- report_9am: render a human report from last run state.

Conservative by design:
- No full-upgrade/dist-upgrade
- Non-security upgrades are applied only from explicit planned list
"""

from __future__ import annotations

import argparse
import fcntl
import json
import logging
import logging.handlers
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# Import auto-review modules
sys.path.insert(0, str(Path(__file__).parent))
import auto_review
import retry_logic

# === Constants ===
DEFAULT_TIMEOUT = 600  # 10 minutes for long-running commands like unattended-upgrade
APT_HISTORY_HOURS = 24  # Only consider upgrades from last N hours

# === Directories ===
BASE_DIR = Path(os.getenv("SYS_UPDATER_BASE_DIR", "/home/moltuser/clawd/sys-updater"))
STATE_DIR = Path(os.getenv("SYS_UPDATER_STATE_DIR", BASE_DIR / "state" / "apt"))
LOG_DIR = Path(os.getenv("SYS_UPDATER_LOG_DIR", BASE_DIR / "state" / "logs"))
LOCK_FILE = STATE_DIR / ".run_6am.lock"

LAST_RUN_PATH = STATE_DIR / "last_run.json"
TRACK_PATH = STATE_DIR / "tracked.json"

# Paths for npm/brew tracking (used by auto-review)
NPM_TRACK_PATH = STATE_DIR / "npm_tracked.json"
PNPM_TRACK_PATH = STATE_DIR / "pnpm_tracked.json"
BREW_TRACK_PATH = STATE_DIR / "brew_tracked.json"

# === Logging setup: daily rotation, keep 10 days ===
LOG_FILE = LOG_DIR / "apt_maint.log"
AUTO_REVIEW_LOG_FILE = LOG_DIR / "auto_review.log"

# Global state
_dry_run = False
_verbose = False


def _setup_auto_review_logging() -> logging.Logger:
    """Configure separate logging for auto-review decisions."""
    logger = logging.getLogger("auto_review")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    
    # File handler: daily rotation, 30 days retention for audit trail
    file_handler = logging.handlers.TimedRotatingFileHandler(
        AUTO_REVIEW_LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
        utc=True,
    )
    file_handler.suffix = "%Y-%m-%d"
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def _ensure_directories() -> None:
    """Create required directories and verify write permissions."""
    for d in (STATE_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
        # Verify write permission
        test_file = d / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            raise PermissionError(f"No write permission for directory: {d}")


def _setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure file logging with daily rotation (10 days retention).

    Args:
        verbose: If True, also log to console (stderr).
    """
    logger = logging.getLogger("sys_updater")

    # Clear existing handlers to allow reconfiguration
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    # File handler: daily rotation, 10 days
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=10,
        encoding="utf-8",
        utc=True,
    )
    file_handler.suffix = "%Y-%m-%d"
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (if verbose)
    if verbose:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


# Initialize with file-only logging; reconfigure if --verbose
_ensure_directories()
log = _setup_logging(verbose=False)


def sh(
    cmd: list[str],
    *,
    check: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command with timeout.

    Args:
        cmd: Command and arguments.
        check: Raise on non-zero exit code.
        timeout: Timeout in seconds (default 600s = 10min).

    Returns:
        CompletedProcess with stdout/stderr captured.

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout.
        subprocess.CalledProcessError: If check=True and command fails.
    """
    global _dry_run
    if _dry_run and cmd[0] == "sudo":
        log.info("[DRY-RUN] Would execute: %s", " ".join(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
    return subprocess.run(cmd, text=True, capture_output=True, check=check, timeout=timeout)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def sudo_cmd(args: list[str]) -> list[str]:
    return ["sudo", "-n", *args]


@dataclass
class RunResult:
    ranAt: str
    aptUpdateOk: bool
    unattendedOk: bool
    simulatedOk: bool
    updatedPackages: list[str]
    plannedApplied: list[str]
    # Per-manager applied upgrades from pkg_maint.py upgrade summary
    pkgAppliedNpm: list[str]
    pkgAppliedPnpm: list[str]
    pkgAppliedBrew: list[str]
    securityNote: str | None
    upgradable: list[str]
    simulateSummary: str


def parse_apt_upgrade_simulation(output: str) -> str:
    m = re.search(r"\d+ upgraded, \d+ newly installed, \d+ to remove and \d+ not upgraded\.", output)
    if m:
        return m.group(0)
    lines = output.strip().splitlines()
    return lines[-1] if lines else ""


def list_upgradable() -> list[str]:
    """List upgradable packages using apt directly (no bash wrapper)."""
    # Use apt list directly, suppressing the warning about CLI stability
    env = os.environ.copy()
    env["LANG"] = "C.UTF-8"
    cp = subprocess.run(
        ["apt", "list", "--upgradable"],
        text=True,
        capture_output=True,
        check=True,
        env=env,
        timeout=60,
    )
    pkgs: list[str] = []
    for line in cp.stdout.splitlines():
        if not line or line.startswith("Listing"):
            continue
        # Format: "package/repo version [upgradable from: old_version]"
        name = line.split("/")[0].strip()
        if name:
            pkgs.append(name)
    return sorted(set(pkgs))


def parse_recent_upgrades_from_history(hours: int = APT_HISTORY_HOURS) -> list[str]:
    """Parse apt history.log for packages upgraded in the last N hours.

    Args:
        hours: Only consider upgrades from the last N hours.

    Returns:
        List of package names that were upgraded recently.
    """
    p = Path("/var/log/apt/history.log")
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except PermissionError:
        return []

    cutoff = now_utc() - timedelta(hours=hours)
    upgraded: list[str] = []

    # Parse history.log blocks
    # Format:
    # Start-Date: 2024-01-15  06:00:05
    # Commandline: ...
    # Upgrade: pkg1:arch (old, new), pkg2:arch (old, new)
    # End-Date: ...
    #
    # IMPORTANT: do NOT split by comma, because version tuples also contain commas.
    # Extract package tokens with regex: <name>:<arch> (

    current_date: datetime | None = None
    for line in text.splitlines():
        if line.startswith("Start-Date:"):
            date_str = line.replace("Start-Date:", "").strip()
            try:
                date_str = re.sub(r"\s+", " ", date_str)
                current_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                current_date = current_date.replace(tzinfo=timezone.utc)
            except ValueError:
                current_date = None
        elif line.startswith("Upgrade:") and current_date and current_date >= cutoff:
            payload = line.replace("Upgrade:", "")
            # Examples matched:
            #   libexpat1:amd64 (2.6.1-2ubuntu0.3, 2.6.1-2ubuntu0.4)
            #   cloud-init:all (24.4.1-0ubuntu0~24.04.2, ...)
            names = re.findall(r"([A-Za-z0-9.+-]+):[^\s]+\s*\(", payload)
            upgraded.extend(names)

    return sorted(set(upgraded))


def apply_planned_apt_upgrades(planned: list[str], upgradable_set: set[str]) -> tuple[list[str], list[str]]:
    """Apply explicitly planned non-security upgrades via apt-get install.

    Returns:
        (applied_packages, failed_packages)
    """
    # Only attempt packages that are still upgradable now.
    targets = sorted([p for p in planned if p in upgradable_set])
    if not targets:
        return [], []

    try:
        log.info("Running: sudo apt-get install -y %s", " ".join(targets))
        cp = sh(sudo_cmd(["apt-get", "install", "-y", *targets]), check=False, timeout=DEFAULT_TIMEOUT)
        if cp.returncode == 0:
            log.info("planned install: OK (%d packages)", len(targets))
            return targets, []

        log.error("planned install: FAIL (rc=%d)", cp.returncode)
        # Conservative fallback: mark all as failed if batch install failed.
        return [], targets
    except subprocess.TimeoutExpired:
        log.error("planned install: TIMEOUT (%ds)", DEFAULT_TIMEOUT)
        return [], targets
    except Exception as e:
        log.error("planned install: FAILED (%s)", e)
        return [], targets


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to load %s: %s; using default", path, e)
        return default


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class LockFile:
    """Context manager for exclusive file locking (prevents parallel runs)."""

    def __init__(self, path: Path):
        self.path = path
        self.fd: int | None = None

    def __enter__(self) -> "LockFile":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(str(self.path), os.O_CREAT | os.O_RDWR)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self.fd)
            raise RuntimeError(f"Another instance is running (lock: {self.path})")
        # Write PID for debugging
        os.ftruncate(self.fd, 0)
        os.write(self.fd, f"{os.getpid()}\n".encode())
        return self

    def __exit__(self, *args: Any) -> None:
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            try:
                self.path.unlink()
            except OSError:
                pass


def extract_last_line(text: str | None) -> str | None:
    """Safely extract the last non-empty line from text."""
    if not text:
        return None
    lines = text.strip().splitlines()
    return lines[-1] if lines else None


def parse_pkg_upgrade_summary(summary_stdout: str) -> dict[str, list[str]]:
    """Parse pkg_maint.py upgrade summary into per-manager applied lists."""
    applied = {"npm": [], "pnpm": [], "brew": []}
    if not summary_stdout:
        return applied

    for line in summary_stdout.splitlines():
        line = line.strip()
        # Expected lines like:
        # "✅ npm: pkg1, pkg2"
        # "✅ brew: uv"
        m = re.match(r"^✅\s+(npm|pnpm|brew):\s+(.+)$", line)
        if not m:
            continue
        manager = m.group(1)
        pkgs = [p.strip() for p in m.group(2).split(",") if p.strip()]
        applied[manager] = sorted(set(pkgs))

    return applied


def run_6am() -> RunResult:
    ran_at = now_iso()
    t0 = datetime.now(timezone.utc)
    log.info("=== run_6am START ===")
    log.info("State files: last_run=%s, tracked=%s", LAST_RUN_PATH, TRACK_PATH)
    log.info("PHASE[apt]: begin")

    apt_update_ok = True
    try:
        log.info("Running: sudo apt-get update")
        sh(sudo_cmd(["apt-get", "update"]), check=True, timeout=300)
        log.info("apt-get update: OK")
    except subprocess.TimeoutExpired:
        apt_update_ok = False
        log.error("apt-get update: TIMEOUT (300s)")
    except Exception as e:
        apt_update_ok = False
        log.error("apt-get update: FAILED (%s)", e)

    unattended_ok = True
    security_note: str | None = None
    try:
        log.info("Running: sudo unattended-upgrade -d")
        cp = sh(sudo_cmd(["unattended-upgrade", "-d"]), check=False, timeout=DEFAULT_TIMEOUT)
        unattended_ok = cp.returncode == 0
        security_note = extract_last_line(cp.stdout)
        log.info("unattended-upgrade: %s (rc=%d)", "OK" if unattended_ok else "FAIL", cp.returncode)
    except subprocess.TimeoutExpired:
        unattended_ok = False
        log.error("unattended-upgrade: TIMEOUT (%ds)", DEFAULT_TIMEOUT)
    except Exception as e:
        unattended_ok = False
        log.error("unattended-upgrade: FAILED (%s)", e)

    simulated_ok = True
    sim_summary = ""
    try:
        log.info("Running: sudo apt-get -s upgrade (simulation)")
        cp = sh(sudo_cmd(["apt-get", "-s", "upgrade"]), check=False, timeout=120)
        simulated_ok = cp.returncode == 0
        sim_summary = parse_apt_upgrade_simulation((cp.stdout or "") + "\n" + (cp.stderr or ""))
        log.info("apt-get -s upgrade: %s; summary=%s", "OK" if simulated_ok else "FAIL", sim_summary)
    except subprocess.TimeoutExpired:
        simulated_ok = False
        log.error("apt-get -s upgrade: TIMEOUT (120s)")
    except Exception as e:
        simulated_ok = False
        log.error("apt-get -s upgrade: FAILED (%s)", e)

    upgradable: list[str] = []
    try:
        upgradable = list_upgradable()
        log.info("Upgradable packages found: %d", len(upgradable))
    except subprocess.TimeoutExpired:
        log.error("list_upgradable: TIMEOUT")
    except Exception as e:
        log.error("list_upgradable: FAILED (%s)", e)

    updated_pkgs = parse_recent_upgrades_from_history(hours=APT_HISTORY_HOURS)
    log.info("Recently updated packages (last %dh): %d", APT_HISTORY_HOURS, len(updated_pkgs))

    # Load and update tracked packages
    tracked = load_json(TRACK_PATH, {"createdAt": ran_at, "items": {}})
    items: dict[str, Any] = tracked.get("items") or {}

    # Track new packages
    new_tracked = 0
    for pkg in upgradable:
        if pkg not in items:
            new_tracked += 1
            items[pkg] = {
                "firstSeenAt": ran_at,
                "reviewedAt": None,
                "planned": False,
                "blocked": False,
                "note": None,
            }

    # Cleanup: remove packages no longer upgradable.
    # Keep only blocked entries as a short-lived safety memory.
    upgradable_set = set(upgradable)
    removed = 0
    to_remove = []
    for pkg, meta in items.items():
        if pkg not in upgradable_set:
            if not meta.get("blocked"):
                to_remove.append(pkg)
    for pkg in to_remove:
        del items[pkg]
        removed += 1

    if removed > 0:
        log.info("Cleanup: removed %d packages no longer upgradable", removed)

    # Recovery: packages reviewed as OK but planned flag wasn't set (review agent bug recovery).
    recovered = 0
    for pkg, meta in items.items():
        note = (meta.get("note") or "").lower()
        if (
            meta.get("reviewedAt")
            and not meta.get("planned")
            and not meta.get("blocked")
            and ("review ok" in note or "auto-approved" in note)
        ):
            meta["planned"] = True
            recovered += 1
            log.info("Recovered stuck package: %s → planned=True (note=%r)", pkg, meta.get("note"))
    if recovered > 0:
        log.info("Recovery: set planned=True for %d stuck packages (reviewed OK but flag missing)", recovered)

    tracked["items"] = items
    save_json(TRACK_PATH, tracked)
    log.info("Updated tracked.json: %d new, %d removed, %d recovered, %d total", new_tracked, removed, recovered, len(items))

    # Log summary of planned/blocked decisions
    planned_count = sum(1 for m in items.values() if m.get("planned") and not m.get("blocked"))
    blocked_count = sum(1 for m in items.values() if m.get("blocked"))
    log.info("Tracking summary: planned=%d, blocked=%d", planned_count, blocked_count)

    # Apply explicitly planned non-security apt upgrades.
    upgradable_set = set(upgradable)
    planned_targets = sorted([p for p, m in items.items() if m.get("planned") and not m.get("blocked")])
    applied_planned, failed_planned = apply_planned_apt_upgrades(planned_targets, upgradable_set)

    pkg_applied = {"npm": [], "pnpm": [], "brew": []}

    # Remove successfully applied packages from tracking (they're no longer upgradable).
    for pkg in applied_planned:
        items.pop(pkg, None)
        log.info("Removed from tracking (installed): %s", pkg)
    if applied_planned:
        log.info("Removed %d installed packages from tracked.json", len(applied_planned))

    tracked["items"] = items
    save_json(TRACK_PATH, tracked)

    result = RunResult(
        ranAt=ran_at,
        aptUpdateOk=apt_update_ok,
        unattendedOk=unattended_ok,
        simulatedOk=simulated_ok,
        updatedPackages=updated_pkgs,
        plannedApplied=applied_planned,
        pkgAppliedNpm=[],
        pkgAppliedPnpm=[],
        pkgAppliedBrew=[],
        securityNote=security_note,
        upgradable=upgradable,
        simulateSummary=sim_summary,
    )
    save_json(LAST_RUN_PATH, result.__dict__)
    log.info("Saved last_run.json")

    if failed_planned:
        log.warning("planned install failed for: %s", ", ".join(failed_planned))

    # Cleanup orphaned dependencies
    try:
        log.info("Running: sudo apt-get autoremove -y")
        cp = sh(sudo_cmd(["apt-get", "autoremove", "-y"]), check=False, timeout=300)
        if cp.returncode == 0:
            log.info("apt-get autoremove: OK")
        else:
            log.warning("apt-get autoremove: FAIL (rc=%d)", cp.returncode)
    except subprocess.TimeoutExpired:
        log.error("apt-get autoremove: TIMEOUT (300s)")
    except Exception as e:
        log.error("apt-get autoremove: FAILED (%s)", e)

    log.info("PHASE[apt]: end")
    log.info("PHASE[pkg-maint]: begin")

    # Run pkg_maint.py for npm/brew checks + planned upgrades
    try:
        pkg_maint_path = Path(__file__).parent / "pkg_maint.py"
        if pkg_maint_path.exists():
            log.info("Running: pkg_maint.py check for npm/brew")
            cp_check = subprocess.run(
                ["python3", str(pkg_maint_path), "check"],
                capture_output=True, text=True, timeout=180
            )
            if cp_check.returncode == 0:
                log.info("pkg_maint.py check: OK")
            else:
                log.warning("pkg_maint.py check: rc=%d, err=%s", cp_check.returncode, cp_check.stderr[:200])

            log.info("Running: pkg_maint.py upgrade for npm/brew planned packages")
            cp_upgrade = subprocess.run(
                ["python3", str(pkg_maint_path), "upgrade"],
                capture_output=True, text=True, timeout=600
            )
            if cp_upgrade.returncode == 0:
                log.info("pkg_maint.py upgrade: OK")
                if cp_upgrade.stdout:
                    log.info("pkg_maint.py upgrade summary: %s", cp_upgrade.stdout.strip().replace("\n", " | ")[:400])
                    pkg_applied = parse_pkg_upgrade_summary(cp_upgrade.stdout)
            else:
                log.warning("pkg_maint.py upgrade: rc=%d, err=%s", cp_upgrade.returncode, cp_upgrade.stderr[:200])
        else:
            log.warning("pkg_maint.py not found at %s", pkg_maint_path)
    except Exception as e:
        log.error("pkg_maint.py failed: %s", e)

    log.info("PHASE[pkg-maint]: end")

    # Persist per-manager applied upgrades (from pkg_maint) for 09:00 reporting.
    result.pkgAppliedNpm = pkg_applied.get("npm", [])
    result.pkgAppliedPnpm = pkg_applied.get("pnpm", [])
    result.pkgAppliedBrew = pkg_applied.get("brew", [])
    save_json(LAST_RUN_PATH, result.__dict__)
    log.info(
        "Saved pkg-applied summary: npm=%d, pnpm=%d, brew=%d",
        len(result.pkgAppliedNpm),
        len(result.pkgAppliedPnpm),
        len(result.pkgAppliedBrew),
    )

    log.info("PHASE[auto-review]: begin")

    # === Auto-Review and Retry Logic for npm/brew packages ===
    try:
        # Setup separate logging for auto-review
        ar_log = _setup_auto_review_logging()
        ar_log.info("=== AUTO-REVIEW START ===")
        
        # First: process any pending retries from previous failures
        log.info("Processing pending retries for failed upgrades...")
        retry_summary = retry_logic.process_retries(
            NPM_TRACK_PATH,
            BREW_TRACK_PATH,
            PNPM_TRACK_PATH,
            dry_run=_dry_run
        )
        total_retry_attempts = (
            retry_summary["npm"]["attempted"] + 
            retry_summary["brew"]["attempted"] + retry_summary.get("pnpm", {}).get("attempted", 0)
        )
        if total_retry_attempts > 0:
            log.info(
                "Retry processing: %d attempted, %d succeeded, %d blocked",
                total_retry_attempts,
                retry_summary["npm"]["succeeded"] + retry_summary["brew"]["succeeded"] + retry_summary.get("pnpm", {}).get("succeeded", 0),
                retry_summary["npm"]["blocked"] + retry_summary["brew"]["blocked"] + retry_summary.get("pnpm", {}).get("blocked", 0)
            )
        
        # Then: run auto-review for new/updated packages
        log.info("Running auto-review for npm/brew packages...")
        ar_summary = auto_review.run_auto_review(
            NPM_TRACK_PATH,
            BREW_TRACK_PATH,
            PNPM_TRACK_PATH,
            dry_run=_dry_run
        )
        
        total_reviewed = (
            ar_summary["npm"]["reviewed"] + 
            ar_summary["brew"]["reviewed"] + ar_summary.get("pnpm", {}).get("reviewed", 0)
        )
        total_approved = (
            ar_summary["npm"]["approved"] + 
            ar_summary["brew"]["approved"] + ar_summary.get("pnpm", {}).get("approved", 0)
        )
        total_blocked = (
            ar_summary["npm"]["blocked"] + 
            ar_summary["brew"]["blocked"] + ar_summary.get("pnpm", {}).get("blocked", 0)
        )
        
        log.info(
            "Auto-review complete: %d reviewed, %d approved, %d blocked",
            total_reviewed,
            total_approved,
            total_blocked
        )
        ar_log.info(
            "Auto-review: reviewed=%d, approved=%d, blocked=%d, pending=%d",
            total_reviewed,
            total_approved,
            total_blocked,
            ar_summary["npm"]["pending"] + ar_summary["brew"]["pending"] + ar_summary.get("pnpm", {}).get("pending", 0)
        )
        
        # Log details of decisions
        for detail in ar_summary.get("details", []):
            if detail["result"] in ("ok", "blocked"):
                ar_log.info(
                    "[%s] %s/%s: %s",
                    detail["result"].upper(),
                    detail["manager"],
                    detail["name"],
                    detail.get("reason", "No reason provided")[:200],
                )

    except Exception as e:
        log.error("Auto-review failed: %s", e)
        ar_log = logging.getLogger("auto_review")
        ar_log.error("Auto-review error: %s", e)
    finally:
        try:
            logging.getLogger("auto_review").info("=== AUTO-REVIEW END ===")
        except Exception:
            pass

    log.info("PHASE[auto-review]: end")
    elapsed = int((datetime.now(timezone.utc) - t0).total_seconds())
    log.info("=== run_6am END (success, duration=%ss) ===", elapsed)
    return result


def render_report(now_msk_label: str = "09:00 MSK") -> str:
    log.info("=== report_9am START ===")
    log.info("Reading state files: last_run=%s, tracked=%s", LAST_RUN_PATH, TRACK_PATH)
    last = load_json(LAST_RUN_PATH, None)
    tracked = load_json(TRACK_PATH, {"items": {}})

    if not last:
        log.warning("No last_run.json found")
        log.info("=== report_9am END ===")
        return "🕘 Отчёт (09:00 MSK)\n\n⚠️ Нет данных: задача 06:00 ещё не запускалась или не смогла сохранить состояние."

    updated_raw = last.get("updatedPackages") or []

    def sanitize_pkg_names(values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for v in values:
            if not isinstance(v, str):
                continue
            name = v.strip()
            if not name:
                continue
            # Drop obvious version fragments from legacy parser output, e.g. "1.2.11-1ubuntu0.2)"
            if name.endswith(")") or re.match(r"^[0-9]", name):
                continue
            cleaned.append(name)
        return sorted(set(cleaned))

    updated = sanitize_pkg_names(updated_raw)
    applied_planned = last.get("plannedApplied") or []
    sim = last.get("simulateSummary") or ""

    items: dict[str, Any] = (tracked.get("items") or {})

    # APT non-security categories
    candidates_pkgs = sorted([p for p, meta in items.items() if not meta.get("reviewedAt") and not meta.get("blocked")])
    planned_pkgs    = sorted([p for p, meta in items.items() if meta.get("planned") and not meta.get("blocked")])
    blocked_pkgs    = sorted([p for p, meta in items.items() if meta.get("blocked")])
    # Stuck = reviewed OK but planned flag was never set (recovery picks these up at next 06:00)
    stuck_pkgs      = sorted([
        p for p, meta in items.items()
        if meta.get("reviewedAt") and not meta.get("planned") and not meta.get("blocked")
        and ("review ok" in (meta.get("note") or "").lower() or "auto-approved" in (meta.get("note") or "").lower())
    ])

    def fmt_list(pkgs: list[str], max_n: int = 25) -> str:
        if not pkgs:
            return "—"
        if len(pkgs) <= max_n:
            return ", ".join(pkgs)
        return ", ".join(pkgs[:max_n]) + f" …(+{len(pkgs)-max_n})"

    def pkg_section(label: str, candidates: list[str], planned: list[str], blocked: list[str],
                    stuck: list[str] | None = None, max_n: int = 15) -> list[str]:
        """Render a uniform package-manager section matching the APT layout."""
        sec: list[str] = [label]
        sec.append(f"- кандидаты (ожидают ревью): {fmt_list(candidates, max_n)}")
        if stuck:
            sec.append(f"- ⚠️ зависших (ревью OK, флаг не выставлен): {fmt_list(stuck, max_n)}")
        sec.append(f"- 🔄 запланировано к установке: {fmt_list(planned, max_n)}")
        if blocked:
            sec.append(f"- 🚫 заблокировано: {fmt_list(blocked, max_n)}")
        return sec

    lines: list[str] = []

    lines.append(f"🕘 Отчёт ({now_msk_label})")
    lines.append("")

    lines.append("⚙️ Сегодня в 06:00:")
    lines.append(f"- apt update: {'OK' if last.get('aptUpdateOk') else 'FAIL'}")
    lines.append(f"- security updates (unattended-upgrade): {'OK' if last.get('unattendedOk') else 'FAIL'}")
    lines.append(f"- обновилось: {fmt_list(updated) if updated else '—'}")
    sim_note = f"{sim} (до установки planned)" if applied_planned and sim else sim
    lines.append(f"- симуляция (до установки): {'OK' if last.get('simulatedOk') else 'FAIL'}; {sim_note}")
    if applied_planned:
        lines.append(f"- ✅ установлено non-security planned: {fmt_list(applied_planned)}")

    pkg_applied_npm = last.get("pkgAppliedNpm") or []
    pkg_applied_pnpm = last.get("pkgAppliedPnpm") or []
    pkg_applied_brew = last.get("pkgAppliedBrew") or []
    if pkg_applied_npm:
        lines.append(f"- ✅ установлено npm planned: {fmt_list(pkg_applied_npm)}")
    if pkg_applied_pnpm:
        lines.append(f"- ✅ установлено pnpm planned: {fmt_list(pkg_applied_pnpm)}")
    if pkg_applied_brew:
        lines.append(f"- ✅ установлено brew planned: {fmt_list(pkg_applied_brew)}")
    lines.append("")

    # APT non-security section (same structure as other managers below)
    lines.extend(pkg_section(
        "📦 apt (non-security):",
        candidates_pkgs, planned_pkgs, blocked_pkgs, stuck=stuck_pkgs,
    ))
    lines.append("")

    # npm / pnpm / brew sections using tracked.json data (mirrors APT layout)
    npm_data    = load_json(NPM_TRACK_PATH,  {"items": {}})
    pnpm_data   = load_json(PNPM_TRACK_PATH, {"items": {}})
    brew_data   = load_json(BREW_TRACK_PATH, {"items": {}})

    def categorise(track_items: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
        cands   = sorted([k for k, v in track_items.items()
                          if not v.get("planned") and not v.get("blocked")
                          and (not v.get("reviewedAt") or v.get("reviewResult") == "pending")])
        planneds = sorted([k for k, v in track_items.items() if v.get("planned") and not v.get("blocked")])
        blockeds = sorted([k for k, v in track_items.items() if v.get("blocked")])
        return cands, planneds, blockeds

    npm_c,  npm_p,  npm_b  = categorise(npm_data.get("items",  {}))
    pnpm_c, pnpm_p, pnpm_b = categorise(pnpm_data.get("items", {}))
    brew_c, brew_p, brew_b = categorise(brew_data.get("items", {}))

    for label, c, p, b in [
        ("📦 npm (global):", npm_c, npm_p, npm_b),
        ("📦 pnpm (global):", pnpm_c, pnpm_p, pnpm_b),
        ("📦 brew:", brew_c, brew_p, brew_b),
    ]:
        if any([c, p, b]):
            lines.extend(pkg_section(label, c, p, b, max_n=10))
            lines.append("")

    # Compute review-due lists for "tomorrow" section
    now_utc = datetime.now(timezone.utc)

    def due_for_review(track_path: Path) -> list[str]:
        data = load_json(track_path, {"items": {}})
        result = []
        for name, meta in data.get("items", {}).items():
            if meta.get("reviewedAt") or meta.get("blocked"):
                continue
            first = meta.get("firstSeenAt")
            if not first:
                continue
            try:
                dt = datetime.fromisoformat(first.replace("Z", "+00:00"))
                if (now_utc - dt).days >= 2:
                    result.append(name)
            except (ValueError, TypeError):
                pass
        return sorted(result)

    apt_review_due = []
    for name, meta in items.items():
        if not meta.get("reviewedAt") and not meta.get("blocked"):
            first = meta.get("firstSeenAt")
            if first:
                try:
                    dt = datetime.fromisoformat(first.replace("Z", "+00:00"))
                    if (now_utc - dt).days >= 1:  # will be due tomorrow
                        apt_review_due.append(name)
                except (ValueError, TypeError):
                    pass

    npm_review_due  = due_for_review(NPM_TRACK_PATH)
    pnpm_review_due = due_for_review(PNPM_TRACK_PATH)
    brew_review_due = due_for_review(BREW_TRACK_PATH)

    lines.append("📅 Запланировано на завтра 06:00:")
    lines.append("- security updates + симуляция (всегда)")
    lines.append(f"- apt non-security install: {fmt_list(planned_pkgs)}")
    lines.append(f"- apt ревью (06:30): {fmt_list(apt_review_due) if apt_review_due else '—'}")
    if npm_review_due or pnpm_review_due or brew_review_due:
        all_pkg_due = (
            [f"npm/{n}" for n in npm_review_due] +
            [f"pnpm/{n}" for n in pnpm_review_due] +
            [f"brew/{n}" for n in brew_review_due]
        )
        lines.append(f"- auto-review pkg (06:00): {fmt_list(all_pkg_due)}")

    # Skills section
    try:
        result = subprocess.run(
            ["clawhub", "list"], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout:
            skill_count = len([l for l in result.stdout.strip().split('\n') if l.strip()])
            
            # Check for skill updates
            skills_updated = []
            skills_with_changes = []
            try:
                update_result = subprocess.run(
                    ["clawhub", "update", "--all", "--no-input"],
                    capture_output=True, text=True, timeout=60
                )
                if update_result.returncode == 0:
                    for line in update_result.stdout.split('\n'):
                        if 'updating' in line.lower() and '->' in line:
                            # Extract skill name and version
                            match = re.search(r'[Uu]pdating\s+(\S+).*->\s+(\S+)', line)
                            if match:
                                skills_updated.append(f"{match.group(1)}({match.group(2)})")
                        elif 'local changes' in line.lower():
                            match = re.search(r'^-\s*Checking\s+(\S+)', line, re.MULTILINE)
                            if match:
                                skills_with_changes.append(match.group(1))
            except Exception:
                pass
            
            lines.append("")
            if skills_updated:
                lines.append(f"🧩 Skills: {skill_count} (обновлены: {', '.join(skills_updated)})")
            elif skills_with_changes:
                lines.append(f"🧩 Skills: {skill_count} ({len(skills_with_changes)} с локальными изменениями)")
            else:
                lines.append(f"🧩 Skills: {skill_count} (обновлений нет)")
    except Exception:
        pass

    log.info("Report generated: updated=%d, tracked=%d, planned=%d, blocked=%d",
             len(updated), len(candidates_pkgs), len(planned_pkgs), len(blocked_pkgs))
    log.info("=== report_9am END ===")
    return "\n".join(lines)


def run_auto_review_command(dry_run: bool = False) -> str:
    """Manual auto-review command for npm/brew packages.
    
    Similar to run_6am auto-review but can be run independently.
    
    Args:
        dry_run: If True, don't save changes
        
    Returns:
        Human-readable report of review results
    """
    log.info("=== AUTO-REVIEW COMMAND START ===")
    ar_log = _setup_auto_review_logging()
    ar_log.info("=== MANUAL AUTO-REVIEW START ===")
    
    lines = ["🔍 Результат авто-ревью пакетов:"]
    
    try:
        # Process retries first
        retry_summary = retry_logic.process_retries(
            NPM_TRACK_PATH,
            BREW_TRACK_PATH,
            PNPM_TRACK_PATH,
            dry_run=dry_run
        )
        
        total_retry_attempts = (
            retry_summary["npm"]["attempted"] + 
            retry_summary["brew"]["attempted"] + retry_summary.get("pnpm", {}).get("attempted", 0)
        )
        
        if total_retry_attempts > 0:
            lines.append("\n🔄 Обработка повторных попыток:")
            lines.append(f"  npm: {retry_summary['npm']['succeeded']} успешно, {retry_summary['npm']['failed']} неудачно, {retry_summary['npm']['blocked']} заблокировано")
            lines.append(f"  pnpm: {retry_summary.get('pnpm', {}).get('succeeded', 0)} успешно, {retry_summary.get('pnpm', {}).get('failed', 0)} неудачно, {retry_summary.get('pnpm', {}).get('blocked', 0)} заблокировано")
            lines.append(f"  brew: {retry_summary['brew']['succeeded']} успешно, {retry_summary['brew']['failed']} неудачно, {retry_summary['brew']['blocked']} заблокировано")
        
        # Run auto-review
        ar_summary = auto_review.run_auto_review(
            NPM_TRACK_PATH,
            BREW_TRACK_PATH,
            PNPM_TRACK_PATH,
            dry_run=dry_run
        )
        
        total_reviewed = (
            ar_summary["npm"]["reviewed"] + 
            ar_summary["brew"]["reviewed"] + ar_summary.get("pnpm", {}).get("reviewed", 0)
        )
        total_approved = (
            ar_summary["npm"]["approved"] + 
            ar_summary["brew"]["approved"] + ar_summary.get("pnpm", {}).get("approved", 0)
        )
        total_blocked = (
            ar_summary["npm"]["blocked"] + 
            ar_summary["brew"]["blocked"] + ar_summary.get("pnpm", {}).get("blocked", 0)
        )
        total_pending = (
            ar_summary["npm"]["pending"] + 
            ar_summary["brew"]["pending"] + ar_summary.get("pnpm", {}).get("pending", 0)
        )
        
        lines.append(f"\n📊 Проверено пакетов: {total_reviewed}")
        lines.append(f"  ✅ Одобрено для обновления: {total_approved}")
        lines.append(f"  🚫 Заблокировано: {total_blocked}")
        lines.append(f"  ⏳ Ожидают (недостаточно времени): {total_pending}")
        
        # Show details of approved packages
        approved_details = [
            d for d in ar_summary.get("details", [])
            if d["result"] == "ok"
        ]
        if approved_details:
            lines.append("\n📦 Одобрены для обновления:")
            for d in approved_details[:10]:  # Limit to 10
                lines.append(f"  - {d['manager']}/{d['name']}")
            if len(approved_details) > 10:
                lines.append(f"  ... и ещё {len(approved_details) - 10}")
        
        # Show details of blocked packages
        blocked_details = [
            d for d in ar_summary.get("details", [])
            if d["result"] == "blocked"
        ]
        if blocked_details:
            lines.append("\n⚠️ Заблокированы:")
            for d in blocked_details[:10]:
                reason = d.get("reason", "")
                # Truncate reason
                if len(reason) > 80:
                    reason = reason[:77] + "..."
                lines.append(f"  - {d['manager']}/{d['name']}: {reason}")
            if len(blocked_details) > 10:
                lines.append(f"  ... и ещё {len(blocked_details) - 10}")
        
        # Log to auto_review.log
        for detail in ar_summary.get("details", []):
            if detail["result"] in ("ok", "blocked"):
                ar_log.info(
                    "[%s] %s/%s: %s",
                    detail["result"].upper(),
                    detail["manager"],
                    detail["name"],
                    detail.get("reason", "No reason")[:200]
                )
        
        ar_log.info("=== MANUAL AUTO-REVIEW END ===")
        log.info("=== AUTO-REVIEW COMMAND END ===")
        
        if dry_run:
            lines.append("\n⚠️ Режим сухого прогона (изменения не сохранены)")
        
        return "\n".join(lines)
        
    except Exception as e:
        log.error("Auto-review command failed: %s", e)
        ar_log.error("Manual auto-review error: %s", e)
        return f"❌ Ошибка авто-ревью: {e}"


def main() -> int:
    global _dry_run, _verbose, log

    ap = argparse.ArgumentParser(
        description="Apt maintenance helper for sys-updater.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 apt_maint.py run_6am           # Run daily maintenance
  python3 apt_maint.py run_6am --dry-run # Simulate without executing sudo commands
  python3 apt_maint.py report_9am        # Generate Telegram report
  python3 apt_maint.py report_9am -v     # Generate report with verbose logging
  python3 apt_maint.py auto-review       # Run auto-review manually
  python3 apt_maint.py auto-review -n    # Dry-run auto-review
""",
    )
    ap.add_argument("mode", choices=["run_6am", "report_9am", "auto-review"], help="Operation mode")
    ap.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Don't execute sudo commands, just log what would happen",
    )
    ap.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Also log to console (stderr)",
    )
    args = ap.parse_args()

    _dry_run = args.dry_run
    _verbose = args.verbose

    # Reconfigure logging if verbose requested
    if _verbose:
        log = _setup_logging(verbose=True)

    if _dry_run:
        log.info("DRY-RUN mode enabled: sudo commands will be skipped")

    exit_code = 0
    try:
        if args.mode == "run_6am":
            with LockFile(LOCK_FILE):
                run_6am()
        elif args.mode == "report_9am":
            print(render_report())
        elif args.mode == "auto-review":
            print(run_auto_review_command(dry_run=_dry_run))
        else:
            log.error("Unknown mode: %s", args.mode)
            exit_code = 2
    except RuntimeError as e:
        # LockFile error (another instance running)
        log.error("%s", e)
        print(f"Error: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        log.exception("Unhandled exception in mode=%s: %s", args.mode, e)
        exit_code = 1

    if exit_code != 0:
        log.error("Exiting with code %d", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
