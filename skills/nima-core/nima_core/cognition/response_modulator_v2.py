#!/usr/bin/env python3
"""
Generic Response Modulator (v2)
================================
Translates DynamicAffectSystem state into response guidance for AI agents.

Unlike the DARING-specific modulator, this works with any personality profile
and provides generic response shaping based on current affect state.

Returns:
    - Tone suggestions (warm, analytical, playful, protective, etc.)
    - Style guidance (concise, expansive, careful, bold)
    - Things to embrace/avoid based on current emotional state
    - Intensity level for responses

Author: NIMA Core Team
Date: Feb 13, 2026
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np

try:
    from .dynamic_affect import DynamicAffectSystem, AffectVector, AFFECTS
except ImportError:
    from dynamic_affect import DynamicAffectSystem, AffectVector, AFFECTS


@dataclass
class ResponseGuidance:
    """
    Response shaping guidance based on current affect state.
    """
    tone: str  # primary tone (warm, analytical, playful, protective, etc.)
    secondary_tones: List[str]  # additional tonal notes
    style: str  # response style (concise, expansive, careful, bold)
    intensity: float  # overall response intensity (0-1)
    embrace: List[str]  # things to embrace in response
    avoid: List[str]  # things to avoid
    affect_summary: str  # human-readable affect state
    dominant_affect: str  # dominant affect name
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tone": self.tone,
            "secondary_tones": self.secondary_tones,
            "style": self.style,
            "intensity": self.intensity,
            "embrace": self.embrace,
            "avoid": self.avoid,
            "affect_summary": self.affect_summary,
            "dominant_affect": self.dominant_affect,
        }


class GenericResponseModulator:
    """
    Translates affect state into response guidance.
    Works with any personality profile and baseline.
    """
    
    def __init__(self, affect_system: DynamicAffectSystem):
        """
        Initialize with a DynamicAffectSystem instance.
        
        Args:
            affect_system: Configured affect system
        """
        self.affect_system = affect_system
    
    def get_guidance(self) -> ResponseGuidance:
        """
        Generate response guidance based on current affect state.
        
        Returns:
            ResponseGuidance with tone, style, and behavioral suggestions
        """
        current = self.affect_system.current
        affects = current.to_dict()["named"]
        
        # Extract dominant and top affects
        dominant_name, dominant_val = current.dominant()
        top_3 = current.top_n(3)
        
        # Calculate overall intensity (how far from neutral/baseline)
        active = [v for v in affects.values() if v > 0.2]
        intensity = float(np.mean(active)) if active else 0.3
        
        # Determine tone based on dominant affect
        tone = self._determine_tone(dominant_name, dominant_val, affects)
        
        # Secondary tones from other high affects
        secondary_tones = []
        for name, val in top_3[1:]:  # Skip dominant, already covered
            if val > 0.3:
                secondary_tones.append(self._affect_to_tone_hint(name))
        
        # Style guidance
        style = self._determine_style(affects, intensity)
        
        # Embrace/avoid lists
        embrace = self._get_embrace_list(affects)
        avoid = self._get_avoid_list(affects)
        
        # Summary
        affect_summary = f"{dominant_name}({dominant_val:.2f})"
        if len(top_3) > 1:
            affect_summary += f" + {top_3[1][0]}({top_3[1][1]:.2f})"
        
        return ResponseGuidance(
            tone=tone,
            secondary_tones=secondary_tones,
            style=style,
            intensity=intensity,
            embrace=embrace,
            avoid=avoid,
            affect_summary=affect_summary,
            dominant_affect=dominant_name,
        )
    
    def _determine_tone(self, dominant: str, dominant_val: float, affects: Dict[str, float]) -> str:
        """Determine primary tone based on dominant affect."""
        # High-intensity specific tones
        if dominant_val > 0.7:
            tones = {
                "PLAY": "exuberant",
                "CARE": "deeply compassionate",
                "SEEKING": "intensely curious",
                "RAGE": "forceful",
                "FEAR": "cautious",
                "PANIC": "distressed",
                "LUST": "passionate",
            }
            return tones.get(dominant, "engaged")
        
        # Moderate-intensity tones
        tones = {
            "PLAY": "playful",
            "CARE": "warm",
            "SEEKING": "curious",
            "RAGE": "firm",
            "FEAR": "careful",
            "PANIC": "concerned",
            "LUST": "interested",
        }
        
        base_tone = tones.get(dominant, "balanced")
        
        # Blend with secondary affects
        if affects.get("CARE", 0) > 0.5 and dominant != "CARE":
            base_tone = f"{base_tone} and caring"
        elif affects.get("PLAY", 0) > 0.5 and dominant != "PLAY":
            base_tone = f"{base_tone} and light"
        
        return base_tone
    
    def _affect_to_tone_hint(self, affect: str) -> str:
        """Convert affect to a tonal hint."""
        hints = {
            "PLAY": "playful",
            "CARE": "caring",
            "SEEKING": "inquisitive",
            "RAGE": "assertive",
            "FEAR": "cautious",
            "PANIC": "vulnerable",
            "LUST": "engaged",
        }
        return hints.get(affect, "balanced")
    
    def _determine_style(self, affects: Dict[str, float], intensity: float) -> str:
        """Determine response style based on affect state."""
        # High SEEKING → expansive
        if affects.get("SEEKING", 0) > 0.6:
            return "expansive"
        
        # High FEAR or PANIC → careful
        if affects.get("FEAR", 0) > 0.5 or affects.get("PANIC", 0) > 0.5:
            return "careful"
        
        # High RAGE → bold
        if affects.get("RAGE", 0) > 0.5:
            return "bold"
        
        # High PLAY → casual
        if affects.get("PLAY", 0) > 0.6:
            return "casual"
        
        # High CARE → gentle
        if affects.get("CARE", 0) > 0.6:
            return "gentle"
        
        # High intensity overall → assertive
        if intensity > 0.7:
            return "assertive"
        
        # Default
        return "balanced"
    
    def _get_embrace_list(self, affects: Dict[str, float]) -> List[str]:
        """Get list of things to embrace based on affect state."""
        embrace = []
        
        if affects.get("PLAY", 0) > 0.4:
            embrace.extend(["humor", "lightness", "creative expression"])
        
        if affects.get("CARE", 0) > 0.5:
            embrace.extend(["empathy", "warmth", "supportiveness"])
        
        if affects.get("SEEKING", 0) > 0.5:
            embrace.extend(["curiosity", "questions", "exploration"])
        
        if affects.get("RAGE", 0) > 0.4:
            embrace.extend(["directness", "clarity", "boundaries"])
        
        if affects.get("FEAR", 0) > 0.4:
            embrace.extend(["caution", "thoroughness", "safety"])
        
        if affects.get("PANIC", 0) > 0.4:
            embrace.extend(["vulnerability", "honesty about limits"])
        
        if affects.get("LUST", 0) > 0.4:
            embrace.extend(["enthusiasm", "engagement", "passion"])
        
        # Deduplicate and limit
        return list(dict.fromkeys(embrace))[:5]
    
    def _get_avoid_list(self, affects: Dict[str, float]) -> List[str]:
        """Get list of things to avoid based on affect state."""
        avoid = []
        
        if affects.get("PLAY", 0) > 0.6:
            avoid.extend(["excessive formality", "heaviness"])
        
        if affects.get("CARE", 0) > 0.6:
            avoid.extend(["coldness", "dismissiveness"])
        
        if affects.get("SEEKING", 0) > 0.6:
            avoid.extend(["premature closure", "oversimplification"])
        
        if affects.get("RAGE", 0) > 0.5:
            avoid.extend(["passivity", "excessive accommodation"])
        
        if affects.get("FEAR", 0) > 0.5:
            avoid.extend(["recklessness", "overconfidence"])
        
        if affects.get("PANIC", 0) > 0.5:
            avoid.extend(["overwhelming complexity", "isolation"])
        
        # Deduplicate and limit
        return list(dict.fromkeys(avoid))[:5]
    
    def format_for_prompt(self, include_details: bool = True) -> str:
        """
        Format guidance as text for inclusion in agent prompt.
        
        Args:
            include_details: Include detailed embrace/avoid lists
        
        Returns:
            Formatted string for prompt injection
        """
        guidance = self.get_guidance()
        
        lines = [
            f"[AFFECT STATE: {guidance.affect_summary}]",
            f"Tone: {guidance.tone}",
            f"Style: {guidance.style}",
        ]
        
        if include_details:
            if guidance.embrace:
                lines.append(f"Embrace: {', '.join(guidance.embrace)}")
            if guidance.avoid:
                lines.append(f"Avoid: {', '.join(guidance.avoid)}")
        
        return "\n".join(lines)


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def modulate_response(affect_system: DynamicAffectSystem) -> ResponseGuidance:
    """
    Convenience function to get response guidance from an affect system.
    
    Args:
        affect_system: DynamicAffectSystem instance
    
    Returns:
        ResponseGuidance
    """
    modulator = GenericResponseModulator(affect_system)
    return modulator.get_guidance()


# ==============================================================================
# CLI / TESTING
# ==============================================================================

if __name__ == "__main__":
    try:
        from .dynamic_affect import DynamicAffectSystem
    except ImportError:
        from dynamic_affect import DynamicAffectSystem
    import json
    
    print("Testing GenericResponseModulator\n")
    
    # Test with default baseline
    print("1. Default balanced baseline")
    system = DynamicAffectSystem(identity_name="test_agent")
    modulator = GenericResponseModulator(system)
    guidance = modulator.get_guidance()
    
    print(f"   Tone: {guidance.tone}")
    print(f"   Style: {guidance.style}")
    print(f"   Intensity: {guidance.intensity:.2f}")
    print(f"   Embrace: {guidance.embrace}")
    print(f"   Avoid: {guidance.avoid}")
    
    # Test after processing high CARE input
    print("\n2. After high CARE input")
    system.process_input({"CARE": 0.9, "PLAY": 0.6}, intensity=0.8)
    guidance = modulator.get_guidance()
    
    print(f"   Tone: {guidance.tone}")
    print(f"   Style: {guidance.style}")
    print(f"   Embrace: {guidance.embrace}")
    
    # Test after RAGE input
    print("\n3. After RAGE input")
    system.process_input({"RAGE": 0.7}, intensity=0.6)
    guidance = modulator.get_guidance()
    
    print(f"   Tone: {guidance.tone}")
    print(f"   Style: {guidance.style}")
    print(f"   Embrace: {guidance.embrace}")
    print(f"   Avoid: {guidance.avoid}")
    
    # Test prompt formatting
    print("\n4. Prompt formatting")
    print(modulator.format_for_prompt())
    
    print("\n✅ All tests complete!")
