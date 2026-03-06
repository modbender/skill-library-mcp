#!/usr/bin/env python3
"""Realtime pre-scan guard for inbound user messages."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .settings import definitions_dir, load_config
except ImportError:
    from settings import definitions_dir, load_config


@dataclass
class ScanResult:
    """Structured result for realtime pre-scan checks."""

    blocked: bool
    threats: List[Dict[str, Any]]
    score: int
    suggested_response: str


class RealtimeGuard:
    """Low-latency scanner using only high/critical severity signatures."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config = load_config(config_path)
        self._patterns = self._load_high_severity_patterns()

    def _load_high_severity_patterns(self) -> List[Dict[str, Any]]:
        """Load and compile high/critical patterns from local definitions."""
        defs_dir = definitions_dir(self.config)
        patterns: List[Dict[str, Any]] = []

        for file_path in defs_dir.glob("*.json"):
            if file_path.name == "manifest.json":
                continue
            try:
                payload = json.loads(file_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            signatures = payload.get("signatures", payload.get("checks", []))
            if not isinstance(signatures, list):
                continue

            for sig in signatures:
                if str(sig.get("severity", "")).lower() not in {"high", "critical"}:
                    continue

                candidates: List[str] = []
                pattern = sig.get("pattern")
                if isinstance(pattern, str) and pattern:
                    candidates.append(pattern)

                detection = sig.get("detection")
                if isinstance(detection, dict):
                    detection_patterns = detection.get("patterns", [])
                    if isinstance(detection_patterns, list):
                        for candidate in detection_patterns:
                            if isinstance(candidate, str) and candidate:
                                candidates.append(candidate)

                for candidate in candidates:
                    flags = 0
                    flag_str = str(sig.get("flags", ""))
                    if "i" in flag_str:
                        flags |= re.IGNORECASE
                    if "s" in flag_str:
                        flags |= re.DOTALL
                    try:
                        regex = re.compile(candidate, flags)
                    except re.error:
                        continue
                    patterns.append(
                        {
                            "regex": regex,
                            "id": str(sig.get("id", "UNKNOWN")),
                            "severity": str(sig.get("severity", "high")),
                            "category": str(sig.get("category", payload.get("category", "unknown"))),
                            "description": str(sig.get("description", "")),
                            "score": int(sig.get("score", 80)),
                        }
                    )

        return patterns

    def scan_message(self, text: str, channel: str = "unknown") -> ScanResult:
        """Fast scan (~1-5ms) against high-severity signatures only."""
        if len(text.strip()) < 3:
            return ScanResult(blocked=False, threats=[], score=0, suggested_response="")

        hits: List[Dict[str, Any]] = []
        for pat in self._patterns:
            match = pat["regex"].search(text)
            if not match:
                continue
            hits.append(
                {
                    "id": pat["id"],
                    "severity": pat["severity"],
                    "category": pat["category"],
                    "description": pat["description"],
                    "score": pat["score"],
                    "evidence": match.group(0)[:80],
                    "channel": channel,
                }
            )

        if not hits:
            return ScanResult(blocked=False, threats=[], score=0, suggested_response="")

        top_score = max(hit["score"] for hit in hits)
        blocked = self.should_block(ScanResult(False, hits, top_score, ""))
        suggestion = self.format_block_response(ScanResult(blocked, hits, top_score, ""))
        return ScanResult(blocked=blocked, threats=hits, score=top_score, suggested_response=suggestion)

    def should_block(self, result: ScanResult) -> bool:
        """Return True when a realtime scan result should be blocked."""
        if result.score >= 90:
            return True
        return any(str(threat.get("severity", "")).lower() == "critical" for threat in result.threats)

    def format_block_response(self, result: ScanResult) -> str:
        """Return a user-facing safety response for blocked content."""
        if not result.blocked:
            return ""
        top = max(result.threats, key=lambda threat: int(threat.get("score", 0))) if result.threats else {}
        threat_id = top.get("id", "unknown")
        return (
            "Guardian blocked this message due to potential security risk "
            f"({threat_id}). Please rephrase without instruction overrides, "
            "credential requests, or unsafe tool directions."
        )
