#!/usr/bin/env python3
"""
Basal Ganglia - Habit Learning System

Implements habit tracking and automatic boosting of search results
for frequently used queries/actions.

The basal ganglia is responsible for habit formation and motor control.
This module learns from repeated user actions and boosts confidence
for matching queries in the search pipeline.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

# Storage path
MEMORY_BASE = Path.home() / ".openclaw" / "memory"
HABITS_FILE = MEMORY_BASE / "habits.json"

# Ensure memory directory exists
MEMORY_BASE.mkdir(parents=True, exist_ok=True)

# Habit thresholds
MIN_OCCURRENCES_FOR_HABIT = 3  # Times an action must occur to become a habit
CONFIDENCE_BOOST_MAX = 0.3    # Maximum confidence boost for matched habits
SIMILARITY_THRESHOLD = 0.85   # Threshold for fuzzy matching queries to habits


def _load_habits() -> dict:
    """Load habits from storage."""
    if not HABITS_FILE.exists():
        return {"habits": [], "version": "1.0"}
    
    try:
        with open(HABITS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"habits": [], "version": "1.0"}


def _save_habits(data: dict):
    """Save habits to storage."""
    with open(HABITS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_habits():
    """Load habits from storage (public API)."""
    return _load_habits()


def save_habits():
    """Save habits to storage (public API)."""
    data = _load_habits()
    _save_habits(data)
    return {"status": "saved", "habits_count": len(data.get("habits", []))}


def _normalize_action(action: str) -> str:
    """Normalize action/query for consistent tracking."""
    return action.lower().strip()


def _find_matching_habit(action: str, habits: list) -> dict | None:
    """ matches theFind a habit that given action using fuzzy matching."""
    normalized = _normalize_action(action)
    
    for habit in habits:
        if not habit.get("enabled", True):
            continue
            
        habit_action = _normalize_action(habit["action"])
        
        # Exact match
        if habit_action == normalized:
            return habit
        
        # Fuzzy match
        similarity = SequenceMatcher(None, habit_action, normalized).ratio()
        if similarity >= SIMILARITY_THRESHOLD:
            return habit
    
    return None


def track_habit(action: str) -> dict:
    """
    Track a habit from a repeated action.
    
    When an action is repeated enough times, it becomes a habit.
    The habit then provides a confidence boost for matching queries.
    
    Args:
        action: The action/query to track
        
    Returns:
        Status of the habit tracking
    """
    if not action or not action.strip():
        return {"error": "Action cannot be empty"}
    
    data = _load_habits()
    habits = data.get("habits", [])
    
    # Find existing habit or create new
    existing = _find_matching_habit(action, habits)
    
    if existing:
        # Increment occurrence count
        existing["occurrences"] += existing.get("occurrences", 1)
        existing["last_seen"] = datetime.now().isoformat()
        
        # Check if it just became a habit
        became_habit = not existing.get("is_habit", False) and existing["occurrences"] >= MIN_OCCURRENCES_FOR_HABIT
        if became_habit:
            existing["is_habit"] = True
            existing["habit_confidence"] = min(
                0.5 + (existing["occurrences"] - MIN_OCCURRENCES_FOR_HABIT) * 0.1,
                1.0
            )
        
        _save_habits(data)
        
        return {
            "status": "updated",
            "habit_id": existing["id"],
            "action": existing["action"],
            "occurrences": existing["occurrences"],
            "is_habit": existing.get("is_habit", False),
            "became_habit": became_habit
        }
    else:
        # Create new habit entry
        new_habit = {
            "id": str(uuid.uuid4())[:8],
            "action": action.strip(),
            "occurrences": 1,
            "created": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "is_habit": False,
            "enabled": True,
            "habit_confidence": 0.0
        }
        
        habits.append(new_habit)
        data["habits"] = habits
        _save_habits(data)
        
        return {
            "status": "created",
            "habit_id": new_habit["id"],
            "action": new_habit["action"],
            "occurrences": 1,
            "is_habit": False,
            "message": f"Need {MIN_OCCURRENCES_FOR_HABIT - 1} more to become a habit"
        }


def get_habit_boost(query: str) -> float:
    """
    Get confidence boost for queries matching learned habits.
    
    This function should be called during search ranking to boost
    results for queries that match established habits.
    
    Args:
        query: The search query
        
    Returns:
        Confidence boost (0.0 to 0.3) based on matching habits
    """
    data = _load_habits()
    habits = data.get("habits", [])
    
    matching = _find_matching_habit(query, habits)
    
    if matching and matching.get("is_habit", False) and matching.get("enabled", True):
        # Return boost capped at CONFIDENCE_BOOST_MAX
        confidence = matching.get("habit_confidence", 0.5)
        boost = min(confidence * CONFIDENCE_BOOST_MAX, CONFIDENCE_BOOST_MAX)
        return boost
    
    return 0.0


def list_habits() -> dict:
    """
    List all learned habits.
    
    Returns:
        Dictionary with all habits and their status
    """
    data = _load_habits()
    habits = data.get("habits", [])
    
    habit_list = []
    for h in habits:
        habit_list.append({
            "id": h["id"],
            "action": h["action"],
            "occurrences": h["occurrences"],
            "is_habit": h.get("is_habit", False),
            "enabled": h.get("enabled", True),
            "habit_confidence": h.get("habit_confidence", 0.0),
            "last_seen": h.get("last_seen"),
            "created": h.get("created")
        })
    
    return {
        "habits": habit_list,
        "total": len(habit_list),
        "active_habits": len([h for h in habit_list if h["is_habit"] and h["enabled"]])
    }


def disable_habit(habit_id: str) -> dict:
    """
    Disable a habit.
    
    Disabled habits won't provide confidence boosts but are retained
    in storage for potential re-enable.
    
    Args:
        habit_id: The ID of the habit to disable
        
    Returns:
        Status of the disable operation
    """
    data = _load_habits()
    habits = data.get("habits", [])
    
    for h in habits:
        if h["id"] == habit_id:
            h["enabled"] = False
            _save_habits(data)
            return {
                "status": "disabled",
                "habit_id": habit_id,
                "action": h["action"]
            }
    
    return {
        "error": f"Habit not found: {habit_id}"
    }


def enable_habit(habit_id: str) -> dict:
    """
    Enable a previously disabled habit.
    
    Args:
        habit_id: The ID of the habit to enable
        
    Returns:
        Status of the enable operation
    """
    data = _load_habits()
    habits = data.get("habits", [])
    
    for h in habits:
        if h["id"] == habit_id:
            h["enabled"] = True
            _save_habits(data)
            return {
                "status": "enabled",
                "habit_id": habit_id,
                "action": h["action"]
            }
    
    return {
        "error": f"Habit not found: {habit_id}"
    }


def delete_habit(habit_id: str) -> dict:
    """
    Delete a habit permanently.
    
    Args:
        habit_id: The ID of the habit to delete
        
    Returns:
        Status of the delete operation
    """
    data = _load_habits()
    habits = data.get("habits", [])
    
    for i, h in enumerate(habits):
        if h["id"] == habit_id:
            deleted = habits.pop(i)
            _save_habits(data)
            return {
                "status": "deleted",
                "habit_id": habit_id,
                "action": deleted["action"]
            }
    
    return {
        "error": f"Habit not found: {habit_id}"
    }


def get_habit_stats() -> dict:
    """
    Get statistics about habit learning.
    
    Returns:
        Statistics about habits
    """
    data = _load_habits()
    habits = data.get("habits", [])
    
    active = [h for h in habits if h.get("is_habit", False) and h.get("enabled", True)]
    developing = [h for h in habits if not h.get("is_habit", False)]
    disabled = [h for h in habits if not h.get("enabled", True)]
    
    return {
        "total_tracked": len(habits),
        "active_habits": len(active),
        "developing": len(developing),
        "disabled": len(disabled),
        "threshold": MIN_OCCURRENCES_FOR_HABIT,
        "max_boost": CONFIDENCE_BOOST_MAX
    }


# Integration helpers for search pipeline

def apply_habit_boost(results: list, query: str) -> list:
    """
    Apply habit-based confidence boost to search results.
    
    This function modifies result scores based on matching habits.
    
    Args:
        results: List of search results
        query: The search query
        
    Returns:
        Results with boosted confidence scores
    """
    boost = get_habit_boost(query)
    
    if boost > 0:
        for result in results:
            # Add habit boost to confidence score
            current_confidence = result.get("confidence", 0.5)
            result["confidence"] = min(current_confidence + boost, 1.0)
            result["habit_boost"] = boost
    
    return results
