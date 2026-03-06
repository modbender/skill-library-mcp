#!/bin/bash
# Log what the agent did AND drift the mood based on outcome
# Usage: log_result.sh <thought_id> <mood> "<summary>" [energy: high|neutral|low] [vibe: positive|neutral|negative]
# Example: log_result.sh build-tool night "Built a disk usage dashboard" high positive

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/load_config.sh"

HISTORY_FILE="$DATA_DIR/history.json"
MOOD_FILE="$DATA_DIR/today_mood.json"

THOUGHT_ID="${1:-unknown}"
MOOD="${2:-unknown}"
SUMMARY="${3:-No summary provided}"
ENERGY="${4:-neutral}"
VIBE="${5:-neutral}"
TIMESTAMP=$(date -Iseconds)

python3 << PYEOF
import json, sys
from datetime import datetime

# Log to history
try:
    with open('$HISTORY_FILE') as f:
        history = json.load(f)
except:
    history = []

entry = {
    'timestamp': '$TIMESTAMP',
    'mood': '$MOOD',
    'thought_id': '$THOUGHT_ID',
    'summary': '''$SUMMARY''',
    'energy': '$ENERGY',
    'vibe': '$VIBE'
}
history.append(entry)
history = history[-500:]

with open('$HISTORY_FILE', 'w') as f:
    json.dump(history, f, indent=2)

# Drift today's mood based on outcome
try:
    with open('$MOOD_FILE') as f:
        today = json.load(f)
except:
    today = {}

if today:
    # Track activity outcomes in the mood file
    if 'activity_log' not in today:
        today['activity_log'] = []
    
    today['activity_log'].append({
        'thought': '$THOUGHT_ID',
        'energy': '$ENERGY',
        'vibe': '$VIBE',
        'time': '$TIMESTAMP'
    })
    
    # Calculate mood drift
    log = today['activity_log']
    energy_score = sum(1 if a['energy']=='high' else (-1 if a['energy']=='low' else 0) for a in log)
    vibe_score = sum(1 if a['vibe']=='positive' else (-1 if a['vibe']=='negative' else 0) for a in log)
    
    # Drift rules — outcomes push the mood
    drift_map = {
        # (energy, vibe) -> suggested mood shifts
        'high_positive': {'boost': ['hyperfocus', 'chaotic', 'social'], 'dampen': ['cozy', 'philosophical']},
        'high_negative': {'boost': ['restless', 'determined'], 'dampen': ['cozy', 'social']},
        'low_positive': {'boost': ['cozy', 'philosophical', 'social'], 'dampen': ['hyperfocus', 'chaotic']},
        'low_negative': {'boost': ['cozy', 'philosophical'], 'dampen': ['chaotic', 'social', 'restless']},
    }
    
    # Apply latest activity's drift
    energy = '$ENERGY'
    vibe = '$VIBE'
    if energy != 'neutral' or vibe != 'neutral':
        key = f"{energy}_{vibe}" if energy != 'neutral' and vibe != 'neutral' else None
        if key and key in drift_map:
            drift = drift_map[key]
            # Merge with existing boosts/dampens (don't replace, accumulate)
            existing_boost = set(today.get('boosted_traits', []))
            existing_dampen = set(today.get('dampened_traits', []))
            
            existing_boost.update(drift['boost'])
            existing_dampen.update(drift['dampen'])
            
            # Remove contradictions (if something is in both, most recent wins)
            for b in drift['boost']:
                existing_dampen.discard(b)
            for d in drift['dampen']:
                existing_boost.discard(d)
            
            today['boosted_traits'] = list(existing_boost)
            today['dampened_traits'] = list(existing_dampen)
    
    # Update mood description with drift note
    today['energy_score'] = energy_score
    today['vibe_score'] = vibe_score
    today['last_drift'] = '$TIMESTAMP'
    
    # If strong enough signal, shift the mood name itself
    if len(log) >= 3:
        if energy_score >= 2 and vibe_score >= 2:
            today['drifted_to'] = 'hyperfocus'
            today['drift_note'] = 'Riding high — everything is clicking today'
        elif energy_score <= -2 and vibe_score <= -2:
            today['drifted_to'] = 'cozy'
            today['drift_note'] = 'Low energy day — pulling back to recharge'
        elif energy_score >= 2 and vibe_score <= -1:
            today['drifted_to'] = 'restless'
            today['drift_note'] = 'High energy but frustrated — need to channel this'
        elif vibe_score >= 2:
            today['drifted_to'] = 'social'
            today['drift_note'] = 'Good vibes — feeling chatty'
    
    with open('$MOOD_FILE', 'w') as f:
        json.dump(today, f, indent=2)
    
    drift_info = today.get('drifted_to', '')
    if drift_info:
        print(f"Mood drifted → {drift_info}: {today.get('drift_note','')}")
    else:
        print(f"Mood adjusted: energy={energy_score:+d} vibe={vibe_score:+d}")
else:
    print("No mood file set — logged activity only")

print(f"Logged: {entry['thought_id']} ({entry['mood']}) - {entry['summary'][:60]}")

# === STREAK TRACKING ===
streaks_file = '$DATA_DIR/streaks.json'
try:
    with open(streaks_file) as f:
        streaks = json.load(f)
except:
    streaks = {
        'version': 1,
        'current_streaks': {'activity_type': [], 'mood': [], 'time_slot': []},
        'recent_activities': [],
        'anti_rut_weights': {},
        'streak_history': []
    }

# Add this activity to recent list
current_hour = datetime.fromisoformat('$TIMESTAMP'.replace('Z', '+00:00')).hour
streaks['recent_activities'].append({
    'thought_id': '$THOUGHT_ID',
    'mood': '$MOOD', 
    'timestamp': '$TIMESTAMP',
    'hour': current_hour,
    'energy': '$ENERGY',
    'vibe': '$VIBE'
})

# Keep only last 20 activities
streaks['recent_activities'] = streaks['recent_activities'][-20:]

# Analyze activity type streaks
recent_thoughts = [a['thought_id'] for a in streaks['recent_activities'][-5:]]
activity_streak = []
for thought in reversed(recent_thoughts):
    if activity_streak and activity_streak[0] != thought:
        break
    if not activity_streak or activity_streak[0] == thought:
        activity_streak.insert(0, thought)

# Analyze mood streaks  
recent_moods = [a['mood'] for a in streaks['recent_activities'][-5:]]
mood_streak = []
for mood in reversed(recent_moods):
    if mood_streak and mood_streak[0] != mood:
        break
    if not mood_streak or mood_streak[0] == mood:
        mood_streak.insert(0, mood)

streaks['current_streaks']['activity_type'] = activity_streak
streaks['current_streaks']['mood'] = mood_streak

# Update anti-rut weights
weights = streaks.get('anti_rut_weights', {})
current_thought = '$THOUGHT_ID'

# If we're in a streak of 3+, reduce weight for the repeated activity
if len(activity_streak) >= 3 and activity_streak[0] == current_thought:
    weights[current_thought] = max(0.3, weights.get(current_thought, 1.0) * 0.7)
    streak_msg = f"Activity streak detected: {activity_streak[0]} x{len(activity_streak)} — reducing weight"
    print(streak_msg)
    
    # Boost complementary activities
    complements = {
        'build-tool': ['moltbook-post', 'creative-chaos', 'share-discovery'],
        'upgrade-project': ['learn', 'memory-review', 'ask-opinion'],
        'moltbook-night': ['build-tool', 'system-tinker', 'learn'],
        'system-tinker': ['moltbook-social', 'creative-chaos'],
        'learn': ['build-tool', 'pitch-idea', 'upgrade-project'],
        'memory-review': ['moltbook-post', 'ask-preference']
    }
    
    for comp in complements.get(current_thought, []):
        weights[comp] = min(2.0, weights.get(comp, 1.0) * 1.3)

# Recovery — if haven't done an activity in a while, boost it
activity_counts = {}
for a in streaks['recent_activities'][-10:]:
    activity_counts[a['thought_id']] = activity_counts.get(a['thought_id'], 0) + 1

for thought_id in ['build-tool', 'upgrade-project', 'moltbook-post', 'creative-chaos']:
    if activity_counts.get(thought_id, 0) == 0:
        weights[thought_id] = min(2.0, weights.get(thought_id, 1.0) * 1.2)

streaks['anti_rut_weights'] = weights

# Save streaks
with open(streaks_file, 'w') as f:
    json.dump(streaks, f, indent=2)

# Check for achievements (if the script exists)
import subprocess
import os
achievements_script = '$DATA_DIR/check_achievements.py'
if os.path.exists(achievements_script):
    try:
        subprocess.run(['python3', achievements_script], cwd='$DATA_DIR', timeout=10)
    except:
        pass

PYEOF
