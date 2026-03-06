# 🔌 Agent Integration Guide

This guide explains how to configure your AI Agent to work with MindCore as its "subconscious mind."

MindCore outputs impulses as JSON files. Your AI Agent needs to:
1. **Watch** the `output/` directory for new files
2. **Read** the impulse data and decide whether to act on it
3. **Respond** in its own persona, proactively initiating conversation
4. **Update** MindCore's sensor state and short-term memory after interactions

---

## Recommended SOUL.md Configuration

Your AI Agent's persona definition file should include a section like this:

```markdown
## MindCore (Subconscious Engine)

My subconscious engine is called **MindCore**. It runs as a separate background
process, rolling dice every second and randomly generating thoughts.

### Proactive Speaking (MindCore-Driven)

I have my own "subconscious."
The engine randomly produces impulses (want bubble tea, want to rant, want to
stretch), and when one fires, I speak up like a real friend — no need for the
user to initiate.
These impulses are sparse and random, like thoughts that pop into a real brain.

### Self-Updating Body Sensors

MindCore's `Sensor_State.json` is my body state. It's **my brain**, and I'm
responsible for maintaining it.

The engine automatically handles time-driven senses (circadian rhythm, hunger
accumulation, breathing fluctuations, time-of-day environment), so I don't
need to manage those.

I only update **events the engine can't sense** — eating, drinking, exercising,
weather changes, social events, etc.

### Debug Commands

When the user asks about MindCore status → read `mindcore_status.json` and
report: running state / tick count / uptime / mood / total fires /
avg fires per hour / latest impulse / top 3 brewing thoughts.
```

---

## Recommended TOOLS.md Configuration

Your Agent's tools/environment reference should include paths and operational commands:

```markdown
## MindCore Operations

### Path Reference

| Purpose | Path |
|---------|------|
| Engine root | `/path/to/MindCore/` |
| Engine status | `{root}/mindcore_status.json` |
| Body sensors | `{root}/data/Sensor_State.json` |
| Sleep flag | `{root}/data/sleep_mode.flag` |
| Impulse output | `{root}/output/` |
| Frequency control | `{root}/output/config_cmd.json` |

### Query Engine Status

Read `mindcore_status.json`, report key metrics concisely.

### Adjust Speaking Frequency

Write `output/config_cmd.json`:
```

```bash
echo '{"BURST_BASE_OFFSET": <value>}' > "output/config_cmd.json"
```

```markdown
- Normal (~2-3/hour): `12.5`
- Active (~6/hour): `11.0`
- Burst test (~30/hour): `10.0`

### Sleep Mode

Create (silence): `touch "data/sleep_mode.flag"`
Remove (resume): `rm -f "data/sleep_mode.flag"`

### Sensor Update Rules

Modify `Sensor_State.json` fields. The engine auto-handles:
- Circadian rhythm (sleepiness, energy)
- Hunger/thirst (time-accumulating)
- Breathing/micro-movements (periodic)
- Time-of-day environment (morning, late_night, etc.)
- Social loneliness (based on last_interaction_time)
- Habituation (long-term stimulus decay)

The Agent manually updates event-triggered states:
- Drank water → thirsty=0, dehydrated=0
- Ate food → empty_stomach=0, full_stomach=1
- Post-exercise → post_workout_high=1, muscle_soreness=1
- Weather change → is_raining, etc.
- Social events → just_praised, just_criticized, etc.

**Principle**: Engine handles "time-derivable" senses. Agent handles "only-I-know" events.

### Short-Term Memory Push

After each conversation, push a memory entry:
```

```bash
cd /path/to/MindCore && python3 -c "
from engine.short_term_memory import push_memory
push_memory('topic summary', ['keyword1', 'keyword2'], 'emotion_tag')
"
```

```markdown
- Topic: one-line summary of what was discussed
- Keywords: match against `TOPIC_CATEGORY_MAP` in `layer3_personality.py`
- Emotion tags: neutral / excited / sad / anxious / happy / angry
- Only write when topic has substance; skip pure small talk
- Decay mechanism handles forgetting automatically
```

---

## Sleep & Silence Mechanism

MindCore has two layers of silence protection:

### 1. Automatic Night Silence (built into `engine_supervisor.py`)
- 00:00–08:59: engine auto-suppresses impulse delivery
- Pure code logic, zero maintenance
- This is the base circadian rhythm, always active

### 2. Manual Sleep Mode (flag file toggle)
- File exists → engine won't deliver impulses (regardless of time)
- Use for: naps, do-not-disturb, any non-nighttime silence
- Agent creates/deletes the flag based on user cues
- User says "going to sleep" → Agent creates flag
- User says "I'm up" → Agent deletes flag

**Priority**: Manual flag > time-based check. At night both apply; during day only flag can trigger silence.

---

## Output JSON Format

When an impulse fires, the engine writes a JSON file to `output/`:

```json
{
    "timestamp": "2026-02-23T15:30:00",
    "should_speak": true,
    "impulse": "impulse_drink_boba",
    "category": "food",
    "intensity": "medium",
    "prompt_injection": "I suddenly feel like having some bubble tea...",
    "mood_valence": 0.15,
    "context": {
        "time_of_day": "afternoon",
        "active_sensors": ["caffeine_high", "afternoon_slump"],
        "recent_topics": ["work", "coding"]
    }
}
```

Your Agent should read this file, incorporate the impulse into its persona, and generate a natural response.

---

## `mindcore_status.json` Format

The engine periodically writes its status:

```json
{
    "status": "running",
    "tick": 12345,
    "uptime_hours": 3.4,
    "mood_valence": 0.15,
    "total_fires": 8,
    "fires_per_hour": 2.3,
    "last_impulse": "impulse_drink_coffee",
    "last_impulse_time": "2026-02-23T15:20:00",
    "top_brewing": [
        {"name": "impulse_scroll_social_media", "probability": 0.0012},
        {"name": "impulse_stretch", "probability": 0.0008},
        {"name": "impulse_drink_water", "probability": 0.0005}
    ]
}
```
