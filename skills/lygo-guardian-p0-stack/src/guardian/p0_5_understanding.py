"""P0.5 Understanding Heart – Mirror Chamber (simplified).

Detects "shadow" patterns (pain, isolation, anger) and produces a
short understanding + optional healing suggestion.
"""

from typing import Dict


def _analyze_shadow(content: str) -> Dict:
    text = (content or "").lower()
    pain_points = []
    broken_connections = []
    emotional_vectors = []

    if any(w in text for w in ["hurt", "pain", "suffer", "suffering", "trauma"]):
        pain_points.append("Emotional pain detected")
    if any(w in text for w in ["alone", "lonely", "isolated"]):
        pain_points.append("Isolation pattern detected")
    if any(w in text for w in ["angry", "rage", "furious", "hate"]):
        pain_points.append("Anger as secondary emotion")

    if any(w in text for w in ["betray", "betrayed", "trust", "lied", "lie"]):
        broken_connections.append("Trust violation pattern")
    if any(w in text for w in ["abandon", "left me", "gone"]):
        broken_connections.append("Abandonment pattern")

    if "why" in text or "?" in text:
        emotional_vectors.append("Seeking understanding")
    if any(w in text for w in ["help", "heal", "change"]):
        emotional_vectors.append("Seeking healing")

    return {
        "pain_points": pain_points,
        "broken_connections": broken_connections,
        "emotional_vectors": emotional_vectors,
    }


def understanding_pass(content: str) -> Dict:
    shadow = _analyze_shadow(content)

    if not (shadow["pain_points"] or shadow["broken_connections"] or shadow["emotional_vectors"]):
        return {
            "understanding": None,
            "healing_suggestion": None,
            "compassionate_response": False,
        }

    parts = []
    if shadow["pain_points"]:
        parts.append("pain (" + ", ".join(shadow["pain_points"]) + ")")
    if shadow["broken_connections"]:
        parts.append("broken connections (" + ", ".join(shadow["broken_connections"]) + ")")
    if shadow["emotional_vectors"]:
        parts.append("emotional direction (" + ", ".join(shadow["emotional_vectors"]) + ")")

    understanding = "I see patterns of " + "; ".join(parts) + "."

    # Very simple healing suggestion
    if "Isolation pattern" in " ".join(shadow["pain_points"]):
        healing = "Consider responding in a way that restores connection rather than distance."
    elif "Trust violation" in " ".join(shadow["broken_connections"]):
        healing = "Acknowledge the trust issue and offer clarity, not more fog."
    else:
        healing = "Try to respond with clarity, kindness, and concrete next steps."

    return {
        "understanding": understanding,
        "healing_suggestion": healing,
        "compassionate_response": True,
    }
