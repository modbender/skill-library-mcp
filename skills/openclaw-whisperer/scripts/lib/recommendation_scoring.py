"""Scoring constants and logic for skill recommendations."""
from __future__ import annotations

from .clawhub_client import SkillInfo


# Channel-skill affinity mapping
CHANNEL_SKILLS = {
    "whatsapp": ["whatsapp-media", "whatsapp-status", "qr-code-gen"],
    "telegram": ["telegram-inline", "telegram-webhooks", "image-gen"],
    "discord": ["discord-voice", "discord-slash", "game-stats"],
    "slack": ["slack-workflows", "slack-apps", "jira-integration"],
    "signal": ["signal-groups", "privacy-tools"],
    "teams": ["teams-meetings", "sharepoint-integration"],
}

# Use case keywords
USE_CASE_KEYWORDS = {
    "calendar": ["calendar", "schedule", "meeting", "event", "reminder"],
    "image": ["image", "photo", "picture", "vision", "ocr", "generation"],
    "code": ["code", "github", "gitlab", "deploy", "ci/cd"],
    "automation": ["workflow", "automation", "task", "schedule"],
    "analytics": ["analytics", "metrics", "stats", "dashboard"],
}


def score_skill(
    skill: SkillInfo,
    channel: str | None,
    use_case: str | None,
    installed: list[str] | None = None,
    comp_scorer=None
) -> tuple[float, list[str]]:
    """Score skill relevance.

    Args:
        skill: Skill to score
        channel: Channel filter
        use_case: Use case filter
        installed: List of installed skill slugs
        comp_scorer: ComplementarySkillScorer instance

    Returns:
        Tuple of (score, reasons list)
    """
    score = 0.0
    reasons = []

    # Base score from verification and downloads
    if skill.verified:
        score += 2.0
        reasons.append("Verified skill")

    if skill.downloads > 1000:
        score += 1.0
        reasons.append("Popular (1000+ downloads)")
    elif skill.downloads > 100:
        score += 0.5

    # Channel affinity
    if channel:
        channel_lower = channel.lower()
        if channel_lower in CHANNEL_SKILLS:
            if any(s in skill.slug for s in CHANNEL_SKILLS[channel_lower]):
                score += 3.0
                reasons.append(f"Optimized for {channel}")

        if channel_lower in skill.name.lower() or channel_lower in skill.description.lower():
            score += 2.0
            reasons.append(f"Matches {channel} channel")

    # Use case matching
    if use_case:
        use_case_lower = use_case.lower()
        keywords = USE_CASE_KEYWORDS.get(use_case_lower, [use_case_lower])
        desc_lower = skill.description.lower()
        matches = sum(1 for kw in keywords if kw in desc_lower)
        if matches > 0:
            score += matches * 1.5
            reasons.append(f"Matches '{use_case}' use case")

    # Tag matching
    if skill.tags:
        if channel and channel.lower() in [t.lower() for t in skill.tags]:
            score += 1.0
        if use_case and use_case.lower() in [t.lower() for t in skill.tags]:
            score += 1.0

    # Complementary skill bonus
    if installed and comp_scorer:
        comp_score, comp_reasons = comp_scorer.score_match(
            installed, skill.slug
        )
        score += comp_score
        reasons.extend(comp_reasons)

    return score, reasons
