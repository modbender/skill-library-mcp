"""Tests for NetworkMonitor.check() — LISTEN detection, DNS cache, suspicious ports."""

from collections import namedtuple
from unittest.mock import patch, MagicMock

from reefwatch.collectors.network_monitor import NetworkMonitor


def _make_config(ports=None, ioc_path=""):
    return {
        "collectors": {
            "network": {
                "enabled": True,
                "interval_seconds": 60,
                "suspicious_ports": ports or [],
                "connection_rate_threshold": 50,
                "ioc_blocklist": ioc_path,
            },
        },
    }


# Fake psutil connection objects
_Addr = namedtuple("Addr", ["ip", "port"])


def _conn(status, raddr=None, laddr=None, pid=None):
    c = MagicMock()
    c.status = status
    c.raddr = _Addr(*raddr) if raddr else None
    c.laddr = _Addr(*laddr) if laddr else None
    c.pid = pid
    return c


class TestSuspiciousPorts:
    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_detects_established_to_suspicious_port(self, mock_conns):
        mock_conns.return_value = [
            _conn("ESTABLISHED", raddr=("1.2.3.4", 4444), laddr=("0.0.0.0", 54321), pid=100),
        ]
        nm = NetworkMonitor(_make_config(ports=[4444, 1337]))
        alerts = nm.check()
        assert any(a["type"] == "Connection to suspicious port" for a in alerts)
        assert any("4444" in a["detail"] for a in alerts)

    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_non_suspicious_port_no_alert(self, mock_conns):
        mock_conns.return_value = [
            _conn("ESTABLISHED", raddr=("1.2.3.4", 443), laddr=("0.0.0.0", 54321), pid=200),
        ]
        nm = NetworkMonitor(_make_config(ports=[4444]))
        alerts = nm.check()
        assert len(alerts) == 0


class TestListenDetection:
    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_detects_listen_on_suspicious_port(self, mock_conns):
        mock_conns.return_value = [
            _conn("LISTEN", laddr=("0.0.0.0", 4444), pid=300),
        ]
        nm = NetworkMonitor(_make_config(ports=[4444]))
        alerts = nm.check()
        assert len(alerts) == 1
        assert alerts[0]["type"] == "Listening on suspicious port"
        assert "LISTEN" in alerts[0]["detail"]

    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_listen_on_normal_port_no_alert(self, mock_conns):
        mock_conns.return_value = [
            _conn("LISTEN", laddr=("0.0.0.0", 80), pid=400),
        ]
        nm = NetworkMonitor(_make_config(ports=[4444]))
        alerts = nm.check()
        assert len(alerts) == 0


class TestIOCBlocklist:
    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_detects_connection_to_ioc_ip(self, mock_conns, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("10.0.0.1\n")
        mock_conns.return_value = [
            _conn("ESTABLISHED", raddr=("10.0.0.1", 80), laddr=("0.0.0.0", 12345), pid=500),
        ]
        nm = NetworkMonitor(_make_config(ioc_path=str(ioc_file)))
        alerts = nm.check()
        assert any(a["type"] == "Connection to known malicious IP" for a in alerts)

    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_non_ioc_ip_no_alert(self, mock_conns, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("10.0.0.1\n")
        mock_conns.return_value = [
            _conn("ESTABLISHED", raddr=("8.8.8.8", 443), laddr=("0.0.0.0", 12345), pid=600),
        ]
        nm = NetworkMonitor(_make_config(ioc_path=str(ioc_file)))
        alerts = nm.check()
        assert not any(a["type"] == "Connection to known malicious IP" for a in alerts)


class TestDNSCache:
    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    @patch("reefwatch.collectors.network_monitor.socket.gethostbyaddr")
    def test_reverse_dns_cached(self, mock_dns, mock_conns, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("evil.com\n")
        mock_dns.return_value = ("evil.com", [], [])
        mock_conns.return_value = [
            _conn("ESTABLISHED", raddr=("5.5.5.5", 80), laddr=("0.0.0.0", 12345), pid=700),
        ]
        nm = NetworkMonitor(_make_config(ioc_path=str(ioc_file)))

        # First check — DNS lookup happens
        nm.check()
        assert mock_dns.call_count == 1
        assert "5.5.5.5" in nm._dns_cache

        # Second check — cached, no new DNS call
        nm.check()
        assert mock_dns.call_count == 1  # Still 1

    def test_reverse_dns_method_caches_result(self):
        nm = NetworkMonitor(_make_config())
        with patch("reefwatch.collectors.network_monitor.socket.gethostbyaddr") as mock_dns:
            mock_dns.return_value = ("example.com", [], [])
            result = nm._reverse_dns("1.2.3.4")
            assert result == "example.com"
            assert nm._dns_cache["1.2.3.4"] == "example.com"

            # Second call doesn't invoke gethostbyaddr
            result2 = nm._reverse_dns("1.2.3.4")
            assert result2 == "example.com"
            assert mock_dns.call_count == 1

    def test_reverse_dns_failure_cached_as_none(self):
        import socket
        nm = NetworkMonitor(_make_config())
        with patch("reefwatch.collectors.network_monitor.socket.gethostbyaddr") as mock_dns:
            mock_dns.side_effect = socket.herror("not found")
            result = nm._reverse_dns("9.9.9.9")
            assert result is None
            assert nm._dns_cache["9.9.9.9"] is None

    def test_dns_cache_eviction(self):
        nm = NetworkMonitor(_make_config())
        nm._max_dns_cache = 10
        # Fill cache to the limit
        for i in range(10):
            nm._dns_cache[f"10.0.0.{i}"] = f"host{i}.com"
        # Add one more via _reverse_dns — triggers eviction (evicts 20% = 2)
        with patch("reefwatch.collectors.network_monitor.socket.gethostbyaddr") as mock_dns:
            mock_dns.return_value = ("new.com", [], [])
            nm._reverse_dns("192.168.1.1")
        # 11 entries, evicts 20% (2), leaves 9
        assert len(nm._dns_cache) <= 10


class TestConnectionRate:
    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_high_rate_alerts(self, mock_conns):
        conns = [
            _conn("ESTABLISHED", raddr=(f"10.0.0.{i}", 80), laddr=("0.0.0.0", 10000 + i), pid=i)
            for i in range(60)
        ]
        mock_conns.return_value = conns
        nm = NetworkMonitor(_make_config())
        nm._prev_connections = set()  # Empty — all 60 are "new"
        alerts = nm.check()
        assert any(a["type"] == "High connection rate" for a in alerts)

    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_low_rate_no_alert(self, mock_conns):
        conns = [
            _conn("ESTABLISHED", raddr=("10.0.0.1", 80), laddr=("0.0.0.0", 12345), pid=1),
        ]
        mock_conns.return_value = conns
        nm = NetworkMonitor(_make_config())
        alerts = nm.check()
        assert not any(a["type"] == "High connection rate" for a in alerts)


class TestAccessDenied:
    @patch("reefwatch.collectors.network_monitor.psutil.net_connections")
    def test_falls_back_to_inet4(self, mock_conns):
        import psutil
        mock_conns.side_effect = [psutil.AccessDenied(pid=0), []]
        nm = NetworkMonitor(_make_config())
        alerts = nm.check()
        assert mock_conns.call_count == 2
        assert alerts == []
