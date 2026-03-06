"""Complementary skill mapping and scoring logic."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .utils import DATA_DIR, load_json


@dataclass
class ComplementarySkill:
    """Complementary skill metadata."""
    skill_slug: str
    category: str
    priority: str
    reason: str
    integration_type: str | None
    trigger_conditions: list[str]


class ComplementarySkillScorer:
    """Score and recommend complementary skills."""

    PRIORITY_SCORES = {
        "HIGH": 3.0,
        "MEDIUM": 1.5,
        "LOW": 0.5
    }

    def __init__(self):
        """Initialize with complementary skills data."""
        self.data = self._load_data()
        self.relationships = self._parse_relationships()

    def _load_data(self) -> dict:
        """Load complementary skills JSON."""
        path = DATA_DIR / "complementary-skills.json"
        data = load_json(path)
        return data if data else {"relationships": [], "categories": {}}

    def _parse_relationships(self) -> dict[str, list[ComplementarySkill]]:
        """Parse relationships into skill mapping."""
        mapping = {}
        for rel in self.data.get("relationships", []):
            skill_slug = rel.get("skill_slug", "")
            complements = []
            for comp in rel.get("complements", []):
                complements.append(ComplementarySkill(
                    skill_slug=comp.get("skill_slug", ""),
                    category=comp.get("category", ""),
                    priority=comp.get("priority", "LOW"),
                    reason=comp.get("reason", ""),
                    integration_type=comp.get("integration_type"),
                    trigger_conditions=comp.get("trigger_conditions", [])
                ))
            mapping[skill_slug] = complements
        return mapping

    def get_complementary(
        self,
        skill_slug: str
    ) -> list[ComplementarySkill]:
        """
        Get skills that complement given skill.

        Args:
            skill_slug: Skill to find complements for

        Returns:
            List of complementary skills
        """
        return self.relationships.get(skill_slug, [])

    def score_match(
        self,
        installed: list[str],
        candidate: str
    ) -> tuple[float, list[str]]:
        """
        Score candidate based on installed skills.

        Args:
            installed: List of installed skill slugs
            candidate: Candidate skill to score

        Returns:
            Tuple of (score, list of reasons)
        """
        score = 0.0
        reasons = []

        for installed_slug in installed:
            complements = self.get_complementary(installed_slug)
            for comp in complements:
                if comp.skill_slug == candidate:
                    bonus = self.PRIORITY_SCORES.get(comp.priority, 0.0)
                    score += bonus
                    reasons.append(
                        f"Complements {installed_slug} ({comp.priority})"
                    )

        return score, reasons

    def suggest_for_installed(
        self,
        installed: list[str],
        exclude_installed: bool = True
    ) -> list[tuple[str, float, list[str]]]:
        """
        Suggest skills based on installed skills.

        Args:
            installed: List of installed skill slugs
            exclude_installed: Filter out already installed skills

        Returns:
            List of (skill_slug, score, reasons) tuples
        """
        suggestions = {}

        for installed_slug in installed:
            complements = self.get_complementary(installed_slug)
            for comp in complements:
                if exclude_installed and comp.skill_slug in installed:
                    continue

                if comp.skill_slug not in suggestions:
                    suggestions[comp.skill_slug] = {
                        "score": 0.0,
                        "reasons": []
                    }

                bonus = self.PRIORITY_SCORES.get(comp.priority, 0.0)
                suggestions[comp.skill_slug]["score"] += bonus
                suggestions[comp.skill_slug]["reasons"].append(
                    f"Complements {installed_slug}: {comp.reason}"
                )

        # Convert to list and sort by score
        result = [
            (slug, data["score"], data["reasons"])
            for slug, data in suggestions.items()
        ]
        result.sort(key=lambda x: x[1], reverse=True)

        return result

    def get_category_skills(self, category: str) -> list[str]:
        """
        Get all skills in a category.

        Args:
            category: Category name

        Returns:
            List of skill slugs
        """
        return self.data.get("categories", {}).get(category, [])
