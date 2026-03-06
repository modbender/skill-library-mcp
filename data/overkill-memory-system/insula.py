#!/usr/bin/env python3
"""
Insula - Internal State Management
Implements the brain's insula function for internal state tracking

Manages: energy, curiosity, mood, fatigue
State affects search result ranking and presentation
"""

import json
import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Any

# Storage path
MEMORY_BASE = Path.home() / ".openclaw" / "memory"
INTERNAL_STATE_FILE = MEMORY_BASE / "internal_state.json"

# Ensure directory exists
MEMORY_BASE.mkdir(parents=True, exist_ok=True)

# Valid state values
VALID_ENERGY = {"low", "medium", "high"}
VALID_CURIOSITY = {"low", "medium", "high"}
VALID_MOOD = {"productive", "tired", "frustrated", "neutral"}
VALID_FATIGUE = {"0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"}


class InternalState:
    """
    Manages internal state (energy, curiosity, mood, fatigue).
    Inspired by the brain's insula - internal awareness.
    """
    
    def __init__(self):
        self._state = {
            "energy": "medium",      # low, medium, high
            "curiosity": "medium",   # low, medium, high
            "mood": "neutral",       # productive, tired, frustrated, neutral
            "fatigue": 0.3           # 0.0 - 1.0
        }
        self._load()
    
    def _load(self):
        """Load state from file"""
        if INTERNAL_STATE_FILE.exists():
            try:
                with open(INTERNAL_STATE_FILE, 'r') as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults on error
    
    def _save(self):
        """Save state to file"""
        with open(INTERNAL_STATE_FILE, 'w') as f:
            json.dump(self._state, f, indent=2)
    
    def set_state(
        self,
        energy: Optional[str] = None,
        curiosity: Optional[str] = None,
        mood: Optional[str] = None,
        fatigue: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Set internal state values.
        
        Args:
            energy: low, medium, or high
            curiosity: low, medium, or high
            mood: productive, tired, frustrated, or neutral
            fatigue: 0.0 to 1.0
        
        Returns:
            Updated state dictionary
        """
        if energy is not None:
            if energy not in VALID_ENERGY:
                raise ValueError(f"Invalid energy: {energy}. Must be one of {VALID_ENERGY}")
            self._state["energy"] = energy
        
        if curiosity is not None:
            if curiosity not in VALID_CURIOSITY:
                raise ValueError(f"Invalid curiosity: {curiosity}. Must be one of {VALID_CURIOSITY}")
            self._state["curiosity"] = curiosity
        
        if mood is not None:
            if mood not in VALID_MOOD:
                raise ValueError(f"Invalid mood: {mood}. Must be one of {VALID_MOOD}")
            self._state["mood"] = mood
        
        if fatigue is not None:
            if not (0.0 <= fatigue <= 1.0):
                raise ValueError(f"Invalid fatigue: {fatigue}. Must be between 0.0 and 1.0")
            self._state["fatigue"] = fatigue
        
        self._save()
        return self._state.copy()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self._state.copy()
    
    def detect_state_from_context(self, conversation: str) -> Dict[str, Any]:
        """
        Auto-detect state from recent conversation text.
        
        Uses keyword matching to infer internal state.
        
        Args:
            conversation: Recent conversation text
        
        Returns:
            Detected state dictionary
        """
        text = conversation.lower()
        
        detected = {}
        
        # Energy detection
        energy_indicators = {
            "high": ["energetic", "pumped", "motivated", "let's go", "excited", "can't wait", "ready to", "fired up"],
            "low": ["tired", "exhausted", "drained", "wiped", "beat", "no energy", "exhausted", "burned out"],
            "medium": []
        }
        
        for level, keywords in energy_indicators.items():
            if any(kw in text for kw in keywords):
                detected["energy"] = level
                break
        
        # Curiosity detection
        curiosity_indicators = {
            "high": ["curious", "wondering", "how does", "why does", "what if", "tell me more", "interesting", "explore", "learn more"],
            "low": ["don't care", "not interested", "skip", "boring", "whatever", "already know"],
            "medium": []
        }
        
        for level, keywords in curiosity_indicators.items():
            if any(kw in text for kw in keywords):
                detected["curiosity"] = level
                break
        
        # Mood detection
        mood_indicators = {
            "productive": ["working", "focused", "getting things done", "accomplished", "making progress", "in the zone"],
            "tired": ["tired", "exhausted", "sleepy", "drowsy", "need rest", "burned out", "drained"],
            "frustrated": ["frustrated", "annoyed", "stuck", "aggravated", "irritated", "fed up", "can't figure out"],
            "neutral": []
        }
        
        for mood, keywords in mood_indicators.items():
            if any(kw in text for kw in keywords):
                detected["mood"] = mood
                break
        
        # Fatigue detection (continuous 0.0-1.0)
        fatigue_indicators = [
            (["completely exhausted", "dead tired", "wiped out"], 0.9),
            (["very tired", "really tired", "exhausted"], 0.7),
            (["tired", "fatigued", "drained"], 0.5),
            (["somewhat tired", "a bit tired"], 0.3),
            (["fine", "okay", "rested"], 0.1),
        ]
        
        for keywords, level in fatigue_indicators:
            if any(kw in text for kw in keywords):
                detected["fatigue"] = level
                break
        
        # Apply detected values
        if detected:
            self.set_state(**detected)
        
        return detected
    
    def adjust_results_for_state(self, results: List[Dict], state: Optional[Dict] = None) -> List[Dict]:
        """
        Adjust search results based on current internal state.
        
        Effects:
        - Low energy → Prefer shorter, simpler results
        - High curiosity → Boost novel/exploratory results
        - Tired mood → Skip complex reasoning
        - High fatigue → Reduce result count
        
        Args:
            results: List of search result dictionaries
            state: Optional state dict (uses current state if not provided)
        
        Returns:
            Adjusted and filtered results
        """
        if state is None:
            state = self._state
        
        adjusted = []
        
        for result in results:
            score = result.get("score", 1.0)
            content = result.get("content", "")
            result_type = result.get("type", "unknown")
            
            # Low energy: Prefer shorter results (simpler)
            if state["energy"] == "low":
                content_length = len(content)
                if content_length > 500:
                    score *= 0.7  # Penalize long content
                elif content_length < 200:
                    score *= 1.2  # Boost short content
            
            # High curiosity: Boost novel/exploratory results
            if state["curiosity"] == "high":
                novel_indicators = ["new", "explore", "discover", "learn", "interesting", "unknown"]
                if any(ind in content.lower() for ind in novel_indicators):
                    score *= 1.3
            
            # Tired mood: Skip complex reasoning results
            if state["mood"] == "tired":
                complex_indicators = ["analysis", "complex", "detailed", "reasoning", "step by step"]
                if any(ind in content.lower() for ind in complex_indicators):
                    score *= 0.5
            
            # High fatigue: Reduce result count
            fatigue = state["fatigue"]
            if fatigue > 0.7:
                if len(content) > 300:
                    score *= 0.6
            elif fatigue > 0.5:
                if len(content) > 500:
                    score *= 0.7
            
            # Frustrated mood: Boost helpful/solution results
            if state["mood"] == "frustrated":
                helpful_indicators = ["solution", "fix", "help", "answer", "resolved"]
                if any(ind in content.lower() for ind in helpful_indicators):
                    score *= 1.4
            
            # Productive mood: Boost detailed/comprehensive results
            if state["mood"] == "productive":
                if len(content) > 200:
                    score *= 1.1  # Reward thoroughness
            
            result = result.copy()
            result["score"] = score
            adjusted.append(result)
        
        # Sort by adjusted score
        adjusted.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Reduce result count based on fatigue
        max_results = len(adjusted)
        if state["fatigue"] > 0.7:
            max_results = min(3, len(adjusted))
        elif state["fatigue"] > 0.5:
            max_results = min(5, len(adjusted))
        elif state["fatigue"] < 0.3:
            max_results = min(10, len(adjusted))
        
        return adjusted[:max_results]


# Singleton instance
_state_instance = None


def get_state() -> InternalState:
    """Get the singleton InternalState instance"""
    global _state_instance
    if _state_instance is None:
        _state_instance = InternalState()
    return _state_instance


if __name__ == "__main__":
    # CLI test
    state = InternalState()
    print("Current state:", state.get_state())
    
    # Test detection
    test_text = "I'm feeling really tired but curious about how this works"
    detected = state.detect_state_from_context(test_text)
    print("Detected:", detected)
    print("Current state:", state.get_state())
