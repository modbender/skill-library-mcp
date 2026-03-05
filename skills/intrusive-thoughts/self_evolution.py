#!/usr/bin/env python3
"""🧬 Self-Evolving Learning System - The agent learns from its own behavior patterns."""

import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from typing import Dict, List, Any, Optional, Tuple
from config import get_file_path

# Data paths
HISTORY_FILE = get_file_path("history.json")
MOOD_HISTORY_FILE = get_file_path("mood_history.json")
EVOLUTION_DIR = Path(__file__).parent / "evolution"
LEARNINGS_FILE = EVOLUTION_DIR / "learnings.json"
LEARNED_WEIGHTS_FILE = EVOLUTION_DIR / "learned_weights.json"

# Value dimensions for optimizing agent behavior
VALUE_DIMENSIONS = {
    "productivity": 0.3,    # tasks completed, code written
    "creativity": 0.2,      # novel actions, diverse activities
    "social": 0.2,          # engagement quality, community participation
    "growth": 0.15,         # new skills, learning activities
    "wellbeing": 0.15       # streak maintenance, balanced moods
}

class SelfEvolutionSystem:
    def __init__(self):
        self.evolution_dir = EVOLUTION_DIR
        self.evolution_dir.mkdir(exist_ok=True)
        
        self.history = self._load_history()
        self.mood_history = self._load_mood_history()
        self.learnings = self._load_learnings()
        self.learned_weights = self._load_learned_weights()
    
    def _load_history(self) -> List[Dict]:
        """Load activity history."""
        try:
            return json.loads(HISTORY_FILE.read_text())
        except:
            return []
    
    def _load_mood_history(self) -> List[Dict]:
        """Load mood history."""
        try:
            data = json.loads(MOOD_HISTORY_FILE.read_text())
            return data.get("history", [])
        except:
            return []
    
    def _load_learnings(self) -> Dict:
        """Load existing learnings."""
        try:
            return json.loads(LEARNINGS_FILE.read_text())
        except:
            return {
                "version": 1,
                "last_evolution": None,
                "patterns": [],
                "weight_adjustments": {"moods": {}, "thoughts": {}},
                "evolution_history": []
            }
    
    def _load_learned_weights(self) -> Dict:
        """Load learned weight adjustments."""
        try:
            return json.loads(LEARNED_WEIGHTS_FILE.read_text())
        except:
            return {"moods": {}, "thoughts": {}}
    
    def _save_learnings(self):
        """Save learnings to file."""
        self.learnings["last_evolution"] = datetime.now().isoformat()
        LEARNINGS_FILE.write_text(json.dumps(self.learnings, indent=2))
    
    def _save_learned_weights(self):
        """Save learned weights to file."""
        LEARNED_WEIGHTS_FILE.write_text(json.dumps(self.learned_weights, indent=2))
    
    def _calculate_value_score(self, entry: Dict) -> float:
        """Calculate multi-dimensional value score for an activity."""
        # Base productivity score (from analyze.py logic)
        energy_score = {"high": 3, "neutral": 1, "low": -1}.get(entry.get("energy", "neutral"), 0)
        vibe_score = {"positive": 3, "neutral": 1, "negative": -1}.get(entry.get("vibe", "neutral"), 0)
        
        # Thought type scoring across value dimensions
        thought_id = entry.get("thought_id", "")
        
        # Productivity dimension
        productivity_scores = {
            "build-tool": 0.9, "upgrade-project": 0.9, "system-tinker": 0.7,
            "learn": 0.6, "memory-review": 0.5, "install-explore": 0.4,
            "creative-chaos": 0.3, "moltbook-post": 0.3, "moltbook-social": 0.2,
            "share-discovery": 0.4, "ask-opinion": 0.1, "random-thought": 0.1
        }
        
        # Creativity dimension
        creativity_scores = {
            "creative-chaos": 0.9, "build-tool": 0.7, "moltbook-post": 0.6,
            "upgrade-project": 0.4, "install-explore": 0.7, "learn": 0.5,
            "system-tinker": 0.3, "share-discovery": 0.4, "ask-opinion": 0.2
        }
        
        # Social dimension
        social_scores = {
            "moltbook-social": 0.9, "moltbook-post": 0.8, "share-discovery": 0.7,
            "ask-opinion": 0.8, "ask-preference": 0.6, "pitch-idea": 0.5,
            "ask-feedback": 0.6, "random-thought": 0.3, "build-tool": 0.1
        }
        
        # Growth dimension
        growth_scores = {
            "learn": 0.9, "install-explore": 0.8, "upgrade-project": 0.6,
            "system-tinker": 0.7, "build-tool": 0.5, "memory-review": 0.4,
            "ask-feedback": 0.5, "creative-chaos": 0.3
        }
        
        # Wellbeing dimension (based on energy/vibe outcomes)
        wellbeing_base = (energy_score + vibe_score) / 6  # normalize to 0-1
        
        # Calculate weighted score
        productivity = productivity_scores.get(thought_id, 0.1)
        creativity = creativity_scores.get(thought_id, 0.1)
        social = social_scores.get(thought_id, 0.1)
        growth = growth_scores.get(thought_id, 0.1)
        wellbeing = max(0, min(1, wellbeing_base))
        
        total_score = (
            VALUE_DIMENSIONS["productivity"] * productivity +
            VALUE_DIMENSIONS["creativity"] * creativity +
            VALUE_DIMENSIONS["social"] * social +
            VALUE_DIMENSIONS["growth"] * growth +
            VALUE_DIMENSIONS["wellbeing"] * wellbeing
        )
        
        return total_score * 10  # Scale to 0-10
    
    def analyze_mood_effectiveness(self) -> Dict:
        """Analyze which moods produce the best outcomes."""
        # Create date -> mood mapping
        mood_by_date = {}
        for mood_entry in self.mood_history:
            mood_by_date[mood_entry["date"]] = mood_entry["mood_id"]
        
        # Group activities by mood
        mood_outcomes = defaultdict(list)
        
        for activity in self.history:
            date = activity["timestamp"][:10]  # Extract YYYY-MM-DD
            mood = mood_by_date.get(date, "unknown")
            if mood == "unknown":
                continue
                
            score = self._calculate_value_score(activity)
            mood_outcomes[mood].append({
                "score": score,
                "energy": activity.get("energy", "neutral"),
                "vibe": activity.get("vibe", "neutral"),
                "thought_id": activity.get("thought_id", "unknown"),
                "timestamp": activity["timestamp"]
            })
        
        # Analyze each mood
        results = {}
        for mood, outcomes in mood_outcomes.items():
            if len(outcomes) < 2:  # Need minimum sample size
                continue
                
            scores = [o["score"] for o in outcomes]
            high_energy = sum(1 for o in outcomes if o["energy"] == "high")
            positive_vibe = sum(1 for o in outcomes if o["vibe"] == "positive")
            
            results[mood] = {
                "average_score": statistics.mean(scores),
                "median_score": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                "total_activities": len(outcomes),
                "high_energy_rate": high_energy / len(outcomes),
                "positive_vibe_rate": positive_vibe / len(outcomes),
                "consistency": 1 - (statistics.stdev(scores) / (statistics.mean(scores) + 0.1) if len(scores) > 1 else 0),
                "recent_trend": self._calculate_trend([o["score"] for o in outcomes[-10:]]),
                "top_activities": Counter(o["thought_id"] for o in outcomes).most_common(3)
            }
        
        return results
    
    def analyze_thought_effectiveness(self) -> Dict:
        """Analyze which thought types work best per mood."""
        mood_by_date = {}
        for mood_entry in self.mood_history:
            mood_by_date[mood_entry["date"]] = mood_entry["mood_id"]
        
        # Group by mood -> thought_id -> outcomes
        mood_thought_outcomes = defaultdict(lambda: defaultdict(list))
        
        for activity in self.history:
            date = activity["timestamp"][:10]
            mood = mood_by_date.get(date, "unknown")
            thought_id = activity.get("thought_id", "unknown")
            
            if mood == "unknown" or thought_id == "unknown":
                continue
                
            score = self._calculate_value_score(activity)
            mood_thought_outcomes[mood][thought_id].append(score)
        
        # Analyze effectiveness
        results = {}
        for mood, thoughts in mood_thought_outcomes.items():
            results[mood] = {}
            for thought_id, scores in thoughts.items():
                if len(scores) < 2:
                    continue
                
                results[mood][thought_id] = {
                    "average_score": statistics.mean(scores),
                    "success_rate": sum(1 for s in scores if s >= 6) / len(scores),
                    "total_attempts": len(scores),
                    "consistency": 1 - (statistics.stdev(scores) / (statistics.mean(scores) + 0.1))
                }
        
        return results
    
    def analyze_time_patterns(self) -> Dict:
        """Analyze temporal productivity patterns."""
        time_outcomes = defaultdict(list)
        
        for activity in self.history:
            try:
                timestamp = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
                hour = timestamp.hour
                score = self._calculate_value_score(activity)
                
                # Group into time slots
                if 2 <= hour <= 5:
                    slot = "deep_night"
                elif 6 <= hour <= 11:
                    slot = "morning"
                elif 12 <= hour <= 17:
                    slot = "afternoon"
                elif 18 <= hour <= 22:
                    slot = "evening"
                else:
                    slot = "late_night"
                    
                time_outcomes[slot].append({
                    "score": score,
                    "hour": hour,
                    "weekday": timestamp.weekday()
                })
            except:
                continue
        
        results = {}
        for slot, outcomes in time_outcomes.items():
            if len(outcomes) < 3:
                continue
                
            scores = [o["score"] for o in outcomes]
            results[slot] = {
                "average_score": statistics.mean(scores),
                "peak_hours": Counter(o["hour"] for o in outcomes).most_common(2),
                "best_weekdays": Counter(o["weekday"] for o in outcomes).most_common(3),
                "total_activities": len(outcomes),
                "consistency": 1 - (statistics.stdev(scores) / (statistics.mean(scores) + 0.1))
            }
        
        return results
    
    def detect_ruts(self) -> List[Dict]:
        """Detect repetitive or stagnant patterns."""
        ruts = []
        
        # Recent activities (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        recent_activities = [
            a for a in self.history
            if datetime.fromisoformat(a["timestamp"].replace('Z', '+00:00')) > cutoff
        ]
        
        if len(recent_activities) < 10:
            return ruts
        
        # Check for mood stagnation
        recent_moods = []
        for activity in recent_activities:
            date = activity["timestamp"][:10]
            for mood_entry in self.mood_history:
                if mood_entry["date"] == date:
                    recent_moods.append(mood_entry["mood_id"])
                    break
        
        if len(set(recent_moods)) <= 2 and len(recent_moods) > 5:
            most_common = Counter(recent_moods).most_common(1)[0]
            ruts.append({
                "type": "mood_stagnation",
                "description": f"Stuck in {most_common[0]} mood for {most_common[1]} recent sessions",
                "severity": "medium",
                "recommendation": "Try deliberately selecting different moods"
            })
        
        # Check for thought pattern repetition
        recent_thoughts = [a.get("thought_id", "") for a in recent_activities]
        thought_counts = Counter(recent_thoughts)
        total_recent = len(recent_activities)
        
        for thought, count in thought_counts.items():
            if thought and count / total_recent > 0.4:  # Over 40% repetition
                ruts.append({
                    "type": "thought_repetition", 
                    "description": f"Over-relying on '{thought}' ({count}/{total_recent} recent activities)",
                    "severity": "low",
                    "recommendation": f"Reduce weight of '{thought}' temporarily"
                })
        
        # Check for declining performance trend
        recent_scores = [self._calculate_value_score(a) for a in recent_activities[-10:]]
        if len(recent_scores) >= 5:
            trend = self._calculate_trend(recent_scores)
            if trend < -0.3:  # Declining trend
                ruts.append({
                    "type": "performance_decline",
                    "description": f"Performance declining over recent activities (trend: {trend:.2f})",
                    "severity": "high",
                    "recommendation": "Review recent patterns and adjust strategies"
                })
        
        return ruts
    
    def _calculate_trend(self, scores: List[float]) -> float:
        """Calculate linear trend of scores (-1 to 1)."""
        if len(scores) < 2:
            return 0
        
        n = len(scores)
        x = list(range(n))
        y = scores
        
        # Simple linear regression slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
        
        slope = numerator / denominator
        
        # Normalize to -1 to 1 range
        max_slope = max(y) - min(y)  # Maximum possible slope
        if max_slope == 0:
            return 0
        
        return max(-1, min(1, slope / max_slope * (n - 1)))
    
    def _discover_patterns(self) -> List[Dict]:
        """Discover new behavioral patterns."""
        patterns = []
        
        mood_effectiveness = self.analyze_mood_effectiveness()
        thought_effectiveness = self.analyze_thought_effectiveness()
        time_patterns = self.analyze_time_patterns()
        
        # Mood correlation patterns
        for mood, data in mood_effectiveness.items():
            if data["total_activities"] >= 5 and data["average_score"] >= 7:
                patterns.append({
                    "id": str(uuid.uuid4()),
                    "discovered": datetime.now().isoformat(),
                    "type": "mood_correlation",
                    "description": f"{mood.title()} mood produces high-value outcomes (avg: {data['average_score']:.1f})",
                    "confidence": min(0.95, data["consistency"] * 0.7 + 0.3),
                    "evidence_count": data["total_activities"],
                    "actionable": True,
                    "recommendation": f"Increase weight for {mood} mood",
                    "data": {"mood": mood, "score": data["average_score"], "consistency": data["consistency"]}
                })
        
        # Time pattern discoveries
        for slot, data in time_patterns.items():
            if data["average_score"] >= 7 and data["total_activities"] >= 5:
                patterns.append({
                    "id": str(uuid.uuid4()),
                    "discovered": datetime.now().isoformat(),
                    "type": "time_pattern",
                    "description": f"{slot.title()} is highly productive (avg: {data['average_score']:.1f})",
                    "confidence": min(0.9, data["consistency"] * 0.8 + 0.2),
                    "evidence_count": data["total_activities"],
                    "actionable": True,
                    "recommendation": f"Schedule important activities during {slot}",
                    "data": {"time_slot": slot, "score": data["average_score"], "peak_hours": data["peak_hours"]}
                })
        
        # Thought-mood synergy patterns
        for mood, thoughts in thought_effectiveness.items():
            best_thoughts = [(t, d) for t, d in thoughts.items() if d["average_score"] >= 7 and d["total_attempts"] >= 3]
            for thought_id, data in best_thoughts:
                patterns.append({
                    "id": str(uuid.uuid4()),
                    "discovered": datetime.now().isoformat(),
                    "type": "sequence",
                    "description": f"{thought_id} + {mood} mood = high effectiveness (avg: {data['average_score']:.1f})",
                    "confidence": min(0.9, data["success_rate"] * 0.6 + data["consistency"] * 0.4),
                    "evidence_count": data["total_attempts"],
                    "actionable": True,
                    "recommendation": f"Prefer {thought_id} when in {mood} mood",
                    "data": {"mood": mood, "thought": thought_id, "score": data["average_score"]}
                })
        
        return patterns
    
    def _calculate_weight_adjustments(self, patterns: List[Dict]) -> Dict:
        """Calculate weight adjustments based on discovered patterns."""
        mood_adjustments = {}
        thought_adjustments = {}
        
        # Base all moods at 1.0 initially
        all_moods = set()
        for pattern in patterns:
            if pattern["type"] in ["mood_correlation", "sequence"] and "mood" in pattern.get("data", {}):
                all_moods.add(pattern["data"]["mood"])
        
        for mood in all_moods:
            mood_adjustments[mood] = 1.0
        
        # Apply pattern-based adjustments
        for pattern in patterns:
            if not pattern["actionable"] or pattern["confidence"] < 0.5:
                continue
            
            data = pattern.get("data", {})
            confidence_weight = pattern["confidence"]
            
            if pattern["type"] == "mood_correlation" and "mood" in data:
                mood = data["mood"]
                score = data["score"]
                # High-scoring moods get boosted
                if score >= 7:
                    adjustment = 1.0 + (score - 6) * 0.1 * confidence_weight
                    mood_adjustments[mood] = max(mood_adjustments.get(mood, 1.0), adjustment)
                elif score <= 4:
                    # Low-scoring moods get reduced
                    adjustment = 1.0 - (5 - score) * 0.05 * confidence_weight
                    mood_adjustments[mood] = min(mood_adjustments.get(mood, 1.0), adjustment)
            
            elif pattern["type"] == "sequence" and "thought" in data:
                thought = data["thought"]
                score = data["score"]
                if score >= 7:
                    adjustment = 1.0 + (score - 6) * 0.05 * confidence_weight
                    thought_adjustments[thought] = max(thought_adjustments.get(thought, 1.0), adjustment)
        
        return {"moods": mood_adjustments, "thoughts": thought_adjustments}
    
    def evolve(self) -> Dict:
        """Run full evolution cycle."""
        print("🧬 Starting evolution cycle...")
        
        # Discover new patterns
        new_patterns = self._discover_patterns()
        
        # Filter out patterns we already know
        existing_pattern_keys = set()
        for p in self.learnings["patterns"]:
            key = f"{p['type']}:{p.get('data', {}).get('mood', '')}:{p.get('data', {}).get('thought', '')}"
            existing_pattern_keys.add(key)
        
        truly_new_patterns = []
        for pattern in new_patterns:
            key = f"{pattern['type']}:{pattern.get('data', {}).get('mood', '')}:{pattern.get('data', {}).get('thought', '')}"
            if key not in existing_pattern_keys:
                truly_new_patterns.append(pattern)
        
        # Add new patterns
        self.learnings["patterns"].extend(truly_new_patterns)
        
        # Calculate weight adjustments
        all_patterns = self.learnings["patterns"]
        weight_adjustments = self._calculate_weight_adjustments(all_patterns)
        
        # Update learned weights
        self.learned_weights.update(weight_adjustments)
        self.learnings["weight_adjustments"] = weight_adjustments
        
        # Record evolution event
        evolution_event = {
            "timestamp": datetime.now().isoformat(),
            "new_patterns_discovered": len(truly_new_patterns),
            "total_patterns": len(self.learnings["patterns"]),
            "weight_adjustments_made": len(weight_adjustments["moods"]) + len(weight_adjustments["thoughts"]),
            "ruts_detected": len(self.detect_ruts())
        }
        
        self.learnings["evolution_history"].append(evolution_event)
        
        # Save everything
        self._save_learnings()
        self._save_learned_weights()
        
        print(f"✅ Evolution complete: {len(truly_new_patterns)} new patterns discovered")
        
        return {
            "new_patterns": truly_new_patterns,
            "weight_adjustments": weight_adjustments,
            "evolution_event": evolution_event,
            "ruts": self.detect_ruts()
        }
    
    def reflect(self) -> str:
        """Generate a text summary of recent patterns and learnings."""
        mood_effectiveness = self.analyze_mood_effectiveness()
        ruts = self.detect_ruts()
        recent_patterns = [p for p in self.learnings["patterns"] 
                          if datetime.fromisoformat(p["discovered"]) > datetime.now() - timedelta(days=30)]
        
        reflection = ["🤔 SELF-REFLECTION", "=" * 40]
        
        # Performance summary
        if mood_effectiveness:
            best_mood = max(mood_effectiveness.items(), key=lambda x: x[1]["average_score"])
            worst_mood = min(mood_effectiveness.items(), key=lambda x: x[1]["average_score"])
            
            reflection.extend([
                "",
                "📊 Recent Performance:",
                f"  • Best mood: {best_mood[0]} (avg score: {best_mood[1]['average_score']:.1f})",
                f"  • Challenging mood: {worst_mood[0]} (avg score: {worst_mood[1]['average_score']:.1f})",
                f"  • Total moods analyzed: {len(mood_effectiveness)}"
            ])
        
        # Patterns learned
        if recent_patterns:
            reflection.extend([
                "",
                f"🧠 Recent Insights ({len(recent_patterns)} patterns discovered):"
            ])
            for pattern in recent_patterns[:5]:  # Top 5 recent patterns
                reflection.append(f"  • {pattern['description']} (confidence: {pattern['confidence']:.0%})")
        
        # Current ruts/issues
        if ruts:
            reflection.extend([
                "",
                f"⚠️ Current Challenges ({len(ruts)} detected):"
            ])
            for rut in ruts:
                reflection.append(f"  • {rut['description']}")
        
        # Evolution stats
        evolution_history = self.learnings.get("evolution_history", [])
        if evolution_history:
            latest = evolution_history[-1]
            reflection.extend([
                "",
                "🔄 Evolution Status:",
                f"  • Last evolution: {latest['timestamp'][:10]}",
                f"  • Total patterns learned: {latest['total_patterns']}",
                f"  • Active weight adjustments: {latest['weight_adjustments_made']}"
            ])
        
        return "\n".join(reflection)
    
    def diagnose(self) -> List[Dict]:
        """Identify current problems and issues."""
        issues = []
        
        # Add detected ruts as issues
        ruts = self.detect_ruts()
        issues.extend([{"type": "behavioral", **rut} for rut in ruts])
        
        # Check for data quality issues
        if len(self.history) < 10:
            issues.append({
                "type": "data_quality",
                "severity": "high",
                "description": f"Insufficient activity data ({len(self.history)} activities)",
                "recommendation": "Use the system more to generate learning data"
            })
        
        if len(self.mood_history) < 5:
            issues.append({
                "type": "data_quality", 
                "severity": "high",
                "description": f"Insufficient mood data ({len(self.mood_history)} mood records)",
                "recommendation": "Ensure mood tracking is working properly"
            })
        
        # Check for learning stagnation
        evolution_history = self.learnings.get("evolution_history", [])
        if not evolution_history:
            issues.append({
                "type": "learning",
                "severity": "medium",
                "description": "No evolution cycles have been run yet",
                "recommendation": "Run first evolution cycle to begin learning"
            })
        elif len(evolution_history) > 0:
            last_evolution = datetime.fromisoformat(evolution_history[-1]["timestamp"])
            if datetime.now() - last_evolution > timedelta(days=7):
                issues.append({
                    "type": "learning",
                    "severity": "medium",
                    "description": f"No evolution cycle for {(datetime.now() - last_evolution).days} days",
                    "recommendation": "Run evolution cycle to update learnings"
                })
        
        # Check for weight adjustment effectiveness
        if self.learned_weights.get("moods") or self.learned_weights.get("thoughts"):
            # TODO: Add logic to check if weight adjustments are actually improving outcomes
            pass
        
        return issues
    
    def prescribe(self) -> List[str]:
        """Suggest specific changes based on diagnosis."""
        issues = self.diagnose()
        recommendations = []
        
        for issue in issues:
            if issue["severity"] == "high":
                recommendations.append(f"🔴 {issue['recommendation']}")
            elif issue["severity"] == "medium":
                recommendations.append(f"🟡 {issue['recommendation']}")
            else:
                recommendations.append(f"🟢 {issue['recommendation']}")
        
        # Add positive suggestions
        mood_effectiveness = self.analyze_mood_effectiveness()
        if mood_effectiveness:
            best_moods = [mood for mood, data in mood_effectiveness.items() 
                         if data["average_score"] >= 7]
            if best_moods:
                recommendations.append(f"✅ Focus on high-performing moods: {', '.join(best_moods)}")
        
        return recommendations
    
    def get_recommendations(self) -> List[str]:
        """Get actionable recommendations."""
        return self.prescribe()
    
    def get_learned_weights(self) -> Dict:
        """Return current learned weight adjustments."""
        return self.learned_weights
    
    def get_stats(self) -> Dict:
        """Return evolution statistics."""
        return {
            "total_patterns": len(self.learnings["patterns"]),
            "evolution_cycles": len(self.learnings.get("evolution_history", [])),
            "last_evolution": self.learnings.get("last_evolution"),
            "weight_adjustments": {
                "moods": len(self.learned_weights.get("moods", {})),
                "thoughts": len(self.learned_weights.get("thoughts", {}))
            },
            "data_quality": {
                "activities": len(self.history),
                "mood_records": len(self.mood_history),
                "patterns_discovered": len(self.learnings["patterns"])
            }
        }


def main():
    """CLI interface for self-evolution system."""
    import sys
    
    system = SelfEvolutionSystem()
    
    if len(sys.argv) < 2:
        print("Usage: python self_evolution.py <command>")
        print("Commands: evolve, reflect, diagnose, prescribe, recommendations, weights, stats")
        return
    
    command = sys.argv[1]
    
    if command == "evolve":
        result = system.evolve()
        print(f"\n🧬 EVOLUTION COMPLETE")
        print(f"New patterns: {len(result['new_patterns'])}")
        print(f"Weight adjustments: {len(result['weight_adjustments']['moods'])} moods, {len(result['weight_adjustments']['thoughts'])} thoughts")
        print(f"Ruts detected: {len(result['ruts'])}")
        
        if result['new_patterns']:
            print(f"\n📈 NEW PATTERNS DISCOVERED:")
            for pattern in result['new_patterns'][:3]:  # Show top 3
                print(f"  • {pattern['description']} (confidence: {pattern['confidence']:.0%})")
    
    elif command == "reflect":
        print(system.reflect())
    
    elif command == "diagnose":
        issues = system.diagnose()
        print("🔍 DIAGNOSIS REPORT")
        print("=" * 30)
        
        if not issues:
            print("✅ No significant issues detected")
        else:
            for issue in issues:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"{severity_emoji.get(issue['severity'], '⚪')} {issue['description']}")
    
    elif command in ["prescribe", "recommendations"]:
        recommendations = system.prescribe()
        print("💊 RECOMMENDATIONS")
        print("=" * 25)
        
        if not recommendations:
            print("✅ No specific recommendations at this time")
        else:
            for rec in recommendations:
                print(f"  {rec}")
    
    elif command == "weights":
        weights = system.get_learned_weights()
        print("⚖️ LEARNED WEIGHT ADJUSTMENTS")
        print("=" * 35)
        
        if weights.get("moods"):
            print("\n🧠 Mood Adjustments:")
            for mood, weight in sorted(weights["moods"].items(), key=lambda x: x[1], reverse=True):
                emoji = "📈" if weight > 1.0 else "📉" if weight < 1.0 else "➖"
                print(f"  {emoji} {mood}: {weight:.2f}x")
        
        if weights.get("thoughts"):
            print("\n💭 Thought Adjustments:")
            for thought, weight in sorted(weights["thoughts"].items(), key=lambda x: x[1], reverse=True):
                emoji = "📈" if weight > 1.0 else "📉" if weight < 1.0 else "➖"
                print(f"  {emoji} {thought}: {weight:.2f}x")
        
        if not weights.get("moods") and not weights.get("thoughts"):
            print("No weight adjustments learned yet. Run 'evolve' first.")
    
    elif command == "stats":
        stats = system.get_stats()
        print("📊 EVOLUTION STATISTICS")
        print("=" * 30)
        print(f"Patterns discovered: {stats['total_patterns']}")
        print(f"Evolution cycles run: {stats['evolution_cycles']}")
        print(f"Last evolution: {stats['last_evolution'][:10] if stats['last_evolution'] else 'Never'}")
        print(f"Weight adjustments: {stats['weight_adjustments']['moods']} moods, {stats['weight_adjustments']['thoughts']} thoughts")
        print(f"Data available: {stats['data_quality']['activities']} activities, {stats['data_quality']['mood_records']} mood records")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()