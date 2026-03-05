#!/usr/bin/env python3
"""Pytest configuration — sets up test contacts.json before tests run."""

import json
import os

import pytest

_TEST_CONTACTS = {
    "known_domains": ["acmecorp.com", "partnerfirm.com"],
    "known_emails": ["alice@acmecorp.com"],
    "trusted_senders": ["google.com", "shopify.com", "github.com", "linear.app"],
}

_CONTACTS_PATH = os.path.join(os.path.dirname(__file__), "contacts.json")


@pytest.fixture(autouse=True, scope="session")
def _setup_test_contacts():
    """Write test contacts.json and reset cache for the entire test session."""
    import sanitize_core

    # Save original if it exists
    had_original = os.path.exists(_CONTACTS_PATH)
    original_content = None
    if had_original:
        with open(_CONTACTS_PATH) as f:
            original_content = f.read()

    # Write test contacts
    with open(_CONTACTS_PATH, "w") as f:
        json.dump(_TEST_CONTACTS, f)

    # Reset the contacts cache so it reloads
    sanitize_core._contacts_cache = None

    yield

    # Cleanup: restore original or remove test file
    sanitize_core._contacts_cache = None
    if had_original and original_content is not None:
        with open(_CONTACTS_PATH, "w") as f:
            f.write(original_content)
    elif os.path.exists(_CONTACTS_PATH):
        os.remove(_CONTACTS_PATH)
