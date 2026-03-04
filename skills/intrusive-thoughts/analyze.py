#!/usr/bin/env python3
"""📊 Productivity Correlation — Analyze which moods and times produce best outcomes."""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import statistics
from config import get_file_path

HISTORY_FILE = get_file_path("history.json")
MOOD_HISTORY_FILE = get_file_path("mood_history.json")

def load_history():
    """Load activity history."""
    try:
        return json.loads(HISTORY_FILE.read_text())
    except:
        return []

def load_mood_history():
    """Load mood history."""
    try:
        data = json.loads(MOOD_HISTORY_FILE.read_text())
        return data.get("history", [])
    except:
        return []

def calculate_outcome_score(entry):
    """Calculate productivity score for an activity (0-10 scale)."""
    energy = entry.get("energy", "neutral")
    vibe = entry.get("vibe", "neutral")
    
    # Energy scoring
    energy_score = {"high": 3, "neutral": 1, "low": -1}.get(energy, 0)
    
    # Vibe scoring  
    vibe_score = {"positive": 3, "neutral": 1, "negative": -1}.get(vibe, 0)
    
    # Thought type scoring (some activities are inherently more "productive")
    thought_scores = {
        "build-tool": 4,
        "upgrade-project": 4,
        "system-tinker": 3,
        "learn": 3,
        "moltbook-post": 2,
        "memory-review": 2,
        "install-explore": 2,
        "creative-chaos": 3,  # Creative work is valuable
        "moltbook-social": 1,
        "share-discovery": 2,
        "ask-opinion": 1,
        "random-thought": 1
    }
    
    thought_score = thought_scores.get(entry.get("thought_id", ""), 1)
    
    # Combine scores (max 10)
    total = energy_score + vibe_score + thought_score
    return max(0, min(10, total))

def analyze_mood_productivity():
    """Analyze productivity by mood."""
    history = load_history()
    mood_history = load_mood_history()
    
    # Create date -> mood mapping
    mood_by_date = {}
    for mood_entry in mood_history:
        mood_by_date[mood_entry["date"]] = mood_entry["mood_id"]
    
    # Group activities by mood
    mood_outcomes = defaultdict(list)
    
    for activity in history:
        date = activity["timestamp"][:10]  # Extract YYYY-MM-DD
        mood = mood_by_date.get(date, "unknown")
        score = calculate_outcome_score(activity)
        
        mood_outcomes[mood].append({
            "score": score,
            "energy": activity.get("energy", "neutral"),
            "vibe": activity.get("vibe", "neutral"),
            "thought_id": activity.get("thought_id", "unknown")
        })
    
    # Analyze each mood
    results = {}
    for mood, outcomes in mood_outcomes.items():
        if len(outcomes) < 3:  # Need minimum sample size
            continue
            
        scores = [o["score"] for o in outcomes]
        high_energy = sum(1 for o in outcomes if o["energy"] == "high")
        positive_vibe = sum(1 for o in outcomes if o["vibe"] == "positive")
        
        results[mood] = {
            "average_score": round(statistics.mean(scores), 2),
            "median_score": statistics.median(scores),
            "total_activities": len(outcomes),
            "high_energy_rate": round(high_energy / len(outcomes) * 100, 1),
            "positive_vibe_rate": round(positive_vibe / len(outcomes) * 100, 1),
            "productivity_grade": get_productivity_grade(statistics.mean(scores)),
            "top_activities": Counter(o["thought_id"] for o in outcomes).most_common(3)
        }
    
    return results

def analyze_time_productivity():
    """Analyze productivity by time of day."""
    history = load_history()
    
    time_outcomes = defaultdict(list)
    
    for activity in history:
        try:
            timestamp = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
            hour = timestamp.hour
            score = calculate_outcome_score(activity)
            
            # Group into time slots
            if 3 <= hour <= 6:
                slot = "night_deep"
            elif 7 <= hour <= 11:
                slot = "morning"
            elif 12 <= hour <= 17:
                slot = "afternoon"
            elif 18 <= hour <= 22:
                slot = "evening"
            else:
                slot = "late_night"
                
            time_outcomes[slot].append(score)
        except:
            continue
    
    results = {}
    for slot, scores in time_outcomes.items():
        if len(scores) < 2:
            continue
            
        results[slot] = {
            "average_score": round(statistics.mean(scores), 2),
            "total_activities": len(scores),
            "productivity_grade": get_productivity_grade(statistics.mean(scores)),
            "best_hours": slot
        }
    
    return results

def analyze_activity_success():
    """Analyze which activity types are most successful."""
    history = load_history()
    
    activity_outcomes = defaultdict(list)
    
    for activity in history:
        thought_id = activity.get("thought_id", "unknown")
        score = calculate_outcome_score(activity)
        activity_outcomes[thought_id].append(score)
    
    results = {}
    for activity, scores in activity_outcomes.items():
        if len(scores) < 2:
            continue
            
        results[activity] = {
            "average_score": round(statistics.mean(scores), 2),
            "total_attempts": len(scores),
            "success_rate": round(sum(1 for s in scores if s >= 6) / len(scores) * 100, 1),
            "productivity_grade": get_productivity_grade(statistics.mean(scores))
        }
    
    return results

def get_productivity_grade(score):
    """Convert numeric score to letter grade."""
    if score >= 8:
        return "A+"
    elif score >= 7:
        return "A"
    elif score >= 6:
        return "B+"
    elif score >= 5:
        return "B"
    elif score >= 4:
        return "C+"
    elif score >= 3:
        return "C"
    else:
        return "D"

def generate_insights():
    """Generate actionable insights from the analysis."""
    mood_analysis = analyze_mood_productivity()
    time_analysis = analyze_time_productivity()
    activity_analysis = analyze_activity_success()
    
    insights = []
    
    # Best mood insight
    if mood_analysis:
        best_mood = max(mood_analysis.items(), key=lambda x: x[1]["average_score"])
        insights.append(f"🔥 Best mood: {best_mood[0]} (avg score: {best_mood[1]['average_score']}) - {best_mood[1]['high_energy_rate']}% high-energy outcomes")
    
    # Best time insight
    if time_analysis:
        best_time = max(time_analysis.items(), key=lambda x: x[1]["average_score"])
        insights.append(f"⏰ Best time slot: {best_time[0]} (avg score: {best_time[1]['average_score']})")
    
    # Best activity insight
    if activity_analysis:
        best_activity = max(activity_analysis.items(), key=lambda x: x[1]["average_score"])
        insights.append(f"🎯 Best activity: {best_activity[0]} (avg score: {best_activity[1]['average_score']}, {best_activity[1]['success_rate']}% success rate)")
    
    # Low performers
    if mood_analysis:
        low_moods = [mood for mood, data in mood_analysis.items() if data["average_score"] < 4]
        if low_moods:
            insights.append(f"⚠️ Challenging moods: {', '.join(low_moods)} - might need different strategies")
    
    return insights

def main():
    """CLI interface for productivity analysis."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON output for dashboard
        result = {
            "moods": analyze_mood_productivity(),
            "times": analyze_time_productivity(), 
            "activities": analyze_activity_success(),
            "insights": generate_insights(),
            "generated_at": datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
        return
    
    # Human-readable output
    print("📊 PRODUCTIVITY CORRELATION ANALYSIS")
    print("=" * 50)
    
    print("\n🧠 MOOD PRODUCTIVITY:")
    mood_results = analyze_mood_productivity()
    for mood, data in sorted(mood_results.items(), key=lambda x: x[1]["average_score"], reverse=True):
        print(f"  {mood:15} | {data['productivity_grade']:2} | {data['average_score']:4.1f} avg | {data['high_energy_rate']:4.1f}% high-energy | {data['positive_vibe_rate']:4.1f}% positive")
    
    print("\n⏰ TIME SLOT PRODUCTIVITY:")
    time_results = analyze_time_productivity()
    for slot, data in sorted(time_results.items(), key=lambda x: x[1]["average_score"], reverse=True):
        print(f"  {slot:15} | {data['productivity_grade']:2} | {data['average_score']:4.1f} avg | {data['total_activities']:3} activities")
    
    print("\n🎯 ACTIVITY SUCCESS RATES:")
    activity_results = analyze_activity_success()
    for activity, data in sorted(activity_results.items(), key=lambda x: x[1]["average_score"], reverse=True):
        print(f"  {activity:20} | {data['productivity_grade']:2} | {data['average_score']:4.1f} avg | {data['success_rate']:4.1f}% success")
    
    print("\n💡 KEY INSIGHTS:")
    insights = generate_insights()
    for insight in insights:
        print(f"  • {insight}")
    
    print(f"\nAnalysis based on {len(load_history())} activities")

if __name__ == "__main__":
    main()