from scripts.audit_utils import (
    calculate_shannon_entropy,
    NetworkForensics,
    SupplyChainForensics,
)


def test_entropy():
    assert calculate_shannon_entropy("") == 0.0
    # "aaaaa" has 0 entropy (only 1 char)
    assert calculate_shannon_entropy("aaaaa") == 0.0
    # High entropy string
    ent = calculate_shannon_entropy("abc123XYZ!@#")
    assert ent > 3.0


def test_network_ips():
    text = "Find 192.168.1.1 and 10.0.0.255"
    ips = NetworkForensics.extract_ips(text)
    assert "192.168.1.1" in ips
    assert "10.0.0.255" in ips


def test_network_urls():
    text = "Visit http://example.com and https://secure-site.org/path"
    urls = NetworkForensics.extract_urls(text)
    assert "http://example.com" in urls
    assert "https://secure-site.org/path" in urls


def test_link_safety():
    # Safe
    assert NetworkForensics.check_link_safety("https://github.com/openclaw") is None
    # IP based
    assert "IP address" in NetworkForensics.check_link_safety("http://1.2.3.4/malware")
    # High risk TLD
    assert "high-risk TLD" in NetworkForensics.check_link_safety("https://super.xyz")
    # Phishing keyword
    assert "phishing keywords" in NetworkForensics.check_link_safety(
        "http://verify-account-now.com"
    )


def test_typosquatting():
    assert SupplyChainForensics.check_typosquatting("requests") is None
    # reqests (missing u)
    assert SupplyChainForensics.check_typosquatting("reqests") == "requests"
    # flask -> flsk
    assert SupplyChainForensics.check_typosquatting("flsk") == "flask"


def test_levenshtein():
    assert SupplyChainForensics.levenshtein("kitten", "sitting") == 3
    assert SupplyChainForensics.levenshtein("abc", "") == 3
    assert SupplyChainForensics.levenshtein("", "abc") == 3
