from core.urlutils import canonicalize


def test_canonicalize_tracking_params_removed_case_insensitive():
    u = "https://Example.com/path/?UTM_Source=x&a=1&fbclid=abc"
    assert canonicalize(u) == "https://example.com/path?a=1"


def test_canonicalize_add_scheme_for_plain_host():
    assert canonicalize("example.com") == "https://example.com/"


def test_canonicalize_empty_safe():
    assert canonicalize("") == ""
