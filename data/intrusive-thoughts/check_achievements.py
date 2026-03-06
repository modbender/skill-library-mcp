#!/usr/bin/env python3
"""🏆 Achievement System — Check and award new achievements."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from config import get_file_path

ACHIEVEMENTS_FILE = get_file_path("achievements.json")
EARNED_FILE = get_file_path("achievements_earned.json")
HISTORY_FILE = get_file_path("history.json")
MOOD_HISTORY_FILE = get_file_path("mood_history.json")

def load_achievements():
    """Load achievement definitions."""
    try:
        return json.loads(ACHIEVEMENTS_FILE.read_text())
    except:
        return {"achievements": {}}

def load_earned():
    """Load earned achievements."""
    try:
        return json.loads(EARNED_FILE.read_text())
    except:
        return {"version": 1, "earned": [], "total_points": 0}

def save_earned(data):
    """Save earned achievements."""
    EARNED_FILE.write_text(json.dumps(data, indent=2))

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

def check_night_owl(history, earned_ids):
    """Check for Night Owl achievement."""
    if "night_owl" in earned_ids:
        return None
    
    for activity in history:
        try:
            timestamp = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
            if timestamp.hour >= 3:  # 3am or later
                return {
                    "id": "night_owl",
                    "earned_at": datetime.now().isoformat(),
                    "trigger_activity": activity["thought_id"],
                    "trigger_time": activity["timestamp"]
                }
        except:
            continue
    return None

def check_early_bird(history, earned_ids):
    """Check for Early Bird achievement."""
    if "early_bird" in earned_ids:
        return None
    
    for activity in history:
        try:
            timestamp = datetime.fromisoformat(activity["timestamp"].replace('Z', '+00:00'))
            if timestamp.hour < 4:  # Before 4am
                return {
                    "id": "early_bird",
                    "earned_at": datetime.now().isoformat(),
                    "trigger_activity": activity["thought_id"],
                    "trigger_time": activity["timestamp"]
                }
        except:
            continue
    return None

def check_social_butterfly(history, earned_ids):
    """Check for Social Butterfly achievement."""
    if "social_butterfly" in earned_ids:
        return None
    
    # Count Moltbook posts by day
    daily_posts = defaultdict(int)
    for activity in history:
        if activity.get("thought_id") in ["moltbook-post", "moltbook-social", "moltbook-night"]:
            date = activity["timestamp"][:10]
            daily_posts[date] += 1
    
    # Check if any day has 5+ posts
    for date, count in daily_posts.items():
        if count >= 5:
            return {
                "id": "social_butterfly",
                "earned_at": datetime.now().isoformat(),
                "trigger_date": date,
                "post_count": count
            }
    return None

def check_tool_hoarder(history, earned_ids):
    """Check for Tool Hoarder achievement."""
    if "tool_hoarder" in earned_ids:
        return None
    
    install_count = sum(1 for a in history if a.get("thought_id") == "install-explore")
    if install_count >= 5:
        return {
            "id": "tool_hoarder",
            "earned_at": datetime.now().isoformat(),
            "tool_count": install_count
        }
    return None

def check_question_master(history, earned_ids):
    """Check for Question Master achievement."""
    if "question_master" in earned_ids:
        return None
    
    question_activities = ["ask-opinion", "ask-preference", "ask-feedback"]
    question_count = sum(1 for a in history if a.get("thought_id") in question_activities)
    if question_count >= 10:
        return {
            "id": "question_master", 
            "earned_at": datetime.now().isoformat(),
            "question_count": question_count
        }
    return None

def check_marathon(history, earned_ids):
    """Check for Marathon achievement."""
    if "marathon" in earned_ids:
        return None
    
    # Count activities by day
    daily_counts = defaultdict(int)
    for activity in history:
        date = activity["timestamp"][:10]
        daily_counts[date] += 1
    
    # Check if any day has 5+ activities
    for date, count in daily_counts.items():
        if count >= 5:
            return {
                "id": "marathon",
                "earned_at": datetime.now().isoformat(),
                "trigger_date": date,
                "activity_count": count
            }
    return None

def check_chaotic_good(history, earned_ids):
    """Check for Chaotic Good achievement."""
    if "chaotic_good" in earned_ids:
        return None
    
    # Need to cross-reference with mood data (simplified check)
    for activity in history:
        if activity.get("thought_id") == "build-tool":
            # Check if summary suggests chaotic mood
            summary = activity.get("summary", "").lower()
            if any(word in summary for word in ["chaotic", "weird", "random", "crazy", "wild"]):
                return {
                    "id": "chaotic_good",
                    "earned_at": datetime.now().isoformat(),
                    "trigger_activity": activity["thought_id"],
                    "summary": activity.get("summary", "")
                }
    return None

def check_philosopher_king(mood_history, earned_ids):
    """Check for Philosopher King achievement."""
    if "philosopher_king" in earned_ids:
        return None
    
    # Check for 3 consecutive philosophical days
    consecutive = 0
    for mood_entry in mood_history:
        if mood_entry.get("mood_id") == "philosophical":
            consecutive += 1
            if consecutive >= 3:
                return {
                    "id": "philosopher_king",
                    "earned_at": datetime.now().isoformat(),
                    "streak_length": consecutive
                }
        else:
            consecutive = 0
    return None

def check_midnight_coder(history, earned_ids):
    """Check for Midnight Coder achievement.""" 
    if "midnight_coder" in earned_ids:
        return None
    
    night_builds = 0
    for activity in history:
        if activity.get("thought_id") == "build-tool" and activity.get("mood") == "night":
            night_builds += 1
    
    if night_builds >= 3:
        return {
            "id": "midnight_coder",
            "earned_at": datetime.now().isoformat(),
            "night_builds": night_builds
        }
    return None

def check_productivity_perfectionist(history, earned_ids):
    """Check for Productivity Perfectionist achievement."""
    if "productivity_perfectionist" in earned_ids:
        return None
    
    # Look for 5 consecutive high-energy positive activities
    streak = 0
    for activity in history:
        if activity.get("energy") == "high" and activity.get("vibe") == "positive":
            streak += 1
            if streak >= 5:
                return {
                    "id": "productivity_perfectionist",
                    "earned_at": datetime.now().isoformat(),
                    "perfect_streak": streak
                }
        else:
            streak = 0
    return None

def check_mood_master(mood_history, earned_ids):
    """Check for Mood Master achievement."""
    if "mood_master" in earned_ids:
        return None
    
    experienced_moods = set(entry.get("mood_id") for entry in mood_history)
    all_moods = {"hyperfocus", "curious", "social", "cozy", "chaotic", "philosophical", "restless", "determined"}
    
    if experienced_moods >= all_moods:
        return {
            "id": "mood_master",
            "earned_at": datetime.now().isoformat(),
            "moods_experienced": list(experienced_moods)
        }
    return None

def check_consistency_champion(history, earned_ids):
    """Check for Consistency Champion achievement."""
    if "consistency_champion" in earned_ids:
        return None
    
    # Group activities by date
    activity_dates = set(activity["timestamp"][:10] for activity in history)
    
    if len(activity_dates) < 7:
        return None
    
    # Check for 7 consecutive days
    sorted_dates = sorted(activity_dates)
    streak = 1
    
    for i in range(1, len(sorted_dates)):
        curr_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        prev_date = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d")
        
        if (curr_date - prev_date).days == 1:
            streak += 1
            if streak >= 7:
                return {
                    "id": "consistency_champion",
                    "earned_at": datetime.now().isoformat(),
                    "streak_days": streak
                }
        else:
            streak = 1
    
    return None

def check_all_achievements():
    """Check all achievements and return newly earned ones."""
    achievements_def = load_achievements()
    earned_data = load_earned()
    history = load_history()
    mood_history = load_mood_history()
    
    earned_ids = set(e["id"] for e in earned_data["earned"])
    new_achievements = []
    
    # Check each achievement
    checks = [
        check_night_owl(history, earned_ids),
        check_early_bird(history, earned_ids),
        check_social_butterfly(history, earned_ids),
        check_tool_hoarder(history, earned_ids),
        check_question_master(history, earned_ids),
        check_marathon(history, earned_ids),
        check_chaotic_good(history, earned_ids),
        check_philosopher_king(mood_history, earned_ids),
        check_midnight_coder(history, earned_ids),
        check_productivity_perfectionist(history, earned_ids),
        check_mood_master(mood_history, earned_ids),
        check_consistency_champion(history, earned_ids)
    ]
    
    for result in checks:
        if result:
            # Add achievement details
            achievement_def = achievements_def["achievements"].get(result["id"], {})
            result.update({
                "name": achievement_def.get("name", "Unknown"),
                "description": achievement_def.get("description", ""),
                "tier": achievement_def.get("tier", "bronze"),
                "points": achievement_def.get("points", 0)
            })
            new_achievements.append(result)
    
    # Update earned achievements
    if new_achievements:
        earned_data["earned"].extend(new_achievements)
        earned_data["total_points"] = sum(a.get("points", 0) for a in earned_data["earned"])
        save_earned(earned_data)
    
    return new_achievements

def main():
    """Check achievements and report new ones."""
    new_achievements = check_all_achievements()
    
    if new_achievements:
        print(f"🎉 NEW ACHIEVEMENTS EARNED: {len(new_achievements)}")
        for achievement in new_achievements:
            tier_emoji = {"bronze": "🥉", "silver": "🥈", "gold": "🥇", "platinum": "💎"}.get(achievement["tier"], "🏆")
            print(f"  {tier_emoji} {achievement['name']} (+{achievement['points']} pts)")
            print(f"     {achievement['description']}")
        
        earned_data = load_earned()
        print(f"\n📊 Total achievements: {len(earned_data['earned'])}")
        print(f"🎯 Total points: {earned_data['total_points']}")
    else:
        print("No new achievements earned")

if __name__ == "__main__":
    main()