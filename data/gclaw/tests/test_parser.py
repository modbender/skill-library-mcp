"""Tests for EmailParser."""

from datetime import datetime

import pytest

from kaimail.models import Email
from kaimail.parser import EmailParser


@pytest.fixture
def parser():
    return EmailParser()


class TestParseFromAddress:
    def test_name_and_email(self, parser):
        name, email = parser._parse_from_address("Ben Thompson <email@stratechery.com>")
        assert name == "Ben Thompson"
        assert email == "email@stratechery.com"

    def test_quoted_name(self, parser):
        name, email = parser._parse_from_address('"Adi Shmorak from Newsletter" <news@example.com>')
        assert name == "Adi Shmorak from Newsletter"
        assert email == "news@example.com"

    def test_email_only(self, parser):
        name, email = parser._parse_from_address("noreply@github.com")
        assert name == "noreply"
        assert email == "noreply@github.com"


class TestCleanSubject:
    def test_strips_fwd(self, parser):
        assert parser._clean_subject("Fwd: Budget Physics") == "Budget Physics"
        assert parser._clean_subject("FW: Budget Physics") == "Budget Physics"

    def test_strips_re(self, parser):
        assert parser._clean_subject("Re: Some Topic") == "Some Topic"
        assert parser._clean_subject("RE: Some Topic") == "Some Topic"

    def test_preserves_clean_subject(self, parser):
        assert (
            parser._clean_subject("Budget Physics in the Age of Agents")
            == "Budget Physics in the Age of Agents"
        )


class TestIsForwarded:
    def test_detects_forward(self, parser):
        assert parser._is_forwarded("Fwd: Budget Physics")
        assert parser._is_forwarded("FW: Meeting Notes")

    def test_non_forward(self, parser):
        assert not parser._is_forwarded("Budget Physics")
        assert not parser._is_forwarded("Re: Budget Physics")


class TestIsReply:
    def test_detects_reply(self, parser):
        assert parser._is_reply("Re: Budget Physics")
        assert parser._is_reply("RE: Meeting Notes")

    def test_non_reply(self, parser):
        assert not parser._is_reply("Budget Physics")
        assert not parser._is_reply("Fwd: Budget Physics")


class TestExtractDomain:
    def test_extracts_domain(self, parser):
        assert parser._extract_domain("user@substack.com") == "substack.com"
        assert parser._extract_domain("noreply@github.com") == "github.com"

    def test_empty_on_invalid(self, parser):
        assert parser._extract_domain("invalid") == ""


class TestCleanBody:
    def test_strips_unsubscribe(self, parser):
        body = "Hello world\n\nUnsubscribe from this newsletter"
        cleaned = parser._clean_body(body)
        assert "Unsubscribe" not in cleaned

    def test_strips_view_in_browser(self, parser):
        body = "View this post on the web at example.com\n\nActual content here"
        cleaned = parser._clean_body(body)
        assert "View this post" not in cleaned

    def test_collapses_newlines(self, parser):
        body = "Line 1\n\n\n\n\nLine 2"
        cleaned = parser._clean_body(body)
        assert "\n\n\n" not in cleaned


class TestParseEmail:
    def test_parses_full_email(self, parser):
        email = Email(
            id="test123",
            threadId="test123",
            date="2026-02-25 21:07",
            **{"from": "Ben Thompson <email@stratechery.com>"},
            subject="This Week in Stratechery",
            labels=["IMPORTANT", "Thoughts"],
        )

        parsed = parser.parse_email(email)

        assert parsed.id == "test123"
        assert parsed.sender_name == "Ben Thompson"
        assert parsed.sender_email == "email@stratechery.com"
        assert parsed.sender_domain == "stratechery.com"
        assert "IMPORTANT" in parsed.labels


class TestParseDate:
    def test_parses_simple_format(self, parser):
        dt = parser._parse_date("2026-02-25 21:07")
        assert dt.year == 2026
        assert dt.month == 2
        assert dt.day == 25

    def test_parses_rfc_format(self, parser):
        dt = parser._parse_date("Wed, 25 Feb 2026 19:07:28 +0000")
        assert dt.year == 2026
        assert dt.month == 2

    def test_fallback_on_invalid(self, parser):
        dt = parser._parse_date("invalid date")
        # Should return current time as fallback
        assert isinstance(dt, datetime)
