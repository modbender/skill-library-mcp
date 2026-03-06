"""
reefwatch.daemon
~~~~~~~~~~~~~~~~
ReefWatchDaemon orchestrator, signal handler, and main entry point.
"""

import argparse
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from reefwatch._common import SYSTEM, expand, get_os_key, logger
from reefwatch.alert_manager import AlertManager
from reefwatch.collectors.file_watcher import FileWatcher
from reefwatch.collectors.log_collector import LogCollector
from reefwatch.collectors.network_monitor import NetworkMonitor
from reefwatch.collectors.process_monitor import ProcessMonitor
from reefwatch.config import load_config, validate_config
from reefwatch.engines.custom_rules import CustomRulesEngine
from reefwatch.engines.sigma_engine import SigmaEngine
from reefwatch.engines.yara_engine import YaraEngine

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
RUNNING = threading.Event()
RUNNING.set()  # Start in "running" state; clear() to signal shutdown


# ---------------------------------------------------------------------------
# Main Daemon Loop
# ---------------------------------------------------------------------------
class ReefWatchDaemon:
    """Orchestrates all collectors and engines."""

    def __init__(self, config: dict, webhook_url: str, webhook_token: str):
        self.config = config
        self.alert_mgr = AlertManager(config, webhook_url, webhook_token)

        # Collectors
        self.log_collector = LogCollector(config)
        self.file_watcher = FileWatcher(config)
        self.process_monitor = ProcessMonitor(config)
        self.network_monitor = NetworkMonitor(config)

        # Engines
        self.yara_engine = YaraEngine(config)
        self.sigma_engine = SigmaEngine(config)
        self.custom_engine = CustomRulesEngine(config)

        # Derive cycle divisors from config intervals
        base_interval = (
            config.get("collectors", {}).get("logs", {}).get("interval_seconds", 10)
        )
        proc_interval = (
            config.get("collectors", {}).get("processes", {}).get("interval_seconds", 30)
        )
        net_interval = (
            config.get("collectors", {}).get("network", {}).get("interval_seconds", 60)
        )
        integrity_interval = (
            config.get("engines", {}).get("custom", {}).get("integrity_interval_seconds", 300)
        )
        self._proc_every = max(1, proc_interval // base_interval)
        self._net_every = max(1, net_interval // base_interval)
        self._integrity_every = max(1, integrity_interval // base_interval)
        self._status_every = max(1, 60 // base_interval)  # ~every 60s

        self._start_time = time.time()
        self._alerts_sent = 0
        self._status_file = Path(
            config.get("general", {}).get(
                "status_file", "~/.openclaw/reefwatch_status.json"
            )
        ).expanduser()

        # Pre-expand critical paths once at init (resolves ~ properly)
        home = str(Path.home())
        self._critical_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "/etc/crontab",
            "/etc/hosts",
            f"{home}/.openclaw/openclaw.json",
            f"{home}/.ssh/authorized_keys",
        ]

        logger.info("ReefWatch daemon initialized")
        logger.info(f"OS: {SYSTEM} ({get_os_key()})")

    def run(self):
        """Main monitoring loop."""
        logger.info("ReefWatch monitoring started")

        cycle = 0
        while RUNNING.is_set():
            try:
                self._cycle(cycle)
                cycle += 1
                RUNNING.wait(
                    timeout=self.config.get("collectors", {})
                    .get("logs", {})
                    .get("interval_seconds", 10)
                )
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}", exc_info=True)
                RUNNING.wait(timeout=5)  # Back off on errors

        self.alert_mgr.shutdown()
        self.network_monitor.shutdown()
        logger.info("ReefWatch monitoring stopped")

    def _submit(self, alert: dict):
        """Submit alert and track count (only if accepted)."""
        if self.alert_mgr.submit(alert):
            self._alerts_sent += 1

    def _cycle(self, cycle: int):
        """Single monitoring cycle."""

        # 1. Collect and analyze logs (every cycle)
        if self.log_collector.enabled:
            log_entries = self.log_collector.collect()
            for entry in log_entries:
                # Run Sigma rules against each log entry
                if self.sigma_engine.enabled:
                    for alert in self.sigma_engine.evaluate(entry):
                        self._submit(alert)

        # 2. Check file changes (every cycle)
        if self.file_watcher.enabled:
            changes = self.file_watcher.check_changes()
            for change in changes:
                # YARA scan changed files (only in realtime/on_change mode)
                if self.yara_engine.enabled and self.yara_engine.mode != "scheduled" and change["type"] in (
                    "file_created",
                    "file_modified",
                    "file_integrity_violation",
                ):
                    ext = Path(change["path"]).suffix
                    if (
                        not self.file_watcher.scan_extensions
                        or ext in self.file_watcher.scan_extensions
                    ):
                        for alert in self.yara_engine.scan_file(change["path"]):
                            self._submit(alert)

                # Alert on file integrity violations (hash mismatch)
                if change.get("integrity"):
                    self._submit(
                        {
                            "type": "File integrity violation (SHA256 mismatch)",
                            "severity": "CRITICAL",
                            "source": "file_watcher",
                            "detail": f"Path: {change['path']}",
                            "rule": "custom/file_integrity_violation",
                            "time": change.get(
                                "timestamp",
                                datetime.now(timezone.utc).isoformat(),
                            ),
                        }
                    )

                # Alert on critical file changes
                for cp in self._critical_paths:
                    changed_path = change.get("path", "")
                    if changed_path == cp:
                        self._submit(
                            {
                                "type": f"Critical file {change['type']}",
                                "severity": "HIGH",
                                "source": "file_watcher",
                                "detail": f"Path: {change['path']}",
                                "rule": "custom/critical_file_change",
                                "time": change.get(
                                    "timestamp",
                                    datetime.now(timezone.utc).isoformat(),
                                ),
                            }
                        )

                # Custom rules against file changes
                if self.custom_engine.enabled:
                    for alert in self.custom_engine.evaluate(change, "file_change"):
                        self._submit(alert)

        # 3. Check processes
        if self.process_monitor.enabled and cycle % self._proc_every == 0:
            proc_alerts = self.process_monitor.check()
            for alert in proc_alerts:
                self._submit(alert)
            # Custom rules against process events
            if self.custom_engine.enabled and proc_alerts:
                for alert in proc_alerts:
                    for custom_alert in self.custom_engine.evaluate(
                        alert, "process"
                    ):
                        self._submit(custom_alert)

        # 4. Check network
        if self.network_monitor.enabled and cycle % self._net_every == 0:
            for alert in self.network_monitor.check():
                self._submit(alert)

        # 5. YARA scheduled full scan
        if self.yara_engine.should_run_scheduled_scan():
            for wp in self.file_watcher.watched_paths:
                if wp.is_dir():
                    for alert in self.yara_engine.scan_directory(str(wp)):
                        self._submit(alert)

        # 6. OpenClaw integrity check
        if self.custom_engine.enabled and cycle % self._integrity_every == 0:
            for alert in self.custom_engine.check_openclaw_integrity():
                self._submit(alert)

        # 7. Write status file periodically
        if cycle % self._status_every == 0:
            self._write_status(cycle)

    def _write_status(self, cycle: int):
        """Write health/status JSON for external monitoring."""
        status = {
            "pid": os.getpid(),
            "uptime_seconds": int(time.time() - self._start_time),
            "cycles": cycle,
            "alerts_sent": self._alerts_sent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collectors": {
                "log_collector": self.log_collector.enabled,
                "file_watcher": self.file_watcher.enabled,
                "process_monitor": self.process_monitor.enabled,
                "network_monitor": self.network_monitor.enabled,
            },
            "engines": {
                "yara": self.yara_engine.enabled,
                "sigma": self.sigma_engine.enabled,
                "custom": self.custom_engine.enabled,
            },
        }
        try:
            self._status_file.parent.mkdir(parents=True, exist_ok=True)
            data = json.dumps(status, indent=2)
            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(str(self._status_file), flags, 0o600)
            os.write(fd, data.encode())
            os.close(fd)
        except Exception as e:
            logger.warning(f"Failed to write status file: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down...")
    RUNNING.clear()


def main():
    parser = argparse.ArgumentParser(description="ReefWatch Security Daemon")
    parser.add_argument(
        "--config",
        default="~/.openclaw/workspace/skills/reefwatch/reefwatch_config.yaml",
        help="Path to config file",
    )
    parser.add_argument("--webhook-url", help="OpenClaw webhook URL")
    parser.add_argument("--log-level", default=None, help="Log level")
    args = parser.parse_args()

    # Load and validate config (must happen before logging setup to read config values)
    config = load_config(args.config)
    for warning in validate_config(config):
        logger.warning(f"Config: {warning}")
    general_cfg = config.get("general", {})

    # Setup logging — CLI --log-level overrides config, config overrides default "INFO"
    effective_level = args.log_level or general_cfg.get("log_level", "INFO")
    log_level = getattr(logging, effective_level.upper(), logging.INFO)
    log_file = expand(general_cfg.get("log_file", "~/.openclaw/logs/reefwatch.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_max_bytes = general_cfg.get("log_max_bytes", 10 * 1024 * 1024)  # 10 MB
    log_backup_count = general_cfg.get("log_backup_count", 5)

    from logging.handlers import RotatingFileHandler

    # Restrict log file permissions (umask 0o077 → files created with 0o600)
    old_umask = os.umask(0o077)
    try:
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                RotatingFileHandler(
                    str(log_file),
                    maxBytes=log_max_bytes,
                    backupCount=log_backup_count,
                ),
                logging.StreamHandler(sys.stdout),
            ],
        )
    finally:
        os.umask(old_umask)

    # Resolve webhook
    webhook_url = (
        args.webhook_url
        or os.environ.get("REEFWATCH_WEBHOOK_URL")
        or config.get("webhook", {}).get("url", "http://127.0.0.1:18789/hooks/wake")
    )
    webhook_token = (
        os.environ.get("OPENCLAW_HOOKS_TOKEN", "")
        or config.get("webhook", {}).get("token", "")
    )

    # Write PID (restricted permissions, no symlink following)
    pid_file = expand(config.get("general", {}).get("pid_file", "~/.openclaw/reefwatch.pid"))
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        pid_flags |= os.O_NOFOLLOW
    fd = os.open(str(pid_file), pid_flags, 0o600)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)

    # Signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start
    daemon = ReefWatchDaemon(config, webhook_url, webhook_token)
    daemon.run()

    # Cleanup — only unlink if it's a regular file (not a symlink)
    if pid_file.exists() and not pid_file.is_symlink():
        pid_file.unlink(missing_ok=True)
