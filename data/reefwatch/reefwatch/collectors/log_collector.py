"""
reefwatch.collectors.log_collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tails system log files for new entries.
"""

import json
import subprocess
from datetime import datetime, timezone

from reefwatch._common import SYSTEM, expand, get_os_key, logger


class LogCollector:
    """Tails system log files for new entries."""

    def __init__(self, config: dict):
        self.enabled = config.get("collectors", {}).get("logs", {}).get("enabled", True)
        self.interval = (
            config.get("collectors", {}).get("logs", {}).get("interval_seconds", 10)
        )
        os_key = get_os_key()
        sources_cfg = config.get("collectors", {}).get("logs", {}).get("sources", {})
        self.sources = [
            expand(s) for s in sources_cfg.get(os_key, []) if expand(s).exists()
        ]
        self._file_positions: dict[str, int] = {}
        self.use_journald = (
            config.get("collectors", {}).get("logs", {}).get("use_journald", True)
            and SYSTEM == "Linux"
        )
        # Pre-set so first cycle captures events since startup
        # Use local time because journalctl --since interprets timestamps as local
        self._last_journald_ts: str | None = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.use_journald else None
        )

        self.use_unified_log = (
            config.get("collectors", {}).get("logs", {}).get("use_unified_log", True)
            and SYSTEM == "Darwin"
        )
        self._last_unified_ts: str | None = None

        # Initialize positions to end of file (only read new lines)
        for src in self.sources:
            try:
                self._file_positions[str(src)] = src.stat().st_size
            except Exception as e:
                logger.debug(f"Cannot get size of {src}, starting from 0: {e}")
                self._file_positions[str(src)] = 0

        log_extras = []
        if self.use_journald:
            log_extras.append("+journald")
        if self.use_unified_log:
            log_extras.append("+unified_log")
        logger.info(
            f"LogCollector initialized: {len(self.sources)} sources"
            + (f" {' '.join(log_extras)}" if log_extras else "")
        )

    def collect(self) -> list[dict]:
        """Returns list of new log entries as dicts."""
        entries = []

        # Collect from journald on Linux
        if self.use_journald:
            entries.extend(self._collect_journald())

        # Collect from macOS unified log
        if self.use_unified_log:
            entries.extend(self._collect_unified_log())

        for src in self.sources:
            try:
                src_str = str(src)
                current_size = src.stat().st_size
                last_pos = self._file_positions.get(src_str, 0)

                # Handle log rotation
                if current_size < last_pos:
                    last_pos = 0

                if current_size > last_pos:
                    max_read = 10 * 1024 * 1024  # 10 MB cap per cycle
                    with open(src, "r", errors="replace") as f:
                        f.seek(last_pos)
                        data = f.read(max_read)
                        actual_pos = f.tell()
                        # Guard against truncation between stat() and read():
                        # if we read nothing despite stat() saying there's data,
                        # the file was likely truncated — reset to current end.
                        if not data and actual_pos <= last_pos:
                            self._file_positions[src_str] = 0
                            continue
                        self._file_positions[src_str] = actual_pos
                    new_lines = data.splitlines()

                    for line in new_lines:
                        line = line.strip()
                        if line:
                            entries.append(
                                {
                                    "source": src.name,
                                    "source_path": src_str,
                                    "line": line[:self._MAX_LOG_LINE],
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }
                            )
            except PermissionError:
                logger.debug(f"No permission to read {src}")
            except Exception as e:
                logger.debug(f"Error reading {src}: {e}")

        return entries

    def _collect_journald(self) -> list[dict]:
        """Collect new entries from systemd journal."""
        entries = []
        try:
            cmd = [
                "journalctl", "--output=json", "--no-pager",
                "--since", self._last_journald_ts,
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                logger.debug(f"journalctl returned {result.returncode}")
                return entries

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    # Use journal entry's own timestamp if available
                    rt = record.get("__REALTIME_TIMESTAMP")
                    if rt:
                        ts = datetime.fromtimestamp(
                            int(rt) / 1_000_000, tz=timezone.utc
                        ).isoformat()
                    else:
                        ts = datetime.now(timezone.utc).isoformat()
                    entries.append(
                        {
                            "source": "journald",
                            "source_path": "journald",
                            "line": record.get("MESSAGE", ""),
                            "unit": record.get("_SYSTEMD_UNIT", ""),
                            "priority": record.get("PRIORITY", ""),
                            "timestamp": ts,
                        }
                    )
                except json.JSONDecodeError:
                    continue

            # Update timestamp for next collection (local time for journalctl).
            # Use the last event's real timestamp + 1µs to avoid the 1-second
            # gap that could miss events.  Fall back to now() if no events.
            if entries:
                last_rt = None
                for line in reversed(result.stdout.strip().split("\n")):
                    try:
                        last_rt = int(json.loads(line).get("__REALTIME_TIMESTAMP", 0))
                    except (json.JSONDecodeError, ValueError, TypeError):
                        continue
                    if last_rt:
                        break
                if last_rt:
                    last_dt = datetime.fromtimestamp(
                        (last_rt + 1) / 1_000_000
                    )
                    self._last_journald_ts = last_dt.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    self._last_journald_ts = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
            else:
                # No events — advance to now so next poll starts fresh
                self._last_journald_ts = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        except FileNotFoundError:
            logger.debug("journalctl not found, disabling journald collection")
            self.use_journald = False
        except subprocess.TimeoutExpired:
            logger.warning("journalctl timed out")
        except Exception as e:
            logger.debug(f"journald collection error: {e}")

        return entries

    _MAX_LOG_LINE = 8192  # Truncate individual log lines to prevent OOM

    def _collect_unified_log(self) -> list[dict]:
        """Collect new entries from macOS unified log via ``log show``."""
        entries = []
        try:
            cmd = [
                "log", "show", "--style", "ndjson",
                "--predicate", "eventType == logEvent",
                "--last", f"{self.interval}s",
            ]
            if self._last_unified_ts:
                cmd = [
                    "log", "show", "--style", "ndjson",
                    "--predicate", "eventType == logEvent",
                    "--start", self._last_unified_ts,
                ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logger.debug(f"log show returned {result.returncode}")
                return entries

            for raw_line in result.stdout.strip().split("\n"):
                if not raw_line:
                    continue
                try:
                    record = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                ts = record.get("timestamp", datetime.now(timezone.utc).isoformat())
                msg = record.get("eventMessage", "")
                if not msg:
                    continue
                entries.append(
                    {
                        "source": "unified_log",
                        "source_path": "unified_log",
                        "line": msg[:self._MAX_LOG_LINE],
                        "process": record.get("processImagePath", ""),
                        "subsystem": record.get("subsystem", ""),
                        "category": record.get("category", ""),
                        "timestamp": ts,
                    }
                )

            # Format compatible with `log show --start` (local time, no tz)
            self._last_unified_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except FileNotFoundError:
            logger.debug("log command not found, disabling unified log collection")
            self.use_unified_log = False
        except subprocess.TimeoutExpired:
            logger.warning("log show timed out")
        except Exception as e:
            logger.debug(f"unified log collection error: {e}")

        return entries
