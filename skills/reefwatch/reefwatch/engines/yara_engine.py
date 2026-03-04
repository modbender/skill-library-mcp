"""
reefwatch.engines.yara_engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Scans files using YARA rules.
"""

import time
from datetime import datetime, timezone
from pathlib import Path

from reefwatch._common import logger


class YaraEngine:
    """Scans files using YARA rules."""

    def __init__(self, config: dict):
        yara_cfg = config.get("engines", {}).get("yara", {})
        self.enabled = yara_cfg.get("enabled", True)
        base = Path(__file__).parent.parent.parent
        raw_rules = yara_cfg.get("rules_dir", "rules/yara")
        if Path(raw_rules).is_absolute():
            candidate = Path(raw_rules).resolve()
        else:
            candidate = (base / raw_rules).resolve()
            if not candidate.is_relative_to(base.resolve()):
                logger.error(f"YARA rules_dir escapes package root: {raw_rules}")
                self.enabled = False
                candidate = base / "rules" / "yara"
        self.rules_dir = candidate
        self.max_file_size = yara_cfg.get("max_file_size_mb", 50) * 1024 * 1024
        self.timeout = yara_cfg.get("timeout_seconds", 30)
        self.mode = yara_cfg.get("mode", "on_change")  # "on_change" or "scheduled"
        self.scheduled_interval = (
            yara_cfg.get("scheduled_interval_hours", 24) * 3600
        )
        self._last_scheduled_scan: float = 0.0
        self._rules = None

        if self.enabled:
            self._compile_rules()

    def _compile_rules(self):
        try:
            import yara

            if not self.rules_dir.exists():
                logger.warning(f"YARA rules dir not found: {self.rules_dir}")
                self.enabled = False
                return

            rule_files = list(self.rules_dir.glob("**/*.yar")) + list(
                self.rules_dir.glob("**/*.yara")
            )
            if not rule_files:
                logger.warning("No YARA rules found")
                self.enabled = False
                return

            filepaths = {f"rule_{i}": str(r) for i, r in enumerate(rule_files)}
            self._rules = yara.compile(filepaths=filepaths)
            logger.info(f"YaraEngine: compiled {len(rule_files)} rule files")

        except ImportError:
            logger.warning("yara-python not installed, YARA engine disabled")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to compile YARA rules: {e}")
            self.enabled = False

    def scan_file(self, filepath: str) -> list[dict]:
        """Scan a single file, return list of alerts."""
        if not self.enabled or not self._rules:
            return []

        alerts = []
        p = Path(filepath)

        try:
            if p.is_symlink() or not p.exists() or not p.is_file():
                return []
            if p.stat().st_size > self.max_file_size:
                return []

            matches = self._rules.match(str(p), timeout=self.timeout)
            for match in matches:
                alerts.append(
                    {
                        "type": f"YARA match: {match.rule}",
                        "severity": "HIGH",
                        "source": "yara_engine",
                        "detail": f"File: {filepath} | Tags: {', '.join(match.tags)}",
                        "rule": f"yara/{match.rule}",
                        "time": datetime.now(timezone.utc).isoformat(),
                    }
                )
        except Exception as e:
            logger.debug(f"YARA scan error on {filepath}: {e}")

        return alerts

    def should_run_scheduled_scan(self) -> bool:
        """Check if a scheduled full scan is due."""
        if not self.enabled or self.mode != "scheduled":
            return False
        return (time.time() - self._last_scheduled_scan) >= self.scheduled_interval

    _MAX_SCAN_FILES = 50_000  # Safety cap for scheduled directory scans

    def scan_directory(self, directory: str) -> list[dict]:
        """Run YARA scan on all files in a directory. Used for scheduled scans."""
        if not self.enabled or not self._rules:
            return []

        alerts = []
        d = Path(directory)
        if not d.is_dir():
            return []

        scanned = 0
        for f in d.rglob("*"):
            if f.is_symlink():
                continue
            if f.is_file():
                alerts.extend(self.scan_file(str(f)))
                scanned += 1
                if scanned >= self._MAX_SCAN_FILES:
                    logger.warning(
                        f"YARA scan cap reached ({self._MAX_SCAN_FILES} files)"
                    )
                    break

        self._last_scheduled_scan = time.time()
        logger.info(f"YARA scheduled scan: {scanned} files, {len(alerts)} matches")
        return alerts
