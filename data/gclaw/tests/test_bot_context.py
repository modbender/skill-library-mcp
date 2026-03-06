"""Tests for BotContext."""

import pytest

from kaimail.bot_context import BotContext


class TestBotContextInit:
    def test_default_values(self):
        ctx = BotContext(bot_id="test")
        assert ctx.bot_id == "test"
        assert ctx.allowed_labels == []
        assert ctx.allowed_senders == []
        assert ctx.max_results == 50
        assert ctx.readonly is True

    def test_custom_values(self):
        ctx = BotContext(
            bot_id="digest",
            allowed_labels=["Thoughts", "INBOX"],
            allowed_senders=["substack.com"],
            max_results=100,
        )
        assert ctx.allowed_labels == ["Thoughts", "INBOX"]
        assert ctx.max_results == 100


class TestCanAccess:
    def test_can_access_label_in_allowlist(self):
        ctx = BotContext(bot_id="test", allowed_labels=["Thoughts"])
        assert ctx.can_access_label("Thoughts")
        assert not ctx.can_access_label("Travel")

    def test_can_access_any_label_when_no_restrictions(self):
        ctx = BotContext(bot_id="test", allowed_labels=[])
        assert ctx.can_access_label("Thoughts")
        assert ctx.can_access_label("Travel")
        assert ctx.can_access_label("Anything")

    def test_can_access_sender_in_allowlist(self):
        ctx = BotContext(bot_id="test", allowed_senders=["substack.com"])
        assert ctx.can_access_sender("substack.com")
        assert ctx.can_access_sender("author.substack.com")  # Partial match
        assert not ctx.can_access_sender("gmail.com")

    def test_can_access_any_sender_when_no_restrictions(self):
        ctx = BotContext(bot_id="test", allowed_senders=[])
        assert ctx.can_access_sender("any.domain.com")


class TestFilterLabels:
    def test_filters_to_allowed(self):
        ctx = BotContext(bot_id="test", allowed_labels=["Thoughts", "Travel"])
        filtered = ctx.filter_labels_for_query(["Thoughts", "Spam", "Travel"])
        assert filtered == ["Thoughts", "Travel"]

    def test_returns_all_when_no_restrictions(self):
        ctx = BotContext(bot_id="test", allowed_labels=[])
        filtered = ctx.filter_labels_for_query(["Any", "Label"])
        assert filtered == ["Any", "Label"]


class TestBuildQuery:
    def test_builds_simple_label_query(self):
        ctx = BotContext(bot_id="test", allowed_labels=["Thoughts"])
        query = ctx.build_query(labels=["Thoughts"])
        assert "label:Thoughts" in query

    def test_raises_for_disallowed_label(self):
        ctx = BotContext(bot_id="test", allowed_labels=["Thoughts"])
        with pytest.raises(ValueError, match="cannot access labels"):
            ctx.build_query(labels=["Travel"])

    def test_auto_adds_allowed_labels_when_none_specified(self):
        ctx = BotContext(bot_id="test", allowed_labels=["Thoughts", "INBOX"])
        query = ctx.build_query()
        assert "label:Thoughts" in query
        assert "label:INBOX" in query

    def test_adds_time_filter(self):
        ctx = BotContext(bot_id="test")
        query = ctx.build_query(newer_than_days=7)
        assert "newer_than:7d" in query

    def test_adds_unread_filter(self):
        ctx = BotContext(bot_id="test")
        query = ctx.build_query(is_unread=True)
        assert "is:unread" in query

    def test_adds_extra_query(self):
        ctx = BotContext(bot_id="test")
        query = ctx.build_query(extra_query="has:attachment")
        assert "has:attachment" in query


class TestEnforceMaxResults:
    def test_caps_to_max(self):
        ctx = BotContext(bot_id="test", max_results=25)
        assert ctx.enforce_max_results(100) == 25
        assert ctx.enforce_max_results(10) == 10

    def test_returns_requested_when_under_max(self):
        ctx = BotContext(bot_id="test", max_results=100)
        assert ctx.enforce_max_results(50) == 50
