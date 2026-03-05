from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any


RUNTIME_CONTRACT_VERSION = "v1"


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        parsed = int(value)
        return parsed if parsed >= 0 else 0
    except Exception:
        return fallback


def _safe_float(
    value: Any,
    fallback: float = 0.0,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    def _coerce(candidate: Any) -> float | None:
        try:
            parsed = float(candidate)
        except Exception:
            return None
        if not math.isfinite(parsed):
            return None
        return parsed

    parsed = _coerce(value)
    if parsed is None:
        parsed = _coerce(fallback)
    if parsed is None:
        parsed = 0.0

    if minimum is not None and parsed < minimum:
        parsed = minimum
    if maximum is not None and parsed > maximum:
        parsed = maximum

    return parsed


def _safe_fingerprint(value: Any) -> str:
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value):
        return value
    return ""


def canonicalize_continuity_packet(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, dict):
        packet = {}

    raw_dropped = packet.get("dropped_fields", [])
    if isinstance(raw_dropped, list):
        dropped = sorted(str(x) for x in raw_dropped)
    else:
        dropped = []

    fields = packet.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}

    token_budget = _safe_int(packet.get("token_budget"), fallback=0)
    estimated_tokens = _safe_int(packet.get("estimated_tokens"), fallback=0)
    estimated_tokens = min(estimated_tokens, token_budget) if token_budget > 0 else estimated_tokens

    return {
        "contract_version": RUNTIME_CONTRACT_VERSION,
        "agent_id": str(packet.get("agent_id", "")),
        "schema_version": str(packet.get("schema_version", "v1")),
        "token_budget": token_budget,
        "estimated_tokens": estimated_tokens,
        "runtime_state_fingerprint": _safe_fingerprint(packet.get("runtime_state_fingerprint", "")),
        "fields": fields,
        "dropped_fields": dropped,
    }


def canonicalize_drift_warning(warning: Any) -> dict[str, Any]:
    if isinstance(warning, dict):
        payload = warning
    else:
        payload = {}
        for key in (
            "warn",
            "non_blocking",
            "reason",
            "score",
            "severity",
            "signals",
            "evidence",
        ):
            if hasattr(warning, key):
                payload[key] = getattr(warning, key)

    signals = payload.get("signals", {})
    if not isinstance(signals, dict):
        signals = {}

    overlap = signals.get("overlap_terms", [])
    if not isinstance(overlap, (list, tuple)):
        overlap = []

    normalized_signals = {
        "weighted_alignment": _safe_float(
            signals.get("weighted_alignment", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
        "domain_coverage": _safe_float(
            signals.get("domain_coverage", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
        "anchor_coverage": _safe_float(
            signals.get("anchor_coverage", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
        "noise_ratio": _safe_float(
            signals.get("noise_ratio", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
        "overlap_terms": sorted(str(x) for x in overlap),
    }

    evidence = payload.get("evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}

    evidence_overlap = evidence.get("matched_terms", [])
    if not isinstance(evidence_overlap, (list, tuple)):
        evidence_overlap = []

    normalized_evidence = {
        "algorithm": str(evidence.get("algorithm", "")),
        "legacy_algorithm": str(evidence.get("legacy_algorithm", "")),
        "legacy_score": _safe_float(
            evidence.get("legacy_score", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
        "matched_terms": sorted(str(x) for x in evidence_overlap),
        "warn_threshold": _safe_float(
            evidence.get("warn_threshold", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
    }

    return {
        "contract_version": RUNTIME_CONTRACT_VERSION,
        "warn": bool(payload.get("warn", False)),
        "non_blocking": bool(payload.get("non_blocking", True)),
        "reason": str(payload.get("reason", "")),
        "score": _safe_float(
            payload.get("score", 0.0),
            fallback=0.0,
            minimum=0.0,
            maximum=1.0,
        ),
        "severity": str(payload.get("severity", "none")),
        "signals": normalized_signals,
        "evidence": normalized_evidence,
    }


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(payload: Any) -> str:
    encoded = canonical_json(payload).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def continuity_packet_digest(packet: Any) -> str:
    return digest(canonicalize_continuity_packet(packet))


def drift_warning_digest(warning: Any) -> str:
    return digest(canonicalize_drift_warning(warning))
