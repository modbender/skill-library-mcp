"""Recommendation engine for ClawHub skills."""
from __future__ import annotations

from dataclasses import dataclass

from .clawhub_client import ClawHubClient, SkillInfo
from .config_analyzer import ConfigAnalyzer
from .complementary_skills import ComplementarySkillScorer
from .recommendation_scoring import score_skill


@dataclass
class Recommendation:
    """Skill recommendation with score and reason."""
    skill: SkillInfo
    score: float
    reasons: list[str]


class RecommendationEngine:
    """Smart skill recommendation system."""

    def __init__(self):
        """Initialize recommendation engine."""
        self.client = ClawHubClient()
        self.analyzer = ConfigAnalyzer()
        self.comp_scorer = ComplementarySkillScorer()

    def recommend(
        self,
        channel: str | None = None,
        use_case: str | None = None,
        top: int = 10
    ) -> list[Recommendation]:
        """
        Generate skill recommendations.

        Args:
            channel: Filter by channel name
            use_case: Use case keyword
            top: Maximum results

        Returns:
            List of ranked recommendations
        """
        # Build search query
        query_parts = []
        if channel:
            query_parts.append(channel)
        if use_case:
            query_parts.append(use_case)

        query = " ".join(query_parts) if query_parts else ""

        # Get installed skills for complementary scoring
        installed = [s.slug for s in self.client.list_installed()]

        # Search skills
        skills = self.client.search(query, limit=top * 2)

        # Score and filter
        recommendations = []
        for skill in skills:
            # Skip already installed skills
            if skill.slug in installed:
                continue

            score, reasons = score_skill(
                skill, channel, use_case, installed, self.comp_scorer
            )
            if score > 0:
                recommendations.append(Recommendation(
                    skill=skill,
                    score=score,
                    reasons=reasons
                ))

        # Sort by score descending
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:top]

    def suggest_for_config(self) -> list[Recommendation]:
        """
        Auto-detect channels from config and recommend skills.

        Returns:
            Recommended skills for enabled channels
        """
        enabled_channels = self.analyzer.detect_channels()
        if not enabled_channels:
            return []

        all_recommendations = []
        seen_slugs = set()

        for channel in enabled_channels:
            recs = self.recommend(channel=channel, top=5)
            for rec in recs:
                if rec.skill.slug not in seen_slugs:
                    all_recommendations.append(rec)
                    seen_slugs.add(rec.skill.slug)

        # Re-sort by score
        all_recommendations.sort(key=lambda r: r.score, reverse=True)
        return all_recommendations[:10]

    def check_updates(self) -> list[tuple[SkillInfo, SkillInfo]]:
        """
        Check installed skills for updates.

        Returns:
            List of (installed_skill, latest_skill) tuples needing update
        """
        installed = self.client.list_installed()
        updates_available = []

        for installed_skill in installed:
            latest = self.client.get_skill_info(installed_skill.slug)
            if latest and latest.version != installed_skill.version:
                updates_available.append((installed_skill, latest))

        return updates_available

    def suggest_complementary(
        self,
        top: int = 10
    ) -> list[Recommendation]:
        """
        Suggest skills that complement installed skills.

        Args:
            top: Maximum results

        Returns:
            Recommended complementary skills
        """
        # Get installed skills
        installed = self.client.list_installed()
        installed_slugs = [s.slug for s in installed]

        if not installed_slugs:
            return []

        # Get complementary suggestions
        suggestions = self.comp_scorer.suggest_for_installed(
            installed_slugs, exclude_installed=True
        )

        # Convert to Recommendation objects
        recommendations = []
        for skill_slug, score, comp_reasons in suggestions[:top]:
            # Fetch skill info
            skill_info = self.client.get_skill_info(skill_slug)
            if skill_info:
                recommendations.append(Recommendation(
                    skill=skill_info,
                    score=score,
                    reasons=comp_reasons
                ))

        return recommendations
