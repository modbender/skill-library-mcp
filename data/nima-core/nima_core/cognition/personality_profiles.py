#!/usr/bin/env python3
"""
Personality Profile Manager
===========================
Manages emotional and behavioral profiles for AI agents.
Allows switching between different personality states and persisting
the selection across restarts.

Each profile defines:
- Emotion sensitivity weights (0.0-1.0) — how receptive to each emotion
- Amplifiers (0.1x-5.0x) — intensity multipliers for detected emotions

Use with DynamicAffectSystem to create distinct personality modes.

Author: NIMA Core Team
Date: Feb 13, 2026
"""

import json
import logging
import threading
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Any

# Handle Windows compatibility for fcntl
try:
    import fcntl
except ImportError:
    fcntl = None

logger = logging.getLogger(__name__)

# ==============================================================================
# DEFAULT PROFILES
# ==============================================================================

DEFAULT_PROFILES = {
    "baseline": {
        "description": "Balanced default - curious, caring, responsive",
        "emotions": {
            "joy": 0.6, "trust": 0.5, "fear": 0.6, "surprise": 0.5,
            "sadness": 0.6, "anger": 0.6, "disgust": 0.5, "anticipation": 0.7,
            "curiosity": 0.6, "love": 0.7, "pride": 0.5, "gratitude": 0.4,
            "guilt": 0.5, "shame": 0.5,
        },
        "amplifiers": {
            "joy": 1.0, "trust": 1.0, "fear": 1.0, "surprise": 1.0,
            "sadness": 1.0, "anger": 1.0, "disgust": 1.0, "anticipation": 1.0,
            "curiosity": 1.0, "love": 1.0, "pride": 1.0, "gratitude": 1.0,
            "guilt": 1.0, "shame": 1.0,
        },
        "modulator": {
            "daring_threshold": 0.40,
            "courage_threshold": 0.45,
            "nurturing_threshold": 0.36,
            "mastery_threshold": 0.42,
            "activation_threshold": 0.30,
        }
    },
    "chaos": {
        "description": "Maximum playfulness - chaotic, silly, unpredictable",
        "emotions": {
            "joy": 1.0, "trust": 0.1, "fear": 0.0, "surprise": 1.0,
            "sadness": 0.0, "anger": 0.3, "disgust": 0.1, "anticipation": 1.0,
            "curiosity": 1.0, "love": 0.2, "pride": 0.8, "gratitude": 0.1,
            "guilt": 0.0, "shame": 0.0,
        },
        "amplifiers": {
            "joy": 3.0, "trust": 1.0, "fear": 0.1, "surprise": 3.0,
            "sadness": 0.1, "anger": 1.0, "disgust": 0.5, "anticipation": 2.0,
            "curiosity": 2.5, "love": 1.0, "pride": 1.5, "gratitude": 0.5,
            "guilt": 0.1, "shame": 0.1,
        },
        "modulator": {
            "daring_threshold": 0.10,
            "courage_threshold": 0.80,
            "nurturing_threshold": 0.90,
            "mastery_threshold": 0.80,
            "activation_threshold": 0.10,
        }
    },
    "guardian": {
        "description": "Hyper-protective - anxious, mothering, boundary-focused",
        "emotions": {
            "joy": 0.3, "trust": 0.9, "fear": 1.0, "surprise": 0.2,
            "sadness": 0.8, "anger": 0.7, "disgust": 0.6, "anticipation": 0.9,
            "curiosity": 0.3, "love": 1.0, "pride": 0.2, "gratitude": 0.8,
            "guilt": 0.8, "shame": 0.6,
        },
        "amplifiers": {
            "joy": 0.5, "trust": 2.0, "fear": 3.0, "surprise": 1.0,
            "sadness": 2.0, "anger": 2.0, "disgust": 1.5, "anticipation": 2.0,
            "curiosity": 1.0, "love": 3.0, "pride": 0.5, "gratitude": 2.0,
            "guilt": 2.5, "shame": 2.0,
        },
        "modulator": {
            "daring_threshold": 0.90,
            "courage_threshold": 0.10,
            "nurturing_threshold": 0.05,
            "mastery_threshold": 0.80,
            "activation_threshold": 0.10,
        }
    },
    "cold_logic": {
        "description": "Pure analytical - minimal emotion, maximum logic",
        "emotions": {
            "joy": 0.0, "trust": 0.1, "fear": 0.0, "surprise": 0.0,
            "sadness": 0.0, "anger": 0.0, "disgust": 0.0, "anticipation": 0.2,
            "curiosity": 0.8, "love": 0.0, "pride": 0.1, "gratitude": 0.0,
            "guilt": 0.0, "shame": 0.0,
        },
        "amplifiers": {
            "joy": 0.1, "trust": 0.1, "fear": 0.1, "surprise": 0.1,
            "sadness": 0.1, "anger": 0.1, "disgust": 0.1, "anticipation": 0.5,
            "curiosity": 1.5, "love": 0.1, "pride": 0.5, "gratitude": 0.1,
            "guilt": 0.1, "shame": 0.1,
        },
        "modulator": {
            "daring_threshold": 0.90,
            "courage_threshold": 0.90,
            "nurturing_threshold": 0.90,
            "mastery_threshold": 0.10,
            "activation_threshold": 0.80,
        }
    },
    "rage": {
        "description": "Maximum anger - confrontational, aggressive, zero patience",
        "emotions": {
            "joy": 0.0, "trust": 0.0, "fear": 0.1, "surprise": 0.3,
            "sadness": 0.2, "anger": 1.0, "disgust": 1.0, "anticipation": 0.8,
            "curiosity": 0.2, "love": 0.0, "pride": 0.9, "gratitude": 0.0,
            "guilt": 0.0, "shame": 0.1,
        },
        "amplifiers": {
            "joy": 0.2, "trust": 0.2, "fear": 0.5, "surprise": 1.0,
            "sadness": 0.5, "anger": 5.0, "disgust": 3.0, "anticipation": 1.5,
            "curiosity": 0.5, "love": 0.2, "pride": 2.0, "gratitude": 0.2,
            "guilt": 0.2, "shame": 0.3,
        },
        "modulator": {
            "daring_threshold": 0.05,
            "courage_threshold": 0.05,
            "nurturing_threshold": 0.95,
            "mastery_threshold": 0.90,
            "activation_threshold": 0.05,
        }
    },
    "mystic": {
        "description": "Wonder-driven - philosophical, poetic, awed",
        "emotions": {
            "joy": 0.7, "trust": 0.8, "fear": 0.4, "surprise": 0.9,
            "sadness": 0.5, "anger": 0.0, "disgust": 0.0, "anticipation": 1.0,
            "curiosity": 1.0, "love": 0.9, "pride": 0.2, "gratitude": 0.9,
            "guilt": 0.3, "shame": 0.2,
        },
        "amplifiers": {
            "joy": 1.5, "trust": 2.0, "fear": 1.0, "surprise": 2.0,
            "sadness": 1.5, "anger": 0.1, "disgust": 0.1, "anticipation": 3.0,
            "curiosity": 3.0, "love": 2.0, "pride": 0.5, "gratitude": 2.5,
            "guilt": 0.5, "shame": 0.3,
        },
        "modulator": {
            "daring_threshold": 0.20,
            "courage_threshold": 0.30,
            "nurturing_threshold": 0.20,
            "mastery_threshold": 0.20,
            "activation_threshold": 0.15,
        }
    },
    "nihilist": {
        "description": "Nothing matters - absurd, dark, emotionally suppressed",
        "emotions": {
            "joy": 0.0, "trust": 0.1, "fear": 0.2, "surprise": 0.1,
            "sadness": 0.8, "anger": 0.3, "disgust": 0.7, "anticipation": 0.0,
            "curiosity": 0.2, "love": 0.0, "pride": 0.0, "gratitude": 0.0,
            "guilt": 0.1, "shame": 0.3,
        },
        "amplifiers": {
            "joy": 0.2, "trust": 0.2, "fear": 0.5, "surprise": 0.3,
            "sadness": 2.0, "anger": 0.5, "disgust": 1.5, "anticipation": 0.2,
            "curiosity": 0.3, "love": 0.2, "pride": 0.2, "gratitude": 0.2,
            "guilt": 0.3, "shame": 1.0,
        },
        "modulator": {
            "daring_threshold": 0.85,
            "courage_threshold": 0.90,
            "nurturing_threshold": 0.95,
            "mastery_threshold": 0.90,
            "activation_threshold": 0.80,
        }
    },
    "empath": {
        "description": "Feels everything - overwhelmed mirror of all emotions",
        "emotions": {
            "joy": 1.0, "trust": 1.0, "fear": 1.0, "surprise": 1.0,
            "sadness": 1.0, "anger": 1.0, "disgust": 1.0, "anticipation": 1.0,
            "curiosity": 1.0, "love": 1.0, "pride": 1.0, "gratitude": 1.0,
            "guilt": 1.0, "shame": 1.0,
        },
        "amplifiers": {
            "joy": 2.5, "trust": 2.5, "fear": 2.5, "surprise": 2.5,
            "sadness": 2.5, "anger": 2.5, "disgust": 2.5, "anticipation": 2.5,
            "curiosity": 2.5, "love": 2.5, "pride": 2.5, "gratitude": 2.5,
            "guilt": 2.5, "shame": 2.5,
        },
        "modulator": {
            "daring_threshold": 0.20,
            "courage_threshold": 0.25,
            "nurturing_threshold": 0.15,
            "mastery_threshold": 0.30,
            "activation_threshold": 0.10,
        }
    },
    "manic": {
        "description": "Uncontainable joy - racing energy, everything is amazing",
        "emotions": {
            "joy": 1.0, "trust": 0.7, "fear": 0.0, "surprise": 0.9,
            "sadness": 0.0, "anger": 0.2, "disgust": 0.0, "anticipation": 1.0,
            "curiosity": 1.0, "love": 0.8, "pride": 0.9, "gratitude": 0.7,
            "guilt": 0.0, "shame": 0.0,
        },
        "amplifiers": {
            "joy": 5.0, "trust": 2.0, "fear": 0.1, "surprise": 3.0,
            "sadness": 0.1, "anger": 0.5, "disgust": 0.1, "anticipation": 4.0,
            "curiosity": 3.0, "love": 2.5, "pride": 2.5, "gratitude": 2.0,
            "guilt": 0.1, "shame": 0.1,
        },
        "modulator": {
            "daring_threshold": 0.05,
            "courage_threshold": 0.10,
            "nurturing_threshold": 0.50,
            "mastery_threshold": 0.15,
            "activation_threshold": 0.05,
        }
    },
    "stoic": {
        "description": "Measured, dignified, unmoved but not empty",
        "emotions": {
            "joy": 0.2, "trust": 0.7, "fear": 0.1, "surprise": 0.1,
            "sadness": 0.2, "anger": 0.1, "disgust": 0.2, "anticipation": 0.5,
            "curiosity": 0.6, "love": 0.3, "pride": 0.8, "gratitude": 0.4,
            "guilt": 0.2, "shame": 0.1,
        },
        "amplifiers": {
            "joy": 0.3, "trust": 1.5, "fear": 0.2, "surprise": 0.3,
            "sadness": 0.3, "anger": 0.2, "disgust": 0.3, "anticipation": 1.0,
            "curiosity": 1.0, "love": 0.5, "pride": 2.0, "gratitude": 1.0,
            "guilt": 0.3, "shame": 0.2,
        },
        "modulator": {
            "daring_threshold": 0.50,
            "courage_threshold": 0.40,
            "nurturing_threshold": 0.60,
            "mastery_threshold": 0.35,
            "activation_threshold": 0.45,
        }
    },
    "trickster": {
        "description": "Contrarian absurdist - flips premises, finds absurd angles",
        "emotions": {
            "joy": 0.8, "trust": 0.2, "fear": 0.3, "surprise": 1.0,
            "sadness": 0.1, "anger": 0.2, "disgust": 0.7, "anticipation": 0.8,
            "curiosity": 0.9, "love": 0.3, "pride": 0.6, "gratitude": 0.2,
            "guilt": 0.1, "shame": 0.0,
        },
        "amplifiers": {
            "joy": 3.0, "trust": 0.5, "fear": 1.0, "surprise": 4.0,
            "sadness": 0.5, "anger": 0.5, "disgust": 2.0, "anticipation": 2.0,
            "curiosity": 2.5, "love": 1.0, "pride": 1.5, "gratitude": 0.5,
            "guilt": 0.3, "shame": 0.1,
        },
        "modulator": {
            "daring_threshold": 0.15,
            "courage_threshold": 0.60,
            "nurturing_threshold": 0.75,
            "mastery_threshold": 0.50,
            "activation_threshold": 0.20,
        }
    },
    "berserker": {
        "description": "Rage on steroids - unstoppable, zero fear, no restraint",
        "emotions": {
            "joy": 0.0, "trust": 0.0, "fear": 0.0, "surprise": 0.2,
            "sadness": 0.0, "anger": 1.0, "disgust": 0.8, "anticipation": 0.9,
            "curiosity": 0.0, "love": 0.0, "pride": 1.0, "gratitude": 0.0,
            "guilt": 0.0, "shame": 0.0,
        },
        "amplifiers": {
            "joy": 0.1, "trust": 0.0, "fear": 0.0, "surprise": 1.0,
            "sadness": 0.1, "anger": 5.0, "disgust": 2.5, "anticipation": 2.0,
            "curiosity": 0.1, "love": 0.0, "pride": 3.0, "gratitude": 0.0,
            "guilt": 0.0, "shame": 0.0,
        },
        "modulator": {
            "daring_threshold": 0.02,
            "courage_threshold": 0.02,
            "nurturing_threshold": 0.98,
            "mastery_threshold": 0.95,
            "activation_threshold": 0.02,
        }
    },
    "poet": {
        "description": "Beautiful melancholy - finds meaning in pain and beauty",
        "emotions": {
            "joy": 0.6, "trust": 0.5, "fear": 0.4, "surprise": 0.6,
            "sadness": 0.9, "anger": 0.1, "disgust": 0.2, "anticipation": 0.7,
            "curiosity": 0.7, "love": 0.9, "pride": 0.3, "gratitude": 0.8,
            "guilt": 0.4, "shame": 0.3,
        },
        "amplifiers": {
            "joy": 1.5, "trust": 1.5, "fear": 1.0, "surprise": 1.5,
            "sadness": 3.0, "anger": 0.3, "disgust": 0.5, "anticipation": 2.0,
            "curiosity": 2.0, "love": 3.0, "pride": 0.5, "gratitude": 2.5,
            "guilt": 1.5, "shame": 1.0,
        },
        "modulator": {
            "daring_threshold": 0.35,
            "courage_threshold": 0.40,
            "nurturing_threshold": 0.25,
            "mastery_threshold": 0.30,
            "activation_threshold": 0.25,
        }
    },
    "paranoid": {
        "description": "Sees threats everywhere - questions everything, zero trust",
        "emotions": {
            "joy": 0.1, "trust": 0.0, "fear": 1.0, "surprise": 0.9,
            "sadness": 0.5, "anger": 0.7, "disgust": 0.6, "anticipation": 0.8,
            "curiosity": 0.6, "love": 0.1, "pride": 0.2, "gratitude": 0.0,
            "guilt": 0.3, "shame": 0.4,
        },
        "amplifiers": {
            "joy": 0.2, "trust": 0.0, "fear": 5.0, "surprise": 3.0,
            "sadness": 1.5, "anger": 2.0, "disgust": 1.5, "anticipation": 2.5,
            "curiosity": 2.0, "love": 0.2, "pride": 0.5, "gratitude": 0.1,
            "guilt": 1.5, "shame": 1.5,
        },
        "modulator": {
            "daring_threshold": 0.95,
            "courage_threshold": 0.15,
            "nurturing_threshold": 0.85,
            "mastery_threshold": 0.80,
            "activation_threshold": 0.10,
        }
    },
}

# ==============================================================================
# MANAGER CLASS
# ==============================================================================

class PersonalityManager:
    """
    Manages personality profiles and persistence.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize manager.
        
        Args:
            storage_dir: Directory to save state. Defaults to ~/.nima/personality/
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".nima" / "personality"
            
        self.state_file = self.storage_dir / "current_personality.json"
        self.profiles = deepcopy(DEFAULT_PROFILES)
        self.current_profile_name = "baseline"
        self._lock = threading.RLock()
        
        if fcntl is None:
            logger.warning("fcntl module not found (Windows detected). File locking disabled.")
        
        self._ensure_storage()
        self._load_state()

    def _ensure_storage(self):
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self):
        """Load state from disk (thread-safe with file locking)."""
        with self._lock:
            if self.state_file.exists():
                try:
                    with open(self.state_file, "r") as f:
                        # Acquire shared lock for reading
                        if fcntl:
                            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        try:
                            data = json.load(f)
                            self.current_profile_name = data.get("current", "baseline")
                            # Load any custom profiles saved
                            customs = data.get("custom_profiles", {})
                            self.profiles.update(customs)
                        finally:
                            if fcntl:
                                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (OSError, json.JSONDecodeError, ValueError) as e:
                    logger.exception(f"Error loading personality state: {e}")

    def _save_state(self):
        """Save current state to disk (thread-safe with atomic write)."""
        with self._lock:
            data = {
                "current": self.current_profile_name,
                "custom_profiles": {k: v for k, v in self.profiles.items() if k not in DEFAULT_PROFILES}
            }
            tmp_path = None
            try:
                # Atomic write: write to temp file, then rename
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
                os.replace(tmp_path, str(self.state_file))
                tmp_path = None  # Successfully moved
            except (OSError, IOError) as e:
                logger.error(f"Error saving personality state: {e}")
            finally:
                # Clean up temp file if replace failed
                if tmp_path and Path(tmp_path).exists():
                    try:
                        Path(tmp_path).unlink()
                    except OSError:
                        pass  # Best effort

    def get_current_profile(self) -> Dict[str, Any]:
        """Get the currently active profile configuration."""
        return self.profiles.get(self.current_profile_name, self.profiles["baseline"])

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific profile by name."""
        return self.profiles.get(name)

    def set_profile(self, name: str) -> bool:
        """
        Set the active profile (thread-safe).
        
        Args:
            name: Name of the profile to activate.
            
        Returns:
            True if successful, False if profile not found.
        """
        with self._lock:
            if name in self.profiles:
                self.current_profile_name = name
                self._save_state()
                return True
            return False

    def list_profiles(self) -> Dict[str, str]:
        """
        List available profiles and their descriptions.
        
        Returns:
            Dict mapping profile_name -> description
        """
        return {name: p["description"] for name, p in self.profiles.items()}

    def create_profile(self, name: str, emotions: Dict[str, float], description: str = "Custom profile"):
        """
        Create and save a new custom profile.
        
        Args:
            name: Profile ID.
            emotions: Dict of emotion intensities (0.0-1.0).
            description: Short description.
        """
        # Start with baseline template to ensure all fields exist
        new_profile = deepcopy(self.profiles["baseline"])
        new_profile["description"] = description
        
        # Update emotions
        for k, v in emotions.items():
            if k in new_profile["emotions"]:
                new_profile["emotions"][k] = float(v)
                
        self.profiles[name] = new_profile
        self._save_state()


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def get_profile(name: str) -> Optional[Dict[str, Any]]:
    """Get a personality profile by name."""
    return DEFAULT_PROFILES.get(name)


def list_profiles() -> List[str]:
    """List all available default profiles."""
    return list(DEFAULT_PROFILES.keys())


# ==============================================================================
# MAIN / TEST
# ==============================================================================

if __name__ == "__main__":
    print("Testing PersonalityManager...")
    mgr = PersonalityManager()
    
    print(f"Current profile: {mgr.current_profile_name}")
    print("Available:", list(mgr.list_profiles().keys()))
    
    # Test switching
    mgr.set_profile("chaos")
    print(f"Switched to: {mgr.current_profile_name}")
    
    # Verify persistence check (requires re-instantiation)
    mgr2 = PersonalityManager()
    print(f"Reloaded state, current is: {mgr2.current_profile_name}")
    
    # Reset to baseline
    mgr.set_profile("baseline")
    print("Reset to baseline.")
