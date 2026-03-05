"""War/Den Audit Log Tests -- hash chain integrity and tamper detection."""

import json
import sqlite3

import pytest

from warden_governance.action_bridge import Action, ActionType, Decision
from warden_governance.audit_log import LocalAuditLog


def _action(
    action_type: ActionType = ActionType.API_CALL,
    agent_id: str = "test-bot",
) -> Action:
    return Action(
        type=action_type,
        data={},
        context={},
        agent_id=agent_id,
    )


class TestAuditLogWrite:
    def test_write_returns_event_id(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        event_id = log.write(_action(), Decision.ALLOW, "ok")
        assert event_id
        assert isinstance(event_id, str)

    def test_write_creates_event_in_db(self, tmp_path):
        db_path = str(tmp_path / "audit.db")
        log = LocalAuditLog(db_path)
        event_id = log.write(_action(), Decision.ALLOW, "ok")

        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT * FROM audit_log WHERE id = ?", (event_id,)
            ).fetchone()
        assert row is not None

    def test_count_increments(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        assert log.count() == 0
        log.write(_action(), Decision.ALLOW, "ok")
        assert log.count() == 1
        log.write(_action(), Decision.DENY, "blocked")
        assert log.count() == 2


class TestHashChainIntegrity:
    def test_empty_chain_is_valid(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        valid, bad_id = log.verify_chain()
        assert valid is True
        assert bad_id is None

    def test_single_event_chain_is_valid(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        log.write(_action(), Decision.ALLOW, "ok")
        valid, bad_id = log.verify_chain()
        assert valid is True
        assert bad_id is None

    def test_multiple_events_chain_is_valid(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        for i in range(10):
            log.write(
                _action(agent_id=f"bot-{i}"),
                Decision.ALLOW if i % 2 == 0 else Decision.DENY,
                f"event-{i}",
            )
        valid, bad_id = log.verify_chain()
        assert valid is True
        assert bad_id is None

    def test_tampered_hash_detected(self, tmp_path):
        db_path = str(tmp_path / "audit.db")
        log = LocalAuditLog(db_path)

        log.write(_action(), Decision.ALLOW, "first")
        event_id = log.write(_action(), Decision.DENY, "second")
        log.write(_action(), Decision.ALLOW, "third")

        # Tamper with the second event's hash
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE audit_log SET hash = 'tampered' WHERE id = ?",
                (event_id,),
            )
            conn.commit()

        valid, bad_id = log.verify_chain()
        assert valid is False
        assert bad_id == event_id

    def test_tampered_prev_hash_detected(self, tmp_path):
        db_path = str(tmp_path / "audit.db")
        log = LocalAuditLog(db_path)

        log.write(_action(), Decision.ALLOW, "first")
        log.write(_action(), Decision.DENY, "second")
        event_id = log.write(_action(), Decision.ALLOW, "third")

        # Tamper with the third event's prev_hash
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "UPDATE audit_log SET prev_hash = 'tampered' WHERE id = ?",
                (event_id,),
            )
            conn.commit()

        valid, bad_id = log.verify_chain()
        assert valid is False
        assert bad_id == event_id

    def test_100_events_chain_integrity(self, tmp_path):
        """Large chain: 100 events must all be valid."""
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        for i in range(100):
            log.write(
                _action(agent_id=f"bot-{i % 5}"),
                Decision.ALLOW,
                f"event-{i}",
            )
        valid, bad_id = log.verify_chain()
        assert valid is True


class TestAuditLogExport:
    def test_export_json(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        log.write(_action(), Decision.ALLOW, "first")
        log.write(_action(), Decision.DENY, "second")

        export = json.loads(log.export("json"))
        assert len(export) == 2
        assert export[0]["decision"] == "allow"
        assert export[1]["decision"] == "deny"

    def test_export_invalid_format_raises(self, tmp_path):
        log = LocalAuditLog(str(tmp_path / "audit.db"))
        with pytest.raises(ValueError, match="Unsupported"):
            log.export("xml")
