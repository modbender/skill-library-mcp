"""
Affect History Module
=====================
Tracks emotion state history with configurable retention.

Provides:
- AffectSnapshot: Frozen moment in affect state
- AffectHistory: History manager with size/time-based pruning
- Pattern analysis utilities

Author: NIMA Core Team
Date: Feb 13, 2026
"""

import json
import logging
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


# Panksepp 7-affect order
AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"]
AFFECT_INDEX = {name: i for i, name in enumerate(AFFECTS)}


@dataclass
class AffectSnapshot:
    """
    A frozen moment in affect state.
    
    Captures the emotional state at a point in time for later analysis.
    """
    values: np.ndarray          # 7D affect vector
    timestamp: float            # Unix timestamp
    source: str                 # What caused this state
    dominant: Tuple[str, float] # (affect_name, value)
    deviation: float            # Distance from baseline
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "values": self.values.tolist(),
            "timestamp": self.timestamp,
            "source": self.source,
            "dominant": self.dominant,
            "deviation": float(self.deviation),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AffectSnapshot':
        """Create from dict (e.g., loaded from JSON)."""
        return cls(
            values=np.array(data["values"], dtype=np.float32),
            timestamp=data["timestamp"],
            source=data["source"],
            dominant=tuple(data["dominant"]),
            deviation=data["deviation"],
            metadata=data.get("metadata", {}),
        )
    
    def __repr__(self) -> str:
        time_str = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        return f"AffectSnapshot({self.dominant[0]}={self.dominant[1]:.2f} at {time_str})"


class AffectHistory:
    """
    Manages emotion state history with size/time-based retention.
    
    Features:
    - LRU eviction when max_snapshots exceeded
    - Age-based pruning of old snapshots
    - Timeline queries for analysis
    - Optional persistence to disk
    """
    
    def __init__(
        self,
        max_snapshots: int = 1000,
        max_age_hours: float = 168,  # 1 week default
        persist_dir: Optional[Path] = None,
        identity_name: str = "agent"
    ):
        """
        Initialize history manager.
        
        Args:
            max_snapshots: Maximum snapshots to keep (LRU eviction)
            max_age_hours: Maximum age of snapshots (older pruned)
            persist_dir: Optional directory to save history
            identity_name: Agent name for file naming
        """
        self.max_snapshots = max_snapshots
        self.max_age_hours = max_age_hours
        self.persist_dir = persist_dir
        # Sanitize identity_name to prevent path traversal attacks
        self.identity_name = self._sanitize_filename(identity_name)
        self._lock = threading.RLock()
        self._snapshots: List[AffectSnapshot] = []
        
        # Load existing history if persistence enabled
        if persist_dir:
            persist_dir.mkdir(parents=True, exist_ok=True)
            self._load()
    
    @staticmethod
    def _sanitize_filename(name: str, max_length: int = 100) -> str:
        """
        Sanitize a string for safe use in filenames.
        
        Prevents path traversal attacks and special character issues.
        
        Args:
            name: Input string (e.g., agent identity name)
            max_length: Maximum allowed length
            
        Returns:
            Sanitized filename-safe string
        """
        import re
        # Remove path separators and parent directory references
        name = name.replace('/', '_').replace('\\', '_').replace('..', '')
        # Keep only alphanumeric, dash, underscore
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Collapse multiple underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Ensure non-empty (fallback to 'default')
        if not name:
            name = 'default'
        # Truncate if too long
        if len(name) > max_length:
            name = name[:max_length]
        return name
    
    def record(
        self,
        values: np.ndarray,
        baseline: np.ndarray,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AffectSnapshot:
        """
        Record a snapshot of current state.
        
        Args:
            values: Current 7D affect vector
            baseline: Baseline vector for deviation calculation
            source: What caused this state
            metadata: Optional additional data
        
        Returns:
            The created snapshot
        """
        # Calculate derived values
        deviation = float(np.linalg.norm(values - baseline))
        dominant_idx = int(np.argmax(values))
        dominant = (AFFECTS[dominant_idx], float(values[dominant_idx]))
        
        snapshot = AffectSnapshot(
            values=values.copy(),
            timestamp=time.time(),
            source=source,
            dominant=dominant,
            deviation=deviation,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._snapshots.append(snapshot)
            self._prune()
        
        self._save()
        
        return snapshot
    
    def _prune(self) -> None:
        """Prune old snapshots beyond limits."""
        now = time.time()
        cutoff = now - (self.max_age_hours * 3600)
        
        # Remove by age
        self._snapshots = [
            s for s in self._snapshots
            if s.timestamp > cutoff
        ]
        
        # Remove by count (LRU: keep newest)
        if len(self._snapshots) > self.max_snapshots:
            self._snapshots = self._snapshots[-self.max_snapshots:]
    
    def _save(self) -> None:
        """Save history to disk if persistence enabled."""
        if not self.persist_dir:
            return
        
        try:
            # Snapshot under lock to avoid race with mutations
            with self._lock:
                snapshots = list(self._snapshots)
            
            path = self.persist_dir / f"history_{self.identity_name}.json"
            data = {
                "snapshots": [s.to_dict() for s in snapshots],
                "saved_at": time.time()
            }
            # Atomic write with proper temp file cleanup
            import tempfile
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    dir=self.persist_dir, 
                    delete=False,
                    suffix='.json'
                ) as f:
                    json.dump(data, f, indent=2)
                    temp_path = Path(f.name)
                # Atomic rename
                temp_path.replace(path)
                temp_path = None  # Successfully moved, don't delete
            finally:
                # Clean up temp file if rename failed
                if temp_path and temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        pass  # Best effort cleanup
        except (OSError, IOError, TypeError, ValueError) as e:
            logger.warning(f"Failed to save affect history: {e}")
    
    def _load(self) -> None:
        """Load history from disk."""
        if not self.persist_dir:
            return
        
        try:
            path = self.persist_dir / f"history_{self.identity_name}.json"
            if not path.exists():
                return
            
            with open(path, 'r') as f:
                data = json.load(f)
            
            with self._lock:
                self._snapshots = [
                    AffectSnapshot.from_dict(s) 
                    for s in data.get("snapshots", [])
                ]
            
            # Prune on load
            self._prune()
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to load affect history, starting fresh: {e}")
            with self._lock:
                self._snapshots = []
    
    def get_state_at(self, timestamp: float) -> Optional[AffectSnapshot]:
        """
        Get state closest to given timestamp.
        
        Args:
            timestamp: Target Unix timestamp
        
        Returns:
            Nearest snapshot within 1 hour, or None
        """
        with self._lock:
            if not self._snapshots:
                return None
            
            closest = min(
                self._snapshots,
                key=lambda s: abs(s.timestamp - timestamp)
            )
            
            # Only return if within 1 hour
            if abs(closest.timestamp - timestamp) < 3600:
                return closest
            return None
    
    def get_timeline(
        self, 
        duration_hours: float = 24,
        limit: int = 100
    ) -> List[AffectSnapshot]:
        """
        Get snapshots from last N hours.
        
        Args:
            duration_hours: How far back to look
            limit: Maximum snapshots to return
        
        Returns:
            List of snapshots, oldest first
        """
        with self._lock:
            cutoff = time.time() - (duration_hours * 3600)
            result = [s for s in self._snapshots if s.timestamp > cutoff]
            return result[-limit:] if len(result) > limit else result
    
    def get_dominant_timeline(
        self,
        duration_hours: float = 24
    ) -> List[Tuple[str, float, float]]:
        """
        Get timeline of dominant affects.
        
        Args:
            duration_hours: How far back to look
        
        Returns:
            List of (dominant_affect, value, timestamp) tuples
        """
        timeline = self.get_timeline(duration_hours)
        return [(s.dominant[0], s.dominant[1], s.timestamp) for s in timeline]
    
    def get_deviation_trend(
        self,
        duration_hours: float = 24
    ) -> Tuple[float, str]:
        """
        Analyze deviation trend over time.
        
        Args:
            duration_hours: How far back to analyze
        
        Returns:
            (slope, direction) where direction is "increasing", "stable", or "decreasing"
        """
        timeline = self.get_timeline(duration_hours)
        if len(timeline) < 2:
            return (0.0, "stable")
        
        # Simple linear regression on deviations
        times = np.array([s.timestamp for s in timeline])
        deviations = np.array([s.deviation for s in timeline])
        
        # Normalize time to hours
        times = (times - times[0]) / 3600
        
        # Calculate slope
        if len(times) > 1:
            slope = np.polyfit(times, deviations, 1)[0]
        else:
            slope = 0.0
        
        if slope > 0.01:
            direction = "increasing"
        elif slope < -0.01:
            direction = "decreasing"
        else:
            direction = "stable"
        
        return (float(slope), direction)
    
    def count_sources(self, duration_hours: float = 24) -> Dict[str, int]:
        """
        Count snapshots by source.
        
        Args:
            duration_hours: How far back to look
        
        Returns:
            Dict mapping source to count
        """
        timeline = self.get_timeline(duration_hours)
        counts: Dict[str, int] = {}
        for s in timeline:
            counts[s.source] = counts.get(s.source, 0) + 1
        return counts
    
    def clear(self) -> None:
        """Clear all history."""
        with self._lock:
            self._snapshots = []
        self._save()
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._snapshots)
    
    def __repr__(self) -> str:
        with self._lock:
            return f"AffectHistory({len(self._snapshots)} snapshots, max_age={self.max_age_hours}h)"