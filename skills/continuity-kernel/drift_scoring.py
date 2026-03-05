from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

LOW_SIGNAL_INTENT_TERMS = {
    "command",
    "commands",
    "exec",
    "file",
    "files",
    "message",
    "messages",
    "path",
    "python",
    "pytest",
    "query",
    "run",
    "runs",
    "script",
    "scripts",
    "search",
    "test",
    "tests",
    "tool",
    "tools",
    "unittest",
}

EXEC_ALIGNMENT_TERMS = {
    "alert",
    "alerts",
    "benchmark",
    "classifier",
    "coverage",
    "drift",
    "execute",
    "guardrail",
    "guardrails",
    "integration",
    "lock",
    "mission",
    "nonblocking",
    "path",
    "regression",
    "scoring",
    "suite",
    "test",
    "tests",
    "validation",
    "warning",
    "warnings",
}


@dataclass(frozen=True)
class MissionProfile:
    weights: dict[str, float]
    anchor_terms: set[str]


@dataclass(frozen=True)
class DriftSignals:
    weighted_alignment: float
    domain_coverage: float
    anchor_coverage: float
    noise_ratio: float
    overlap_terms: tuple[str, ...]


class MissionProfileBuilder:
    @staticmethod
    def keywords(text: str) -> set[str]:
        normalized = (text or "").lower().replace("_", " ")
        parts = re.findall(r"[a-zA-Z0-9]+", normalized)
        return {p for p in parts if len(p) > 2 and p not in STOPWORDS}

    @classmethod
    def _collect_terms(cls, value: Any, sink: set[str]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                sink.update(cls.keywords(str(key)))
                cls._collect_terms(child, sink)
            return
        if isinstance(value, list):
            for item in value:
                cls._collect_terms(item, sink)
            return
        if isinstance(value, (str, int, float, bool)):
            sink.update(cls.keywords(str(value)))

    @classmethod
    def constraint_terms(cls, constraints_json: str) -> set[str]:
        if not constraints_json:
            return set()
        parsed = json.loads(constraints_json)
        terms: set[str] = set()
        cls._collect_terms(parsed, terms)
        return terms

    @classmethod
    def build(cls, mission_text: str, done_text: str, constraints_json: str = "") -> MissionProfile:
        mission_terms = cls.keywords(mission_text)
        done_terms = cls.keywords(done_text)
        constraint_terms = cls.constraint_terms(constraints_json)

        weights: dict[str, float] = {}
        anchor_terms: set[str] = set()

        for term in mission_terms:
            is_anchor = term not in LOW_SIGNAL_INTENT_TERMS
            weights[term] = max(weights.get(term, 0.0), 1.65 if is_anchor else 1.25)
            if is_anchor:
                anchor_terms.add(term)

        for term in done_terms:
            weights[term] = max(weights.get(term, 0.0), 1.1)
            if term not in LOW_SIGNAL_INTENT_TERMS:
                anchor_terms.add(term)

        for term in constraint_terms:
            weights[term] = max(weights.get(term, 0.0), 1.25)
            if term not in LOW_SIGNAL_INTENT_TERMS:
                anchor_terms.add(term)

        # Shared mission + DoD terms are strongest semantic anchors.
        for term in mission_terms & done_terms:
            weights[term] = max(weights.get(term, 0.0), 1.95)
            if term not in LOW_SIGNAL_INTENT_TERMS:
                anchor_terms.add(term)

        return MissionProfile(weights=weights, anchor_terms=anchor_terms)


class MissionIntentScorer:
    @staticmethod
    def extract_intent(tool_name: str, tool_input: Any) -> str:
        if isinstance(tool_input, str):
            return f"{tool_name} {tool_input}"
        if isinstance(tool_input, dict):
            chunks = [tool_name]
            for key in ("command", "query", "url", "message", "path", "file_path"):
                val = tool_input.get(key)
                if isinstance(val, str):
                    chunks.append(val)
            return " ".join(chunks)
        return tool_name

    @staticmethod
    def intent_weight(term: str) -> float:
        return 0.35 if term in LOW_SIGNAL_INTENT_TERMS else 1.0

    @classmethod
    def score(cls, profile: MissionProfile, intent_text: str) -> tuple[float, DriftSignals]:
        intent_terms = MissionProfileBuilder.keywords(intent_text)
        if not intent_terms:
            return 0.0, DriftSignals(0.0, 0.0, 0.0, 1.0, tuple())

        mission_terms = set(profile.weights.keys())
        max_mission_weight = max(profile.weights.values(), default=1.0)

        total_mass = 0.0
        overlap_mass = 0.0
        domain_total = 0
        domain_overlap = 0
        anchor_overlap = 0
        low_signal_count = 0

        overlap_terms = intent_terms & mission_terms

        for term in intent_terms:
            weight = cls.intent_weight(term)
            total_mass += weight

            is_domain = term not in LOW_SIGNAL_INTENT_TERMS
            if is_domain:
                domain_total += 1
            else:
                low_signal_count += 1

            mission_weight = profile.weights.get(term, 0.0)
            if mission_weight > 0:
                overlap_mass += weight * (mission_weight / max_mission_weight)
                if is_domain:
                    domain_overlap += 1
                if term in profile.anchor_terms:
                    anchor_overlap += 1

        weighted_alignment = overlap_mass / max(total_mass, 1e-9)
        domain_coverage = domain_overlap / domain_total if domain_total else 0.0
        anchor_coverage = anchor_overlap / max(len(profile.anchor_terms), 1)
        noise_ratio = low_signal_count / max(len(intent_terms), 1)

        # Signal blend chosen for high precision on mission-lock tasks.
        score = (
            (0.5 * weighted_alignment)
            + (0.3 * domain_coverage)
            + (0.15 * anchor_coverage)
            + (0.05 * (1.0 - noise_ratio))
        )

        # Guardrails against adversarial partial-overlap false negatives.
        if domain_total > 0:
            if domain_overlap == 0:
                score *= 0.2
            elif domain_coverage < 0.34:
                score *= 0.5
            elif domain_coverage < 0.67:
                score *= 0.75

        if domain_total <= 4 and domain_overlap < 3:
            score *= 0.65

        if profile.anchor_terms:
            if anchor_overlap == 0:
                score *= 0.45
            elif anchor_coverage < 0.2:
                score *= 0.75

        # Precision boost for clearly engineering-oriented exec intents where
        # semantic overlap exists but lexical overlap is sparse.
        is_exec_intent = intent_text.strip().lower().startswith("exec ")
        exec_alignment_hits = len(intent_terms & EXEC_ALIGNMENT_TERMS)
        if is_exec_intent and noise_ratio <= 0.6:
            if len(overlap_terms) >= 3 and exec_alignment_hits >= 3 and domain_coverage >= 0.3:
                score += 0.28
            elif len(overlap_terms) >= 2 and exec_alignment_hits >= 2 and domain_coverage >= 0.34:
                score += 0.2

        score = min(max(score, 0.0), 1.0)

        signals = DriftSignals(
            weighted_alignment=round(weighted_alignment, 3),
            domain_coverage=round(domain_coverage, 3),
            anchor_coverage=round(anchor_coverage, 3),
            noise_ratio=round(noise_ratio, 3),
            overlap_terms=tuple(sorted(overlap_terms)),
        )
        return round(score, 3), signals
