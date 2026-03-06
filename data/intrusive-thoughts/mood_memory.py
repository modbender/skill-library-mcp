#!/usr/bin/env python3
"""🧠 Mood Memory — Track and analyze mood patterns across days."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar
from config import get_file_path, get_human_name

MOOD_HISTORY_FILE = get_file_path("mood_history.json")
TODAY_MOOD_FILE = get_file_path("today_mood.json")

def load_mood_history():
    """Load mood history, creating empty structure if needed."""
    try:
        return json.loads(MOOD_HISTORY_FILE.read_text())
    except:
        return {"version": 1, "history": []}

def save_mood_history(data):
    """Save mood history to file."""
    MOOD_HISTORY_FILE.write_text(json.dumps(data, indent=2))

def append_today_mood():
    """Append today's mood to history if not already recorded."""
    try:
        today_mood = json.loads(TODAY_MOOD_FILE.read_text())
        date = datetime.now().strftime("%Y-%m-%d")
        
        history = load_mood_history()
        
        # Check if today is already recorded
        existing = next((h for h in history["history"] if h["date"] == date), None)
        if existing:
            # Update existing entry
            existing.update({
                "mood_id": today_mood.get("drifted_to", today_mood.get("id")),
                "emoji": today_mood.get("emoji"),
                "name": today_mood.get("name"),
                "description": today_mood.get("description"),
                "energy_score": today_mood.get("energy_score", 0),
                "vibe_score": today_mood.get("vibe_score", 0),
                "activity_count": len(today_mood.get("activity_log", [])),
                "updated_at": datetime.now().isoformat()
            })
        else:
            # Add new entry
            history["history"].append({
                "date": date,
                "mood_id": today_mood.get("drifted_to", today_mood.get("id")),
                "emoji": today_mood.get("emoji"),
                "name": today_mood.get("name"), 
                "description": today_mood.get("description"),
                "energy_score": today_mood.get("energy_score", 0),
                "vibe_score": today_mood.get("vibe_score", 0),
                "activity_count": len(today_mood.get("activity_log", [])),
                "recorded_at": datetime.now().isoformat()
            })
        
        # Keep only last 90 days
        history["history"] = history["history"][-90:]
        save_mood_history(history)
        
    except Exception as e:
        print(f"Failed to append today's mood: {e}")

def analyze_patterns():
    """Analyze mood patterns and provide insights."""
    history = load_mood_history()["history"]
    if len(history) < 3:
        return {"error": "Need at least 3 days of history"}
    
    # Day-of-week patterns
    dow_moods = defaultdict(list)
    month_moods = defaultdict(list)
    
    for entry in history:
        date = datetime.strptime(entry["date"], "%Y-%m-%d")
        dow = calendar.day_name[date.weekday()]
        month = calendar.month_name[date.month]
        
        dow_moods[dow].append(entry["mood_id"])
        month_moods[month].append(entry["mood_id"])
    
    # Most common mood overall
    all_moods = [entry["mood_id"] for entry in history]
    mood_counts = Counter(all_moods)
    
    # Recent trend (last 7 days)
    recent_moods = [entry["mood_id"] for entry in history[-7:]]
    
    # Productivity patterns (energy + vibe scores)
    productive_moods = []
    for entry in history:
        if entry.get("energy_score", 0) >= 1 and entry.get("vibe_score", 0) >= 1:
            productive_moods.append(entry["mood_id"])
    
    return {
        "total_days": len(history),
        "most_common_mood": mood_counts.most_common(1)[0] if mood_counts else ("unknown", 0),
        "day_of_week_patterns": {
            day: Counter(moods).most_common(1)[0] if moods else ("none", 0)
            for day, moods in dow_moods.items()
        },
        "monthly_patterns": {
            month: Counter(moods).most_common(1)[0] if moods else ("none", 0) 
            for month, moods in month_moods.items()
        },
        "recent_trend": recent_moods,
        "productive_moods": Counter(productive_moods).most_common(3),
        "mood_distribution": dict(mood_counts)
    }

def suggest_mood():
    """Suggest mood based on historical patterns."""
    try:
        patterns = analyze_patterns()
        if "error" in patterns:
            return {"suggestion": "curious", "reason": "No history available"}
        
        today = datetime.now()
        dow = calendar.day_name[today.weekday()]
        month = calendar.month_name[today.month]
        
        # Get patterns for today
        dow_suggestion = patterns["day_of_week_patterns"].get(dow, ("curious", 0))[0]
        month_suggestion = patterns["monthly_patterns"].get(month, ("curious", 0))[0]
        
        # Check if we've been in the same mood too long
        recent = patterns["recent_trend"]
        if len(recent) >= 3 and len(set(recent[-3:])) == 1:
            # Same mood 3 days in a row - suggest something different
            current = recent[-1]
            alternatives = [m for m, c in patterns["mood_distribution"].items() if m != current]
            suggestion = alternatives[0] if alternatives else "curious"
            reason = f"You've been {current} for 3+ days — time for a change!"
        else:
            # Use day-of-week pattern as primary, month as secondary
            suggestion = dow_suggestion if dow_suggestion != "none" else month_suggestion
            reason = f"Historically, {dow}s tend to be {suggestion} days"
        
        return {
            "suggestion": suggestion,
            "reason": reason,
            "dow_pattern": dow_suggestion,
            "month_pattern": month_suggestion,
            "recent_streak": recent[-3:] if len(recent) >= 3 else recent
        }
    except Exception as e:
        return {"suggestion": "curious", "reason": f"Error: {e}"}

def main():
    """CLI interface."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: mood_memory.py <command>")
        print("Commands: append, analyze, suggest")
        return
    
    command = sys.argv[1]
    
    if command == "append":
        append_today_mood()
        print("Today's mood appended to history")
    
    elif command == "analyze":
        result = analyze_patterns()
        print(json.dumps(result, indent=2))
    
    elif command == "suggest":
        result = suggest_mood()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()