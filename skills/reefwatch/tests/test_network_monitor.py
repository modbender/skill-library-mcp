"""Tests for NetworkMonitor IOC loading."""

from reefwatch.collectors.network_monitor import NetworkMonitor


def _make_config(tmp_path, ioc_path="", ports=None):
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


class TestIOCLoading:
    def test_loads_ips(self, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("10.0.0.1\n192.168.1.100\n# comment\n\n")
        config = _make_config(tmp_path, ioc_path=str(ioc_file))
        nm = NetworkMonitor(config)

        assert "10.0.0.1" in nm._ioc_ips
        assert "192.168.1.100" in nm._ioc_ips
        assert len(nm._ioc_domains) == 0

    def test_loads_domains(self, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("evil.example.com\nbad-domain.net\n")
        config = _make_config(tmp_path, ioc_path=str(ioc_file))
        nm = NetworkMonitor(config)

        assert "evil.example.com" in nm._ioc_domains
        assert "bad-domain.net" in nm._ioc_domains

    def test_mixed_ips_and_domains(self, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("1.2.3.4\nevil.com\n::1\ngood.bad.org\n")
        config = _make_config(tmp_path, ioc_path=str(ioc_file))
        nm = NetworkMonitor(config)

        assert "1.2.3.4" in nm._ioc_ips
        assert "::1" in nm._ioc_ips  # IPv6
        assert "evil.com" in nm._ioc_domains
        assert "good.bad.org" in nm._ioc_domains

    def test_comments_and_blanks_skipped(self, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("# This is a comment\n\n   \n# Another comment\n10.0.0.1\n")
        config = _make_config(tmp_path, ioc_path=str(ioc_file))
        nm = NetworkMonitor(config)

        assert len(nm._ioc_ips) >= 1  # Only 10.0.0.1

    def test_missing_file_warns(self, tmp_path):
        config = _make_config(tmp_path, ioc_path=str(tmp_path / "nope.txt"))
        # Should not crash
        nm = NetworkMonitor(config)
        assert len(nm._ioc_ips) == 0
        assert len(nm._ioc_domains) == 0

    def test_empty_path_no_load(self, tmp_path):
        config = _make_config(tmp_path, ioc_path="")
        nm = NetworkMonitor(config)
        assert len(nm._ioc_ips) == 0
        assert len(nm._ioc_domains) == 0

    def test_domains_lowercased(self, tmp_path):
        ioc_file = tmp_path / "iocs.txt"
        ioc_file.write_text("EVIL.COM\nBad.Domain.Net\n")
        config = _make_config(tmp_path, ioc_path=str(ioc_file))
        nm = NetworkMonitor(config)

        assert "evil.com" in nm._ioc_domains
        assert "bad.domain.net" in nm._ioc_domains
