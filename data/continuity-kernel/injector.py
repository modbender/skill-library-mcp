from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Optional

from contracts import ContinuityRepository
from diagnostics import FailOpenDiagnostics
from policy import (
    COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL,
    COMPACTION_POLICY_SIZE_ONLY,
    DEFAULT_FIELD_ORDER,
    DEFAULT_SCHEMA_VERSION,
    DEFAULT_TOKEN_BUDGET,
    MAX_TOKEN_BUDGET,
    MIN_TOKEN_BUDGET,
    SELECTOR_MODE_DETERMINISTIC,
    SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL,
    InjectionPolicy,
    clamp_token_budget,
    normalize_compaction_policy,
    normalize_selector_mode,
)


@dataclass(frozen=True)
class InjectedPacket:
    agent_id: str
    schema_version: str
    token_budget: int
    estimated_tokens: int
    runtime_state_fingerprint: str
    fields: dict[str, Any]
    dropped_fields: list[str]


class ContinuityInjector:
    """Build llm_input continuity packets under a hard token budget.

    Contract:
    - deterministic field ordering by default
    - optional dual-route selector (experimental) behind explicit policy flag
    - strict bounded token budget
    - deterministic runtime_state_fingerprint for restart-invariant state checks
    - fail-open empty packet on unexpected errors
    - diagnostics emitted on fallback and budget normalization
    """

    def __init__(
        self,
        store: ContinuityRepository,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        diagnostics: Optional[FailOpenDiagnostics] = None,
        policy: Optional[InjectionPolicy] = None,
    ):
        self.store = store
        self.diagnostics = diagnostics or getattr(store, "diagnostics", None) or FailOpenDiagnostics()

        default_budget, default_reason = clamp_token_budget(token_budget)
        if default_reason == "invalid_type":
            self._emit(
                "token_budget_invalid_type",
                "Token budget could not be coerced to int; using default.",
                {"provided": repr(token_budget), "default": DEFAULT_TOKEN_BUDGET},
            )
        elif default_reason == "clamped_low":
            self._emit(
                "token_budget_clamped_low",
                "Token budget below minimum; clamped.",
                {"provided": token_budget, "effective": default_budget},
            )
        elif default_reason == "clamped_high":
            self._emit(
                "token_budget_clamped_high",
                "Token budget above maximum; clamped.",
                {"provided": token_budget, "effective": default_budget},
            )

        base_policy = policy or InjectionPolicy(token_budget=default_budget)

        effective_budget, policy_budget_reason = clamp_token_budget(base_policy.token_budget)
        if policy_budget_reason == "invalid_type":
            self._emit(
                "policy_token_budget_invalid_type",
                "Policy token_budget invalid; falling back to default token budget.",
                {"provided": repr(base_policy.token_budget), "default": DEFAULT_TOKEN_BUDGET},
            )
        elif policy_budget_reason == "clamped_low":
            self._emit(
                "policy_token_budget_clamped_low",
                "Policy token_budget below minimum; clamped.",
                {"provided": base_policy.token_budget, "effective": effective_budget},
            )
        elif policy_budget_reason == "clamped_high":
            self._emit(
                "policy_token_budget_clamped_high",
                "Policy token_budget above maximum; clamped.",
                {"provided": base_policy.token_budget, "effective": effective_budget},
            )

        selector_mode, selector_reason = normalize_selector_mode(base_policy.selector_mode)
        if selector_reason == "invalid_type":
            self._emit(
                "selector_mode_invalid_type",
                "selector_mode must be a non-empty string; fallback to deterministic mode.",
                {"provided": repr(base_policy.selector_mode), "effective": SELECTOR_MODE_DETERMINISTIC},
            )
        elif selector_reason == "unsupported":
            self._emit(
                "selector_mode_unsupported",
                "Unsupported selector_mode; fallback to deterministic mode.",
                {"provided": base_policy.selector_mode, "effective": SELECTOR_MODE_DETERMINISTIC},
            )

        compaction_policy, compaction_reason = normalize_compaction_policy(base_policy.compaction_policy)
        if compaction_reason == "invalid_type":
            self._emit(
                "compaction_policy_invalid_type",
                "compaction_policy must be a non-empty string; fallback to size_only.",
                {"provided": repr(base_policy.compaction_policy), "effective": COMPACTION_POLICY_SIZE_ONLY},
            )
        elif compaction_reason == "unsupported":
            self._emit(
                "compaction_policy_unsupported",
                "Unsupported compaction_policy; fallback to size_only.",
                {"provided": base_policy.compaction_policy, "effective": COMPACTION_POLICY_SIZE_ONLY},
            )

        self.policy = InjectionPolicy(
            schema_version=base_policy.schema_version,
            token_budget=effective_budget,
            field_order=base_policy.field_order,
            selector_mode=selector_mode,
            compaction_policy=compaction_policy,
        )
        self.token_budget = self.policy.token_budget
        self.selector_mode = self.policy.selector_mode
        self.compaction_policy = self.policy.compaction_policy
        self.field_order = self._normalize_field_order(self.policy.field_order)

    def _emit(self, code: str, detail: str, context: Optional[dict[str, Any]] = None) -> None:
        self.diagnostics.emit(
            component="injector",
            code=code,
            detail=detail,
            context=context or {},
        )

    def _normalize_field_order(self, field_order: Any) -> tuple[str, ...]:
        if not isinstance(field_order, (list, tuple)):
            self._emit(
                "field_order_fallback",
                "Policy field_order had invalid type; using default order.",
                {"field_order_type": type(field_order).__name__},
            )
            return DEFAULT_FIELD_ORDER

        normalized: list[str] = []
        seen: set[str] = set()
        for item in field_order:
            if not isinstance(item, str) or not item:
                self._emit(
                    "field_order_item_ignored",
                    "Non-string/empty field_order entry ignored.",
                    {"item": repr(item)},
                )
                continue
            if item in seen:
                continue
            seen.add(item)
            normalized.append(item)

        if not normalized:
            self._emit(
                "field_order_empty_fallback",
                "Normalized field_order was empty; using default order.",
            )
            return DEFAULT_FIELD_ORDER

        return tuple(normalized)

    @staticmethod
    def _estimate_tokens(value: Any) -> int:
        if value is None:
            return 0
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
        # conservative heuristic: max(word-estimate, char-estimate)
        words = [w for w in text.replace("\n", " ").split(" ") if w]
        by_words = int(len(words) * 1.3)
        by_chars = int(len(text) / 4)
        return max(1, by_words, by_chars)

    @staticmethod
    def _keywords(value: Any) -> set[str]:
        if isinstance(value, str):
            text = value
        else:
            try:
                text = json.dumps(value, ensure_ascii=False, sort_keys=True)
            except Exception:
                text = str(value)

        parts = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return {p for p in parts if len(p) > 2}

    @staticmethod
    def _safe_dict(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    def _runtime_state_fingerprint(self, agent_id: str, soul: Any, mission: Any) -> str:
        payload = {
            "agent_id": str(agent_id),
            "role": str(getattr(soul, "role", "")) if soul else "",
            "soul_constraints": self._safe_dict(getattr(soul, "constraints", {})) if soul else {},
            "mission": str(getattr(mission, "mission", "")) if mission else "",
            "definition_of_done": str(getattr(mission, "definition_of_done", "")) if mission else "",
            "mission_constraints": self._safe_dict(getattr(mission, "constraints", {})) if mission else {},
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _safe_field_value(self, field: str, value: Any) -> Any | None:
        if isinstance(value, str):
            return value

        try:
            json.dumps(value, ensure_ascii=False, sort_keys=True)
            return value
        except Exception as exc:
            self._emit(
                "field_value_unserializable",
                "Field value not JSON-serializable; dropping field fail-open.",
                {"field": field, "error": str(exc)},
            )
            return None

    def _safe_field_cost(self, field: str, value: Any) -> int | None:
        try:
            return self._estimate_tokens(value)
        except Exception as exc:
            self._emit(
                "token_estimate_error",
                "Token estimation failed for field; dropping field fail-open.",
                {"field": field, "error": str(exc)},
            )
            return None

    @staticmethod
    def _packet_empty(
        agent_id: str,
        schema_version: str,
        token_budget: int,
        runtime_state_fingerprint: str = "",
    ) -> InjectedPacket:
        return InjectedPacket(
            agent_id=agent_id,
            schema_version=schema_version,
            token_budget=token_budget,
            estimated_tokens=0,
            runtime_state_fingerprint=runtime_state_fingerprint,
            fields={},
            dropped_fields=[],
        )

    def _prepare_candidates(self, pool: dict[str, Any]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        for idx, field in enumerate(self.field_order):
            value = pool.get(field)
            if value in (None, "", {}, []):
                continue

            safe_value = self._safe_field_value(field, value)
            if safe_value is None:
                candidates.append(
                    {
                        "idx": idx,
                        "field": field,
                        "value": value,
                        "safe_value": None,
                        "cost": None,
                        "drop_reason": "unserializable",
                    }
                )
                continue

            cost = self._safe_field_cost(field, safe_value)
            if cost is None:
                candidates.append(
                    {
                        "idx": idx,
                        "field": field,
                        "value": safe_value,
                        "safe_value": safe_value,
                        "cost": None,
                        "drop_reason": "cost_error",
                    }
                )
                continue

            candidates.append(
                {
                    "idx": idx,
                    "field": field,
                    "value": safe_value,
                    "safe_value": safe_value,
                    "cost": cost,
                    "drop_reason": None,
                }
            )

        return candidates

    @staticmethod
    def _attention_priority_weight(field: str) -> float:
        weights = {
            "mission": 1.0,
            "definition_of_done": 0.95,
            "mission_constraints": 0.9,
            "role": 0.82,
            "soul_constraints": 0.78,
            "persona": 0.74,
            "user_profile": 0.68,
            "preferences": 0.55,
        }
        return weights.get(field, 0.5)

    def _deterministic_candidate_order(
        self,
        candidates: list[dict[str, Any]],
        mission_terms: set[str],
        constraint_terms: set[str],
    ) -> list[dict[str, Any]]:
        ordered = sorted(candidates, key=lambda c: int(c["idx"]))
        if self.compaction_policy != COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL:
            return ordered

        scored: list[dict[str, Any]] = []
        field_count = max(len(self.field_order), 1)
        for candidate in ordered:
            field = str(candidate.get("field", ""))
            local_relevance, global_coverage, priority_bonus = self._dual_route_score(
                candidate,
                mission_terms=mission_terms,
                constraint_terms=constraint_terms,
                field_count=field_count,
            )
            attention_score = (
                0.5 * self._attention_priority_weight(field)
                + 0.3 * local_relevance
                + 0.2 * global_coverage
            )
            scored.append(
                {
                    **candidate,
                    "attention_score": round(attention_score, 6),
                    "priority_bonus": round(priority_bonus, 6),
                }
            )

        scored.sort(
            key=lambda c: (
                -float(c.get("attention_score", 0.0)),
                int(c.get("idx", 0)),
                str(c.get("field", "")),
            )
        )
        return scored

    def _select_deterministic(
        self,
        candidates: list[dict[str, Any]],
        mission_terms: set[str],
        constraint_terms: set[str],
    ) -> tuple[dict[str, Any], list[str], int]:
        selected: dict[str, Any] = {}
        dropped: list[str] = []
        running = 0

        ordered = self._deterministic_candidate_order(
            candidates,
            mission_terms=mission_terms,
            constraint_terms=constraint_terms,
        )

        for candidate in ordered:
            field = str(candidate["field"])
            cost = candidate.get("cost")
            safe_value = candidate.get("safe_value")

            if safe_value is None or cost is None:
                dropped.append(field)
                continue

            if running + int(cost) <= self.token_budget:
                selected[field] = safe_value
                running += int(cost)
            else:
                dropped.append(field)

        return selected, dropped, running

    def _dual_route_score(
        self,
        candidate: dict[str, Any],
        mission_terms: set[str],
        constraint_terms: set[str],
        field_count: int,
    ) -> tuple[float, float, float]:
        value_terms = self._keywords(candidate.get("safe_value"))

        if mission_terms:
            local_overlap = len(value_terms & mission_terms)
            local_relevance = local_overlap / max(len(mission_terms), 1)
        else:
            local_relevance = 0.0

        if constraint_terms:
            constraint_overlap = len(value_terms & constraint_terms)
            global_coverage = constraint_overlap / max(len(constraint_terms), 1)
        else:
            global_coverage = 1.0 if "constraints" in str(candidate.get("field", "")) else 0.0

        idx = int(candidate.get("idx", 0))
        priority_bonus = (field_count - idx) / max(field_count, 1)

        return local_relevance, global_coverage, priority_bonus

    def _select_dual_route(
        self,
        candidates: list[dict[str, Any]],
        mission_terms: set[str],
        constraint_terms: set[str],
    ) -> tuple[dict[str, Any], list[str], int]:
        scored: list[dict[str, Any]] = []
        field_count = max(len(self.field_order), 1)

        for candidate in candidates:
            local_relevance, global_coverage, priority_bonus = self._dual_route_score(
                candidate,
                mission_terms=mission_terms,
                constraint_terms=constraint_terms,
                field_count=field_count,
            )
            score = (0.6 * local_relevance) + (0.3 * global_coverage) + (0.1 * priority_bonus)
            scored.append(
                {
                    **candidate,
                    "dual_route_score": round(score, 6),
                    "local_relevance": round(local_relevance, 6),
                    "global_coverage": round(global_coverage, 6),
                    "priority_bonus": round(priority_bonus, 6),
                }
            )

        scored.sort(
            key=lambda c: (
                -float(c.get("dual_route_score", 0.0)),
                int(c.get("idx", 0)),
                str(c.get("field", "")),
            )
        )

        selected: dict[str, Any] = {}
        dropped: list[str] = []
        running = 0

        for candidate in scored:
            field = str(candidate["field"])
            cost = candidate.get("cost")
            safe_value = candidate.get("safe_value")

            if safe_value is None or cost is None:
                dropped.append(field)
                continue

            if running + int(cost) <= self.token_budget:
                selected[field] = safe_value
                running += int(cost)
            else:
                dropped.append(field)

        return selected, dropped, running

    def _select_fields(
        self,
        candidates: list[dict[str, Any]],
        mission_terms: set[str],
        constraint_terms: set[str],
    ) -> tuple[dict[str, Any], list[str], int, str]:
        mode = self.selector_mode

        if mode == SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL:
            try:
                selected, dropped, running = self._select_dual_route(
                    candidates,
                    mission_terms=mission_terms,
                    constraint_terms=constraint_terms,
                )
                return selected, dropped, running, mode
            except Exception as exc:
                self._emit(
                    "selector_mode_fallback",
                    "Dual-route selector failed; fallback to deterministic field order.",
                    {"error": str(exc), "from_mode": mode, "to_mode": SELECTOR_MODE_DETERMINISTIC},
                )
                mode = SELECTOR_MODE_DETERMINISTIC

        selected, dropped, running = self._select_deterministic(
            candidates,
            mission_terms=mission_terms,
            constraint_terms=constraint_terms,
        )
        return selected, dropped, running, mode

    def build_packet(self, agent_id: str) -> InjectedPacket:
        try:
            soul = self.store.get_soul_card(agent_id)
            mission = self.store.get_mission_ticket(agent_id)

            runtime_state_fingerprint = self._runtime_state_fingerprint(agent_id, soul=soul, mission=mission)

            if not soul and not mission:
                return self._packet_empty(
                    agent_id,
                    schema_version=self.policy.schema_version,
                    token_budget=self.token_budget,
                    runtime_state_fingerprint=runtime_state_fingerprint,
                )

            mission_constraints = self._safe_dict(getattr(mission, "constraints", {})) if mission else {}
            soul_constraints = self._safe_dict(getattr(soul, "constraints", {})) if soul else {}

            pool = {
                "mission": mission.mission if mission else None,
                "definition_of_done": mission.definition_of_done if mission else None,
                "role": soul.role if soul else None,
                "persona": soul.persona if soul else None,
                "mission_constraints": mission_constraints,
                "user_profile": soul.user_profile if soul else None,
                "soul_constraints": soul_constraints,
                "preferences": soul.preferences if soul else {},
            }

            mission_terms = self._keywords(
                {
                    "mission": mission.mission if mission else "",
                    "definition_of_done": mission.definition_of_done if mission else "",
                    "role": soul.role if soul else "",
                    "persona": soul.persona if soul else "",
                }
            )
            constraint_terms = self._keywords(
                {
                    "mission_constraints": mission_constraints,
                    "soul_constraints": soul_constraints,
                }
            )

            candidates = self._prepare_candidates(pool)
            selected, dropped, running, selected_mode = self._select_fields(
                candidates,
                mission_terms=mission_terms,
                constraint_terms=constraint_terms,
            )

            self._emit(
                "selector_mode_used",
                "Selector mode applied for continuity packet field selection.",
                {
                    "agent_id": agent_id,
                    "selector_mode": selected_mode,
                    "compaction_policy": self.compaction_policy,
                },
            )

            return InjectedPacket(
                agent_id=agent_id,
                schema_version=self.policy.schema_version,
                token_budget=self.token_budget,
                estimated_tokens=running,
                runtime_state_fingerprint=runtime_state_fingerprint,
                fields=selected,
                dropped_fields=dropped,
            )
        except Exception as exc:
            self._emit(
                "build_packet_error",
                "Failed to build continuity packet; returning empty packet.",
                {"agent_id": agent_id, "error": str(exc)},
            )
            return self._packet_empty(
                agent_id,
                schema_version=DEFAULT_SCHEMA_VERSION,
                token_budget=self.token_budget,
                runtime_state_fingerprint="",
            )

    @staticmethod
    def as_json(packet: InjectedPacket) -> str:
        return json.dumps(asdict(packet), ensure_ascii=False, indent=2, sort_keys=True)
