from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
import re
import threading
from typing import Any, Optional

from contracts import ContinuityPacketBuilder, ContinuityRepository
from diagnostics import FailOpenDiagnostics
from injector import ContinuityInjector
from policy import DEFAULT_SCHEMA_VERSION
from store import ContinuityStore


class ContinuityRuntimeService:
    """Integration-ready runtime boundary for continuity injection.

    Responsibilities:
    - first-run bootstrap via repository migration (optional)
    - llm_input payload injection with fail-open behavior
    - structured diagnostics for bootstrap and runtime fallback paths
    """

    def __init__(
        self,
        repository: ContinuityRepository,
        packet_builder: ContinuityPacketBuilder,
        diagnostics: Optional[FailOpenDiagnostics] = None,
        auto_migrate: bool = True,
    ):
        self.repository = repository
        self.packet_builder = packet_builder
        self.diagnostics = diagnostics or FailOpenDiagnostics()
        self.auto_migrate = auto_migrate

        self._bootstrap_lock = threading.Lock()
        self._bootstrap_attempted = False

    @classmethod
    def from_db_path(
        cls,
        db_path: str,
        token_budget: int = 220,
        diagnostics: Optional[FailOpenDiagnostics] = None,
        auto_migrate: bool = True,
    ) -> "ContinuityRuntimeService":
        diagnostics = diagnostics or FailOpenDiagnostics()
        repository = ContinuityStore(db_path, diagnostics=diagnostics)
        packet_builder = ContinuityInjector(
            repository,
            token_budget=token_budget,
            diagnostics=diagnostics,
        )
        return cls(
            repository=repository,
            packet_builder=packet_builder,
            diagnostics=diagnostics,
            auto_migrate=auto_migrate,
        )

    def _emit(self, code: str, detail: str, context: Optional[dict[str, Any]] = None) -> None:
        self.diagnostics.emit(
            component="runtime_service",
            code=code,
            detail=detail,
            context=context or {},
        )

    def _ensure_bootstrap(self) -> None:
        if self._bootstrap_attempted or not self.auto_migrate:
            return

        with self._bootstrap_lock:
            if self._bootstrap_attempted:
                return

            self._bootstrap_attempted = True
            try:
                ok = self.repository.migrate()
                if not ok:
                    self._emit(
                        "bootstrap_migrate_error",
                        "Auto-migrate failed during first-run bootstrap.",
                    )
            except Exception as exc:
                self._emit(
                    "bootstrap_unexpected_error",
                    "Unexpected bootstrap error; continuing fail-open.",
                    {"error": str(exc)},
                )

    @staticmethod
    def _safe_nonneg_int(value: Any, default: int = 0) -> int:
        try:
            parsed = int(value)
            return parsed if parsed >= 0 else default
        except Exception:
            return default

    @staticmethod
    def _is_fingerprint(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return re.fullmatch(r"[0-9a-f]{64}", value) is not None

    def _normalize_fingerprint(self, value: Any, agent_id: str) -> str:
        if self._is_fingerprint(value):
            return str(value)
        if value not in (None, ""):
            self._emit(
                "packet_fingerprint_fallback",
                "runtime_state_fingerprint was malformed; using empty fallback.",
                {"agent_id": agent_id, "value_type": type(value).__name__},
            )
        return ""

    @staticmethod
    def _packet_default(agent_id: str) -> dict[str, Any]:
        return {
            "agent_id": str(agent_id),
            "schema_version": DEFAULT_SCHEMA_VERSION,
            "token_budget": 0,
            "estimated_tokens": 0,
            "runtime_state_fingerprint": "",
            "fields": {},
            "dropped_fields": [],
        }

    @staticmethod
    def _packet_to_mapping(packet: Any) -> dict[str, Any]:
        if is_dataclass(packet):
            return asdict(packet)
        if isinstance(packet, dict):
            return dict(packet)
        return {}

    @staticmethod
    def _is_json_safe(value: Any) -> bool:
        try:
            json.dumps(value, ensure_ascii=False, sort_keys=True)
            return True
        except Exception:
            return False

    def _normalize_packet(self, agent_id: str, packet_obj: Any) -> dict[str, Any]:
        raw = self._packet_to_mapping(packet_obj)
        if not raw:
            self._emit(
                "packet_normalize_fallback",
                "Packet builder returned non-mapping payload; using empty packet.",
                {"agent_id": agent_id, "packet_type": type(packet_obj).__name__},
            )
            return self._packet_default(agent_id)

        packet = self._packet_default(agent_id)

        packet["agent_id"] = str(raw.get("agent_id") or agent_id)

        schema_version = raw.get("schema_version")
        if isinstance(schema_version, str) and schema_version:
            packet["schema_version"] = schema_version

        token_budget = self._safe_nonneg_int(raw.get("token_budget"), default=0)
        estimated_tokens = self._safe_nonneg_int(raw.get("estimated_tokens"), default=0)

        if token_budget > 0 and estimated_tokens > token_budget:
            self._emit(
                "packet_estimate_clamped",
                "estimated_tokens exceeded token_budget; clamped to budget.",
                {
                    "agent_id": agent_id,
                    "estimated_tokens": estimated_tokens,
                    "token_budget": token_budget,
                },
            )
            estimated_tokens = token_budget

        packet["token_budget"] = token_budget
        packet["estimated_tokens"] = estimated_tokens
        packet["runtime_state_fingerprint"] = self._normalize_fingerprint(
            raw.get("runtime_state_fingerprint"),
            agent_id=agent_id,
        )

        raw_fields = raw.get("fields")
        raw_dropped = raw.get("dropped_fields")

        dropped: list[str] = []
        if isinstance(raw_dropped, list):
            dropped = [str(x) for x in raw_dropped]

        if not isinstance(raw_fields, dict):
            if raw_fields not in (None, {}):
                self._emit(
                    "packet_fields_type_fallback",
                    "Packet fields were not a dict; replaced with empty dict.",
                    {"agent_id": agent_id, "fields_type": type(raw_fields).__name__},
                )
            packet["fields"] = {}
            packet["dropped_fields"] = dropped
            return packet

        normalized_fields: dict[str, Any] = {}
        for key, value in raw_fields.items():
            field_name = str(key)
            if self._is_json_safe(value):
                normalized_fields[field_name] = value
            else:
                dropped.append(field_name)
                self._emit(
                    "packet_field_serialize_fallback",
                    "Packet field value not JSON-serializable; field dropped.",
                    {"agent_id": agent_id, "field": field_name},
                )

        packet["fields"] = normalized_fields
        packet["dropped_fields"] = sorted(set(dropped))
        return packet

    def inject_llm_input(self, agent_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            self._emit(
                "llm_input_payload_type",
                "Payload was not a dict; returning original payload fail-open.",
                {"agent_id": agent_id, "payload_type": type(payload).__name__},
            )
            return payload

        try:
            self._ensure_bootstrap()
            packet = self.packet_builder.build_packet(agent_id)
            out = dict(payload)
            out["continuity_packet"] = self._normalize_packet(agent_id, packet)
            return out
        except Exception as exc:
            self._emit(
                "llm_input_error",
                "Service-level llm_input injection failure; returning original payload.",
                {"agent_id": agent_id, "error": str(exc)},
            )
            return payload
