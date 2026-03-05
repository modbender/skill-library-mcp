"""
reefwatch.collectors.network_monitor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Monitors network connections for suspicious activity.
"""

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from datetime import datetime, timezone
from pathlib import Path

import psutil

from reefwatch._common import logger

# Default socket timeout for reverse DNS (prevents blocking)
_DNS_TIMEOUT = 2.0


class NetworkMonitor:
    """Monitors network connections for suspicious activity."""

    def __init__(self, config: dict):
        net_cfg = config.get("collectors", {}).get("network", {})
        self.enabled = net_cfg.get("enabled", True)
        self.interval = net_cfg.get("interval_seconds", 60)
        self.suspicious_ports = set(net_cfg.get("suspicious_ports", []))
        self.rate_threshold = net_cfg.get("connection_rate_threshold", 50)
        self._prev_connections: set[tuple] = set()
        self._ioc_ips: set[str] = set()
        self._ioc_domains: set[str] = set()

        # DNS reverse-lookup cache: ip -> (hostname | None)
        self._dns_cache: dict[str, str | None] = {}
        self._max_dns_cache = 5_000
        self._max_rdns_per_cycle = 20  # Cap reverse lookups per check()
        self._rdns_executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="rdns"
        )

        # Load IOC blocklist
        ioc_path = net_cfg.get("ioc_blocklist", "")
        if ioc_path:
            self._load_iocs(ioc_path)

        logger.info(
            f"NetworkMonitor initialized: {len(self.suspicious_ports)} ports, "
            f"{len(self._ioc_ips)} IOC IPs"
        )

    def _load_iocs(self, path: str):
        p = Path(path)
        if not p.is_absolute():
            # Resolve relative to project root (same convention as engines)
            p = Path(__file__).parent.parent.parent / p
        if not p.exists():
            logger.warning(f"IOC blocklist not found: {p}")
            return
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    ipaddress.ip_address(line)
                    self._ioc_ips.add(line)
                except ValueError:
                    # Not a valid IP — treat as domain
                    self._ioc_domains.add(line.lower())
                    # Pre-resolve domain to IPs for efficient matching
                    try:
                        for info in socket.getaddrinfo(line, None):
                            self._ioc_ips.add(info[4][0])
                    except socket.gaierror:
                        logger.debug(f"Cannot resolve IOC domain: {line}")
        logger.info(
            f"IOCs loaded: {len(self._ioc_ips)} IPs, "
            f"{len(self._ioc_domains)} domains"
        )

    def _reverse_dns(self, ip: str) -> str | None:
        """Cached reverse DNS lookup with timeout (thread-safe, no global state)."""
        if ip in self._dns_cache:
            return self._dns_cache[ip]
        try:
            future = self._rdns_executor.submit(socket.gethostbyaddr, ip)
            hostname, _, _ = future.result(timeout=_DNS_TIMEOUT)
            self._dns_cache[ip] = hostname.lower() if hostname else None
        except (FuturesTimeout, socket.herror, socket.gaierror, OSError):
            self._dns_cache[ip] = None
        # Evict oldest if cache too large
        if len(self._dns_cache) > self._max_dns_cache:
            # Remove first 20% of entries (insertion order in Python 3.7+)
            evict = len(self._dns_cache) // 5
            for k in list(self._dns_cache)[:evict]:
                del self._dns_cache[k]
        return self._dns_cache.get(ip)

    def _is_ioc_domain(self, hostname: str) -> bool:
        """Check if hostname matches an IOC domain or is a subdomain of one."""
        hostname = hostname.lower()
        if hostname in self._ioc_domains:
            return True
        for ioc_domain in self._ioc_domains:
            if hostname.endswith("." + ioc_domain):
                return True
        return False

    def check(self) -> list[dict]:
        alerts = []
        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, PermissionError):
            logger.debug("No permission for net_connections, trying inet4 only")
            try:
                connections = psutil.net_connections(kind="inet4")
            except Exception as e:
                logger.warning(f"Cannot access network connections: {e}")
                return alerts

        current_conns = set()
        rdns_count = 0

        for conn in connections:
            # Detect LISTEN sockets on suspicious ports
            if conn.status == "LISTEN" and conn.laddr:
                local_port = conn.laddr.port
                if local_port in self.suspicious_ports:
                    alerts.append(
                        {
                            "type": "Listening on suspicious port",
                            "severity": "HIGH",
                            "source": "network_monitor",
                            "detail": (
                                f"LISTEN on {conn.laddr.ip}:{local_port} "
                                f"(PID: {conn.pid})"
                            ),
                            "rule": f"custom/suspicious_listen/{local_port}",
                            "time": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            if conn.status == "ESTABLISHED" and conn.raddr:
                remote_ip = conn.raddr.ip
                remote_port = conn.raddr.port
                current_conns.add((remote_ip, remote_port))

                # Check suspicious ports
                if remote_port in self.suspicious_ports:
                    alerts.append(
                        {
                            "type": "Connection to suspicious port",
                            "severity": "HIGH",
                            "source": "network_monitor",
                            "detail": (
                                f"Connection to {remote_ip}:{remote_port} "
                                f"(PID: {conn.pid})"
                            ),
                            "rule": f"custom/suspicious_port/{remote_port}",
                            "time": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                # Check IOC blocklist (IPs)
                if remote_ip in self._ioc_ips:
                    alerts.append(
                        {
                            "type": "Connection to known malicious IP",
                            "severity": "CRITICAL",
                            "source": "network_monitor",
                            "detail": (
                                f"Connection to IOC {remote_ip}:{remote_port} "
                                f"(PID: {conn.pid})"
                            ),
                            "rule": "custom/ioc_blocklist",
                            "time": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                # Reverse-DNS check against IOC domains (with cache + cap)
                if (
                    self._ioc_domains
                    and remote_ip not in self._ioc_ips
                    and rdns_count < self._max_rdns_per_cycle
                ):
                    rdns_count += 1
                    hostname = self._reverse_dns(remote_ip)
                    if hostname and self._is_ioc_domain(hostname):
                        alerts.append(
                            {
                                "type": "Connection to known malicious domain",
                                "severity": "CRITICAL",
                                "source": "network_monitor",
                                "detail": (
                                    f"Connection to IOC domain "
                                    f"{hostname} ({remote_ip}:{remote_port}) "
                                    f"(PID: {conn.pid})"
                                ),
                                "rule": "custom/ioc_domain",
                                "time": datetime.now(timezone.utc).isoformat(),
                            }
                        )

        # Check connection rate (normalized to per-minute)
        new_conns = current_conns - self._prev_connections
        rate_per_minute = len(new_conns) * 60 / max(self.interval, 1)
        if rate_per_minute > self.rate_threshold:
            alerts.append(
                {
                    "type": "High connection rate",
                    "severity": "MEDIUM",
                    "source": "network_monitor",
                    "detail": (
                        f"{len(new_conns)} new connections in {self.interval}s "
                        f"({rate_per_minute:.0f}/min)"
                    ),
                    "rule": "custom/connection_rate",
                    "time": datetime.now(timezone.utc).isoformat(),
                }
            )

        self._prev_connections = current_conns
        return alerts

    def shutdown(self):
        """Release the reverse-DNS thread pool."""
        self._rdns_executor.shutdown(wait=False)
