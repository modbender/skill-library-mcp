from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sqlite3
from typing import Any, Optional

from diagnostics import FailOpenDiagnostics


SCHEMA_VERSION = "v1"
SUPPORTED_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION})


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SoulCard:
    agent_id: str
    role: str
    persona: str
    user_profile: str
    preferences: dict[str, Any]
    constraints: dict[str, Any]
    updated_at: str
    schema_version: str


@dataclass(frozen=True)
class MissionTicket:
    agent_id: str
    mission: str
    definition_of_done: str
    constraints: dict[str, Any]
    priority: int
    status: str
    updated_at: str
    schema_version: str


class ContinuityStore:
    """SQLite-backed Soul Card + Mission Ticket persistence.

    First-principles contract:
    - fail-open always (never raise in public methods)
    - explicit schema-version compatibility checks on read
    - deterministic JSON encoding for object fields
    - structured diagnostics for all fallback paths
    """

    def __init__(self, db_path: str, diagnostics: Optional[FailOpenDiagnostics] = None):
        self.db_path = db_path
        self.diagnostics = diagnostics or FailOpenDiagnostics()

    def _emit(self, code: str, detail: str, context: Optional[dict[str, Any]] = None) -> None:
        self.diagnostics.emit(
            component="store",
            code=code,
            detail=detail,
            context={"db_path": self.db_path, **(context or {})},
        )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _is_obj(value: Any) -> bool:
        return isinstance(value, dict)

    def _encode_obj(self, value: Any, code: str, context: dict[str, Any]) -> str:
        if value is None:
            value = {}
        if not self._is_obj(value):
            self._emit(
                code,
                "Non-object value provided where JSON object expected; coercing to empty object.",
                {**context, "provided_type": type(value).__name__},
            )
            value = {}

        try:
            return json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        except Exception as exc:
            self._emit(
                code,
                "JSON encode failed; coercing to empty object.",
                {**context, "error": str(exc)},
            )
            return "{}"

    def _decode_obj(
        self,
        raw: Any,
        code: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if raw in (None, ""):
            return {}
        if not isinstance(raw, str):
            self._emit(
                code,
                "JSON decode expected string payload; coercing to empty object.",
                {**context, "provided_type": type(raw).__name__},
            )
            return {}

        try:
            parsed = json.loads(raw)
        except Exception as exc:
            self._emit(
                code,
                "JSON decode failed; coercing to empty object.",
                {**context, "error": str(exc)},
            )
            return {}

        if not isinstance(parsed, dict):
            self._emit(
                code,
                "Decoded JSON was not an object; coercing to empty object.",
                {**context, "decoded_type": type(parsed).__name__},
            )
            return {}

        return parsed

    def migrate(self) -> bool:
        try:
            with self._connect() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS soul_card_v1 (
                        agent_id TEXT PRIMARY KEY,
                        role TEXT NOT NULL,
                        persona TEXT NOT NULL,
                        user_profile TEXT NOT NULL,
                        preferences_json TEXT NOT NULL DEFAULT '{}',
                        constraints_json TEXT NOT NULL DEFAULT '{}',
                        updated_at TEXT NOT NULL,
                        schema_version TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS mission_ticket_v1 (
                        agent_id TEXT PRIMARY KEY,
                        mission TEXT NOT NULL,
                        definition_of_done TEXT NOT NULL,
                        constraints_json TEXT NOT NULL DEFAULT '{}',
                        priority INTEGER NOT NULL DEFAULT 3,
                        status TEXT NOT NULL DEFAULT 'active',
                        updated_at TEXT NOT NULL,
                        schema_version TEXT NOT NULL
                    );
                    """
                )
            return True
        except Exception as exc:
            self._emit("migrate_error", "SQLite migration failed.", {"error": str(exc)})
            return False

    def upsert_soul_card(
        self,
        agent_id: str,
        role: str,
        persona: str,
        user_profile: str,
        preferences: Optional[dict[str, Any]] = None,
        constraints: Optional[dict[str, Any]] = None,
    ) -> bool:
        try:
            preferences_json = self._encode_obj(
                preferences,
                "preferences_encode_fallback",
                {"agent_id": agent_id},
            )
            constraints_json = self._encode_obj(
                constraints,
                "soul_constraints_encode_fallback",
                {"agent_id": agent_id},
            )

            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO soul_card_v1 (
                        agent_id, role, persona, user_profile,
                        preferences_json, constraints_json, updated_at, schema_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(agent_id) DO UPDATE SET
                        role = excluded.role,
                        persona = excluded.persona,
                        user_profile = excluded.user_profile,
                        preferences_json = excluded.preferences_json,
                        constraints_json = excluded.constraints_json,
                        updated_at = excluded.updated_at,
                        schema_version = excluded.schema_version;
                    """,
                    (
                        agent_id,
                        role,
                        persona,
                        user_profile,
                        preferences_json,
                        constraints_json,
                        utc_now_iso(),
                        SCHEMA_VERSION,
                    ),
                )
            return True
        except Exception as exc:
            self._emit(
                "upsert_soul_card_error",
                "Soul Card upsert failed.",
                {"agent_id": agent_id, "error": str(exc)},
            )
            return False

    def upsert_mission_ticket(
        self,
        agent_id: str,
        mission: str,
        definition_of_done: str,
        constraints: Optional[dict[str, Any]] = None,
        priority: int = 3,
        status: str = "active",
    ) -> bool:
        try:
            constraints_json = self._encode_obj(
                constraints,
                "mission_constraints_encode_fallback",
                {"agent_id": agent_id},
            )

            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO mission_ticket_v1 (
                        agent_id, mission, definition_of_done,
                        constraints_json, priority, status, updated_at, schema_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(agent_id) DO UPDATE SET
                        mission = excluded.mission,
                        definition_of_done = excluded.definition_of_done,
                        constraints_json = excluded.constraints_json,
                        priority = excluded.priority,
                        status = excluded.status,
                        updated_at = excluded.updated_at,
                        schema_version = excluded.schema_version;
                    """,
                    (
                        agent_id,
                        mission,
                        definition_of_done,
                        constraints_json,
                        priority,
                        status,
                        utc_now_iso(),
                        SCHEMA_VERSION,
                    ),
                )
            return True
        except Exception as exc:
            self._emit(
                "upsert_mission_ticket_error",
                "Mission Ticket upsert failed.",
                {"agent_id": agent_id, "error": str(exc)},
            )
            return False

    def get_soul_card(self, agent_id: str) -> Optional[SoulCard]:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM soul_card_v1 WHERE agent_id = ?",
                    (agent_id,),
                ).fetchone()
                if not row:
                    return None

                payload = dict(row)
                schema_version = payload.get("schema_version")
                if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
                    self._emit(
                        "soul_card_schema_mismatch",
                        "Incompatible Soul Card schema_version on read.",
                        {
                            "agent_id": agent_id,
                            "found_schema_version": schema_version,
                            "supported": sorted(SUPPORTED_SCHEMA_VERSIONS),
                        },
                    )
                    return None

                return SoulCard(
                    agent_id=str(payload.get("agent_id", "")),
                    role=str(payload.get("role", "")),
                    persona=str(payload.get("persona", "")),
                    user_profile=str(payload.get("user_profile", "")),
                    preferences=self._decode_obj(
                        payload.get("preferences_json"),
                        "preferences_decode_fallback",
                        {"agent_id": agent_id},
                    ),
                    constraints=self._decode_obj(
                        payload.get("constraints_json"),
                        "soul_constraints_decode_fallback",
                        {"agent_id": agent_id},
                    ),
                    updated_at=str(payload.get("updated_at", "")),
                    schema_version=str(schema_version),
                )
        except Exception as exc:
            self._emit(
                "get_soul_card_error",
                "Soul Card read failed.",
                {"agent_id": agent_id, "error": str(exc)},
            )
            return None

    def get_mission_ticket(self, agent_id: str) -> Optional[MissionTicket]:
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM mission_ticket_v1 WHERE agent_id = ?",
                    (agent_id,),
                ).fetchone()
                if not row:
                    return None

                payload = dict(row)
                schema_version = payload.get("schema_version")
                if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
                    self._emit(
                        "mission_ticket_schema_mismatch",
                        "Incompatible Mission Ticket schema_version on read.",
                        {
                            "agent_id": agent_id,
                            "found_schema_version": schema_version,
                            "supported": sorted(SUPPORTED_SCHEMA_VERSIONS),
                        },
                    )
                    return None

                return MissionTicket(
                    agent_id=str(payload.get("agent_id", "")),
                    mission=str(payload.get("mission", "")),
                    definition_of_done=str(payload.get("definition_of_done", "")),
                    constraints=self._decode_obj(
                        payload.get("constraints_json"),
                        "mission_constraints_decode_fallback",
                        {"agent_id": agent_id},
                    ),
                    priority=int(payload.get("priority", 3)),
                    status=str(payload.get("status", "active")),
                    updated_at=str(payload.get("updated_at", "")),
                    schema_version=str(schema_version),
                )
        except Exception as exc:
            self._emit(
                "get_mission_ticket_error",
                "Mission Ticket read failed.",
                {"agent_id": agent_id, "error": str(exc)},
            )
            return None
