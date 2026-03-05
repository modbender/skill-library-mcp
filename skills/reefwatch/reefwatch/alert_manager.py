"""
reefwatch.alert_manager
~~~~~~~~~~~~~~~~~~~~~~~
Deduplicates, batches, and delivers alerts to OpenClaw webhook.
"""

import hashlib
import ipaddress
import json
import os
import socket
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from reefwatch._common import expand, logger


class AlertManager:
    """Deduplicates, batches, and delivers alerts to OpenClaw webhook."""

    def __init__(self, config: dict, webhook_url: str, webhook_token: str):
        self.alerting_config = config.get("alerting", {})
        self.webhook_config = config.get("webhook", {})
        self.webhook_url = webhook_url
        self.webhook_token = webhook_token
        self._webhook_host_header: str = ""  # Original Host for HTTP header
        self._validate_webhook_url()
        self.dedup_window = self.alerting_config.get("dedup_window_seconds", 300)
        self.min_severity = self.alerting_config.get("min_severity", "MEDIUM")
        self.batch_alerts_flag = self.alerting_config.get("batch_alerts", True)
        self.batch_window = self.alerting_config.get("batch_window_seconds", 30)

        self._recent: dict[str, float] = {}  # dedup_key -> last_alert_timestamp
        self._max_dedup_entries = 10_000  # Cap dedup dict to prevent unbounded growth
        self._dedup_lock = threading.Lock()
        self._batch: list[dict] = []
        self._batch_lock = threading.Lock()
        self._history_lock = threading.Lock()
        self._batch_timer: threading.Timer | None = None

        self.history_file = expand(
            config.get("general", {}).get(
                "alerts_history",
                "~/.openclaw/workspace/skills/reefwatch/scripts/alerts_history.json",
            )
        )
        self.max_history = config.get("general", {}).get("max_alerts_history", 500)

        # Seed _history_count from existing file so rotation triggers correctly
        self._history_count: int = 0
        try:
            if self.history_file.exists():
                with open(self.history_file) as f:
                    self._history_count = sum(1 for _ in f)
        except Exception:
            pass

        severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        self._min_sev_idx = (
            severity_order.index(self.min_severity)
            if self.min_severity in severity_order
            else 1
        )
        self._severity_order = severity_order

    def submit(self, alert: dict) -> bool:
        """Submit an alert for processing. Returns True if accepted (not filtered/deduped)."""
        sev = alert.get("severity", "MEDIUM")
        try:
            sev_idx = self._severity_order.index(sev)
        except ValueError:
            logger.warning(f"Unknown severity '{sev}' in alert, treating as MEDIUM")
            sev_idx = self._severity_order.index("MEDIUM")
        if sev_idx < self._min_sev_idx:
            logger.debug(f"Alert below min severity ({sev}): {alert.get('type')}")
            return False

        # Dedup key includes rule + hash of detail to avoid collisions
        # on long paths sharing a prefix
        detail_hash = hashlib.md5(
            alert.get("detail", "").encode(), usedforsecurity=False
        ).hexdigest()[:16]
        dedup_key = f"{alert.get('rule', 'unknown')}:{detail_hash}"
        now = time.time()
        with self._dedup_lock:
            if dedup_key in self._recent:
                if now - self._recent[dedup_key] < self.dedup_window:
                    logger.debug(f"Dedup: skipping repeat alert for {dedup_key}")
                    return False
            self._recent[dedup_key] = now

            # Clean old dedup entries and enforce cap
            cutoff = now - self.dedup_window
            self._recent = {k: v for k, v in self._recent.items() if v > cutoff}
            if len(self._recent) > self._max_dedup_entries:
                sorted_keys = sorted(self._recent, key=self._recent.get)
                for k in sorted_keys[: len(self._recent) - self._max_dedup_entries]:
                    del self._recent[k]

        self._save_to_history(alert)

        if self.batch_alerts_flag:
            self._add_to_batch(alert)
        else:
            self._send([alert])
        return True

    def _add_to_batch(self, alert: dict):
        with self._batch_lock:
            self._batch.append(alert)
            if self._batch_timer is None:
                self._batch_timer = threading.Timer(
                    self.batch_window, self._flush_batch
                )
                self._batch_timer.daemon = True
                self._batch_timer.start()

    def _flush_batch(self):
        with self._batch_lock:
            batch = self._batch[:]
            self._batch.clear()
            self._batch_timer = None
        if batch:
            self._send(batch)

    def _send(self, alerts: list[dict]):
        """Send alert(s) to OpenClaw via webhook."""
        if not self.webhook_url:
            logger.warning("No webhook URL configured, printing alert to log only")
            for a in alerts:
                logger.warning(f"ALERT: {json.dumps(a)}")
            return

        lines = ["🔴 REEFWATCH ALERT", "━" * 24]
        for a in alerts:
            lines.append(f"Type: {a.get('type', 'Unknown')}")
            lines.append(f"Severity: {a.get('severity', 'MEDIUM')}")
            lines.append(f"Source: {a.get('source', 'N/A')}")
            lines.append(f"Detail: {a.get('detail', 'N/A')}")
            lines.append(f"Rule: {a.get('rule', 'N/A')}")
            lines.append(f"Time: {a.get('time', datetime.now(timezone.utc).isoformat())}")
            if len(alerts) > 1:
                lines.append("─" * 24)
        lines.append("━" * 24)

        message = "\n".join(lines)

        headers = {"Content-Type": "application/json"}
        if self._webhook_host_header:
            headers["Host"] = self._webhook_host_header
        if self.webhook_token:
            headers["Authorization"] = f"Bearer {self.webhook_token}"

        retry = self._config_retry()
        for attempt in range(retry["attempts"]):
            try:
                resp = requests.post(
                    self.webhook_url,
                    json={"text": message, "mode": "now"},
                    headers=headers,
                    timeout=10,
                )
                if resp.ok:
                    logger.info(f"Alert delivered ({len(alerts)} alerts)")
                    return
                logger.warning(f"Webhook returned {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.warning(f"Webhook attempt {attempt+1} failed: {e}")
            if attempt < retry["attempts"] - 1:
                time.sleep(retry["delay"])

        logger.error("Failed to deliver alert after retries")

    def shutdown(self):
        """Cancel pending timer and flush remaining alerts before exit."""
        with self._batch_lock:
            if self._batch_timer is not None:
                self._batch_timer.cancel()
                self._batch_timer = None
            batch = self._batch[:]
            self._batch.clear()
        if batch:
            self._send(batch)

    @staticmethod
    def _is_loopback(hostname: str) -> bool:
        """Check if hostname resolves to a loopback address."""
        # Fast-path for common names
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return True
        try:
            addr = ipaddress.ip_address(hostname)
            return addr.is_loopback
        except ValueError:
            pass
        # Resolve hostname and check all resulting IPs
        try:
            for info in socket.getaddrinfo(hostname, None, socket.AF_UNSPEC):
                addr = ipaddress.ip_address(info[4][0])
                if not addr.is_loopback:
                    return False
            return True  # All resolved IPs are loopback
        except (socket.gaierror, OSError):
            return False

    def _validate_webhook_url(self):
        """SSRF prevention: resolve hostname to IP at init time and pin it.

        This prevents DNS rebinding attacks where the hostname resolves to
        a loopback at validation time but a different IP at send time.
        The resolved IP is substituted into the URL and the original Host
        header is preserved for the HTTP request.
        """
        if not self.webhook_url:
            return
        parsed = urlparse(self.webhook_url)
        if parsed.scheme not in ("http", "https"):
            logger.error(
                f"Webhook URL has unsupported scheme '{parsed.scheme}', disabling webhook"
            )
            self.webhook_url = ""
            return
        hostname = parsed.hostname or ""
        is_local = self._is_loopback(hostname)
        allow_external = self.webhook_config.get("allow_external", False)
        if not is_local and not allow_external:
            logger.error(
                f"Webhook URL host '{hostname}' is not localhost. "
                f"Refusing to send alerts externally. "
                f"Set webhook.allow_external: true in config to allow."
            )
            self.webhook_url = ""
            return
        # Require HTTPS for non-loopback targets (when allow_external is true)
        if not is_local and parsed.scheme != "https":
            logger.error(
                f"Webhook URL uses HTTP for external host '{hostname}'. "
                f"HTTPS is required for external webhooks."
            )
            self.webhook_url = ""
            return

        # Pin the resolved IP to prevent DNS rebinding between validation
        # and request time (TOCTOU).  For loopback names we resolve to the
        # canonical 127.0.0.1 so that requests.post() never re-resolves.
        try:
            resolved_ip = self._resolve_to_ip(hostname)
        except OSError:
            logger.error(f"Cannot resolve webhook hostname '{hostname}', disabling")
            self.webhook_url = ""
            return

        if resolved_ip and resolved_ip != hostname:
            # Rewrite URL to use resolved IP, keep original host for Host header
            self._webhook_host_header = hostname
            # IPv6 literals must be bracketed in URLs (RFC 2732)
            ip_str = f"[{resolved_ip}]" if ":" in resolved_ip else resolved_ip
            port = f":{parsed.port}" if parsed.port else ""
            self.webhook_url = (
                f"{parsed.scheme}://{ip_str}{port}{parsed.path}"
                + (f"?{parsed.query}" if parsed.query else "")
            )

    @staticmethod
    def _resolve_to_ip(hostname: str) -> str:
        """Resolve a hostname to its first IP address string.

        Returns the IP unchanged if *hostname* is already an IP literal.
        Raises OSError on DNS failure.
        """
        try:
            ipaddress.ip_address(hostname)
            return hostname  # Already an IP literal
        except ValueError:
            pass
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
        if infos:
            return infos[0][4][0]
        return hostname

    def _config_retry(self):
        return {
            "attempts": self.webhook_config.get("retry_attempts", 3),
            "delay": self.webhook_config.get("retry_delay_seconds", 5),
        }

    def _save_to_history(self, alert: dict):
        with self._history_lock:
            try:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                hist_flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
                if hasattr(os, "O_NOFOLLOW"):
                    hist_flags |= os.O_NOFOLLOW
                fd = os.open(str(self.history_file), hist_flags, 0o600)
                with os.fdopen(fd, "a") as f:
                    f.write(json.dumps(alert, default=str) + "\n")
                self._history_count += 1
                if self._history_count % 50 == 0:
                    self._rotate_history_locked()
            except Exception as e:
                logger.warning(f"Failed to save alert history: {e}")

    def _rotate_history_locked(self):
        """Keep only the last max_history alerts (caller holds _history_lock)."""
        try:
            lines = self.history_file.read_text().strip().splitlines()
            if len(lines) <= self.max_history:
                return
            trimmed = "\n".join(lines[-self.max_history:]) + "\n"
            fd, tmp_path = tempfile.mkstemp(
                dir=str(self.history_file.parent)
            )
            try:
                os.fchmod(fd, 0o600)
                os.write(fd, trimmed.encode())
                os.close(fd)
                fd = -1
                os.replace(tmp_path, str(self.history_file))
                self._history_count = min(len(lines), self.max_history)
                tmp_path = None
            except Exception:
                if fd >= 0:
                    os.close(fd)
                if tmp_path and Path(tmp_path).exists():
                    os.unlink(tmp_path)
                raise
        except Exception as e:
            logger.debug(f"History rotation failed: {e}")
