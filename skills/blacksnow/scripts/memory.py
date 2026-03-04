#!/usr/bin/env python3
"""
BlackSnow Memory Persistence
Stores signals and risk primitives in workspace memory for longitudinal analysis.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# ============================================================================
# CONFIG
# ============================================================================

BLACKSNOW_DIR = Path.home() / ".openclaw" / "blacksnow"
SIGNALS_DIR = BLACKSNOW_DIR / "signals"
VECTORS_DIR = BLACKSNOW_DIR / "vectors"
STATE_FILE = BLACKSNOW_DIR / "state.json"

# ============================================================================
# MEMORY MANAGER
# ============================================================================

class BlackSnowMemory:
    """Manages persistent storage for BlackSnow signals and vectors."""
    
    def __init__(self):
        self._ensure_dirs()
        self.state = self._load_state()
    
    def _ensure_dirs(self):
        """Create storage directories if they don't exist."""
        BLACKSNOW_DIR.mkdir(parents=True, exist_ok=True)
        SIGNALS_DIR.mkdir(exist_ok=True)
        VECTORS_DIR.mkdir(exist_ok=True)
    
    def _load_state(self) -> Dict:
        """Load or initialize state."""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_harvest": None,
            "total_signals": 0,
            "total_vectors": 0,
            "belief_states": {}
        }
    
    def _save_state(self):
        """Persist state to disk."""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)
    
    # ========================================================================
    # SIGNALS
    # ========================================================================
    
    def store_signals(self, signals: List[Any]) -> int:
        """Store raw signals to daily file."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = SIGNALS_DIR / f"signals_{today}.jsonl"
        
        stored = 0
        with open(filepath, 'a') as f:
            for sig in signals:
                record = asdict(sig) if hasattr(sig, '__dataclass_fields__') else sig
                record["_stored_at"] = datetime.now(timezone.utc).isoformat()
                f.write(json.dumps(record, default=str) + "\n")
                stored += 1
        
        self.state["total_signals"] += stored
        self.state["last_harvest"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        return stored
    
    def get_signals(self, days_back: int = 7) -> List[Dict]:
        """Retrieve signals from recent days."""
        signals = []
        for filepath in sorted(SIGNALS_DIR.glob("signals_*.jsonl"), reverse=True)[:days_back]:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        signals.append(json.loads(line))
        return signals
    
    # ========================================================================
    # VECTORS (Risk Primitives)
    # ========================================================================
    
    def store_vectors(self, vectors: List[Any]) -> int:
        """Store risk primitives to daily file."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = VECTORS_DIR / f"vectors_{today}.jsonl"
        
        stored = 0
        with open(filepath, 'a') as f:
            for vec in vectors:
                record = asdict(vec) if hasattr(vec, '__dataclass_fields__') else vec
                record["_generated_at"] = datetime.now(timezone.utc).isoformat()
                f.write(json.dumps(record, default=str) + "\n")
                stored += 1
        
        self.state["total_vectors"] += stored
        self._save_state()
        
        return stored
    
    def get_vectors(self, days_back: int = 30) -> List[Dict]:
        """Retrieve vectors from recent days."""
        vectors = []
        for filepath in sorted(VECTORS_DIR.glob("vectors_*.jsonl"), reverse=True)[:days_back]:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        vectors.append(json.loads(line))
        return vectors
    
    # ========================================================================
    # BELIEF STATES (Longitudinal)
    # ========================================================================
    
    def update_belief_states(self, belief_states: Dict[str, float]):
        """Update and persist belief states for drift detection."""
        for vector, belief in belief_states.items():
            if vector not in self.state["belief_states"]:
                self.state["belief_states"][vector] = {
                    "history": [],
                    "current": belief
                }
            
            # Append to history
            self.state["belief_states"][vector]["history"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "value": belief
            })
            
            # Keep last 100 entries
            self.state["belief_states"][vector]["history"] = \
                self.state["belief_states"][vector]["history"][-100:]
            
            self.state["belief_states"][vector]["current"] = belief
        
        self._save_state()
    
    def get_belief_history(self, vector: str) -> List[Dict]:
        """Get historical belief values for a vector."""
        if vector in self.state["belief_states"]:
            return self.state["belief_states"][vector]["history"]
        return []
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    def get_status(self) -> Dict:
        """Return memory status summary."""
        signal_files = list(SIGNALS_DIR.glob("signals_*.jsonl"))
        vector_files = list(VECTORS_DIR.glob("vectors_*.jsonl"))
        
        return {
            "storage_path": str(BLACKSNOW_DIR),
            "signal_files": len(signal_files),
            "vector_files": len(vector_files),
            "total_signals": self.state["total_signals"],
            "total_vectors": self.state["total_vectors"],
            "tracked_vectors": list(self.state["belief_states"].keys()),
            "last_harvest": self.state["last_harvest"],
            "created_at": self.state["created_at"]
        }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys
    
    memory = BlackSnowMemory()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "status":
            status = memory.get_status()
            print(json.dumps(status, indent=2))
        
        elif cmd == "signals":
            signals = memory.get_signals(days_back=7)
            print(f"Found {len(signals)} signals from last 7 days")
            for sig in signals[:5]:
                print(f"  - {sig.get('source_id', 'unknown')}: {sig.get('title', '')[:50]}...")
        
        elif cmd == "vectors":
            vectors = memory.get_vectors(days_back=30)
            print(f"Found {len(vectors)} vectors from last 30 days")
            for vec in vectors[:5]:
                print(f"  - {vec.get('risk_vector', 'unknown')}: conf={vec.get('signal_confidence', 0):.2f}")
        
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python memory.py [status|signals|vectors]")
    else:
        status = memory.get_status()
        print("BlackSnow Memory Status:")
        print(json.dumps(status, indent=2))
