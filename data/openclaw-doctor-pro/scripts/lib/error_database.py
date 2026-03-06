"""Error pattern matching engine for OpenClaw diagnostics."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .utils import DATA_DIR, load_json


@dataclass
class ErrorPattern:
    """Structured error pattern with diagnostic metadata."""
    id: str
    category: str
    code: str
    pattern: str
    severity: str
    title: str
    description: str
    causes: list[str]
    fix_steps: list[str]
    fix_recipe_id: str
    related_codes: list[str]
    doc_url: str


class ErrorDatabase:
    """Multi-layer error pattern matching database."""

    def __init__(self):
        """Initialize and load error patterns from JSON."""
        self.patterns: list[ErrorPattern] = []
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load error patterns from data/error-patterns.json."""
        data = load_json(DATA_DIR / "error-patterns.json")
        if data:
            self.patterns = self._parse_patterns(data)

    def _parse_patterns(self, data: dict) -> list[ErrorPattern]:
        """
        Convert JSON data to ErrorPattern instances.

        Args:
            data: Loaded JSON dict with patterns key

        Returns:
            List of ErrorPattern instances
        """
        patterns = []
        for item in data.get("patterns", []):
            try:
                pattern = ErrorPattern(
                    id=item.get("id", ""),
                    category=item.get("category", ""),
                    code=item.get("code", ""),
                    pattern=item.get("pattern", ""),
                    severity=item.get("severity", "medium"),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    causes=item.get("causes", []),
                    fix_steps=item.get("fix_steps", []),
                    fix_recipe_id=item.get("fix_recipe_id", ""),
                    related_codes=item.get("related_codes", []),
                    doc_url=item.get("doc_url", "")
                )
                patterns.append(pattern)
            except (KeyError, TypeError):
                continue
        return patterns

    def match_exact_code(self, code: str) -> list[ErrorPattern]:
        """
        Layer 1: Exact error code matching.

        Args:
            code: Error code to match

        Returns:
            List of matching ErrorPattern instances
        """
        code_upper = code.upper()
        return [p for p in self.patterns if p.code.upper() == code_upper]

    def match_regex(self, text: str) -> list[ErrorPattern]:
        """
        Layer 2: Regex pattern matching.

        Args:
            text: Text to search for pattern matches

        Returns:
            List of matching ErrorPattern instances
        """
        matches = []
        for pattern in self.patterns:
            if pattern.pattern:
                try:
                    if re.search(pattern.pattern, text, re.IGNORECASE):
                        matches.append(pattern)
                except re.error:
                    continue
        return matches

    def match_semantic(self, text: str) -> list[ErrorPattern]:
        """
        Layer 3: Keyword-based semantic matching.

        Args:
            text: Text to search for semantic matches

        Returns:
            List of matching ErrorPattern instances scored by relevance
        """
        text_lower = text.lower()
        words = set(re.findall(r'\w+', text_lower))

        scored_patterns = []
        for pattern in self.patterns:
            score = 0

            # Score against title
            title_words = set(re.findall(r'\w+', pattern.title.lower()))
            score += len(words & title_words) * 3

            # Score against description
            desc_words = set(re.findall(r'\w+', pattern.description.lower()))
            score += len(words & desc_words) * 2

            # Score against causes
            for cause in pattern.causes:
                cause_words = set(re.findall(r'\w+', cause.lower()))
                score += len(words & cause_words)

            if score > 0:
                scored_patterns.append((score, pattern))

        # Sort by score descending and return patterns
        scored_patterns.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_patterns[:5]]  # Top 5 semantic matches

    def diagnose(self, text: str, code: str | None = None) -> list[ErrorPattern]:
        """
        Run all matching layers and return deduplicated results.

        Args:
            text: Error text to diagnose
            code: Optional error code for exact matching

        Returns:
            List of matching ErrorPattern instances sorted by severity
        """
        matches = []
        seen_ids = set()

        # Layer 1: Exact code match
        if code:
            for pattern in self.match_exact_code(code):
                if pattern.id not in seen_ids:
                    matches.append(pattern)
                    seen_ids.add(pattern.id)

        # Layer 2: Regex match
        for pattern in self.match_regex(text):
            if pattern.id not in seen_ids:
                matches.append(pattern)
                seen_ids.add(pattern.id)

        # Layer 3: Semantic match
        for pattern in self.match_semantic(text):
            if pattern.id not in seen_ids:
                matches.append(pattern)
                seen_ids.add(pattern.id)

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        matches.sort(key=lambda p: severity_order.get(p.severity, 4))

        return matches

    def get_by_id(self, pattern_id: str) -> ErrorPattern | None:
        """Get pattern by ID."""
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                return pattern
        return None

    def get_by_category(self, category: str) -> list[ErrorPattern]:
        """Get all patterns in a category."""
        return [p for p in self.patterns if p.category.lower() == category.lower()]

    def list_categories(self) -> list[str]:
        """Get list of unique categories."""
        return sorted(set(p.category for p in self.patterns))
