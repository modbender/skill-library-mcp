"""
Affect Correlation Analysis
============================
Analyzes patterns between inputs and affect state changes.

Provides:
- AffectCorrelation: Tracks and analyzes input→state correlations
- Pattern detection utilities

Author: NIMA Core Team
Date: Feb 13, 2026
"""

import math
import threading
from collections import deque
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from time import time as get_time


# Panksepp 7-affect order
AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]
AFFECT_INDEX = {name: i for i, name in enumerate(AFFECTS)}


@dataclass
class StateTransition:
    """Records a state transition for correlation analysis."""
    input_affects: Dict[str, float]  # What was input
    from_values: np.ndarray           # State before
    to_values: np.ndarray             # State after
    timestamp: float                  # When it happened
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_affects": self.input_affects,
            "from_values": self.from_values.tolist(),
            "to_values": self.to_values.tolist(),
            "timestamp": self.timestamp,
        }


class AffectCorrelation:
    """
    Analyzes correlation between input patterns and affect states.
    
    Tracks transitions and identifies which inputs trigger which affects.
    Useful for:
    - Understanding what inputs drive emotional responses
    - Learning which affects are most sensitive
    - Detecting patterns over time
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize correlation tracker.
        
        Args:
            window_size: Number of recent transitions to analyze
        """
        self.window_size = window_size
        self._lock = threading.RLock()
        # Use deque for O(1) append/popleft instead of O(n) list operations
        self._transitions: deque = deque(maxlen=window_size)
    
    def record_transition(
        self,
        input_affects: Dict[str, float],
        from_state: np.ndarray,
        to_state: np.ndarray
    ) -> None:
        """
        Record a state transition.
        
        Args:
            input_affects: Dict of affect_name -> intensity that was input
            from_state: State before the input
            to_state: State after the input
        """
        transition = StateTransition(
            input_affects=input_affects.copy(),
            from_values=from_state.copy(),
            to_values=to_state.copy(),
            timestamp=get_time()
        )
        
        # deque with maxlen auto-prunes when full (O(1))
        with self._lock:
            self._transitions.append(transition)
    
    def analyze_triggers(
        self,
        target_affect: str,
        min_samples: int = 3,
        min_correlation: float = 0.2
    ) -> List[Tuple[str, float, int]]:
        """
        Analyze which input patterns trigger a target affect.
        
        Args:
            target_affect: Name of affect to analyze (e.g., "CARE", "FEAR")
            min_samples: Minimum samples needed for correlation
            min_correlation: Minimum correlation to include in results
        
        Returns:
            List of (input_pattern, correlation_strength, sample_count)
            sorted by correlation strength
        """
        target_idx = AFFECT_INDEX.get(target_affect.upper())
        if target_idx is None:
            return []
        
        # Collect correlation data under lock
        correlations: Dict[str, List[Tuple[float, float]]] = {}
        
        with self._lock:
            # Snapshot transitions for thread-safe iteration
            transitions = list(self._transitions)
        
        for trans in transitions:
            # Calculate change in target affect
            delta = trans.to_values[target_idx] - trans.from_values[target_idx]
            
            # Only analyze increases
            if delta <= 0:
                continue
            
            # Correlate each input affect with this change
            for input_name, input_val in trans.input_affects.items():
                if input_val < 0.1:  # Threshold for significance
                    continue
                
                if input_name not in correlations:
                    correlations[input_name] = []
                
                correlations[input_name].append((input_val, delta))
        
        # Calculate correlation strength for each input
        results: List[Tuple[str, float, int]] = []
        
        for input_name, pairs in correlations.items():
            if len(pairs) < min_samples:
                continue
            
            inputs = [p[0] for p in pairs]
            deltas = [p[1] for p in pairs]
            
            # Correlation: avg change / avg input intensity
            avg_input = sum(inputs) / len(inputs)
            avg_delta = sum(deltas) / len(deltas)
            
            # Normalized correlation strength
            strength = avg_delta / (avg_input + 0.01)
            
            if strength > min_correlation:
                results.append((input_name, round(strength, 3), len(pairs)))
        
        # Sort by strength
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def analyze_sensitivity(self) -> Dict[str, float]:
        """
        Analyze which affects are most sensitive to inputs.
        
        Returns:
            Dict mapping affect name to sensitivity score (higher = more reactive)
        """
        sensitivities: Dict[str, List[float]] = {a: [] for a in AFFECTS}
        
        with self._lock:
            transitions = list(self._transitions)
        
        for trans in transitions:
            for i, affect in enumerate(AFFECTS):
                delta = abs(trans.to_values[i] - trans.from_values[i])
                sensitivities[affect].append(delta)
        
        # Calculate average change per affect
        result = {}
        for affect, changes in sensitivities.items():
            if changes:
                result[affect] = round(sum(changes) / len(changes), 4)
            else:
                result[affect] = 0.0
        
        return result
    
    def get_input_distribution(self) -> Dict[str, int]:
        """
        Get distribution of input affects.
        
        Returns:
            Dict mapping input affect to count
        """
        distribution: Dict[str, int] = {}
        
        with self._lock:
            transitions = list(self._transitions)
        
        for trans in transitions:
            for affect in trans.input_affects.keys():
                distribution[affect] = distribution.get(affect, 0) + 1
        
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def get_recent_transitions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent transitions for debugging/display.
        
        Args:
            count: Maximum number to return
        
        Returns:
            List of transition summaries
        """
        with self._lock:
            recent = list(self._transitions)[-count:] if self._transitions else []
        
        result = []
        for trans in recent:
            # Find dominant change
            deltas = trans.to_values - trans.from_values
            max_idx = int(np.argmax(np.abs(deltas)))
            dominant_change = (AFFECTS[max_idx], float(deltas[max_idx]))
            
            result.append({
                "inputs": trans.input_affects,
                "dominant_change": dominant_change,
                "timestamp": trans.timestamp,
            })
        
        return result
    
    def clear(self) -> None:
        """Clear all transition history."""
        with self._lock:
            self._transitions.clear()
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._transitions)
    
    def __repr__(self) -> str:
        with self._lock:
            return f"AffectCorrelation({len(self._transitions)} transitions)"


def detect_emotional_patterns(
    history: 'AffectHistory',
    min_occurrences: int = 3
) -> List[Dict[str, Any]]:
    """
    Detect patterns in emotional history.
    
    Args:
        history: AffectHistory instance
        min_occurrences: Minimum times pattern must occur
    
    Returns:
        List of detected patterns
    """
    patterns = []
    timeline = history.get_timeline(duration_hours=168)  # 1 week
    
    if len(timeline) < min_occurrences:
        return patterns
    
    # Pattern 1: Dominant affect streaks
    streaks: Dict[str, int] = {}
    for snapshot in timeline:
        affect = snapshot.dominant[0]
        streaks[affect] = streaks.get(affect, 0) + 1
    
    for affect, count in streaks.items():
        if count >= min_occurrences:
            patterns.append({
                "type": "dominant_streak",
                "affect": affect,
                "count": count,
                "description": f"'{affect}' dominant {count} times in past week"
            })
    
    # Pattern 2: High deviation events
    high_deviation = [s for s in timeline if s.deviation > 0.3]
    if len(high_deviation) >= min_occurrences:
        avg_deviation = sum(s.deviation for s in high_deviation) / len(high_deviation)
        patterns.append({
            "type": "high_deviation",
            "count": len(high_deviation),
            "avg_deviation": round(avg_deviation, 3),
            "description": f"{len(high_deviation)} high-emotion events (avg deviation: {avg_deviation:.2f})"
        })
    
    # Pattern 3: Source patterns
    source_counts = history.count_sources(168)
    dominant_source = max(source_counts.items(), key=lambda x: x[1], default=(None, 0))
    if dominant_source[1] >= min_occurrences:
        patterns.append({
            "type": "frequent_source",
            "source": dominant_source[0],
            "count": dominant_source[1],
            "description": f"'{dominant_source[0]}' triggered {dominant_source[1]} emotional events"
        })
    
    return patterns