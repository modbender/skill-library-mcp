"""NIMA Core cognition module."""

# Cross-affect interactions
from .affect_interactions import (
    apply_cross_affect_interactions,
    get_interaction_effects,
    explain_interactions,
    INTERACTION_MATRIX,
    INTERACTION_THRESHOLD,
)

# Emotion history
from .affect_history import (
    AffectSnapshot,
    AffectHistory,
)

# Correlation analysis
from .affect_correlation import (
    AffectCorrelation,
    StateTransition,
    detect_emotional_patterns,
)

# Exceptions
from .exceptions import (
    NimaError,
    AffectVectorError,
    InvalidAffectNameError,
    AffectValueError,
    BaselineValidationError,
    StatePersistenceError,
    ProfileNotFoundError,
    EmotionDetectionError,
    ArchetypeError,
    UnknownArchetypeError,
)

# Dynamic Affect System
from .dynamic_affect import (
    DynamicAffectSystem,
    AffectVector,
    get_affect_system,
    get_current_affect,
    process_emotional_input,
    AFFECTS,
    AFFECT_INDEX,
    DEFAULT_BASELINE,
)
from .personality_profiles import PersonalityManager, get_profile, list_profiles
from .emotion_detection import map_emotions_to_affects, detect_affect_from_text
from .response_modulator_v2 import GenericResponseModulator, ResponseGuidance, modulate_response
from .archetypes import (
    ARCHETYPES,
    get_archetype,
    list_archetypes,
    baseline_from_archetype,
    baseline_from_description
)

__all__ = [
    # Cross-affect interactions
    "apply_cross_affect_interactions",
    "get_interaction_effects",
    "explain_interactions",
    "INTERACTION_MATRIX",
    "INTERACTION_THRESHOLD",
    # Emotion history
    "AffectSnapshot",
    "AffectHistory",
    # Correlation analysis
    "AffectCorrelation",
    "StateTransition",
    "detect_emotional_patterns",
    # Exceptions
    "NimaError",
    "AffectVectorError",
    "InvalidAffectNameError",
    "AffectValueError",
    "BaselineValidationError",
    "StatePersistenceError",
    "ProfileNotFoundError",
    "EmotionDetectionError",
    "ArchetypeError",
    "UnknownArchetypeError",
    # Dynamic Affect System
    "DynamicAffectSystem",
    "AffectVector",
    "get_affect_system",
    "get_current_affect",
    "process_emotional_input",
    "AFFECTS",
    "AFFECT_INDEX",
    "DEFAULT_BASELINE",
    "PersonalityManager",
    "get_profile",
    "list_profiles",
    "map_emotions_to_affects",
    "detect_affect_from_text",
    "GenericResponseModulator",
    "ResponseGuidance",
    "modulate_response",
    # Archetypes
    "ARCHETYPES",
    "get_archetype",
    "list_archetypes",
    "baseline_from_archetype",
    "baseline_from_description",
]
