
import requests
import pytest
import secrets

BASE_URL = "http://127.0.0.1:8000"

def test_scrub_logic():
    from scripts.core import scrub_data
    data = {"secret": "private-key", "nested": {"url": "http://user:pass@example.com"}}
    scrubbed = scrub_data(data)
    assert "private-key" not in str(scrubbed)
    assert "pass" not in str(scrubbed)
