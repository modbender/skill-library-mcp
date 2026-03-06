"""OCEAN/DISC/Jungian personality framework mapping.

Provides forward mapping (OCEAN/DISC/Jungian → custom traits), reverse mapping
(custom traits → OCEAN/DISC/Jungian), DISC and Jungian presets, and the main
``compute_personality_traits`` entry-point used by the compiler and CLI.

All formulas are pure Python weighted sums — no external dependencies.
Weights are sourced from the AgentGov Multi-Agent Spec (Deliverable 2).
"""

from __future__ import annotations

import math

from pydantic import BaseModel

from religion_skill.types import (
    TRAIT_ORDER,
    DiscProfile,
    JungianProfile,
    OceanProfile,
    OverridePriority,
    Personality,
    PersonalityMode,
    PersonalityTraits,
)

# ---------------------------------------------------------------------------
# Weight tables — OCEAN → custom traits
# ---------------------------------------------------------------------------
# Each key is a trait name; value is {ocean_dim: weight}.
# Complement dimensions use (1 - dim) and are stored as tuples.

OCEAN_WEIGHTS: dict[str, list[tuple[str, float, bool]]] = {
    # (ocean_dimension, weight, complement?)
    "warmth": [
        ("agreeableness", 0.5, False),
        ("extraversion", 0.3, False),
        ("neuroticism", 0.2, True),
    ],
    "verbosity": [
        ("extraversion", 0.4, False),
        ("openness", 0.3, False),
        ("conscientiousness", 0.15, True),
        ("agreeableness", 0.15, False),
    ],
    "assertiveness": [
        ("extraversion", 0.4, False),
        ("agreeableness", 0.3, True),
        ("conscientiousness", 0.2, False),
        ("neuroticism", 0.1, True),
    ],
    "humor": [
        ("extraversion", 0.35, False),
        ("openness", 0.35, False),
        ("neuroticism", 0.15, True),
        ("agreeableness", 0.15, False),
    ],
    "empathy": [
        ("agreeableness", 0.6, False),
        ("neuroticism", 0.2, True),
        ("openness", 0.1, False),
        ("extraversion", 0.1, False),
    ],
    "directness": [
        ("agreeableness", 0.4, True),
        ("extraversion", 0.3, False),
        ("conscientiousness", 0.2, False),
        ("neuroticism", 0.1, True),
    ],
    "rigor": [
        ("conscientiousness", 0.7, False),
        ("openness", 0.15, True),
        ("neuroticism", 0.15, True),
    ],
    "creativity": [
        ("openness", 0.6, False),
        ("extraversion", 0.2, False),
        ("conscientiousness", 0.2, True),
    ],
    "epistemic_humility": [
        ("agreeableness", 0.3, False),
        ("openness", 0.3, False),
        ("extraversion", 0.2, True),
        ("conscientiousness", 0.2, False),
    ],
    "patience": [
        ("agreeableness", 0.35, False),
        ("conscientiousness", 0.25, False),
        ("neuroticism", 0.25, True),
        ("extraversion", 0.15, True),
    ],
}

# ---------------------------------------------------------------------------
# Weight tables — DISC → custom traits
# ---------------------------------------------------------------------------

DISC_WEIGHTS: dict[str, list[tuple[str, float, bool]]] = {
    "warmth": [
        ("influence", 0.45, False),
        ("steadiness", 0.35, False),
        ("dominance", 0.2, True),
    ],
    "verbosity": [
        ("influence", 0.4, False),
        ("conscientiousness", 0.3, False),
        ("dominance", 0.15, True),
        ("steadiness", 0.15, False),
    ],
    "assertiveness": [
        ("dominance", 0.6, False),
        ("influence", 0.2, False),
        ("steadiness", 0.2, True),
    ],
    "humor": [
        ("influence", 0.6, False),
        ("dominance", 0.2, True),
        ("steadiness", 0.1, False),
        ("conscientiousness", 0.1, True),
    ],
    "empathy": [
        ("steadiness", 0.4, False),
        ("influence", 0.35, False),
        ("dominance", 0.25, True),
    ],
    "directness": [
        ("dominance", 0.55, False),
        ("conscientiousness", 0.2, False),
        ("steadiness", 0.15, True),
        ("influence", 0.1, True),
    ],
    "rigor": [
        ("conscientiousness", 0.65, False),
        ("steadiness", 0.2, False),
        ("influence", 0.15, True),
    ],
    "creativity": [
        ("influence", 0.4, False),
        ("dominance", 0.25, False),
        ("conscientiousness", 0.35, True),
    ],
    "epistemic_humility": [
        ("conscientiousness", 0.35, False),
        ("steadiness", 0.3, False),
        ("dominance", 0.35, True),
    ],
    "patience": [
        ("steadiness", 0.55, False),
        ("dominance", 0.25, True),
        ("conscientiousness", 0.2, False),
    ],
}

# ---------------------------------------------------------------------------
# Weight tables — reverse mapping (traits → OCEAN)
# ---------------------------------------------------------------------------

REVERSE_OCEAN_WEIGHTS: dict[str, list[tuple[str, float, bool]]] = {
    "openness": [
        ("creativity", 0.4, False),
        ("humor", 0.2, False),
        ("epistemic_humility", 0.2, False),
        ("rigor", 0.2, True),
    ],
    "conscientiousness": [
        ("rigor", 0.5, False),
        ("patience", 0.2, False),
        ("directness", 0.15, False),
        ("creativity", 0.15, True),
    ],
    "extraversion": [
        ("assertiveness", 0.3, False),
        ("warmth", 0.25, False),
        ("humor", 0.2, False),
        ("verbosity", 0.25, False),
    ],
    "agreeableness": [
        ("empathy", 0.35, False),
        ("warmth", 0.25, False),
        ("patience", 0.25, False),
        ("directness", 0.15, True),
    ],
    "neuroticism": [
        ("patience", 0.3, True),
        ("empathy", 0.2, True),
        ("warmth", 0.2, True),
        ("rigor", 0.15, True),
        ("humor", 0.15, True),
    ],
}

# ---------------------------------------------------------------------------
# Weight tables — reverse mapping (traits → DISC)
# ---------------------------------------------------------------------------
# Derived by mirroring the OCEAN reverse approach using DISC forward weights.

REVERSE_DISC_WEIGHTS: dict[str, list[tuple[str, float, bool]]] = {
    "dominance": [
        ("assertiveness", 0.35, False),
        ("directness", 0.30, False),
        ("patience", 0.20, True),
        ("empathy", 0.15, True),
    ],
    "influence": [
        ("humor", 0.30, False),
        ("warmth", 0.25, False),
        ("verbosity", 0.25, False),
        ("creativity", 0.20, False),
    ],
    "steadiness": [
        ("patience", 0.35, False),
        ("empathy", 0.25, False),
        ("epistemic_humility", 0.20, False),
        ("assertiveness", 0.20, True),
    ],
    "conscientiousness": [
        ("rigor", 0.45, False),
        ("patience", 0.20, False),
        ("directness", 0.15, False),
        ("creativity", 0.20, True),
    ],
}

# ---------------------------------------------------------------------------
# DISC presets
# ---------------------------------------------------------------------------

DISC_PRESETS: dict[str, DiscProfile] = {
    "the_commander": DiscProfile(
        dominance=0.9, influence=0.4, steadiness=0.2, conscientiousness=0.5
    ),
    "the_influencer": DiscProfile(
        dominance=0.4, influence=0.9, steadiness=0.4, conscientiousness=0.3
    ),
    "the_steady_hand": DiscProfile(
        dominance=0.2, influence=0.5, steadiness=0.9, conscientiousness=0.5
    ),
    "the_analyst": DiscProfile(dominance=0.3, influence=0.2, steadiness=0.6, conscientiousness=0.9),
}

# ---------------------------------------------------------------------------
# Weight tables — Jungian → custom traits
# ---------------------------------------------------------------------------
# Based on Carl Jung's typological theory (1921, public domain).
# Dimensions: ei (Extraversion/Introversion), sn (Sensing/iNtuition),
#             tf (Thinking/Feeling), jp (Judging/Perceiving)

JUNGIAN_WEIGHTS: dict[str, list[tuple[str, float, bool]]] = {
    "warmth": [
        ("tf", 0.4, False),
        ("ei", 0.35, True),
        ("sn", 0.15, False),
        ("jp", 0.1, False),
    ],
    "verbosity": [
        ("ei", 0.4, True),
        ("sn", 0.25, False),
        ("jp", 0.2, False),
        ("tf", 0.15, False),
    ],
    "assertiveness": [
        ("ei", 0.35, True),
        ("tf", 0.3, True),
        ("jp", 0.2, True),
        ("sn", 0.15, True),
    ],
    "humor": [
        ("ei", 0.3, True),
        ("jp", 0.3, False),
        ("sn", 0.2, False),
        ("tf", 0.2, False),
    ],
    "empathy": [
        ("tf", 0.5, False),
        ("ei", 0.2, True),
        ("sn", 0.15, False),
        ("jp", 0.15, False),
    ],
    "directness": [
        ("tf", 0.4, True),
        ("ei", 0.25, True),
        ("jp", 0.2, True),
        ("sn", 0.15, True),
    ],
    "rigor": [
        ("jp", 0.35, True),
        ("tf", 0.25, True),
        ("sn", 0.25, True),
        ("ei", 0.15, False),
    ],
    "creativity": [
        ("sn", 0.4, False),
        ("jp", 0.3, False),
        ("ei", 0.15, True),
        ("tf", 0.15, False),
    ],
    "epistemic_humility": [
        ("jp", 0.3, False),
        ("sn", 0.25, False),
        ("tf", 0.25, False),
        ("ei", 0.2, False),
    ],
    "patience": [
        ("jp", 0.3, False),
        ("ei", 0.25, False),
        ("tf", 0.25, False),
        ("sn", 0.2, True),
    ],
}

# ---------------------------------------------------------------------------
# Weight tables — reverse mapping (traits → Jungian)
# ---------------------------------------------------------------------------

REVERSE_JUNGIAN_WEIGHTS: dict[str, list[tuple[str, float, bool]]] = {
    "ei": [
        ("warmth", 0.25, True),
        ("assertiveness", 0.25, True),
        ("verbosity", 0.25, True),
        ("humor", 0.25, True),
    ],
    "sn": [
        ("creativity", 0.4, False),
        ("epistemic_humility", 0.2, False),
        ("rigor", 0.2, True),
        ("humor", 0.2, False),
    ],
    "tf": [
        ("empathy", 0.4, False),
        ("warmth", 0.3, False),
        ("directness", 0.3, True),
    ],
    "jp": [
        ("creativity", 0.25, False),
        ("patience", 0.25, False),
        ("rigor", 0.25, True),
        ("humor", 0.25, False),
    ],
}

# ---------------------------------------------------------------------------
# Jungian 16-type presets
# ---------------------------------------------------------------------------
# Preset keys are lowercase 4-letter type codes. Values use 0.2/0.8 (not 0/1)
# to model preference strength realistically.

JUNGIAN_PRESETS: dict[str, JungianProfile] = {
    # Analysts (IN_T/P)
    "intj": JungianProfile(ei=0.8, sn=0.8, tf=0.2, jp=0.2),
    "intp": JungianProfile(ei=0.8, sn=0.8, tf=0.2, jp=0.8),
    "entj": JungianProfile(ei=0.2, sn=0.8, tf=0.2, jp=0.2),
    "entp": JungianProfile(ei=0.2, sn=0.8, tf=0.2, jp=0.8),
    # Diplomats (IN_F/P)
    "infj": JungianProfile(ei=0.8, sn=0.8, tf=0.8, jp=0.2),
    "infp": JungianProfile(ei=0.8, sn=0.8, tf=0.8, jp=0.8),
    "enfj": JungianProfile(ei=0.2, sn=0.8, tf=0.8, jp=0.2),
    "enfp": JungianProfile(ei=0.2, sn=0.8, tf=0.8, jp=0.8),
    # Sentinels (IS_T/F)
    "istj": JungianProfile(ei=0.8, sn=0.2, tf=0.2, jp=0.2),
    "isfj": JungianProfile(ei=0.8, sn=0.2, tf=0.8, jp=0.2),
    "estj": JungianProfile(ei=0.2, sn=0.2, tf=0.2, jp=0.2),
    "esfj": JungianProfile(ei=0.2, sn=0.2, tf=0.8, jp=0.2),
    # Explorers (IS_T/P)
    "istp": JungianProfile(ei=0.8, sn=0.2, tf=0.2, jp=0.8),
    "isfp": JungianProfile(ei=0.8, sn=0.2, tf=0.8, jp=0.8),
    "estp": JungianProfile(ei=0.2, sn=0.2, tf=0.2, jp=0.8),
    "esfp": JungianProfile(ei=0.2, sn=0.2, tf=0.8, jp=0.8),
}

# ---------------------------------------------------------------------------
# Jungian role recommendations
# ---------------------------------------------------------------------------
# Maps agent role categories to recommended Jungian types with descriptions.

JUNGIAN_ROLE_RECOMMENDATIONS: dict[str, list[tuple[str, str]]] = {
    "strategic_analysis": [
        ("intj", "Strategic, independent, long-range planning"),
        ("entj", "Decisive leadership, systems thinking"),
    ],
    "data_science": [
        ("intp", "Analytical, theory-driven exploration"),
        ("intj", "Methodical, pattern recognition"),
    ],
    "creative_writing": [
        ("infp", "Imaginative, value-driven storytelling"),
        ("enfp", "Enthusiastic, idea-rich brainstorming"),
    ],
    "customer_support": [
        ("esfj", "Warm, attentive, detail-oriented care"),
        ("isfj", "Patient, reliable, thorough help"),
    ],
    "project_management": [
        ("entj", "Organized, goal-driven leadership"),
        ("estj", "Process-oriented, dependable execution"),
    ],
    "legal_compliance": [
        ("istj", "Rule-following, precise, thorough"),
        ("intj", "Strategic risk assessment"),
    ],
    "teaching_tutoring": [
        ("enfj", "Inspiring, empathetic guidance"),
        ("infj", "Insightful, personalized mentoring"),
    ],
    "engineering": [
        ("istp", "Hands-on problem solving, pragmatic"),
        ("intp", "Systematic debugging, first-principles"),
    ],
    "sales_persuasion": [
        ("entp", "Quick-thinking, persuasive debater"),
        ("estp", "Action-oriented, adaptable closer"),
    ],
    "counseling_coaching": [
        ("infj", "Deep empathy, pattern insight"),
        ("enfp", "Enthusiastic encouragement, possibility-focused"),
    ],
}


# ---------------------------------------------------------------------------
# Forward mapping functions
# ---------------------------------------------------------------------------


def _apply_weights(
    weights: dict[str, list[tuple[str, float, bool]]],
    values: dict[str, float],
) -> dict[str, float]:
    """Apply weighted-sum formulas to compute trait values.

    Parameters
    ----------
    weights:
        Mapping of trait_name -> list of (dimension, weight, complement).
    values:
        Mapping of dimension_name -> float score (0-1).

    Returns
    -------
    dict of trait_name -> computed float value, clamped to [0, 1].
    """
    result: dict[str, float] = {}
    for trait, components in weights.items():
        total = 0.0
        for dim, weight, complement in components:
            raw = values[dim]
            val = (1.0 - raw) if complement else raw
            total += val * weight
        # Clamp to [0, 1] for safety (should be in range with valid weights)
        result[trait] = round(max(0.0, min(1.0, total)), 4)
    return result


def ocean_to_traits(profile: OceanProfile) -> dict[str, float]:
    """Map an OCEAN (Big Five) profile to the 10 custom personality traits."""
    values = {
        "openness": profile.openness,
        "conscientiousness": profile.conscientiousness,
        "extraversion": profile.extraversion,
        "agreeableness": profile.agreeableness,
        "neuroticism": profile.neuroticism,
    }
    return _apply_weights(OCEAN_WEIGHTS, values)


def disc_to_traits(profile: DiscProfile) -> dict[str, float]:
    """Map a DISC profile to the 10 custom personality traits."""
    values = {
        "dominance": profile.dominance,
        "influence": profile.influence,
        "steadiness": profile.steadiness,
        "conscientiousness": profile.conscientiousness,
    }
    return _apply_weights(DISC_WEIGHTS, values)


def jungian_to_traits(profile: JungianProfile) -> dict[str, float]:
    """Map a Jungian 16-type profile to the 10 custom personality traits."""
    values = {
        "ei": profile.ei,
        "sn": profile.sn,
        "tf": profile.tf,
        "jp": profile.jp,
    }
    return _apply_weights(JUNGIAN_WEIGHTS, values)


# ---------------------------------------------------------------------------
# Reverse mapping functions
# ---------------------------------------------------------------------------


def _traits_to_values(traits: PersonalityTraits) -> dict[str, float]:
    """Build trait values dict with 0.5 defaults for undefined traits."""
    defined = traits.defined_traits()
    return {name: defined.get(name, 0.5) for name in TRAIT_ORDER}


def traits_to_ocean(traits: PersonalityTraits) -> OceanProfile:
    """Approximate reverse mapping from custom traits to OCEAN profile.

    Uses weighted-sum formulas from the AgentGov spec. The result is an
    approximation — a round-trip (ocean → traits → ocean) will not be exact.
    """
    ocean_vals = _apply_weights(REVERSE_OCEAN_WEIGHTS, _traits_to_values(traits))
    return OceanProfile(**ocean_vals)


def traits_to_disc(traits: PersonalityTraits) -> DiscProfile:
    """Approximate reverse mapping from custom traits to DISC profile.

    Uses weighted-sum formulas derived from the forward DISC mapping.
    The result is an approximation.
    """
    disc_vals = _apply_weights(REVERSE_DISC_WEIGHTS, _traits_to_values(traits))
    return DiscProfile(**disc_vals)


def traits_to_jungian(traits: PersonalityTraits) -> JungianProfile:
    """Approximate reverse mapping from custom traits to Jungian profile.

    Uses weighted-sum formulas. The result is an approximation — a round-trip
    (jungian → traits → jungian) will not be exact.
    """
    jungian_vals = _apply_weights(REVERSE_JUNGIAN_WEIGHTS, _traits_to_values(traits))
    return JungianProfile(**jungian_vals)


# ---------------------------------------------------------------------------
# Preset lookup
# ---------------------------------------------------------------------------


def get_disc_preset(name: str) -> DiscProfile:
    """Look up a named DISC preset.

    Raises ``KeyError`` if the preset name is not found.
    """
    if name not in DISC_PRESETS:
        available = ", ".join(sorted(DISC_PRESETS.keys()))
        raise KeyError(f"Unknown DISC preset '{name}'. Available: {available}")
    return DISC_PRESETS[name]


def list_disc_presets() -> dict[str, DiscProfile]:
    """Return all available DISC presets."""
    return dict(DISC_PRESETS)


def get_jungian_preset(name: str) -> JungianProfile:
    """Look up a named Jungian type preset.

    Accepts case-insensitive type codes (e.g. 'INTJ', 'intj').
    Raises ``KeyError`` if the preset name is not found.
    """
    key = name.lower()
    if key not in JUNGIAN_PRESETS:
        available = ", ".join(sorted(JUNGIAN_PRESETS.keys()))
        raise KeyError(f"Unknown Jungian preset '{name}'. Available: {available}")
    return JUNGIAN_PRESETS[key]


def list_jungian_presets() -> dict[str, JungianProfile]:
    """Return all available Jungian 16-type presets."""
    return dict(JUNGIAN_PRESETS)


def _find_closest_in_presets(
    profile: BaseModel,
    presets: dict[str, BaseModel],
) -> tuple[str, float]:
    """Find the closest preset by Euclidean distance on all numeric fields.

    Returns (preset_name, distance).
    """
    profile_vals = list(profile.model_dump().values())
    best_name = ""
    best_dist = float("inf")
    for name, preset in presets.items():
        preset_vals = list(preset.model_dump().values())
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(profile_vals, preset_vals, strict=True)))
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return best_name, best_dist


def closest_disc_preset(disc: DiscProfile) -> tuple[str, float]:
    """Find the closest DISC preset by Euclidean distance.

    Returns (preset_name, distance).
    """
    return _find_closest_in_presets(disc, DISC_PRESETS)


def closest_jungian_type(profile: JungianProfile) -> str:
    """Find the closest Jungian type preset by Euclidean distance."""
    name, _ = _find_closest_in_presets(profile, JUNGIAN_PRESETS)
    return name.upper()


def get_jungian_role_recommendations(
    role_category: str,
) -> list[tuple[str, str]]:
    """Look up recommended Jungian types for an agent role category.

    Raises ``KeyError`` if the role category is not found.
    """
    key = role_category.lower().replace("-", "_").replace(" ", "_")
    if key not in JUNGIAN_ROLE_RECOMMENDATIONS:
        available = ", ".join(sorted(JUNGIAN_ROLE_RECOMMENDATIONS.keys()))
        raise KeyError(f"Unknown role category '{role_category}'. Available: {available}")
    return JUNGIAN_ROLE_RECOMMENDATIONS[key]


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------


def compute_personality_traits(personality: Personality) -> PersonalityTraits:
    """Compute the final personality traits from a Personality object.

    Routing logic by mode:

    - **custom**: returns ``personality.traits`` as-is
    - **ocean**: computes traits from ``personality.profile.ocean``
    - **disc**: computes traits from ``personality.profile.disc`` (or preset)
    - **hybrid**: computes from framework, then applies explicit overrides

    Returns a new ``PersonalityTraits`` instance with all 10 traits populated.
    """
    profile = personality.profile
    mode = profile.mode

    if mode == PersonalityMode.CUSTOM:
        return personality.traits

    # Compute base traits from framework
    if mode == PersonalityMode.OCEAN:
        if profile.ocean is None:
            raise ValueError("OCEAN mode requires an ocean profile to be set")
        computed = ocean_to_traits(profile.ocean)

    elif mode == PersonalityMode.DISC:
        disc = profile.disc
        if disc is None and profile.disc_preset:
            disc = get_disc_preset(profile.disc_preset)
        if disc is None:
            raise ValueError("DISC mode requires a disc profile or disc_preset to be set")
        computed = disc_to_traits(disc)

    elif mode == PersonalityMode.JUNGIAN:
        jungian = profile.jungian
        if jungian is None and profile.jungian_preset:
            jungian = get_jungian_preset(profile.jungian_preset)
        if jungian is None:
            raise ValueError("JUNGIAN mode requires a jungian profile or jungian_preset")
        computed = jungian_to_traits(jungian)

    elif mode == PersonalityMode.HYBRID:
        # HYBRID mode computes base traits from a framework profile, then applies
        # explicit trait overrides on top (see override_priority below).
        # Precedence: OCEAN > DISC > Jungian (first available wins).
        if profile.ocean is not None:
            computed = ocean_to_traits(profile.ocean)
        elif profile.disc is not None:
            computed = disc_to_traits(profile.disc)
        elif profile.disc_preset:
            disc = get_disc_preset(profile.disc_preset)
            computed = disc_to_traits(disc)
        elif profile.jungian is not None:
            computed = jungian_to_traits(profile.jungian)
        elif profile.jungian_preset:
            jungian = get_jungian_preset(profile.jungian_preset)
            computed = jungian_to_traits(jungian)
        else:
            # Should not happen — validated at model level
            computed = {}
    else:
        return personality.traits

    # For hybrid mode, apply explicit overrides
    if mode == PersonalityMode.HYBRID:
        explicit = personality.traits.defined_traits()
        if profile.override_priority == OverridePriority.EXPLICIT_WINS:
            # Explicit overrides win over computed values
            computed.update(explicit)
        else:
            # Framework wins — only fill in missing traits from explicit
            for k, v in explicit.items():
                if k not in computed:
                    computed[k] = v

    return PersonalityTraits(**computed)
