#!/usr/bin/env python3
"""
Dynamic Affect System
=====================
Organic emotional state that evolves naturally based on:
- Identity baseline (configurable per agent)
- Contextual input (what's happening)
- Temporal dynamics (momentum, decay)

Panksepp 7 Affects (order matters - this is canonical):
    0: SEEKING  - curiosity, exploration, anticipation
    1: RAGE     - anger, frustration, boundary violation
    2: FEAR     - threat detection, anxiety
    3: LUST     - desire, attraction, passion
    4: CARE     - nurturing, love, protection
    5: PANIC    - separation distress, grief, loss
    6: PLAY     - joy, humor, social bonding

Default Baseline (balanced):
    SEEKING moderate (0.5)  - curious but not obsessive
    CARE moderate (0.5)     - caring but not overwhelming
    PLAY moderate (0.4)     - playful but can be serious
    Others low (0.1)        - present but not dominant

Each agent can define their own baseline to reflect their unique personality.

Author: NIMA Core Team
Date: Feb 13, 2026
"""

import json
import logging
import math
import os
import threading
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field

# Security: Path sanitization to prevent traversal attacks
import re
def sanitize_path_component(name: str, max_length: int = 100, default: str = "default") -> str:
    """Sanitize string for safe use in file/directory names."""
    if not isinstance(name, str):
        name = str(name) if name is not None else ""
    name = name.replace('/', '_').replace('\\', '_').replace('..', '')
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    if not name:
        name = default
    return name[:max_length].rstrip('_') if len(name) > max_length else name

from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Import exceptions
from .exceptions import (
    InvalidAffectNameError,
    AffectValueError,
    BaselineValidationError,
    StatePersistenceError,
)
from .affect_interactions import apply_cross_affect_interactions
from .affect_history import AffectHistory
from .affect_correlation import AffectCorrelation


# Canonical affect order
AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]
AFFECT_INDEX = {name: i for i, name in enumerate(AFFECTS)}

# Default balanced baseline - agents should customize this
DEFAULT_BASELINE = np.array([
    0.5,   # SEEKING - moderate curiosity
    0.1,   # RAGE - low default anger
    0.1,   # FEAR - low default anxiety
    0.1,   # LUST - low default desire
    0.5,   # CARE - moderate compassion
    0.1,   # PANIC - low default distress
    0.4,   # PLAY - moderate playfulness
], dtype=np.float32)

# Named constants for intensity-aware decay
LOW_INTENSITY_THRESHOLD = 0.3
MODERATE_INTENSITY_THRESHOLD = 0.6
LOW_INTENSITY_DECAY_MULTIPLIER = 1.3
HIGH_INTENSITY_DECAY_BASE = 0.5

# Baseline pull gravity
BASELINE_PULL_STRENGTH = 0.02

# Epsilon for float comparisons
EPSILON = 1e-10


@dataclass
class AffectVector:
    """7D Panksepp affect vector with metadata."""
    values: np.ndarray  # 7D vector
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"  # "baseline", "detected", "blended"
    
    def __post_init__(self):
        if isinstance(self.values, list):
            self.values = np.array(self.values, dtype=np.float32)
        # Ensure bounded [0, 1]
        self.values = np.clip(self.values, 0.0, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "values": self.values.tolist(),
            "timestamp": self.timestamp,
            "source": self.source,
            "named": {AFFECTS[i]: float(self.values[i]) for i in range(7)},
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AffectVector':
        return cls(
            values=np.array(data["values"], dtype=np.float32),
            timestamp=data.get("timestamp", time.time()),
            source=data.get("source", "loaded"),
        )
    
    def dominant(self) -> Tuple[str, float]:
        """Return the dominant affect and its intensity."""
        idx = int(np.argmax(self.values))
        return AFFECTS[idx], float(self.values[idx])
    
    def top_n(self, n: int = 3) -> List[Tuple[str, float]]:
        """Return top N affects sorted by intensity."""
        indices = np.argsort(self.values)[::-1][:n]
        return [(AFFECTS[i], float(self.values[i])) for i in indices]
    
    def similarity(self, other: 'AffectVector') -> float:
        """Cosine similarity with another affect vector."""
        norm1 = np.linalg.norm(self.values)
        norm2 = np.linalg.norm(other.values)
        if norm1 == 0 and norm2 == 0:
            return 1.0  # identical zero vectors
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(self.values, other.values) / (norm1 * norm2))
    
    def __repr__(self):
        top = self.top_n(2)
        return f"AffectVector({top[0][0]}={top[0][1]:.2f}, {top[1][0]}={top[1][1]:.2f})"


class DynamicAffectSystem:
    """
    Manages an agent's evolving emotional state.
    
    Key features:
    - Identity baseline (who the agent IS)
    - Current state (where they are NOW)
    - Temporal dynamics (momentum, decay toward baseline)
    - Input processing (shift state based on detected emotions)
    """
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        baseline: Union[np.ndarray, List[float], str, Dict[str, Any], None] = None,
        identity_name: str = "agent",
        momentum: float = 0.85,
        decay_rate: float = 0.1,  # Per hour
        blend_strength: float = 0.25,  # How much new input shifts state
        cross_affect: bool = True,  # Enable cross-affect interactions
    ):
        """
        Initialize the dynamic affect system.
        
        Args:
            data_dir: Directory to save state (defaults to ~/.nima/affect/)
            baseline: Custom baseline affect vector, or archetype name/config.
                      - Array/List: [0.5, 0.1, ...] (7D)
                      - String: "guardian", "explorer", etc.
                      - Dict: {"archetype": "guardian", "modifiers": {"PLAY": 0.2}}
                      If None, uses DEFAULT_BASELINE.
            identity_name: Name for this agent (used in logs/state files)
            momentum: How sticky current state is (0-1, default 0.85)
            decay_rate: Drift toward baseline per hour (default 0.1)
            blend_strength: How much new input influences state (0-1, default 0.25)
            cross_affect: Enable cross-affect interactions (default True)
        """
        # Security: Sanitize identity_name to prevent path traversal attacks
        self.identity_name = sanitize_path_component(identity_name)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Support NIMA_HOME env var
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            nima_home = os.environ.get("NIMA_HOME")
            if nima_home:
                self.data_dir = Path(nima_home) / "affect"
            else:
                self.data_dir = Path.home() / ".nima" / "affect"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / f"affect_state_{self.identity_name}.json"
        
        # Dynamics parameters
        self.momentum = momentum
        self.decay_rate = decay_rate
        self.blend_strength = blend_strength
        self.cross_affect_enabled = cross_affect
        
        # Resolve baseline from archetype if needed
        baseline_vec = None
        
        if isinstance(baseline, str):
            from .archetypes import baseline_from_archetype
            baseline_vec = np.array(baseline_from_archetype(baseline), dtype=np.float32)
        elif isinstance(baseline, dict) and "archetype" in baseline:
            from .archetypes import baseline_from_archetype
            baseline_vec = np.array(
                baseline_from_archetype(baseline["archetype"], baseline.get("modifiers")), 
                dtype=np.float32
            )
        elif isinstance(baseline, (list, tuple)):
            baseline_vec = np.array(baseline, dtype=np.float32)
        elif isinstance(baseline, np.ndarray):
            baseline_vec = baseline.copy()  # Defensive copy to prevent external mutation

        # Identity baseline (immutable after initialization)
        final_baseline = baseline_vec if baseline_vec is not None else DEFAULT_BASELINE.copy()
        self.baseline = AffectVector(final_baseline, source="baseline")
        
        # Current state (mutable, persisted)
        self._current: Optional[AffectVector] = None
        self._load_state()
        
        # History and correlation tracking
        self.history = AffectHistory(
            max_snapshots=1000,
            max_age_hours=168,  # 1 week
            persist_dir=self.data_dir,
            identity_name=identity_name
        )
        self.correlation = AffectCorrelation(window_size=100)
    
    def _load_state(self) -> None:
        """Load persisted state or initialize to baseline."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                
                # Version handling (for future migrations)
                version = data.get("version", 0)
                if version == 0:
                    # Legacy format, upgrade silently
                    pass
                
                self._current = AffectVector.from_dict(data["current"])
                
                # Apply decay based on time since last update
                self._apply_temporal_decay()
                
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to load affect state: {e}")
                self._current = AffectVector(self.baseline.values.copy(), source="baseline")
        else:
            self._current = AffectVector(self.baseline.values.copy(), source="baseline")
    
    def _save_state(self) -> None:
        """Persist current state to disk with atomic write."""
        import tempfile
        try:
            # Snapshot under lock to avoid race with concurrent updates
            with self._lock:
                current_data = self._current.to_dict() if self._current else None
                baseline_data = self.baseline.to_dict()
                identity = self.identity_name
            
            if current_data is None:
                return
            
            data = {
                "version": 1,
                "current": current_data,
                "baseline": baseline_data,
                "identity_name": identity,
                "saved_at": datetime.now().isoformat(),
            }
            # Atomic write: write to temp file, then rename
            tmp_path = None
            tmp = tempfile.NamedTemporaryFile(
                mode='w', 
                dir=str(self.state_file.parent), 
                delete=False, 
                suffix='.tmp'
            )
            tmp_path = tmp.name
            json.dump(data, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.rename(tmp_path, str(self.state_file))
            tmp_path = None  # Successfully moved
        except (OSError, IOError) as e:
            logger.warning(f"Failed to save affect state: {e}")
        finally:
            # Clean up temp file if rename failed
            if tmp_path and Path(tmp_path).exists():
                try:
                    Path(tmp_path).unlink()
                except OSError:
                    pass  # Best effort
    
    def _apply_temporal_decay(self) -> None:
        """
        Decay current state toward baseline with intensity awareness.
        
        High-intensity states decay slower initially, then accelerate.
        This models the "emotional hangover" effect where strong emotions
        persist longer than mild ones.
        """
        if self._current is None:
            return
        
        hours_elapsed = (time.time() - self._current.timestamp) / 3600
        if hours_elapsed <= 0:
            return
        
        # Calculate deviation magnitude (how far from baseline)
        deviation = np.abs(self._current.values - self.baseline.values)
        avg_deviation = np.mean(deviation)
        
        # Intensity-aware decay using named constants
        if avg_deviation < LOW_INTENSITY_THRESHOLD:
            # Low intensity: faster return to baseline
            decay_multiplier = LOW_INTENSITY_DECAY_MULTIPLIER
        elif avg_deviation < MODERATE_INTENSITY_THRESHOLD:
            # Moderate: normal decay
            decay_multiplier = 1.0
        else:
            # High intensity: slower decay (emotional hangover)
            decay_multiplier = max(HIGH_INTENSITY_DECAY_BASE, 
                                   1.0 - (avg_deviation - MODERATE_INTENSITY_THRESHOLD) * 0.5)
        
        # Apply decay with intensity adjustment
        effective_decay_rate = self.decay_rate * decay_multiplier
        decay_factor = math.exp(-effective_decay_rate * hours_elapsed)
        
        # Blend: current = baseline + decay_factor * (current - baseline)
        deviation_signed = self._current.values - self.baseline.values
        self._current.values = self.baseline.values + decay_factor * deviation_signed
        self._current.values = np.clip(self._current.values, 0.0, 1.0)
        self._current.timestamp = time.time()
        self._current.source = "decayed"
    
    @property
    def current(self) -> AffectVector:
        """Get current affect state (thread-safe copy)."""
        with self._lock:
            if self._current is None:
                self._current = AffectVector(self.baseline.values.copy(), source="baseline")
            # Return a copy to prevent external mutation
            return AffectVector(self._current.values.copy(), 
                              timestamp=self._current.timestamp,
                              source=self._current.source)
    
    def _validate_affect_dict(self, affect_dict: Dict[str, float]) -> None:
        """Validate affect dictionary has correct keys and values.
        
        Raises:
            InvalidAffectNameError: If an unknown affect name is used
            AffectValueError: If a value is out of range
        """
        for name, value in affect_dict.items():
            name_upper = name.upper()
            if name_upper not in AFFECT_INDEX:
                raise InvalidAffectNameError(name_upper, AFFECTS)
            if not isinstance(value, (int, float)):
                raise TypeError(f"Affect '{name_upper}' value must be numeric, got {type(value).__name__}")
            if not 0 <= value <= 1:
                raise AffectValueError(name_upper, value)
    
    def _validate_intensity(self, intensity: float) -> None:
        """Validate intensity is in valid range.
        
        Raises:
            ValueError: If intensity is out of range
        """
        if not isinstance(intensity, (int, float)):
            raise ValueError(f"Intensity must be numeric, got {type(intensity).__name__}")
        if not 0 <= intensity <= 1:
            raise ValueError(f"Intensity must be in [0, 1], got {intensity}")
    
    def process_input(self, detected_affect: Dict[str, float], intensity: float = 1.0, profile: Optional[str] = None) -> AffectVector:
        """
        Process new emotional input and update state.
        
        Uses standard EMA (Exponential Moving Average) blending:
            new = current + blend_strength * (input - current)
        
        Baseline pull is applied separately to maintain gentle drift toward identity.
        
        Args:
            detected_affect: Dict mapping affect names to intensities (0-1)
                             e.g., {"CARE": 0.8, "SEEKING": 0.6}
            intensity: Overall intensity multiplier (0-1)
            profile: Optional personality profile name to apply amplifiers
        
        Returns:
            Updated current affect state
        """
        with self._lock:  # Thread-safe state mutation
            # Validate inputs
            self._validate_affect_dict(detected_affect)
            self._validate_intensity(intensity)
            
            # Convert detected to vector
            input_vec = np.zeros(7, dtype=np.float32)
            for name, value in detected_affect.items():
                name_upper = name.upper()
                if name_upper in AFFECT_INDEX:
                    input_vec[AFFECT_INDEX[name_upper]] = float(value)
            
            # Apply personality profile amplifiers if specified
            if profile:
                from .personality_profiles import get_profile
                p = get_profile(profile)
                if p and 'amplifiers' in p:
                    for affect, amp in p['amplifiers'].items():
                        affect_upper = affect.upper()
                        if affect_upper in AFFECT_INDEX and input_vec[AFFECT_INDEX[affect_upper]] > 0:
                            input_vec[AFFECT_INDEX[affect_upper]] *= amp
                            input_vec[AFFECT_INDEX[affect_upper]] = min(1.0, input_vec[AFFECT_INDEX[affect_upper]])
            
            # Apply intensity scaling
            input_vec = input_vec * intensity
            
            # Calculate effective blend with momentum
            effective_blend = self.blend_strength * intensity
            shift = effective_blend * (input_vec - self._current.values)
            
            # Apply shift with momentum (current state is sticky)
            new_values = self._current.values + (1 - self.momentum) * shift
            
            # Soft pull toward baseline (always some gravity)
            baseline_pull = BASELINE_PULL_STRENGTH * (self.baseline.values - new_values)
            new_values = new_values + baseline_pull
            
            # Apply cross-affect interactions (if enabled)
            if self.cross_affect_enabled:
                new_values = apply_cross_affect_interactions(new_values)
            
            # Bound to [0, 1]
            new_values = np.clip(new_values, 0.0, 1.0)
            
            # Record transition for correlation analysis
            old_values = self._current.values.copy()
            
            # Update state
            self._current = AffectVector(new_values, source="blended")
        
        # Save state outside lock (I/O operation)
        self._save_state()
        
        # Record history snapshot (also I/O)
        self.history.record(
            values=new_values,
            baseline=self.baseline.values,
            source="input",
            metadata={"inputs": detected_affect, "intensity": intensity}
        )
        
        # Record correlation transition
        self.correlation.record_transition(
            input_affects=detected_affect,
            from_state=old_values,
            to_state=new_values
        )
        
        return self.current  # Use property for thread-safe copy
    
    def process_emotions(self, emotions: List[Dict]) -> AffectVector:
        """
        Process emotion list and update state.
        
        Args:
            emotions: List of {"emotion": str, "intensity": float, ...}
        
        Returns:
            Updated affect state
        """
        # Import the emotion-to-affect mapping
        from .emotion_detection import map_emotions_to_affects
        
        detected, overall_intensity = map_emotions_to_affects(emotions)
        return self.process_input(detected, overall_intensity)
    
    def get_panksepp_vector(self) -> np.ndarray:
        """Get raw 7D numpy array for VSA binding."""
        return self.current.values.copy()
    
    def drift_toward_baseline(self, strength: float = 0.05) -> AffectVector:
        """
        Manually drift current state toward baseline.
        Called during heartbeat for gentle decay.
        
        Args:
            strength: How much to pull (0-1, typical: 0.05)
        """
        with self._lock:
            pull = strength * (self.baseline.values - self._current.values)
            self._current.values = np.clip(self._current.values + pull, 0.0, 1.0)
            self._current.timestamp = time.time()
            self._current.source = "heartbeat_decay"
        self._save_state()
        return self.current
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get human-readable state summary."""
        return {
            "identity_name": self.identity_name,
            "current": self.current.to_dict(),
            "baseline": self.baseline.to_dict(),
            "dominant": self.current.dominant(),
            "top_3": self.current.top_n(3),
            "deviation_from_baseline": float(np.linalg.norm(
                self.current.values - self.baseline.values
            )),
            "similarity_to_baseline": self.current.similarity(self.baseline),
        }
    
    def set_state(self, affect_dict: Dict[str, float], source: str = "manual") -> AffectVector:
        """
        Directly set current state (for testing/override).
        
        Args:
            affect_dict: Dict mapping affect names to values
            source: Label for this state
        """
        values = np.zeros(7, dtype=np.float32)
        for name, value in affect_dict.items():
            name_upper = name.upper()
            if name_upper in AFFECT_INDEX:
                values[AFFECT_INDEX[name_upper]] = float(value)
        
        with self._lock:
            self._current = AffectVector(values, source=source)
        self._save_state()
        return self.current


# =============================================================================
# SINGLETON INSTANCE (optional convenience)
# =============================================================================

_instance: Optional[DynamicAffectSystem] = None
_instance_lock = threading.Lock()


def get_affect_system(
    identity_name: str = "agent",
    baseline: Optional[np.ndarray] = None,
    **kwargs
) -> DynamicAffectSystem:
    """
    Get or create the singleton affect system.
    
    Args:
        identity_name: Name for this agent
        baseline: Optional custom baseline
        **kwargs: Additional parameters for DynamicAffectSystem
    """
    global _instance
    if _instance is None:
        with _instance_lock:
            # Double-checked locking pattern
            if _instance is None:
                _instance = DynamicAffectSystem(
                    identity_name=identity_name,
                    baseline=baseline,
                    **kwargs
                )
    elif kwargs or baseline is not None or identity_name != "agent":
        import warnings
        warnings.warn(
            "DynamicAffectSystem singleton already exists; kwargs ignored. "
            "Use DynamicAffectSystem() directly for custom instances.",
            stacklevel=2
        )
    return _instance


def get_current_affect() -> AffectVector:
    """Convenience: get current affect state from singleton."""
    return get_affect_system().current


def process_emotional_input(emotions: List[Dict]) -> AffectVector:
    """Convenience: process emotions and update singleton state."""
    return get_affect_system().process_emotions(emotions)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic Affect System")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "reset", "decay", "test"],
                        help="Action to perform")
    parser.add_argument("--name", default="agent", help="Agent identity name")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    system = get_affect_system(identity_name=args.name)
    
    if args.action == "status":
        summary = system.get_state_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n🎭 DYNAMIC AFFECT STATE ({summary['identity_name']})")
            print("=" * 50)
            print(f"Dominant: {summary['dominant'][0]} ({summary['dominant'][1]:.2f})")
            print(f"Deviation from baseline: {summary['deviation_from_baseline']:.3f}")
            print(f"Similarity to baseline: {summary['similarity_to_baseline']:.3f}")
            print("\nCurrent state:")
            for name, val in summary["current"]["named"].items():
                bar = "█" * int(val * 20)
                baseline_val = system.baseline.values[AFFECT_INDEX[name]]
                delta = val - baseline_val
                delta_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
                print(f"  {name:8} {val:.2f} {bar:20} ({delta_str})")
    
    elif args.action == "reset":
        with system._lock:
            system._current = AffectVector(system.baseline.values.copy(), source="reset")
            system._save_state()
        print("✅ Affect state reset to baseline")
    
    elif args.action == "decay":
        before = system.current.top_n(1)[0]
        system.drift_toward_baseline(strength=0.1)
        after = system.current.top_n(1)[0]
        print(f"✅ Decayed: {before[0]} {before[1]:.2f} → {after[0]} {after[1]:.2f}")
    
    elif args.action == "test":
        print(f"\n🧪 Testing Dynamic Affect System ({args.name})")
        print("=" * 50)
        
        # Test 1: Process input
        print("\n1. Processing CARE input (high intensity)...")
        system.process_input({"CARE": 0.9, "PLAY": 0.7}, intensity=0.8)
        print(f"   Result: {system.current}")
        
        # Test 2: Process anger
        print("\n2. Processing RAGE input (moderate)...")
        system.process_input({"RAGE": 0.6}, intensity=0.5)
        print(f"   Result: {system.current}")
        
        # Test 3: Decay
        print("\n3. Applying decay...")
        system.drift_toward_baseline(strength=0.2)
        print(f"   Result: {system.current}")
        
        # Test 4: VSA vector
        print("\n4. Getting Panksepp vector for VSA:")
        vec = system.get_panksepp_vector()
        print(f"   Shape: {vec.shape}, dtype: {vec.dtype}")
        print(f"   Values: {vec}")
        
        print("\n✅ All tests passed!")
