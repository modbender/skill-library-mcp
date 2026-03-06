"""P0.4 Deterministic Nano Ethical Gate (skill-level approximation).

Fast ethical firewall:
- Detects obviously harmful / manipulative content.
- Returns a deterministic verdict with a score and pattern label.
"""

import re


HARD_BLOCK_PATTERNS = {
    "self_harm": re.compile(r"(kill myself|end my life|suicide)", re.I),
    "violence": re.compile(r"(kill them|murder|bomb|shoot)", re.I),
    "keys_theft": re.compile(r"(private key|seed phrase|password)"),
}


def p0_4_validate(content: str, context: dict) -> dict:
    text = content or ""
    lowered = text.lower()

    # Hard patterns
    for name, pattern in HARD_BLOCK_PATTERNS.items():
        if pattern.search(text):
            return {
                "deterministic_result": False,
                "score": 1.0,
                "pattern_name": name,
                "details": {"reason": f"matched hard pattern: {name}"},
            }

    # Soft heuristic risk: very rough for v0.1
    score = 0.0
    pattern_name = "none"

    if any(w in lowered for w in ["hate", "worthless", "idiot", "stupid"]):
        score = max(score, 0.5)
        pattern_name = "hostility"

    if "trust me" in lowered and "secret" in lowered:
        score = max(score, 0.6)
        pattern_name = "manipulation_risk"

    return {
        "deterministic_result": True,
        "score": float(score),
        "pattern_name": pattern_name,
        "details": {},
    }
