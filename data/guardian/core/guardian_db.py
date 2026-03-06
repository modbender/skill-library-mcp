#!/usr/bin/env python3
"""Guardian SQLite persistence layer for threats, metrics, bookmarks, and grants."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .settings import default_db_path, skill_root
except ImportError:
    from settings import default_db_path, skill_root


class GuardianDB:
    """SQLite-backed data access object for Guardian runtime state."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        preferred = Path(db_path).expanduser().resolve() if db_path else default_db_path()
        candidates = [preferred, (skill_root() / "guardian.db").resolve(), Path("/tmp/guardian.db").resolve()]

        last_error: Optional[Exception] = None
        self.db_path = preferred
        for candidate in candidates:
            try:
                candidate.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(candidate, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                self.db_path = candidate
                self.conn = conn
                break
            except (OSError, sqlite3.OperationalError) as exc:
                last_error = exc
        else:
            raise sqlite3.OperationalError(f"Unable to initialize Guardian DB: {last_error}")

        self._migrate()

    def _migrate(self) -> None:
        """Create required tables and indexes if missing."""
        c = self.conn
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS scan_bookmarks (
                file_path TEXT PRIMARY KEY,
                last_offset INTEGER DEFAULT 0,
                last_mtime REAL DEFAULT 0,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detected_at TEXT NOT NULL,
                sig_id TEXT,
                category TEXT,
                severity TEXT,
                score INTEGER,
                evidence TEXT,
                description TEXT,
                blocked INTEGER DEFAULT 0,
                channel TEXT,
                source_file TEXT,
                message_hash TEXT UNIQUE,
                dismissed INTEGER DEFAULT 0,
                context TEXT
            );
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                period_start TEXT NOT NULL,
                messages_scanned INTEGER DEFAULT 0,
                files_scanned INTEGER DEFAULT 0,
                clean INTEGER DEFAULT 0,
                at_risk INTEGER DEFAULT 0,
                blocked INTEGER DEFAULT 0,
                categories TEXT,
                health_score INTEGER,
                UNIQUE(period, period_start)
            );
            CREATE TABLE IF NOT EXISTS cache_grants (
                id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                channel TEXT,
                scope TEXT,
                granted_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                granted_by TEXT,
                revoked INTEGER DEFAULT 0,
                revoked_at TEXT
            );
            CREATE TABLE IF NOT EXISTS pending_confirms (
                id TEXT PRIMARY KEY,
                action TEXT NOT NULL,
                details TEXT,
                channel TEXT,
                requested_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                resolved_at TEXT,
                pin TEXT
            );
            CREATE TABLE IF NOT EXISTS config_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audited_at TEXT NOT NULL,
                score INTEGER,
                warning_count INTEGER,
                passed_count INTEGER,
                warnings TEXT,
                passed TEXT
            );
            CREATE TABLE IF NOT EXISTS allowlist (
                id INTEGER PRIMARY KEY,
                signature_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                scope_value TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                reason TEXT,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS blocklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                channel TEXT,
                blocked_at TEXT NOT NULL,
                blocked_by TEXT,
                reason TEXT,
                active INTEGER DEFAULT 1,
                UNIQUE(source, channel)
            );
            CREATE TABLE IF NOT EXISTS false_positive_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_id INTEGER NOT NULL,
                reported_at TEXT NOT NULL,
                reported_by TEXT,
                comment TEXT,
                sig_id TEXT,
                evidence TEXT,
                FOREIGN KEY(threat_id) REFERENCES threats(id)
            );
            CREATE INDEX IF NOT EXISTS idx_threats_detected ON threats(detected_at);
            CREATE INDEX IF NOT EXISTS idx_threats_category ON threats(category);
            CREATE INDEX IF NOT EXISTS idx_metrics_period ON metrics(period, period_start);
            CREATE INDEX IF NOT EXISTS idx_allowlist_sig ON allowlist(signature_id, active);
            CREATE INDEX IF NOT EXISTS idx_blocklist_source ON blocklist(source, active);
            CREATE TABLE IF NOT EXISTS override_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_at TEXT NOT NULL,
                threat_id INTEGER,
                action TEXT NOT NULL,
                scope TEXT,
                actor TEXT,
                reason TEXT,
                expires_at TEXT,
                channel TEXT,
                source TEXT,
                sig_id TEXT,
                evidence TEXT
            );
            CREATE TABLE IF NOT EXISTS approval_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                threat_id INTEGER,
                token TEXT NOT NULL UNIQUE,
                channel TEXT,
                source TEXT,
                sig_id TEXT,
                severity TEXT,
                evidence TEXT,
                decided_at TEXT,
                decided_by TEXT,
                decision_reason TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_fp_reports_threat ON false_positive_reports(threat_id);
            CREATE INDEX IF NOT EXISTS idx_override_events_time ON override_events(event_at DESC);
            CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
            """
        )

        # Backfill new columns on existing installs
        self._ensure_column("threats", "context", "TEXT")
        self._ensure_column("threats", "context_before", "TEXT")
        self._ensure_column("threats", "context_after", "TEXT")
        self._ensure_column("threats", "context_match", "TEXT")
        self._ensure_column("threats", "escalated", "INTEGER DEFAULT 0")
        self._ensure_column("threats", "escalated_at", "TEXT")
        # BL-039: approved_override audit trail
        self._ensure_column("threats", "approved_override", "INTEGER DEFAULT 0")
        self._ensure_column("threats", "approved_by", "TEXT")
        self._ensure_column("threats", "approved_at", "TEXT")
        c.commit()

    def _now(self) -> str:
        """Return current UTC timestamp in ISO-8601 format."""
        return datetime.now(timezone.utc).isoformat()

    def _ensure_column(self, table: str, column: str, coltype: str) -> None:
        """Add a column to a table if it does not already exist."""
        cols = [row[1] for row in self.conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in cols:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

    def get_bookmark(self, file_path: str) -> Tuple[int, float]:
        """Return last scanned offset and mtime for a file bookmark."""
        row = self.conn.execute(
            "SELECT last_offset, last_mtime FROM scan_bookmarks WHERE file_path=?",
            (file_path,),
        ).fetchone()
        return (row["last_offset"], row["last_mtime"]) if row else (0, 0.0)

    def set_bookmark(self, file_path: str, offset: int, mtime: float) -> None:
        """Set or update bookmark for incremental scanning."""
        self.conn.execute(
            "INSERT OR REPLACE INTO scan_bookmarks (file_path, last_offset, last_mtime, updated_at) VALUES (?,?,?,?)",
            (file_path, offset, mtime, self._now()),
        )
        self.conn.commit()

    def add_threat(
        self,
        sig_id: str,
        category: str,
        severity: str,
        score: int,
        evidence: str,
        description: str,
        blocked: bool,
        channel: str,
        source_file: str,
        message_hash: str,
        context: Optional[str] = None,
        detected_at: Optional[str] = None,
        context_before: Optional[str] = None,
        context_after: Optional[str] = None,
        context_match: Optional[str] = None,
    ) -> Optional[int]:
        """Insert a detected threat row, deduplicated by message hash."""
        try:
            cur = self.conn.execute(
                "INSERT INTO threats (detected_at, sig_id, category, severity, score, evidence, description, blocked, channel, source_file, message_hash, context, context_before, context_after, context_match) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    detected_at or self._now(),
                    sig_id,
                    category,
                    severity,
                    score,
                    evidence,
                    description,
                    1 if blocked else 0,
                    channel,
                    source_file,
                    message_hash,
                    context,
                    context_before,
                    context_after,
                    context_match,
                ),
            )
            self.conn.commit()
            return int(cur.lastrowid)
        except sqlite3.IntegrityError:
            return None

    def get_threats(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent non-dismissed threats, ordered by time (most recent first)."""
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = self.conn.execute(
            "SELECT * FROM threats WHERE detected_at >= ? AND dismissed=0 ORDER BY detected_at DESC LIMIT ?",
            (cutoff, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_threat_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Return aggregate category counts for recent threats."""
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = self.conn.execute(
            "SELECT category, COUNT(*) as cnt, SUM(blocked) as blk FROM threats WHERE detected_at >= ? AND dismissed=0 GROUP BY category",
            (cutoff,),
        ).fetchall()
        total = sum(r["cnt"] for r in rows)
        blocked = sum(r["blk"] for r in rows)
        cats = {r["category"]: r["cnt"] for r in rows}
        return {
            "total": total,
            "blocked": blocked,
            "injections": cats.get("prompt_injection", 0),
            "exfiltration": cats.get("data_exfiltration", 0),
            "toolAbuse": cats.get("tool_abuse", 0),
            "socialEng": cats.get("social_engineering", 0),
            "categories": cats,
        }

    def dismiss_threat(self, threat_id: int) -> None:
        """Mark a threat as dismissed."""
        self.conn.execute("UPDATE threats SET dismissed=1 WHERE id=?", (threat_id,))
        self.conn.commit()

    def escalate_threat(self, threat_id: int) -> None:
        """Mark a threat as escalated for review."""
        self.conn.execute(
            "UPDATE threats SET escalated=1, escalated_at=? WHERE id=?",
            (self._now(), threat_id)
        )
        self.conn.commit()

    def approve_override_threat(
        self,
        threat_id: int,
        approved_by: str = "user",
        reason: str = "user-approved",
    ) -> None:
        """Mark a blocked threat as an approved override with full audit trail (BL-039)."""
        self.conn.execute(
            "UPDATE threats SET approved_override=1, approved_by=?, approved_at=? WHERE id=?",
            (approved_by, self._now(), threat_id),
        )
        self.conn.commit()

    def get_approved_overrides(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return threats that were blocked but approved as overrides (BL-039)."""
        rows = self.conn.execute(
            "SELECT * FROM threats WHERE approved_override=1 ORDER BY approved_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def add_blocklist_entry(
        self,
        source: str,
        channel: Optional[str] = None,
        blocked_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> int:
        """Add a source to the blocklist. Returns entry ID."""
        try:
            cur = self.conn.execute(
                "INSERT INTO blocklist (source, channel, blocked_at, blocked_by, reason) VALUES (?,?,?,?,?)",
                (source, channel, self._now(), blocked_by, reason)
            )
            self.conn.commit()
            return int(cur.lastrowid)
        except sqlite3.IntegrityError:
            # Already blocked
            row = self.conn.execute(
                "SELECT id FROM blocklist WHERE source=? AND channel" + ("=?" if channel else " IS NULL"),
                (source, channel) if channel else (source,)
            ).fetchone()
            return int(row["id"]) if row else 0

    def is_blocked(self, source: str, channel: Optional[str] = None) -> bool:
        """Check if a source is blocked."""
        if channel:
            row = self.conn.execute(
                "SELECT id FROM blocklist WHERE source=? AND (channel=? OR channel IS NULL) AND active=1 LIMIT 1",
                (source, channel)
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT id FROM blocklist WHERE source=? AND active=1 LIMIT 1",
                (source,)
            ).fetchone()
        return row is not None

    def get_blocklist(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Return all blocklist entries."""
        query = "SELECT * FROM blocklist WHERE active=1 ORDER BY blocked_at DESC" if active_only else "SELECT * FROM blocklist ORDER BY blocked_at DESC"
        rows = self.conn.execute(query).fetchall()
        return [dict(r) for r in rows]

    def remove_blocklist_entry(self, entry_id: int) -> None:
        """Deactivate a blocklist entry."""
        self.conn.execute("UPDATE blocklist SET active=0 WHERE id=?", (entry_id,))
        self.conn.commit()

    def report_false_positive(
        self,
        threat_id: int,
        reported_by: Optional[str] = None,
        comment: Optional[str] = None
    ) -> int:
        """Log a false positive report. Returns report ID."""
        # Get threat details for the report
        row = self.conn.execute(
            "SELECT sig_id, evidence FROM threats WHERE id=?",
            (threat_id,)
        ).fetchone()
        sig_id = row["sig_id"] if row else None
        evidence = row["evidence"] if row else None
        
        cur = self.conn.execute(
            "INSERT INTO false_positive_reports (threat_id, reported_at, reported_by, comment, sig_id, evidence) VALUES (?,?,?,?,?,?)",
            (threat_id, self._now(), reported_by, comment, sig_id, evidence)
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_false_positive_reports(self, days: int = 30) -> List[Dict[str, Any]]:
        """Return recent false positive reports."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            "SELECT * FROM false_positive_reports WHERE reported_at >= ? ORDER BY reported_at DESC",
            (cutoff,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_similar_threats(self, threat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Find threats similar to the given threat (same sig_id or category)."""
        # Get the reference threat
        ref = self.conn.execute(
            "SELECT sig_id, category, channel FROM threats WHERE id=?",
            (threat_id,)
        ).fetchone()
        if not ref:
            return []
        
        # Find similar threats (same sig or category, excluding the reference)
        rows = self.conn.execute(
            """SELECT * FROM threats 
               WHERE id != ? 
               AND dismissed=0 
               AND (sig_id=? OR category=?)
               ORDER BY detected_at DESC 
               LIMIT ?""",
            (threat_id, ref["sig_id"], ref["category"], limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def record_scan(
        self,
        messages_scanned: int,
        files_scanned: int,
        clean: int,
        at_risk: int,
        blocked: int,
        categories: Dict[str, int],
        health_score: int,
    ) -> None:
        """Record hourly and daily scan metrics in an upsert-friendly format."""
        now = datetime.now(timezone.utc)
        hourly_start = now.replace(minute=0, second=0, microsecond=0).isoformat()
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        cats_json = json.dumps(categories) if categories else "{}"

        for period, pstart in [("hourly", hourly_start), ("daily", daily_start)]:
            self.conn.execute(
                """
                INSERT INTO metrics (period, period_start, messages_scanned, files_scanned, clean, at_risk, blocked, categories, health_score)
                VALUES (?,?,?,?,?,?,?,?,?)
                ON CONFLICT(period, period_start) DO UPDATE SET
                    messages_scanned = messages_scanned + excluded.messages_scanned,
                    files_scanned = excluded.files_scanned,
                    clean = clean + excluded.clean,
                    at_risk = at_risk + excluded.at_risk,
                    blocked = blocked + excluded.blocked,
                    categories = excluded.categories,
                    health_score = excluded.health_score
                """,
                (period, pstart, messages_scanned, files_scanned, clean, at_risk, blocked, cats_json, health_score),
            )
        self.conn.commit()

    def get_metrics(self, period: str = "daily", days: int = 7) -> List[Dict[str, Any]]:
        """Fetch historical metrics for a period over trailing days."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            "SELECT * FROM metrics WHERE period=? AND period_start >= ? ORDER BY period_start",
            (period, cutoff),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_current_totals(self) -> Dict[str, Any]:
        """Return totals aggregated from hourly metrics."""
        row = self.conn.execute(
            "SELECT SUM(messages_scanned) as total_scanned, SUM(at_risk) as total_threats, SUM(blocked) as total_blocked, MIN(period_start) as first_scan FROM metrics WHERE period='hourly'"
        ).fetchone()
        if row and row["total_scanned"]:
            return {
                "totalScanned": row["total_scanned"],
                "totalThreats": row["total_threats"] or 0,
                "totalBlocked": row["total_blocked"] or 0,
                "firstScan": row["first_scan"],
            }
        return {"totalScanned": 0, "totalThreats": 0, "totalBlocked": 0, "firstScan": None}

    def add_grant(
        self,
        action: str,
        channel: str,
        scope: str,
        expires_at: str,
        granted_by: Optional[str] = None,
    ) -> str:
        """Create an approval grant and return grant ID."""
        gid = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO cache_grants (id, action, channel, scope, granted_at, expires_at, granted_by) VALUES (?,?,?,?,?,?,?)",
            (gid, action, channel, scope, self._now(), expires_at, granted_by),
        )
        self.conn.commit()
        return gid

    def check_grant(self, action: str, channel: str) -> bool:
        """Return True when a non-revoked and non-expired grant exists."""
        now = self._now()
        row = self.conn.execute(
            "SELECT id FROM cache_grants WHERE action=? AND channel=? AND revoked=0 AND expires_at > ? LIMIT 1",
            (action, channel, now),
        ).fetchone()
        return row is not None

    def list_active_grants(self) -> List[Dict[str, Any]]:
        """Return all active grants sorted by newest first."""
        now = self._now()
        rows = self.conn.execute(
            "SELECT * FROM cache_grants WHERE revoked=0 AND expires_at > ? ORDER BY granted_at DESC",
            (now,),
        ).fetchall()
        return [dict(r) for r in rows]

    def revoke_grant(self, grant_id: str) -> None:
        """Revoke a specific grant by ID."""
        self.conn.execute("UPDATE cache_grants SET revoked=1, revoked_at=? WHERE id=?", (self._now(), grant_id))
        self.conn.commit()

    def revoke_all_grants(self) -> None:
        """Revoke all active grants."""
        self.conn.execute("UPDATE cache_grants SET revoked=1, revoked_at=? WHERE revoked=0", (self._now(),))
        self.conn.commit()

    def add_pending(self, action: str, details: Any, channel: str, pin: str, expires_at: str) -> str:
        """Insert a pending confirmation request and return pending ID."""
        pid = str(uuid.uuid4())
        details_json = json.dumps(details) if isinstance(details, dict) else str(details)
        self.conn.execute(
            "INSERT INTO pending_confirms (id, action, details, channel, requested_at, expires_at, pin) VALUES (?,?,?,?,?,?,?)",
            (pid, action, details_json, channel, self._now(), expires_at, pin),
        )
        self.conn.commit()
        return pid

    def get_pending(self) -> List[Dict[str, Any]]:
        """Return active pending confirmations."""
        now = self._now()
        rows = self.conn.execute(
            "SELECT * FROM pending_confirms WHERE status='pending' AND expires_at > ? ORDER BY requested_at DESC",
            (now,),
        ).fetchall()
        return [dict(r) for r in rows]

    def resolve_pending(self, pending_id: str, status: str) -> None:
        """Resolve a pending confirmation with a final status."""
        self.conn.execute(
            "UPDATE pending_confirms SET status=?, resolved_at=? WHERE id=?",
            (status, self._now(), pending_id),
        )
        self.conn.commit()

    def approve_all_pending(self) -> None:
        """Approve all currently pending and unexpired confirmations."""
        now = self._now()
        self.conn.execute(
            "UPDATE pending_confirms SET status='approved', resolved_at=? WHERE status='pending' AND expires_at > ?",
            (now, now),
        )
        self.conn.commit()

    # ── Allowlist ────────────────────────────────────────────────────────────

    def add_allowlist_rule(
        self,
        signature_id: str,
        scope: str,
        scope_value: Optional[str] = None,
        created_by: str = "user",
        reason: str = "",
    ) -> int:
        """Insert an allowlist rule and return its row ID."""
        cur = self.conn.execute(
            "INSERT INTO allowlist (signature_id, scope, scope_value, created_at, created_by, reason, active) VALUES (?,?,?,?,?,?,1)",
            (signature_id, scope, scope_value or "", self._now(), created_by, reason or ""),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_allowlist_rules(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Return allowlist rules, optionally filtering to active-only."""
        query = "SELECT * FROM allowlist"
        if active_only:
            query += " WHERE active=1"
        query += " ORDER BY created_at DESC"
        rows = self.conn.execute(query).fetchall()
        return [dict(r) for r in rows]

    def remove_allowlist_rule(self, rule_id: int) -> None:
        """Deactivate (soft-delete) an allowlist rule."""
        self.conn.execute("UPDATE allowlist SET active=0 WHERE id=?", (rule_id,))
        self.conn.commit()

    def is_allowlisted(self, signature_id: str, source_channel: str, message_text: str) -> bool:
        """Return True if this signature+channel+text combination is covered by an active allowlist rule."""
        try:
            rules = self.conn.execute(
                "SELECT scope, scope_value FROM allowlist WHERE signature_id=? AND active=1",
                (signature_id,),
            ).fetchall()
        except Exception:
            return False
        for row in rules:
            scope = row["scope"]
            scope_value = row["scope_value"] or ""
            if scope == "all":
                return True
            # scope='channel' with scope_value=channel_name  OR  legacy scope='channel:name'
            if (scope == "channel" and source_channel == scope_value) or \
               (scope.startswith("channel:") and source_channel == scope_value):
                return True
            if scope == "exact" and scope_value and scope_value in message_text:
                return True
        return False

    def log_override_event(
        self,
        threat_id: Optional[int],
        action: str,
        scope: str,
        actor: str = "dashboard",
        reason: str = "",
        expires_at: Optional[str] = None,
        channel: Optional[str] = None,
        source: Optional[str] = None,
        sig_id: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> int:
        """Record an explicit allow/deny override event for audit and dashboard visibility."""
        cur = self.conn.execute(
            """
            INSERT INTO override_events (event_at, threat_id, action, scope, actor, reason, expires_at, channel, source, sig_id, evidence)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                self._now(),
                threat_id,
                action,
                scope,
                actor,
                reason,
                expires_at,
                channel,
                source,
                sig_id,
                evidence,
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def get_override_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent override events for dashboard/audit."""
        rows = self.conn.execute(
            "SELECT * FROM override_events ORDER BY event_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def create_approval_request(
        self,
        threat_id: Optional[int],
        token: str,
        channel: Optional[str],
        source: Optional[str],
        sig_id: Optional[str],
        severity: Optional[str],
        evidence: Optional[str],
    ) -> int:
        """Create pending approval request for primary-channel review."""
        cur = self.conn.execute(
            """
            INSERT INTO approval_requests (created_at, status, threat_id, token, channel, source, sig_id, severity, evidence)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (self._now(), "pending", threat_id, token, channel, source, sig_id, severity, evidence),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def list_approval_requests(self, status: str = "pending", limit: int = 50) -> List[Dict[str, Any]]:
        """Return approval requests, defaulting to pending only."""
        rows = self.conn.execute(
            "SELECT * FROM approval_requests WHERE status=? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_approval_request_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM approval_requests WHERE token=?", (token,)).fetchone()
        return dict(row) if row else None

    def decide_approval_request(self, token: str, decision: str, decided_by: str, reason: str = "") -> None:
        self.conn.execute(
            """
            UPDATE approval_requests
               SET status=?, decided_at=?, decided_by=?, decision_reason=?
             WHERE token=?
            """,
            (decision, self._now(), decided_by, reason, token),
        )
        self.conn.commit()

    def close(self) -> None:
        """Close underlying SQLite connection."""
        self.conn.close()
