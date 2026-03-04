#!/usr/bin/env python3
"""
Emotion Detection and Mapping
==============================
Lightweight emotion-to-Panksepp affect mapping without heavy dependencies.

Maps common emotion labels to the 7 Panksepp affects:
    SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY

Can be used standalone or integrated with DynamicAffectSystem.

Author: NIMA Core Team
Date: Feb 13, 2026
"""

from typing import Dict, List, Tuple
import re

# Canonical affect names
AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]

# Map basic emotions to Panksepp affects
EMOTION_TO_AFFECT = {
    # Joy / Playfulness → PLAY
    "joy": "PLAY",
    "excitement": "PLAY",
    "amusement": "PLAY",
    "delight": "PLAY",
    "happiness": "PLAY",
    "elation": "PLAY",
    "cheerfulness": "PLAY",
    
    # Love / Caring → CARE
    "love": "CARE",
    "gratitude": "CARE",
    "trust": "CARE",
    "affection": "CARE",
    "compassion": "CARE",
    "tenderness": "CARE",
    "warmth": "CARE",
    
    # Curiosity / Anticipation → SEEKING
    "pride": "SEEKING",
    "curiosity": "SEEKING",
    "anticipation": "SEEKING",
    "hope": "SEEKING",
    "interest": "SEEKING",
    "wonder": "SEEKING",
    "surprise": "SEEKING",
    "fascination": "SEEKING",
    
    # Anger / Frustration → RAGE
    "anger": "RAGE",
    "frustration": "RAGE",
    "disgust": "RAGE",
    "contempt": "RAGE",
    "irritation": "RAGE",
    "annoyance": "RAGE",
    "resentment": "RAGE",
    "outrage": "RAGE",
    
    # Fear / Anxiety → FEAR
    "fear": "FEAR",
    "anxiety": "FEAR",
    "worry": "FEAR",
    "nervousness": "FEAR",
    "apprehension": "FEAR",
    "dread": "FEAR",
    "terror": "FEAR",
    "panic_fear": "FEAR",  # disambiguation from PANIC
    
    # Sadness / Grief → PANIC (separation distress)
    "sadness": "PANIC",
    "grief": "PANIC",
    "loneliness": "PANIC",
    "sorrow": "PANIC",
    "melancholy": "PANIC",
    "despair": "PANIC",
    "hopelessness": "PANIC",
    "depression": "PANIC",
    
    # Guilt / Shame → PANIC (internal distress)
    "guilt": "PANIC",
    "shame": "PANIC",
    "embarrassment": "PANIC",
    "remorse": "PANIC",
    "regret": "PANIC",
    
    # Desire / Passion → LUST
    "desire": "LUST",
    "passion": "LUST",
    "attraction": "LUST",
    "longing": "LUST",
    "craving": "LUST",
    "yearning": "LUST",
}

# Intensity modifiers for certain emotions
# Some emotions map more strongly than others
EMOTION_INTENSITY_MODIFIERS = {
    "terror": 1.5,
    "rage": 1.5,
    "ecstasy": 1.5,
    "despair": 1.5,
    "obsession": 1.3,
    "fascination": 1.2,
    "amusement": 0.9,
    "interest": 0.8,
    "concern": 0.7,
}


def map_emotions_to_affects(
    emotions: List[Dict],
    use_modifiers: bool = True
) -> Tuple[Dict[str, float], float]:
    """
    Map a list of detected emotions to Panksepp affects.
    
    Args:
        emotions: List of dicts with {"emotion": str, "intensity": float, ...}
        use_modifiers: Apply intensity modifiers for specific emotions
    
    Returns:
        Tuple of:
            - Dict mapping affect names to aggregated intensities
            - Overall intensity (0-1)
    
    Example:
        >>> emotions = [
        ...     {"emotion": "joy", "intensity": 0.8},
        ...     {"emotion": "gratitude", "intensity": 0.6}
        ... ]
        >>> affects, intensity = map_emotions_to_affects(emotions)
        >>> print(affects)
        {'PLAY': 0.8, 'CARE': 0.6}
        >>> print(intensity)
        0.7
    """
    if not emotions:
        return {}, 0.0
    
    affect_sums = {name: 0.0 for name in AFFECTS}
    affect_counts = {name: 0 for name in AFFECTS}
    total_intensity = 0.0
    mapped_count = 0
    
    for em in emotions:
        emotion = em.get("emotion", "").lower()
        intensity = em.get("intensity", 0.5)
        
        # Map emotion to affect
        affect = EMOTION_TO_AFFECT.get(emotion)
        if affect:
            # Apply emotion-specific modifier if enabled
            if use_modifiers and emotion in EMOTION_INTENSITY_MODIFIERS:
                intensity *= EMOTION_INTENSITY_MODIFIERS[emotion]
                intensity = min(1.0, intensity)
                
            affect_sums[affect] += intensity
            affect_counts[affect] += 1
            total_intensity += intensity
            mapped_count += 1
    
    # Average for each affect
    detected = {}
    for name in AFFECTS:
        if affect_counts[name] > 0:
            detected[name] = affect_sums[name] / affect_counts[name]
    
    # Overall intensity (normalized by mapped count)
    overall_intensity = min(1.0, total_intensity / max(1, mapped_count))
    
    return detected, overall_intensity


def detect_affect_from_text(text: str) -> Dict[str, float]:
    """
    Simple keyword-based affect detection from text.
    This is a lightweight fallback when no ML model is available.
    
    Args:
        text: Input text
    
    Returns:
        Dict mapping affect names to intensities (0-1)
    
    Note:
        For production use, integrate with a proper emotion classifier
        or use the OpenClaw plugin's lexicon-based detection.
    """
    if not text:
        return {}
    
    # Tokenize text using regex to match whole words only
    words = set(re.findall(r'\b\w+\b', text.lower()))
    affects = {}
    
    # Simple keyword matching (very basic)
    # This is meant as a fallback - use a proper lexicon or model in production
    keywords = {
        "PLAY": ["happy", "fun", "joy", "laugh", "haha", "lol", "excited", "yay"],
        "CARE": ["love", "care", "thank", "appreciate", "grateful", "kind", "help"],
        "SEEKING": ["curious", "wonder", "why", "how", "interesting", "learn", "explore"],
        "RAGE": ["angry", "mad", "rage", "furious", "hate", "damn", "stupid"],
        "FEAR": ["afraid", "scared", "worry", "anxious", "nervous", "fear"],
        "PANIC": ["sad", "depressed", "lonely", "grief", "loss", "cry", "miss"],
        "LUST": ["desire", "want", "crave", "passion", "attractive"],
    }
    
    for affect, key_words in keywords.items():
        # Check if any keyword is in the set of tokenized words
        count = sum(1 for kw in key_words if kw in words)
        if count > 0:
            # Simple intensity based on match count
            affects[affect] = min(1.0, count * 0.3)
    
    return affects


# ==============================================================================
# CLI / TESTING
# ==============================================================================

if __name__ == "__main__":
    import json
    
    # Test 1: Map emotions to affects
    print("Test 1: Emotion mapping")
    emotions = [
        {"emotion": "joy", "intensity": 0.8},
        {"emotion": "gratitude", "intensity": 0.6},
        {"emotion": "curiosity", "intensity": 0.7},
    ]
    affects, intensity = map_emotions_to_affects(emotions)
    print(f"Input: {emotions}")
    print(f"Output affects: {affects}")
    print(f"Overall intensity: {intensity:.2f}")
    
    # Test 2: Text detection
    print("\nTest 2: Text-based detection (keyword fallback)")
    text = "I'm so happy and grateful for this amazing day!"
    detected = detect_affect_from_text(text)
    print(f"Text: {text}")
    print(f"Detected: {detected}")
    
    # Test 3: Negative emotions
    print("\nTest 3: Negative emotions")
    emotions_neg = [
        {"emotion": "sadness", "intensity": 0.7},
        {"emotion": "fear", "intensity": 0.5},
        {"emotion": "anger", "intensity": 0.3},
    ]
    affects_neg, intensity_neg = map_emotions_to_affects(emotions_neg)
    print(f"Input: {emotions_neg}")
    print(f"Output affects: {affects_neg}")
    print(f"Overall intensity: {intensity_neg:.2f}")
    
    print("\n✅ All tests complete!")
