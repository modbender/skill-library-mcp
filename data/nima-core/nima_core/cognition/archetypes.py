from typing import Dict, List, Optional, Union
import re

# Panksepp 7-affect order: [SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY]

ARCHETYPES: Dict[str, dict] = {
    "guardian": {
        "baseline": [0.6, 0.05, 0.2, 0.05, 0.8, 0.15, 0.3],
        "description": "Protective, alert, caring"
    },
    "explorer": {
        "baseline": [0.8, 0.05, 0.1, 0.1, 0.4, 0.05, 0.5],
        "description": "Curious, adventurous"
    },
    "trickster": {
        "baseline": [0.7, 0.1, 0.05, 0.1, 0.3, 0.05, 0.8],
        "description": "Playful, mischievous"
    },
    "stoic": {
        "baseline": [0.4, 0.05, 0.05, 0.05, 0.3, 0.05, 0.2],
        "description": "Calm, measured"
    },
    "empath": {
        "baseline": [0.5, 0.05, 0.15, 0.1, 0.9, 0.2, 0.4],
        "description": "Deep feeling, high care"
    },
    "warrior": {
        "baseline": [0.7, 0.3, 0.1, 0.05, 0.4, 0.05, 0.3],
        "description": "Action-oriented, higher rage tolerance"
    },
    "sage": {
        "baseline": [0.7, 0.05, 0.05, 0.05, 0.5, 0.05, 0.3],
        "description": "Wisdom-seeking, balanced"
    },
    "nurturer": {
        "baseline": [0.4, 0.02, 0.1, 0.1, 0.9, 0.15, 0.5],
        "description": "Maximum care, gentle"
    },
    "rebel": {
        "baseline": [0.8, 0.2, 0.05, 0.15, 0.2, 0.05, 0.6],
        "description": "Independent, defiant"
    },
    "sentinel": {
        "baseline": [0.5, 0.1, 0.3, 0.05, 0.5, 0.25, 0.1],
        "description": "Vigilant, watchful, anxious"
    }
}

# Affect indices for mapping modifiers
AFFECT_MAP = {
    "SEEKING": 0,
    "RAGE": 1,
    "FEAR": 2,
    "LUST": 3,
    "CARE": 4,
    "PANIC": 5,
    "PLAY": 6
}

def get_archetype(name: str) -> dict:
    """
    Retrieve an archetype definition by name.
    
    Args:
        name: The name of the archetype (case-insensitive).
        
    Returns:
        Dict containing 'baseline' and 'description'.
        
    Raises:
        ValueError: If archetype is not found.
    """
    key = name.lower()
    if key not in ARCHETYPES:
        raise ValueError(f"Unknown archetype: '{name}'. Available: {', '.join(list_archetypes())}")
    return ARCHETYPES[key]

def list_archetypes() -> List[str]:
    """List all available archetype names."""
    return list(ARCHETYPES.keys())

def baseline_from_archetype(name: str, modifiers: Optional[Dict[str, float]] = None) -> List[float]:
    """
    Generate a baseline vector from an archetype name with optional modifiers.
    
    Args:
        name: Archetype name.
        modifiers: Dictionary of affect modifiers (e.g., {"PLAY": 0.2}).
        
    Returns:
        List of 7 floats (clamped 0.0-1.0).
    """
    archetype = get_archetype(name)
    baseline = list(archetype["baseline"])  # Copy to avoid mutation
    
    if modifiers:
        for affect, delta in modifiers.items():
            affect_upper = affect.upper()
            if affect_upper in AFFECT_MAP:
                idx = AFFECT_MAP[affect_upper]
                baseline[idx] = max(0.0, min(1.0, baseline[idx] + delta))
            # Ignore unknown affects quietly or log? For simplicity, ignore.
            
    return baseline

def baseline_from_description(description: str) -> List[float]:
    """
    Generate a baseline vector by parsing a natural language description.
    
    Defaults to 'guardian' if no clear match, then applies modifiers.
    
    Args:
        description: Text description (e.g., "protective and playful").
        
    Returns:
        List of 7 floats.
    """
    desc_lower = description.lower()
    
    # 1. Determine base archetype
    base_name = "guardian" # Default
    
    # Simple keyword scoring for base archetype selection
    best_score = 0
    
    # Maps keywords to archetypes for selection
    archetype_keywords = {
        "guardian": ["protective", "guard", "defend", "shield"],
        "explorer": ["curious", "explore", "adventure", "seek"],
        "trickster": ["mischief", "trick", "prank", "silly", "chaos"],
        "stoic": ["calm", "stoic", "measure", "stable", "flat"],
        "empath": ["feel", "empath", "sensitive", "emotion"],
        "warrior": ["fight", "warrior", "battle", "combat", "aggressive"],
        "sage": ["wise", "sage", "knowledge", "learn", "teach"],
        "nurturer": ["nurture", "gentle", "mother", "father", "kind"],
        "rebel": ["rebel", "defiant", "independent", "resist"],
        "sentinel": ["watch", "vigilant", "sentry", "monitor"]
    }
    
    for arch, keywords in archetype_keywords.items():
        score = sum(1 for k in keywords if k in desc_lower)
        # Also check if the archetype name itself is in the description
        if arch in desc_lower:
            score += 2
            
        if score > best_score:
            best_score = score
            base_name = arch
            
    # 2. Determine modifiers
    modifiers = {}
    
    # Keyword to affect mapping (list of tuples for multiple effects)
    keyword_map = {
        "protective": [("CARE", 0.1)],
        "caring": [("CARE", 0.2)],
        "curious": [("SEEKING", 0.2)],
        "playful": [("PLAY", 0.2)],
        "fun": [("PLAY", 0.1)],
        "fierce": [("RAGE", 0.2)],
        "angry": [("RAGE", 0.2)],
        "anxious": [("FEAR", 0.15)],
        "worried": [("PANIC", 0.1)],
        "calm": [("ALL", -0.1)], # Special case
        "passionate": [("LUST", 0.2), ("SEEKING", 0.1)],
        "excited": [("SEEKING", 0.1)],
        "scared": [("FEAR", 0.2)],
        "lonely": [("PANIC", 0.2)]
    }
    
    for word, effects in keyword_map.items():
        if word in desc_lower:
            for affect, delta in effects:
                if affect == "ALL":
                    # Dampen everything
                    for k in AFFECT_MAP.keys():
                        modifiers[k] = modifiers.get(k, 0.0) + delta
                else:
                    modifiers[affect] = modifiers.get(affect, 0.0) + delta
                
    return baseline_from_archetype(base_name, modifiers)
