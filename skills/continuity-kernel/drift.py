from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from typing import Any

from diagnostics import FailOpenDiagnostics
from drift_scoring import MissionIntentScorer, MissionProfileBuilder
from store import ContinuityStore


@dataclass
class DriftWarning:
    warn: bool
    non_blocking: bool
    reason: str
    score: float
    severity: str  # none|low|medium|high
    signals: dict[str, Any]
    evidence: dict[str, Any]


class BeforeToolCallDriftClassifier:
    """Mission-lock drift detector for before_tool_call.

    Fail-open + non-blocking by contract: classification never raises and
    never blocks execution, it only emits warnings.
    """

    def __init__(
        self,
        store: ContinuityStore,
        warn_threshold: float = 0.35,
        diagnostics: FailOpenDiagnostics | None = None,
    ):
        self.store = store
        self.warn_threshold = warn_threshold
        self.diagnostics = diagnostics or FailOpenDiagnostics()

    @staticmethod
    def _severity(score: float, warn: bool) -> str:
        if not warn:
            return "none"
        if score < 0.08:
            return "high"
        if score < 0.2:
            return "medium"
        return "low"

    @staticmethod
    def _legacy_keywords(text: str) -> set[str]:
        normalized = (text or "").lower().replace("_", " ")
        parts = re.findall(r"[a-zA-Z0-9]+", normalized)
        return {p for p in parts if len(p) > 2}

    @classmethod
    def _legacy_score(cls, mission_text: str, intent_text: str) -> float:
        mission_kw = cls._legacy_keywords(mission_text)
        intent_kw = cls._legacy_keywords(intent_text)
        if not intent_kw:
            return 0.0
        overlap = len(mission_kw & intent_kw)
        return round(overlap / max(min(len(intent_kw), len(mission_kw)), 1), 3)

    @staticmethod
    def _extract_intent(tool_name: str, tool_input: Any) -> str:
        return MissionIntentScorer.extract_intent(tool_name, tool_input)

    def diagnostics_snapshot(self) -> dict[str, Any]:
        return self.diagnostics.snapshot()

    def classify(self, agent_id: str, tool_name: str, tool_input: Any = None) -> DriftWarning:
        try:
            mission = self.store.get_mission_ticket(agent_id)
            if not mission:
                self.diagnostics.emit(
                    "drift_classifier",
                    "no_mission_ticket",
                    detail="No mission ticket available.",
                    context={"agent_id": agent_id},
                )
                return DriftWarning(
                    False,
                    True,
                    "No mission ticket; skip drift warning.",
                    0.0,
                    "none",
                    {},
                    {
                        "algorithm": "signal_blend_v1",
                        "legacy_algorithm": "legacy_overlap_min_v1",
                        "legacy_score": 0.0,
                        "matched_terms": [],
                        "warn_threshold": self.warn_threshold,
                    },
                )

            intent = self._extract_intent(tool_name, tool_input)

            constraints_json = ""
            raw_constraints_json = getattr(mission, "constraints_json", "")
            if isinstance(raw_constraints_json, str) and raw_constraints_json:
                constraints_json = raw_constraints_json
            else:
                raw_constraints = getattr(mission, "constraints", {})
                if isinstance(raw_constraints, dict):
                    try:
                        constraints_json = json.dumps(raw_constraints, ensure_ascii=False, sort_keys=True)
                    except Exception:
                        constraints_json = json.dumps({})

            try:
                profile = MissionProfileBuilder.build(
                    mission_text=mission.mission,
                    done_text=mission.definition_of_done,
                    constraints_json=constraints_json,
                )
            except Exception as exc:
                # Parse/profile failures are non-blocking; emit diagnostic then
                # continue with mission+DoD-only profile.
                self.diagnostics.emit(
                    "drift_classifier",
                    "profile_build_fallback",
                    detail=f"{type(exc).__name__}: {exc}",
                    context={"agent_id": agent_id},
                )
                profile = MissionProfileBuilder.build(
                    mission_text=mission.mission,
                    done_text=mission.definition_of_done,
                    constraints_json=json.dumps({}),
                )

            score, signals_obj = MissionIntentScorer.score(profile, intent)
            warn = score < self.warn_threshold
            severity = self._severity(score, warn)
            signals = asdict(signals_obj)

            mission_text = f"{mission.mission} {mission.definition_of_done}"
            legacy_score = self._legacy_score(mission_text, intent)
            evidence = {
                "algorithm": "signal_blend_v1",
                "legacy_algorithm": "legacy_overlap_min_v1",
                "legacy_score": legacy_score,
                "matched_terms": signals.get("overlap_terms", []),
                "warn_threshold": self.warn_threshold,
                "signals": signals,
            }

            if warn:
                self.diagnostics.emit(
                    "drift_classifier",
                    "warning_emitted",
                    detail=f"severity={severity}, score={score:.3f}",
                    context={
                        "agent_id": agent_id,
                        "tool_name": tool_name,
                        "signals": signals,
                        "legacy_score": legacy_score,
                    },
                )

            reason = (
                f"Potential mission drift before tool call (severity={severity})."
                if warn
                else "Tool call aligned with mission lock."
            )
            return DriftWarning(warn, True, reason, score, severity, signals, evidence)
        except Exception as exc:
            self.diagnostics.emit(
                "drift_classifier",
                "fail_open_exception",
                detail=f"{type(exc).__name__}: {exc}",
                context={"agent_id": agent_id, "tool_name": tool_name},
            )
            return DriftWarning(
                False,
                True,
                "Fail-open on drift classifier error.",
                0.0,
                "none",
                {},
                {
                    "algorithm": "signal_blend_v1",
                    "legacy_algorithm": "legacy_overlap_min_v1",
                    "legacy_score": 0.0,
                    "matched_terms": [],
                    "warn_threshold": self.warn_threshold,
                },
            )
