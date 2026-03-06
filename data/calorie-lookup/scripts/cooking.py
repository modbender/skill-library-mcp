"""Cooking method modifier table for nutrition adjustments.

Based on USDA Table of Nutrient Retention Factors for Home Cooking
(https://www.ars.usda.gov/ARSUserFiles/80400525/Data/retn/retn06.pdf)

Modifiers adjust nutrition data based on cooking method (e.g., frying adds oil
and calories, grilling removes fat through dripping). Each method multiplier
reflects typical losses or gains of specific nutrients.

Nutrient keys: kcal, protein_g, carb_g, fat_g, fiber_g (from core.py)
"""

from typing import Dict


COOKING_MODIFIERS: Dict[str, Dict[str, float]] = {
    "raw": {
        "kcal": 1.0,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 1.0,
        "fiber_g": 1.0,
    },
    "steamed": {
        "kcal": 1.0,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 1.0,
        "fiber_g": 1.0,
    },
    "boiled": {
        "kcal": 0.9,
        "protein_g": 0.95,
        "carb_g": 0.85,
        "fat_g": 0.9,
        "fiber_g": 0.85,
    },
    "grilled": {
        "kcal": 0.95,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 0.85,
        "fiber_g": 1.0,
    },
    "baked": {
        "kcal": 0.95,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 0.9,
        "fiber_g": 1.0,
    },
    "roasted": {
        "kcal": 0.95,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 0.9,
        "fiber_g": 1.0,
    },
    "fried": {
        "kcal": 1.3,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 1.5,
        "fiber_g": 1.0,
    },
    "deep_fried": {
        "kcal": 1.3,
        "protein_g": 1.0,
        "carb_g": 1.0,
        "fat_g": 1.5,
        "fiber_g": 1.0,
    },
}


def _round(x: float) -> float:
    """Round to 1 decimal place, matching core.py pattern."""
    return round(float(x), 1)


def apply_cooking_modifier(
    nutrients: Dict[str, float], cooking_method: str
) -> Dict[str, float]:
    """Apply cooking method modifier to nutrient values.

    Args:
        nutrients: Dict with keys: kcal, protein_g, carb_g, fat_g, fiber_g
        cooking_method: Cooking method name (case-insensitive, whitespace-stripped)

    Returns:
        New dict with modified nutrient values, rounded to 1 decimal.
        If cooking_method is unknown, returns unchanged nutrients dict.

    Example:
        >>> base = {'kcal': 100, 'protein_g': 20, 'carb_g': 10, 'fat_g': 5, 'fiber_g': 2}
        >>> fried = apply_cooking_modifier(base, 'fried')
        >>> fried['kcal']
        130.0
        >>> fried['fat_g']
        7.5
        >>> base['kcal']  # original unchanged
        100
    """
    # Normalize method lookup: case-insensitive, strip whitespace
    method = cooking_method.lower().strip()

    # Fail open: unknown method returns unchanged nutrients
    if method not in COOKING_MODIFIERS:
        return dict(nutrients)

    # Get modifier dict for this method
    modifiers = COOKING_MODIFIERS[method]

    # Apply modifier to each nutrient, return new dict
    result = {}
    for key, value in nutrients.items():
        multiplier = modifiers.get(key, 1.0)
        result[key] = _round(value * multiplier)

    return result
