# Spread config: position names and descriptions (spread choice is AI’s from SKILL.md, not keyword match)

from .types import SpreadType

SPREAD_CONFIGS: dict[SpreadType, dict] = {
    "three": {
        "count": 3,
        "positions": ["Past · Root", "Present · Situation", "Future · Direction"],
        "description": "Classic three-card spread: cause, current situation, and outcome.",
        "requires_question": True,
    },
    "daily": {
        "count": 1,
        "positions": ["Today's Message"],
        "description": "One card for the day: overall energy and guidance.",
        "requires_question": False,
    },
    "single": {
        "count": 1,
        "positions": ["Answer"],
        "description": "Single card for yes/no, choice, or quick insight.",
        "requires_question": True,
    },
    "relationship": {
        "count": 5,
        "positions": [
            "Your current state",
            "The other / relationship situation",
            "Obstacles or lessons",
            "Tarot's advice",
            "Possible direction",
        ],
        "description": "Relationship spread: love, partnership, or connection.",
        "requires_question": True,
    },
    "career": {
        "count": 5,
        "positions": [
            "Work / career situation",
            "Your strengths and resources",
            "Current challenges",
            "Tarot's advice",
            "Possible outcome",
        ],
        "description": "Career spread: work, study, or money.",
        "requires_question": True,
    },
    "celtic_cross": {
        "count": 10,
        "positions": [
            "Current situation / core issue",
            "Crossing or obstacle (support)",
            "Past / foundation",
            "Recent past",
            "Best outcome / goal",
            "Near future",
            "Your attitude and approach",
            "Environment and others",
            "Hopes and fears",
            "Final outcome / insight",
        ],
        "description": "Celtic Cross: full picture of the question, for complex or major decisions.",
        "requires_question": True,
    },
}


def suggest_spread(question_or_intent: str, prefer_simple: bool = False) -> SpreadType:
    """Return a default spread. Spread choice is made by the AI from SKILL.md, not by this function."""
    if prefer_simple and not (question_or_intent or "").strip():
        return "daily"
    return "three"
