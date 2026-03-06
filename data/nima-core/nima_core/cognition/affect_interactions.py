"""
Cross-Affect Interactions
=========================
Models how certain affects suppress or amplify others.

Based on Panksepp's affective neuroscience:
- FEAR suppresses PLAY (anxiety kills joy)
- RAGE suppresses CARE (anger blocks nurturing)
- PLAY suppresses PANIC (joy reduces distress)
- etc.

Author: NIMA Core Team
Date: Feb 13, 2026
"""

import numpy as np
from typing import Dict

# Panksepp 7-affect order (must match dynamic_affect.py)
AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]
AFFECT_INDEX = {name: i for i, name in enumerate(AFFECTS)}

# Interaction matrix: source affects influence target affects
# Negative = suppression, Positive = amplification
# Strength scales with source intensity (only applied when source > threshold)
# Values are moderate to avoid over-suppression
INTERACTION_MATRIX: Dict[str, Dict[str, float]] = {
    "FEAR": {
        "PLAY": -0.25,      # Fear suppresses playfulness
        "SEEKING": -0.15,   # Fear reduces curiosity
        "LUST": -0.2,       # Anxiety dampens desire
    },
    "RAGE": {
        "CARE": -0.3,       # Anger suppresses nurturing
        "FEAR": -0.2,       # Rage can override fear (fight response)
        "PLAY": -0.2,       # Anger kills playfulness
    },
    "PANIC": {
        "SEEKING": -0.2,    # Distress reduces exploration
        "PLAY": -0.3,       # Grief suppresses joy
        "LUST": -0.15,      # Sadness dampens desire
    },
    "CARE": {
        "RAGE": -0.3,       # Caring suppresses anger
        "FEAR": -0.15,      # Love reduces anxiety
    },
    "PLAY": {
        "PANIC": -0.2,      # Joy reduces distress
        "FEAR": -0.15,      # Playfulness reduces fear
        "RAGE": -0.15,      # Fun softens anger
    },
    "SEEKING": {
        "PANIC": -0.15,     # Curiosity reduces anxiety
        "FEAR": -0.1,       # Engagement reduces fear
    },
    "LUST": {
        "RAGE": -0.15,      # Passion can soften anger
        "FEAR": -0.1,       # Desire can override fear
    },
}

# Threshold for applying interactions (source must be this high)
# Higher threshold = only strong emotions affect others
INTERACTION_THRESHOLD = 0.5


def apply_cross_affect_interactions(
    values: np.ndarray,
    affect_index: Dict[str, int] = None
) -> np.ndarray:
    """
    Apply cross-affect interactions to a 7D affect vector.
    
    When one affect is high, it can suppress or amplify others.
    For example, high FEAR suppresses PLAY.
    
    FIXED: Calculate all deltas first, then apply them at once to avoid
    sequential dependency issues.
    
    Args:
        values: 7D numpy array of affect values [SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY]
        affect_index: Optional custom affect index (defaults to AFFECT_INDEX)
    
    Returns:
        New 7D numpy array with interactions applied (original is not modified)
    """
    if affect_index is None:
        affect_index = AFFECT_INDEX
    
    result = values.copy()
    
    # Calculate all deltas first (to avoid sequential dependency)
    deltas = np.zeros(7, dtype=np.float32)
    
    for source_affect, interactions in INTERACTION_MATRIX.items():
        source_idx = affect_index.get(source_affect)
        if source_idx is None:
            continue
        
        source_val = values[source_idx]
        
        # Only apply interactions if source is above threshold
        if source_val < INTERACTION_THRESHOLD:
            continue
        
        for target_affect, strength in interactions.items():
            target_idx = affect_index.get(target_affect)
            if target_idx is None:
                continue
            
            # Accumulate delta (don't apply yet)
            deltas[target_idx] += source_val * strength
    
    # Apply all deltas at once
    result = np.clip(result + deltas, 0.0, 1.0)
    
    return result


def get_interaction_effects(values: np.ndarray) -> Dict[str, Dict[str, float]]:
    """
    Get a human-readable summary of interaction effects.
    
    Args:
        values: 7D numpy array of affect values
    
    Returns:
        Dict mapping source affects to their effects on targets
        e.g., {"FEAR": {"PLAY": -0.24, "SEEKING": -0.12}}
    """
    result = {}
    
    for source_affect, interactions in INTERACTION_MATRIX.items():
        source_idx = AFFECT_INDEX.get(source_affect)
        if source_idx is None:
            continue
        
        source_val = values[source_idx]
        if source_val < INTERACTION_THRESHOLD:
            continue
        
        effects = {}
        for target_affect, strength in interactions.items():
            delta = source_val * strength
            if abs(delta) > 0.05:  # Only report significant effects
                effects[target_affect] = round(delta, 3)
        
        if effects:
            result[source_affect] = effects
    
    return result


def explain_interactions() -> str:
    """
    Return a human-readable explanation of the interaction model.
    """
    lines = [
        "# Cross-Affect Interaction Model",
        "",
        "Based on Panksepp's affective neuroscience, certain emotions",
        "naturally suppress or amplify others:",
        "",
    ]
    
    for source, targets in INTERACTION_MATRIX.items():
        suppressions = []
        amplifications = []
        
        for target, strength in targets.items():
            if strength < 0:
                suppressions.append(f"{target} ({strength:.1f})")
            else:
                amplifications.append(f"{target} (+{strength:.1f})")
        
        if suppressions:
            lines.append(f"- **{source}** suppresses: {', '.join(suppressions)}")
        if amplifications:
            lines.append(f"- **{source}** amplifies: {', '.join(amplifications)}")
    
    lines.extend([
        "",
        f"Interactions only apply when source affect > {INTERACTION_THRESHOLD}",
    ])
    
    return "\n".join(lines)