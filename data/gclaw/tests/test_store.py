"""Tests for EmailStore."""

import tempfile
from datetime import datetime, timedelta

import pytest

from kaimail.models import EmailCategory, ParsedEmail
from kaimail.store import EmailStore


@pytest.fixture
def temp_store():
    """Create a store in a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = EmailStore(base_path=tmpdir)
        yield store


def make_email(
    id: str = "test123",
    category: EmailCategory = EmailCategory.NEWSLETTER,
    date: datetime | None = None,
) -> ParsedEmail:
    """Helper to create test emails."""
    return ParsedEmail(
        id=id,
        thread_id=id,
        date=date or datetime.now(),
        sender_email="test@example.com",
        sender_name="Test",
        sender_domain="example.com",
        subject="Test Subject",
        subject_clean="Test Subject",
        body_text="Body content",
        body_preview="Body content",
        labels=[],
        category=category,
    )


class TestSeenTracking:
    def test_mark_seen(self, temp_store):
        assert not temp_store.is_seen("msg123")
        temp_store.mark_seen("msg123")
        assert temp_store.is_seen("msg123")

    def test_mark_seen_batch(self, temp_store):
        ids = ["msg1", "msg2", "msg3"]
        temp_store.mark_seen_batch(ids)

        for id in ids:
            assert temp_store.is_seen(id)

    def test_seen_persists(self, temp_store):
        temp_store.mark_seen("persistent")

        # Create new store instance pointing to same path
        new_store = EmailStore(base_path=str(temp_store.base_path))
        assert new_store.is_seen("persistent")


class TestSaveAndLoad:
    def test_save_single(self, temp_store):
        email = make_email(id="email1")
        temp_store.save(email)

        assert temp_store.is_seen("email1")
        assert temp_store.count() == 1

    def test_save_batch(self, temp_store):
        emails = [make_email(id=f"email{i}") for i in range(5)]
        temp_store.save_batch(emails)

        assert temp_store.count() == 5
        assert temp_store.seen_count() == 5

    def test_load_all(self, temp_store):
        emails = [make_email(id=f"email{i}") for i in range(3)]
        temp_store.save_batch(emails)

        loaded = temp_store.load_all()
        assert len(loaded) == 3
        ids = {e.id for e in loaded}
        assert ids == {"email0", "email1", "email2"}

    def test_load_recent(self, temp_store):
        now = datetime.now()
        emails = [
            make_email(id="old", date=now - timedelta(days=10)),
            make_email(id="new", date=now),
            make_email(id="middle", date=now - timedelta(days=5)),
        ]
        temp_store.save_batch(emails)

        recent = temp_store.load_recent(limit=2)
        assert len(recent) == 2
        # Should be sorted by date descending
        assert recent[0].id == "new"
        assert recent[1].id == "middle"


class TestFiltering:
    def test_load_by_category(self, temp_store):
        emails = [
            make_email(id="news1", category=EmailCategory.NEWSLETTER),
            make_email(id="promo1", category=EmailCategory.PROMOTIONAL),
            make_email(id="news2", category=EmailCategory.NEWSLETTER),
        ]
        temp_store.save_batch(emails)

        newsletters = temp_store.load_by_category("newsletter")
        assert len(newsletters) == 2
        assert all(e.category == "newsletter" for e in newsletters)

    def test_load_by_sender(self, temp_store):
        email1 = make_email(id="sub1")
        email1 = email1.model_copy(update={"sender_domain": "substack.com"})
        email2 = make_email(id="other")
        email2 = email2.model_copy(update={"sender_domain": "other.com"})

        temp_store.save_batch([email1, email2])

        substack = temp_store.load_by_sender("substack.com")
        assert len(substack) == 1
        assert substack[0].id == "sub1"

    def test_load_since(self, temp_store):
        now = datetime.now()
        cutoff = now - timedelta(days=3)

        emails = [
            make_email(id="old", date=now - timedelta(days=10)),
            make_email(id="recent1", date=now - timedelta(days=1)),
            make_email(id="recent2", date=now),
        ]
        temp_store.save_batch(emails)

        recent = temp_store.load_since(cutoff)
        assert len(recent) == 2
        ids = {e.id for e in recent}
        assert ids == {"recent1", "recent2"}


class TestGetById:
    def test_finds_email(self, temp_store):
        emails = [make_email(id=f"email{i}") for i in range(3)]
        temp_store.save_batch(emails)

        found = temp_store.get_by_id("email1")
        assert found is not None
        assert found.id == "email1"

    def test_returns_none_for_missing(self, temp_store):
        assert temp_store.get_by_id("nonexistent") is None


class TestClear:
    def test_clears_all(self, temp_store):
        emails = [make_email(id=f"email{i}") for i in range(3)]
        temp_store.save_batch(emails)

        assert temp_store.count() == 3
        assert temp_store.seen_count() == 3

        temp_store.clear()

        assert temp_store.count() == 0
        assert temp_store.seen_count() == 0


class TestExportForBot:
    def test_exports_essential_fields(self, temp_store):
        email = make_email(id="test1", category=EmailCategory.NEWSLETTER)
        temp_store.save(email)

        exported = temp_store.export_for_bot()
        assert len(exported) == 1

        item = exported[0]
        assert item["id"] == "test1"
        assert item["category"] == "newsletter"
        assert "sender" in item
        assert "subject" in item
        assert "preview" in item

    def test_filters_by_category(self, temp_store):
        emails = [
            make_email(id="news", category=EmailCategory.NEWSLETTER),
            make_email(id="promo", category=EmailCategory.PROMOTIONAL),
        ]
        temp_store.save_batch(emails)

        exported = temp_store.export_for_bot(category="newsletter")
        assert len(exported) == 1
        assert exported[0]["id"] == "news"


class TestSyncSeen:
    def test_syncs_from_stored(self, temp_store):
        # Manually append to JSONL without marking seen
        email = make_email(id="orphan")
        with open(temp_store.emails_file, "a") as f:
            f.write(email.model_dump_json() + "\n")

        assert not temp_store.is_seen("orphan")

        count = temp_store.sync_seen_from_stored()
        assert count == 1
        assert temp_store.is_seen("orphan")
