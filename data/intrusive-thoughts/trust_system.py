#!/usr/bin/env python3
"""
Trust & Escalation System for Intrusive Thoughts AI

Tracks action outcomes to learn when the agent should act autonomously 
vs ask for permission. Integrates with mood system for risk tolerance.
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import math

class TrustSystem:
    def __init__(self, data_dir: str = "trust_store"):
        """Initialize trust system with data directory"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "trust_data.json"
        self.load_data()
    
    def load_data(self):
        """Load trust data from JSON file or initialize defaults"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            # Ensure all required keys exist for backward compatibility
            if "escalation_patterns" not in self.data:
                self.data["escalation_patterns"] = []
            if "last_decay" not in self.data:
                self.data["last_decay"] = time.time()
        else:
            self.data = {
                "trust_level": 0.5,  # Global trust level (0-1)
                "action_categories": {
                    "file_operations": {"trust": 0.8, "successes": 0, "failures": 0, "escalations": 0},
                    "messaging": {"trust": 0.6, "successes": 0, "failures": 0, "escalations": 0},
                    "external_api": {"trust": 0.3, "successes": 0, "failures": 0, "escalations": 0},
                    "system_changes": {"trust": 0.4, "successes": 0, "failures": 0, "escalations": 0},
                    "web_operations": {"trust": 0.7, "successes": 0, "failures": 0, "escalations": 0},
                    "code_execution": {"trust": 0.5, "successes": 0, "failures": 0, "escalations": 0}
                },
                "history": [],  # Recent action logs
                "escalation_patterns": [],  # Learned patterns of when human says no
                "last_decay": time.time()  # For time-based trust decay
            }
            self.save_data()
    
    def save_data(self):
        """Save trust data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_current_mood(self) -> Dict[str, Any]:
        """Get current mood from mood system for risk tolerance adjustment"""
        try:
            mood_file = Path("today_mood.json")
            if mood_file.exists():
                with open(mood_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {"mood": "cozy", "intensity": 0.5}  # Safe default
    
    def get_mood_risk_modifier(self, mood: str, intensity: float) -> float:
        """Get risk tolerance modifier based on current mood"""
        mood_modifiers = {
            "hyperfocus": 0.1,      # Higher risk tolerance when focused
            "determined": 0.05,     # Slightly higher
            "cozy": 0.0,           # Standard tolerance
            "curious": 0.0,        # Standard
            "social": 0.0,         # Standard
            "philosophical": 0.0,   # Standard
            "chaotic": -0.15,      # Lower tolerance (might do something regrettable)
            "restless": -0.1       # Lower tolerance (rushing = mistakes)
        }
        
        base_modifier = mood_modifiers.get(mood, 0.0)
        # Scale by intensity (0.5 = no effect, higher = stronger effect)
        return base_modifier * (intensity - 0.5) * 2
    
    def get_risk_level(self, action_type: str, context: Dict[str, Any]) -> str:
        """Determine risk level for an action"""
        # Risk keywords that bump up the risk level
        high_risk_keywords = [
            "delete", "remove", "destroy", "format", "drop", "truncate",
            "public", "post", "tweet", "broadcast", "send", "email",
            "install", "sudo", "chmod", "chown", "rm -rf"
        ]
        
        critical_risk_keywords = [
            "financial", "payment", "money", "bitcoin", "transaction",
            "production", "live", "deploy", "publish", "release"
        ]
        
        context_str = str(context).lower()
        
        # Check for critical risk keywords first
        if any(keyword in context_str for keyword in critical_risk_keywords):
            return "critical"
        
        # Action type based risk levels
        type_risks = {
            "file_operations": "low",
            "messaging": "high",
            "external_api": "medium", 
            "system_changes": "high",
            "web_operations": "low",
            "code_execution": "medium"
        }
        
        base_risk = type_risks.get(action_type, "medium")
        
        # Escalate based on keywords
        if any(keyword in context_str for keyword in high_risk_keywords):
            if base_risk == "low":
                return "medium"
            elif base_risk == "medium":
                return "high"
            elif base_risk == "high":
                return "critical"
        
        return base_risk
    
    def get_risk_assessment(self, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive risk assessment for an action"""
        risk_level = self.get_risk_level(action_type, context)
        category_trust = self.get_trust_level(action_type)
        global_trust = self.get_trust_level()
        
        # Risk thresholds for auto-proceeding
        risk_thresholds = {
            "low": 0.6,
            "medium": 0.75,
            "high": 0.85,
            "critical": 0.95
        }
        
        threshold = risk_thresholds[risk_level]
        effective_trust = (category_trust + global_trust) / 2
        
        # Apply mood modifier
        mood_data = self.get_current_mood()
        mood_modifier = self.get_mood_risk_modifier(
            mood_data.get("mood", "cozy"), 
            mood_data.get("intensity", 0.5)
        )
        
        adjusted_trust = min(1.0, max(0.0, effective_trust + mood_modifier))
        
        should_proceed = adjusted_trust >= threshold
        confidence = abs(adjusted_trust - threshold) / threshold
        
        recommendation = "proceed" if should_proceed else "escalate"
        
        return {
            "risk_level": risk_level,
            "category_trust": category_trust,
            "global_trust": global_trust,
            "mood_modifier": mood_modifier,
            "adjusted_trust": adjusted_trust,
            "threshold": threshold,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": f"Risk: {risk_level}, Trust: {adjusted_trust:.2f}, Threshold: {threshold:.2f}"
        }
    
    def should_escalate(self, action_type: str, risk_level: str, context: Dict[str, Any]) -> Tuple[bool, float]:
        """Determine if an action should be escalated with confidence level"""
        assessment = self.get_risk_assessment(action_type, context)
        should_escalate = assessment["recommendation"] == "escalate"
        return should_escalate, assessment["confidence"]
    
    def log_action(self, action_type: str, description: str, outcome: str, human_feedback: Optional[str] = None):
        """Log an action outcome and update trust levels"""
        timestamp = time.time()
        
        # Add to history
        log_entry = {
            "timestamp": timestamp,
            "action_type": action_type,
            "description": description,
            "outcome": outcome,
            "human_feedback": human_feedback,
            "date": datetime.fromtimestamp(timestamp).isoformat()
        }
        
        self.data["history"].append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.data["history"]) > 1000:
            self.data["history"] = self.data["history"][-1000:]
        
        # Update trust levels based on outcome
        if action_type in self.data["action_categories"]:
            category = self.data["action_categories"][action_type]
            
            if outcome == "success":
                category["successes"] += 1
                # Success increases trust by 0.02 * (1 - current_trust) (harder to gain at top)
                trust_increase = 0.02 * (1 - category["trust"])
                category["trust"] = min(1.0, category["trust"] + trust_increase)
                
                # Also slightly increase global trust
                global_increase = 0.01 * (1 - self.data["trust_level"])
                self.data["trust_level"] = min(1.0, self.data["trust_level"] + global_increase)
                
            elif outcome == "failure":
                category["failures"] += 1
                # Failure decreases trust by 0.1 * current_trust (proportional loss)
                trust_decrease = 0.1 * category["trust"]
                category["trust"] = max(0.0, category["trust"] - trust_decrease)
                
                # Also decrease global trust
                global_decrease = 0.05 * self.data["trust_level"]
                self.data["trust_level"] = max(0.0, self.data["trust_level"] - global_decrease)
        
        self.save_data()
    
    def log_escalation(self, action_type: str, description: str, human_response: str):
        """Log an escalation and track patterns"""
        timestamp = time.time()
        
        escalation_entry = {
            "timestamp": timestamp,
            "action_type": action_type,
            "description": description,
            "human_response": human_response,
            "date": datetime.fromtimestamp(timestamp).isoformat()
        }
        
        self.data["escalation_patterns"].append(escalation_entry)
        
        # Keep only last 500 escalation entries
        if len(self.data["escalation_patterns"]) > 500:
            self.data["escalation_patterns"] = self.data["escalation_patterns"][-500:]
        
        # Update escalation count
        if action_type in self.data["action_categories"]:
            self.data["action_categories"][action_type]["escalations"] += 1
            
            # If human says "yes, go ahead" -> small trust increase
            if any(word in human_response.lower() for word in ["yes", "ok", "proceed", "go", "fine"]):
                category = self.data["action_categories"][action_type]
                trust_increase = 0.01 * (1 - category["trust"])
                category["trust"] = min(1.0, category["trust"] + trust_increase)
            
            # If human says "no" -> trust decrease + pattern learning
            elif any(word in human_response.lower() for word in ["no", "stop", "don't", "cancel", "abort"]):
                category = self.data["action_categories"][action_type]
                trust_decrease = 0.05 * category["trust"]
                category["trust"] = max(0.0, category["trust"] - trust_decrease)
        
        self.save_data()
    
    def get_trust_level(self, category: Optional[str] = None) -> float:
        """Get trust level for a category or global trust"""
        if category is None:
            return self.data["trust_level"]
        
        if category in self.data["action_categories"]:
            return self.data["action_categories"][category]["trust"]
        
        return 0.5  # Default for unknown categories
    
    def adjust_trust(self, category: str, delta: float, reason: str):
        """Manually adjust trust level"""
        if category == "global":
            self.data["trust_level"] = max(0.0, min(1.0, self.data["trust_level"] + delta))
        elif category in self.data["action_categories"]:
            cat = self.data["action_categories"][category]
            cat["trust"] = max(0.0, min(1.0, cat["trust"] + delta))
        
        # Log the manual adjustment
        self.log_action(category, f"Manual adjustment: {reason}", "adjustment")
        self.save_data()
    
    def apply_time_decay(self):
        """Apply time-based trust decay (slowly regress toward 0.5)"""
        now = time.time()
        last_decay = self.data.get("last_decay", now)
        
        # Decay every 24 hours
        hours_passed = (now - last_decay) / 3600
        if hours_passed >= 24:
            decay_factor = 0.01 * (hours_passed / 24)  # 1% decay per day
            
            # Decay global trust toward 0.5
            if self.data["trust_level"] > 0.5:
                self.data["trust_level"] = max(0.5, self.data["trust_level"] - decay_factor)
            else:
                self.data["trust_level"] = min(0.5, self.data["trust_level"] + decay_factor)
            
            # Decay category trust toward 0.5
            for category in self.data["action_categories"].values():
                if category["trust"] > 0.5:
                    category["trust"] = max(0.5, category["trust"] - decay_factor)
                else:
                    category["trust"] = min(0.5, category["trust"] + decay_factor)
            
            self.data["last_decay"] = now
            self.save_data()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trust statistics for dashboard"""
        self.apply_time_decay()  # Apply decay before showing stats
        
        total_actions = sum(
            cat["successes"] + cat["failures"] 
            for cat in self.data["action_categories"].values()
        )
        
        total_successes = sum(
            cat["successes"] 
            for cat in self.data["action_categories"].values()
        )
        
        success_rate = total_successes / total_actions if total_actions > 0 else 0
        
        # Recent activity (last 7 days)
        week_ago = time.time() - (7 * 24 * 3600)
        recent_actions = [
            entry for entry in self.data["history"] 
            if entry["timestamp"] > week_ago
        ]
        
        mood_data = self.get_current_mood()
        
        return {
            "global_trust": self.data["trust_level"],
            "category_trust": {k: v["trust"] for k, v in self.data["action_categories"].items()},
            "category_stats": self.data["action_categories"],
            "total_actions": total_actions,
            "success_rate": success_rate,
            "recent_actions": len(recent_actions),
            "total_escalations": len(self.data["escalation_patterns"]),
            "current_mood": mood_data,
            "mood_risk_modifier": self.get_mood_risk_modifier(
                mood_data.get("mood", "cozy"),
                mood_data.get("intensity", 0.5)
            )
        }
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent action history"""
        return self.data["history"][-limit:]


# CLI convenience functions
def check_action(action_desc: str, category: str, risk: str = None) -> Dict[str, Any]:
    """Check if an action should be escalated"""
    trust = TrustSystem()
    context = {"description": action_desc}
    if risk:
        context["suggested_risk"] = risk
    
    return trust.get_risk_assessment(category, context)


def log_success(description: str, category: str):
    """Log a successful action"""
    trust = TrustSystem()
    trust.log_action(category, description, "success")
    print(f"✅ Logged success: {description}")


def log_failure(description: str, category: str, details: str = ""):
    """Log a failed action"""
    trust = TrustSystem()
    trust.log_action(category, f"{description} - {details}", "failure")
    print(f"❌ Logged failure: {description}")


def show_stats():
    """Show trust statistics"""
    trust = TrustSystem()
    stats = trust.get_stats()
    
    print(f"🔒 Trust & Escalation System Stats")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Global Trust: {stats['global_trust']:.2f}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"Total Actions: {stats['total_actions']}")
    print(f"Recent Actions (7d): {stats['recent_actions']}")
    print(f"Total Escalations: {stats['total_escalations']}")
    print(f"Current Mood: {stats['current_mood']['mood']} (modifier: {stats['mood_risk_modifier']:+.2f})")
    print()
    print("Category Trust Levels:")
    for category, trust_level in stats['category_trust'].items():
        category_stats = stats['category_stats'][category]
        print(f"  {category}: {trust_level:.2f} "
              f"({category_stats['successes']}✅ {category_stats['failures']}❌ "
              f"{category_stats['escalations']}⬆️)")


def show_history(limit: int = 20):
    """Show recent action history"""
    trust = TrustSystem()
    history = trust.get_history(limit)
    
    print(f"📚 Recent Action History (last {len(history)})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for entry in reversed(history):  # Show most recent first
        date = datetime.fromtimestamp(entry['timestamp']).strftime('%m-%d %H:%M')
        outcome_emoji = {"success": "✅", "failure": "❌", "adjustment": "⚙️"}.get(entry['outcome'], "❓")
        print(f"{date} {outcome_emoji} [{entry['action_type']}] {entry['description']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 trust_system.py [stats|history|check|log-success|log-failure]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "stats":
        show_stats()
    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        show_history(limit)
    elif command == "check" and len(sys.argv) >= 4:
        result = check_action(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
        print(f"Risk Assessment: {result['recommendation'].upper()}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
    elif command == "log-success" and len(sys.argv) >= 4:
        log_success(sys.argv[2], sys.argv[3])
    elif command == "log-failure" and len(sys.argv) >= 4:
        log_failure(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else:
        print("Invalid command or missing arguments")
        sys.exit(1)