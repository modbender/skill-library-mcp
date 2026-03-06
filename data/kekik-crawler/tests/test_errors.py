from core.errors import classify_status


def test_classify_status_basic():
    assert classify_status(404) == "not_found"
    assert classify_status(429) == "rate_limited"
    assert classify_status(503) == "server_error"
