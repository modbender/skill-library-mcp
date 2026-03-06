"""
short_term_memory.py — Short-Term Working Memory
Biomimetic Mind Engine

5-slot FIFO buffer simulating human working memory.
Each memory has a timestamp and decay weight — older memories fade.

Write method: atomic write (tmp + rename) to prevent engine reading half-written JSON.
"""

import json
import os
import time
import tempfile
from engine.config import SHORT_TERM_MEMORY_PATH

MAX_SLOTS = 5
HALFLIFE_SECONDS = 7200  # 2-hour half-life

# Emotion → valence mapping
EMOTION_VALENCE = {
    "excited": 0.5,
    "happy": 0.4,
    "touched": 0.35,
    "curious": 0.3,
    "relaxed": 0.25,
    "neutral": 0.0,
    "bored": -0.15,
    "anxious": -0.2,
    "embarrassed": -0.25,
    "irritated": -0.25,
    "angry": -0.3,
    "wronged": -0.35,
    "sad": -0.4,
}

# New emotion's influence on mood (0~1, higher = more sensitive)
MOOD_BLEND_ALPHA = 0.3


def _load_stm() -> dict:
    """Safely read ShortTermMemory.json"""
    try:
        with open(SHORT_TERM_MEMORY_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "mood_valence": 0.0,
            "unresolved_events": [],
            "conversation_buffer": [],
        }


def _save_stm(data: dict):
    """Atomic write: write to temp file, then rename"""
    dir_path = os.path.dirname(SHORT_TERM_MEMORY_PATH)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, SHORT_TERM_MEMORY_PATH)
    except Exception:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def push_memory(topic: str, keywords: list, emotion: str = "neutral"):
    """
    Push a conversation memory into the buffer.

    Args:
        topic: Conversation topic summary (e.g., "discussed climbing plans")
        keywords: Keyword list (e.g., ["climbing", "exercise", "weekend"])
        emotion: Emotion tag (e.g., "excited", "neutral", "sad")
    """
    data = _load_stm()
    buf = data.get("conversation_buffer", [])

    entry = {
        "topic": topic,
        "keywords": keywords,
        "emotion": emotion,
        "timestamp": time.time(),
    }

    buf.append(entry)

    # FIFO: evict oldest when exceeding MAX_SLOTS
    if len(buf) > MAX_SLOTS:
        buf = buf[-MAX_SLOTS:]

    data["conversation_buffer"] = buf

    # Update mood_valence: old_mood * (1-alpha) + new_emotion * alpha
    emotion_val = EMOTION_VALENCE.get(emotion, 0.0)
    old_mood = data.get("mood_valence", 0.0)
    new_mood = old_mood * (1 - MOOD_BLEND_ALPHA) + emotion_val * MOOD_BLEND_ALPHA
    # Clamp to [-1, 1]
    data["mood_valence"] = round(max(-1.0, min(1.0, new_mood)), 4)

    _save_stm(data)
    return entry


def get_memories_weighted() -> list:
    """
    Read buffer and compute decay weights.

    Returns:
        list of dict: each memory with weight (0.0~1.0)
    """
    data = _load_stm()
    buf = data.get("conversation_buffer", [])
    now = time.time()
    result = []

    for entry in buf:
        age = now - entry.get("timestamp", now)
        # Exponential decay: weight = 0.5 ^ (age / halflife)
        weight = 0.5 ** (age / HALFLIFE_SECONDS)
        result.append({
            **entry,
            "weight": round(weight, 4),
        })

    return result


def clear_buffer():
    """Clear conversation buffer (preserve mood and events)"""
    data = _load_stm()
    data["conversation_buffer"] = []
    _save_stm(data)


# ============================================================
# Unified Update Interface: mood + sensors in one call
# ============================================================

from engine.config import SENSOR_STATE_PATH

# Common event → sensor field presets
EVENT_PRESETS = {
    "drink_water": {"thirsty": 0, "dehydrated": 0},
    "eat_food": {"empty_stomach": 0, "full_stomach": 1},
    "feel_hungry": {"empty_stomach": 1, "full_stomach": 0},
    "post_workout": {"post_workout_high": 1, "muscle_soreness": 1, "heart_racing": 1},
    "rest_well": {"eye_fatigue": 0, "sleep_deprived": 0, "heavy_eyelids": 0},
    "got_praised": {"just_praised": 1},
    "got_criticized": {"just_criticized": 1},
    "rain_start": {"is_raining": 1, "sunny_outside": 0},
    "rain_stop": {"is_raining": 0},
    "sunny": {"sunny_outside": 1, "is_raining": 0},
    "caffeine": {"caffeine_high": 1},
    "headache": {"headache": 1},
    "deep_talk": {"deep_conversation": 1, "small_talk": 0},
    "small_talk": {"small_talk": 1, "deep_conversation": 0},
}


def _load_sensor() -> dict:
    """Safely read Sensor_State.json"""
    try:
        with open(SENSOR_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_sensor(data: dict):
    """Atomic write Sensor_State.json"""
    dir_path = os.path.dirname(SENSOR_STATE_PATH)
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp_path, SENSOR_STATE_PATH)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _apply_sensor_changes(sensor_data: dict, changes: dict) -> int:
    """Apply changes to sensor_data's body/environment/social sub-objects, return update count"""
    count = 0
    for section in ("body", "environment", "social"):
        sub = sensor_data.get(section, {})
        for key, val in changes.items():
            if key in sub:
                sub[key] = val
                count += 1
    return count


def mindcore_update(topic: str, keywords: list, emotion: str = "neutral",
                    event: str = None, sensors: dict = None):
    """
    Unified update interface: update mood (short-term memory) and sensors simultaneously.

    Args:
        topic: Conversation/event summary
        keywords: Keyword list
        emotion: Emotion tag (see EMOTION_VALENCE)
        event: Preset event name (see EVENT_PRESETS), auto-maps to sensor fields
        sensors: Manual sensor changes dict, merged with event preset (manual takes priority)
    
    Returns:
        dict: {"mood": new_mood, "sensors_updated": count}
    """
    # 1. Update mood + conversation memory
    push_memory(topic, keywords, emotion)

    # 2. Merge sensor changes
    changes = {}
    if event and event in EVENT_PRESETS:
        changes.update(EVENT_PRESETS[event])
    if sensors:
        changes.update(sensors)  # Manual overrides preset

    sensors_updated = 0
    if changes:
        sensor_data = _load_sensor()
        sensors_updated = _apply_sensor_changes(sensor_data, changes)
        # Update timestamp
        if "_meta" in sensor_data:
            from datetime import datetime, timezone, timedelta
            tz = timezone(timedelta(hours=8))
            sensor_data["_meta"]["last_updated"] = datetime.now(tz).isoformat()
        _save_sensor(sensor_data)

    # Read back latest mood
    stm = _load_stm()
    new_mood = stm.get("mood_valence", 0.0)

    return {"mood": new_mood, "sensors_updated": sensors_updated}
