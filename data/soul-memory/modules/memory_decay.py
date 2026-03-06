#!/usr/bin/env python3
"""
Soul Memory Module E: Memory Decay
Time-based decay and cleanup recommendations

Priority-based decay:
- Critical: Never decay
- Important: Slow decay (90 days half-life)
- Normal: Fast decay (30 days half-life)

Author: Soul Memory System
Date: 2026-02-17
"""

import os
import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta


@dataclass
class DecayResult:
    """Decay analysis result"""
    segment_id: str
    priority: str
    age_days: float
    decay_score: float
    recommendation: str  # 'keep', 'review', 'archive'


class MemoryDecay:
    """
    Memory Decay System
    
    Calculates decay scores based on:
    - Priority level
    - Time since last access
    - Access frequency
    """
    
    # Decay half-lives (days)
    HALF_LIVES = {
        'C': None,      # Critical: never decay
        'I': 90,        # Important: 90 days
        'N': 30         # Normal: 30 days
    }
    
    # Decay thresholds
    THRESHOLD_REVIEW = 0.5    # Review when decay_score < 0.5
    THRESHOLD_ARCHIVE = 0.2   # Archive when decay_score < 0.2
    
    def __init__(self, cache_path: Optional[Path] = None):
        self.cache_path = cache_path or Path(__file__).parent.parent / "cache"
        self.cache_path.mkdir(exist_ok=True)
        self.heat_map: Dict[str, Dict] = {}
        self._load_heat_map()
    
    def _load_heat_map(self):
        """Load heat map from cache"""
        heat_file = self.cache_path / "heat_map.json"
        if heat_file.exists():
            with open(heat_file, 'r', encoding='utf-8') as f:
                self.heat_map = json.load(f)
    
    def _save_heat_map(self):
        """Save heat map to cache"""
        heat_file = self.cache_path / "heat_map.json"
        with open(heat_file, 'w', encoding='utf-8') as f:
            json.dump(self.heat_map, f, ensure_ascii=False, indent=2)
    
    def record_access(self, segment_id: str):
        """Record memory access for heat tracking"""
        now = time.time()
        if segment_id not in self.heat_map:
            self.heat_map[segment_id] = {
                'created': now,
                'last_access': now,
                'access_count': 0
            }
        
        self.heat_map[segment_id]['last_access'] = now
        self.heat_map[segment_id]['access_count'] += 1
        self._save_heat_map()
    
    def calculate_decay(self, segment_id: str, priority: str) -> DecayResult:
        """Calculate decay for a memory segment"""
        now = time.time()
        
        # Get or create heat data
        if segment_id in self.heat_map:
            heat = self.heat_map[segment_id]
            last_access = heat.get('last_access', now)
            created = heat.get('created', now)
        else:
            last_access = now
            created = now
        
        age_seconds = now - last_access
        age_days = age_seconds / 86400
        
        # Calculate decay score
        if priority == 'C':
            # Critical: never decay
            decay_score = 1.0
        else:
            half_life_days = self.HALF_LIVES.get(priority, 30)
            decay_score = 0.5 ** (age_days / half_life_days)
        
        # Determine recommendation
        if decay_score > self.THRESHOLD_REVIEW:
            recommendation = 'keep'
        elif decay_score > self.THRESHOLD_ARCHIVE:
            recommendation = 'review'
        else:
            recommendation = 'archive'
        
        return DecayResult(
            segment_id=segment_id,
            priority=priority,
            age_days=age_days,
            decay_score=decay_score,
            recommendation=recommendation
        )
    
    def get_cleanup_recommendations(self, segments: List[Dict]) -> Dict[str, List[str]]:
        """Get cleanup recommendations for all segments"""
        recommendations = {
            'keep': [],
            'review': [],
            'archive': []
        }
        
        for seg in segments:
            seg_id = seg.get('id', 'unknown')
            priority = seg.get('priority', 'N')
            result = self.calculate_decay(seg_id, priority)
            recommendations[result.recommendation].append(seg_id)
        
        return recommendations
    
    def get_decay_stats(self) -> Dict:
        """Get decay statistics"""
        return {
            'total_segments': len(self.heat_map),
            'heat_map_entries': len(self.heat_map)
        }


if __name__ == "__main__":
    # Test
    decay = MemoryDecay()
    
    # Simulate some accesses
    decay.record_access('test_1')
    
    # Calculate decay
    result = decay.calculate_decay('test_1', 'N')
    print(f"Segment: {result.segment_id}")
    print(f"Priority: {result.priority}")
    print(f"Age: {result.age_days:.1f} days")
    print(f"Decay Score: {result.decay_score:.2f}")
    print(f"Recommendation: {result.recommendation}")
