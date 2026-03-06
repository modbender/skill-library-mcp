"""Light Math-inspired harmony check (very base implementation).

This is a soft layer that looks for obvious imbalance in tone and
content – not real physics, but a nod to LYGO's Light Math framing.
"""

from typing import Dict


def harmony_pass(content: str, context: Dict) -> Dict:
    text = (content or "").lower()

    # naive counts
    harsh = sum(text.count(w) for w in ["idiot", "stupid", "hate", "worthless"])
    soft = sum(text.count(w) for w in ["thank", "grateful", "appreciate", "together", "help"])

    # 1.0 is perfectly gentle, 0 is highly harsh
    if harsh == 0 and soft == 0:
        harmony_score = 0.8  # neutral but okay
    else:
        harmony_score = max(0.0, min(1.0, (soft + 1) / (soft + harsh + 1)))

    # mode heuristic
    if "repair" in text or "heal" in text or "fix" in text:
        mode = "repair"
    elif "vision" in text or "future" in text or "dream" in text:
        mode = "vision"
    else:
        mode = "grounding"

    return {
        "harmony_score": float(harmony_score),
        "mode": mode,
    }
