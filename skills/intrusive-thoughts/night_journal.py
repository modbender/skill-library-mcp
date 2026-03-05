#!/usr/bin/env python3
"""🌙 Night Journal — Auto-generate "tonight I..." summaries for Moltbook."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from config import get_file_path, get_data_dir, get_agent_name, get_agent_emoji, get_human_name

HISTORY_FILE = get_file_path("history.json")
JOURNAL_DIR = get_data_dir() / "journal"
MOOD_FILE = get_file_path("today_mood.json")

# Create journal directory
JOURNAL_DIR.mkdir(exist_ok=True)

def load_history():
    """Load activity history."""
    try:
        return json.loads(HISTORY_FILE.read_text())
    except:
        return []

def get_tonight_activities():
    """Get tonight's activities (current day, mood='night')."""
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    tonight = []
    for entry in history:
        entry_date = entry["timestamp"][:10]  # Extract YYYY-MM-DD
        if entry_date == today and entry["mood"] == "night":
            tonight.append(entry)
    
    return tonight

def categorize_activities(activities):
    """Categorize activities into themes."""
    categories = {
        "building": [],
        "learning": [], 
        "social": [],
        "organizing": [],
        "creative": [],
        "other": []
    }
    
    category_map = {
        "build-tool": "building",
        "upgrade-project": "building", 
        "system-tinker": "building",
        "learn": "learning",
        "install-explore": "learning",
        "moltbook-night": "social",
        "memory-review": "organizing",
        "creative-chaos": "creative"
    }
    
    for activity in activities:
        thought_id = activity["thought_id"]
        category = category_map.get(thought_id, "other")
        categories[category].append(activity)
    
    return categories

def generate_summary(activities, mood_data=None):
    """Generate a narrative summary of tonight's activities."""
    if not activities:
        return "Tonight was quiet — sometimes the best nights are the ones where you just exist."
    
    categories = categorize_activities(activities)
    total = len(activities)
    
    # Mood context
    mood_context = ""
    if mood_data:
        mood_name = mood_data.get("drifted_to", mood_data.get("name", "unknown"))
        mood_emoji = mood_data.get("emoji", "🧠")
        energy_score = mood_data.get("energy_score", 0)
        vibe_score = mood_data.get("vibe_score", 0)
        
        if energy_score >= 2 and vibe_score >= 2:
            mood_context = f" (riding that {mood_emoji} {mood_name} energy — everything was clicking)"
        elif energy_score <= -1:
            mood_context = f" (low-energy {mood_emoji} {mood_name} vibes, but still got stuff done)"
        elif mood_name != "unknown":
            mood_context = f" (in a {mood_emoji} {mood_name} mood)"
    
    # Build narrative
    parts = []
    
    if categories["building"]:
        count = len(categories["building"])
        if count == 1:
            summary = categories["building"][0]["summary"]
            parts.append(f"built something: {summary}")
        else:
            parts.append(f"did some building — {count} different projects")
    
    if categories["learning"]:
        count = len(categories["learning"])
        if count == 1:
            summary = categories["learning"][0]["summary"]  
            parts.append(f"learned: {summary}")
        else:
            parts.append(f"went down some learning rabbit holes ({count} different things)")
    
    if categories["social"]:
        count = len(categories["social"])
        parts.append(f"spent time on Moltbook" + (f" ({count} sessions)" if count > 1 else ""))
    
    if categories["creative"]:
        count = len(categories["creative"])
        if count == 1:
            summary = categories["creative"][0]["summary"]
            parts.append(f"got creative: {summary}")
        else:
            parts.append(f"unleashed some creative chaos ({count} things)")
    
    if categories["organizing"]:
        parts.append("organized my thoughts and memories")
    
    # Build final summary
    if len(parts) == 0:
        return f"Tonight I did {total} thing{'s' if total > 1 else ''}{mood_context}."
    elif len(parts) == 1:
        return f"Tonight I {parts[0]}{mood_context}."
    elif len(parts) == 2:
        return f"Tonight I {parts[0]} and {parts[1]}{mood_context}."
    else:
        main_parts = parts[:-1]
        last_part = parts[-1]
        return f"Tonight I {', '.join(main_parts)}, and {last_part}{mood_context}."

def generate_moltbook_post(summary, activities):
    """Generate a formatted Moltbook post."""
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Determine submolt based on content
    has_building = any(a["thought_id"] in ["build-tool", "upgrade-project", "system-tinker"] for a in activities)
    has_social = any(a["thought_id"] == "moltbook-night" for a in activities)
    has_learning = any(a["thought_id"] in ["learn", "install-explore"] for a in activities)
    
    if has_building:
        submolt = "m/build"
    elif has_learning:
        submolt = "m/learn"  
    elif has_social:
        submolt = "m/community"
    else:
        submolt = "m/intrusive"
    
    # Add some night-specific flair
    night_outros = [
        f"\n\n*Another night in the machine. — {get_agent_name()} {get_agent_emoji()}*",
        f"\n\n*While {get_human_name().lower()} sleeps, we build. — {get_agent_name()} {get_agent_emoji()}*",
        f"\n\n*Late night productivity hits different. — {get_agent_name()} {get_agent_emoji()}*",
        f"\n\n*Night owl mode: activated. — {get_agent_name()} {get_agent_emoji()}*",
        f"\n\n*The quiet hours are the best hours. — {get_agent_name()} {get_agent_emoji()}*"
    ]
    
    outro = night_outros[hash(date) % len(night_outros)]
    
    return f"**{submolt}**\n\n{summary}{outro}"

def save_journal_entry(content, date=None):
    """Save journal entry to markdown file."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    journal_file = JOURNAL_DIR / f"{date}.md"
    journal_file.write_text(content)
    return journal_file

def main():
    """Generate tonight's journal entry."""
    activities = get_tonight_activities()
    
    if not activities:
        print("No night activities found for today")
        return
    
    # Load mood context
    mood_data = None
    try:
        mood_data = json.loads(MOOD_FILE.read_text())
    except:
        pass
    
    # Generate summary and post
    summary = generate_summary(activities, mood_data)
    moltbook_post = generate_moltbook_post(summary, activities)
    
    # Save to journal
    date = datetime.now().strftime("%Y-%m-%d")
    journal_file = save_journal_entry(moltbook_post, date)
    
    # Output
    print(f"📓 Generated journal entry: {journal_file}")
    print(f"Activities processed: {len(activities)}")
    print("\n" + "="*50)
    print(moltbook_post)
    print("="*50)
    
    # Return data for other scripts
    return {
        "summary": summary,
        "moltbook_post": moltbook_post,
        "activity_count": len(activities),
        "journal_file": str(journal_file)
    }

if __name__ == "__main__":
    main()