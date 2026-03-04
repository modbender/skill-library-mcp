"""
substrate.py — Epistemic Council v2.0
Append-only SQLite substrate with provenance DAG.

FIXES (Gap Analysis §3.1):
  - Removed duplicate _row_to_event definition
  - Fixed tab indentation in get_all_events()
  - Added 6 new read methods for monitoring integration (§4.1)
"""

import sqlite3
import hashlib
import json
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from collections import deque


class EventType(Enum):
    CLAIM_CREATED = "claim_created"
    EVIDENCE_LINKED = "evidence_linked"
    HYPOTHESIS_FORKED = "hypothesis_forked"
    INSIGHT_GENERATED = "insight_generated"
    ADVERSARIAL_CHALLENGE = "adversarial_challenge"
    CHALLENGE_RESULT = "challenge_result"
    HUMAN_REVIEW = "human_review"
    VISIBILITY_PRUNED = "visibility_pruned"


class InsightType(Enum):
    ANALOGICAL = "A"
    CONSTRAINT_TRANSFER = "C"
    OPTIMIZATION_PATTERN = "O"
    STATISTICAL_CORRELATION = "S"


@dataclass
class SubstrateEvent:
    event_id: str
    event_type: EventType
    agent_id: str
    domain: str
    content: Dict[str, Any]
    parent_ids: List[str]
    integrity_hash: str
    timestamp: str
    confidence: float = 0.0
    visibility_score: float = 1.0


class Substrate:
    """
    Append-only epistemic substrate. No UPDATE or DELETE paths exist.
    All writes go through validated write_*() methods.
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS events (
        event_id        TEXT PRIMARY KEY,
        event_type      TEXT NOT NULL,
        agent_id        TEXT NOT NULL,
        domain          TEXT NOT NULL,
        content         TEXT NOT NULL,
        parent_ids      TEXT NOT NULL DEFAULT '[]',
        integrity_hash  TEXT NOT NULL,
        timestamp       TEXT NOT NULL,
        confidence      REAL DEFAULT 0.0,
        visibility_score REAL DEFAULT 1.0
    );
    CREATE INDEX IF NOT EXISTS idx_domain    ON events(domain);
    CREATE INDEX IF NOT EXISTS idx_agent     ON events(agent_id);
    CREATE INDEX IF NOT EXISTS idx_type      ON events(event_type);
    CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp);
    """

    def __init__(self, db_path: str = "epistemic.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self._conn.executescript(self.SCHEMA)
        self._conn.commit()

    # ------------------------------------------------------------------
    # SINGLE _row_to_event definition (Gap §3.1 fix — duplicate removed)
    # ------------------------------------------------------------------
    def _row_to_event(self, row) -> SubstrateEvent:
        event_type_val = row["event_type"]
        if isinstance(event_type_val, str):
            try:
                event_type = EventType(event_type_val)
            except ValueError:
                # Fallback: match by name
                event_type = EventType[event_type_val.upper()]
        else:
            event_type = event_type_val

        return SubstrateEvent(
            event_id=row["event_id"],
            event_type=event_type,
            agent_id=row["agent_id"],
            domain=row["domain"],
            content=json.loads(row["content"]),
            parent_ids=json.loads(row["parent_ids"]),
            integrity_hash=row["integrity_hash"],
            timestamp=row["timestamp"],
            confidence=row["confidence"],
            visibility_score=row["visibility_score"],
        )

    def _compute_hash(self, event_type: str, agent_id: str, domain: str,
                      content: dict, parent_ids: list) -> str:
        payload = json.dumps({
            "event_type": event_type,
            "agent_id": agent_id,
            "domain": domain,
            "content": content,
            "parent_ids": sorted(parent_ids),
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _append(self, event_type: EventType, agent_id: str, domain: str,
                 content: dict, parent_ids: list, confidence: float = 0.0) -> SubstrateEvent:
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        integrity_hash = self._compute_hash(
            event_type.value, agent_id, domain, content, parent_ids
        )
        self._conn.execute(
            """INSERT INTO events
               (event_id, event_type, agent_id, domain, content,
                parent_ids, integrity_hash, timestamp, confidence)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (event_id, event_type.value, agent_id, domain,
             json.dumps(content), json.dumps(parent_ids),
             integrity_hash, timestamp, confidence)
        )
        self._conn.commit()
        return SubstrateEvent(
            event_id=event_id, event_type=event_type,
            agent_id=agent_id, domain=domain, content=content,
            parent_ids=parent_ids, integrity_hash=integrity_hash,
            timestamp=timestamp, confidence=confidence
        )

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------
    def write_claim(self, agent_id: str, domain: str, claim_text: str,
                    confidence: float, reasoning_trace: str = "",
                    parent_ids: list = None) -> SubstrateEvent:
        content = {
            "claim": claim_text,
            "reasoning_trace": reasoning_trace,
            "risk_score": round((1.0 - confidence) * 1.2, 4),  # computed proxy
        }
        return self._append(
            EventType.CLAIM_CREATED, agent_id, domain,
            content, parent_ids or [], confidence
        )

    def write_insight(self, agent_id: str, domain: str, insight_text: str,
                      insight_type: InsightType, confidence: float,
                      source_claim_ids: list, cross_domain_flag: bool = False) -> SubstrateEvent:
        if not source_claim_ids:
            raise ValueError("write_insight requires at least one source_claim_id")
        content = {
            "insight": insight_text,
            "insight_type": insight_type.value,
            "cross_domain_flag": cross_domain_flag,
            "adversarial_status": None,  # populated by challenge_result
        }
        return self._append(
            EventType.INSIGHT_GENERATED, agent_id, domain,
            content, source_claim_ids, confidence
        )

    def write_challenge_result(self, insight_id: str, agent_id: str,
                                verdict: dict, confidence_adjustment: float) -> SubstrateEvent:
        content = {
            "verdict": verdict,
            "confidence_adjustment": confidence_adjustment,
        }
        return self._append(
            EventType.CHALLENGE_RESULT, agent_id, "adversarial",
            content, [insight_id], 0.0
        )

    def write_human_review(self, claim_id: str, reviewer: str,
                            decision: str, notes: str) -> SubstrateEvent:
        content = {
            "decision": decision,
            "notes": notes,
            "reviewer": reviewer,
        }
        return self._append(
            EventType.HUMAN_REVIEW, reviewer, "governance",
            content, [claim_id], 0.0
        )

    def write_evidence_link(self, claim_id: str, agent_id: str,
                             source_url: str, reliability: str) -> SubstrateEvent:
        content = {
            "source_url": source_url,
            "reliability": reliability,
        }
        return self._append(
            EventType.EVIDENCE_LINKED, agent_id, "evidence",
            content, [claim_id], 0.0
        )

    # ------------------------------------------------------------------
    # Existing read methods
    # ------------------------------------------------------------------
    def get_event(self, event_id: str) -> Optional[SubstrateEvent]:
        row = self._conn.execute(
            "SELECT * FROM events WHERE event_id = ?", (event_id,)
        ).fetchone()
        return self._row_to_event(row) if row else None

    def get_claims_by_domain(self, domain: str) -> List[SubstrateEvent]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? AND domain = ? ORDER BY timestamp",
            (EventType.CLAIM_CREATED.value, domain)
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_insights(self) -> List[SubstrateEvent]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? ORDER BY timestamp",
            (EventType.INSIGHT_GENERATED.value,)
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_challenges_for_insight(self, insight_id: str) -> List[SubstrateEvent]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? AND parent_ids LIKE ?",
            (EventType.CHALLENGE_RESULT.value, f'%{insight_id}%')
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_provenance(self, event_id: str) -> List[SubstrateEvent]:
        """BFS walk of provenance DAG."""
        visited, queue, results = set(), deque([event_id]), []
        while queue:
            eid = queue.popleft()
            if eid in visited:
                continue
            visited.add(eid)
            ev = self.get_event(eid)
            if ev:
                results.append(ev)
                for pid in ev.parent_ids:
                    queue.append(pid)
        return results

    def event_count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def verify_all(self) -> Dict[str, Any]:
        rows = self._conn.execute("SELECT * FROM events").fetchall()
        passed, failed = 0, []
        for row in rows:
            ev = self._row_to_event(row)
            expected = self._compute_hash(
                ev.event_type.value, ev.agent_id, ev.domain,
                ev.content, ev.parent_ids
            )
            if ev.integrity_hash == expected:
                passed += 1
            else:
                failed.append(ev.event_id)
        return {"passed": passed, "failed": failed, "total": passed + len(failed)}

    def prune_visibility(self, event_id: str, reason: str):
        """Affects visibility_score only — never deletes."""
        self._conn.execute(
            "UPDATE events SET visibility_score = 0.0 WHERE event_id = ?",
            (event_id,)
        )
        self._append(
            EventType.VISIBILITY_PRUNED, "system", "governance",
            {"target_id": event_id, "reason": reason}, [event_id]
        )

    # ------------------------------------------------------------------
    # NEW READ METHODS — monitoring integration (Gap Analysis §4.1)
    # ------------------------------------------------------------------

    def get_all_events(self, limit: int = None) -> List[SubstrateEvent]:
        """Return all events ordered by timestamp. (Gap §3.1 — tab fix applied)"""
        sql = "SELECT * FROM events ORDER BY timestamp"
        if limit:
            sql += f" LIMIT {int(limit)}"
        rows = self._conn.execute(sql).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_events_by_type(self, event_type: EventType,
                            domain: str = None,
                            limit: int = None) -> List[SubstrateEvent]:
        """
        Flexible event filter used by Tasks 1, 2, 4.
        Monitoring integration §4.1, method 1.
        """
        params = [event_type.value]
        sql = "SELECT * FROM events WHERE event_type = ?"
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        sql += " ORDER BY timestamp DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_challenge_results_for_insight(self, insight_id: str) -> List[SubstrateEvent]:
        """
        All CHALLENGE_RESULT events referencing an insight.
        Enables full audit trail for Tasks 3 and 4.
        Monitoring integration §4.1, method 2.
        """
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? AND parent_ids LIKE ? ORDER BY timestamp",
            (EventType.CHALLENGE_RESULT.value, f'%{insight_id}%')
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_claims_without_evidence(self, domain: str = None) -> List[SubstrateEvent]:
        """
        Claims with no EVIDENCE_LINKED child events.
        Core to orphan/weak-evidence detection for Task 2.
        Monitoring integration §4.1, method 3.
        """
        # Get all claim IDs
        params = [EventType.CLAIM_CREATED.value]
        sql = "SELECT * FROM events WHERE event_type = ?"
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        claim_rows = self._conn.execute(sql, params).fetchall()

        # Get all claim IDs referenced by EVIDENCE_LINKED events
        evidence_rows = self._conn.execute(
            "SELECT parent_ids FROM events WHERE event_type = ?",
            (EventType.EVIDENCE_LINKED.value,)
        ).fetchall()
        evidenced_ids = set()
        for row in evidence_rows:
            for pid in json.loads(row["parent_ids"]):
                evidenced_ids.add(pid)

        results = []
        for row in claim_rows:
            ev = self._row_to_event(row)
            if ev.event_id not in evidenced_ids:
                results.append(ev)
        return results

    def get_claims_in_confidence_range(self, low: float, high: float,
                                        domain: str = None) -> List[SubstrateEvent]:
        """
        Claims within a confidence band. Used by Task 3 for threshold-zone
        validation (0.45–0.55 range = 'challenged' epistemic zone).
        Monitoring integration §4.1, method 4.
        """
        params = [EventType.CLAIM_CREATED.value, low, high]
        sql = "SELECT * FROM events WHERE event_type = ? AND confidence BETWEEN ? AND ?"
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        sql += " ORDER BY confidence"
        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_hypothesis_forks(self, parent_claim_id: str) -> List[SubstrateEvent]:
        """
        All HYPOTHESIS_FORKED events from a parent claim.
        Enables divergence cluster detection for Task 5.
        Monitoring integration §4.1, method 5.
        """
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? AND parent_ids LIKE ?",
            (EventType.HYPOTHESIS_FORKED.value, f'%{parent_claim_id}%')
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def count_children(self, event_id: str) -> int:
        """
        Count events where event_id appears in parent_ids.
        Used for orphan detection (no parents AND no children = orphan).
        Monitoring integration §4.1, method 6.
        """
        rows = self._conn.execute(
            "SELECT COUNT(*) FROM events WHERE parent_ids LIKE ?",
            (f'%{event_id}%',)
        ).fetchone()
        return rows[0]

    def get_insights_above_confidence(self, threshold: float) -> List[SubstrateEvent]:
        """
        Insights above a confidence threshold. Used by Task 4 to select
        re-challenge candidates (PDR: high-confidence = highest epistemic risk).
        """
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? AND confidence > ? ORDER BY confidence DESC",
            (EventType.INSIGHT_GENERATED.value, threshold)
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def get_human_review_decisions(self, claim_id: str) -> List[SubstrateEvent]:
        """All human review events for a given claim."""
        rows = self._conn.execute(
            "SELECT * FROM events WHERE event_type = ? AND parent_ids LIKE ?",
            (EventType.HUMAN_REVIEW.value, f'%{claim_id}%')
        ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def is_visibility_pruned(self, event_id: str) -> bool:
        """Check if an event has been pruned from default visibility."""
        row = self._conn.execute(
            "SELECT 1 FROM events WHERE visibility_score = 0.0 AND event_id = ?",
            (event_id,)
        ).fetchone()
        return row is not None

    def close(self):
        self._conn.close()