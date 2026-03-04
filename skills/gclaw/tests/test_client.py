"""Tests for GogGmailClient."""

import pytest

from kaimail.client import GogGmailClient


class TestParseThreadOutput:
    """Test thread output parsing without actual gog calls."""

    @pytest.fixture
    def client(self, monkeypatch):
        # Set env var to avoid validation error
        monkeypatch.setenv("GOG_KEYRING_PASSWORD", "test-password")
        return GogGmailClient()

    def test_parses_single_message_thread(self, client):
        output = """Thread contains 1 message(s)

=== Message 1/1: 19ca2f4accefff70 ===
From: GitHub <noreply@github.com>
To: Yonatan <user@gmail.com>
Subject: [GitHub] A third-party GitHub Application has been added
Date: Fri, 27 Feb 2026 22:34:29 -0800

Hey testuser!

A third-party GitHub Application (Codecov) was authorized.

Thanks,
The GitHub Team"""

        thread = client._parse_thread_output("19ca2f4accefff70", output)

        assert thread.thread_id == "19ca2f4accefff70"
        assert thread.message_count == 1
        assert len(thread.messages) == 1

        msg = thread.messages[0]
        assert msg.id == "19ca2f4accefff70"
        assert msg.from_address == "GitHub <noreply@github.com>"
        assert msg.subject == "[GitHub] A third-party GitHub Application has been added"
        assert "Codecov" in msg.body

    def test_parses_multi_message_thread(self, client):
        output = """Thread contains 2 message(s)

=== Message 1/2: 19c9633273a35834 ===
From: Saanya Ojha <saanyaojha@substack.com>
To: user@gmail.com
Subject: Budget Physics in the Age of Agents
Date: Wed, 25 Feb 2026 19:07:28 +0000

Remember how this was supposed to be the age of agents?

=== Message 2/2: 19c99d6d9aad75ff ===
From: Test User <user@gmail.com>
To: Test User <user@gmail.com>
Subject: Fwd: Budget Physics in the Age of Agents
Date: Thu, 26 Feb 2026 14:05:19 +0200

Traditional vertical SaaS gets boxed in."""

        thread = client._parse_thread_output("19c9633273a35834", output)

        assert thread.message_count == 2
        assert len(thread.messages) == 2

        assert thread.messages[0].id == "19c9633273a35834"
        assert thread.messages[1].id == "19c99d6d9aad75ff"

    def test_parses_message_with_attachments(self, client):
        output = """Thread contains 1 message(s)

=== Message 1/1: 19c7a7ecd1f32fcb ===
From: Tabit <tabit-guest-no-reply@tabit.cloud>
To: user@gmail.com
Subject: Reservation Confirmation
Date: Fri, 20 Feb 2026 10:00:54 +0000

Please confirm your reservation.

Attachments:
attachment	reservation.ics	679 B	text/calendar	LONG_ID_HERE"""

        thread = client._parse_thread_output("19c7a7ecd1f32fcb", output)

        assert len(thread.messages) == 1
        msg = thread.messages[0]
        assert msg.attachments == ["reservation.ics"]

    def test_primary_message_property(self, client):
        output = """Thread contains 1 message(s)

=== Message 1/1: test123 ===
From: Sender <sender@example.com>
To: recipient@example.com
Subject: Test Subject
Date: Wed, 25 Feb 2026 10:00:00 +0000

Body content here."""

        thread = client._parse_thread_output("test123", output)

        assert thread.primary_message is not None
        assert thread.primary_message.subject == "Test Subject"
        assert thread.subject == "Test Subject"


class TestClientInitialization:
    def test_requires_keyring_password(self):
        # Should raise without GOG_KEYRING_PASSWORD
        with pytest.raises(ValueError, match="GOG_KEYRING_PASSWORD"):
            GogGmailClient(keyring_password=None)

    def test_accepts_explicit_password(self):
        client = GogGmailClient(keyring_password="explicit-password")
        assert client.keyring_password == "explicit-password"

    def test_uses_env_password(self, monkeypatch):
        monkeypatch.setenv("GOG_KEYRING_PASSWORD", "env-password")
        client = GogGmailClient()
        assert client.keyring_password == "env-password"
