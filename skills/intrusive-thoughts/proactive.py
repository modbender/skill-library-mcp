#!/usr/bin/env python3
"""
Proactive Agent Protocol - WAL and Working Buffer for Intrusive Thoughts

This module provides structured action logging (Write-Ahead Log) and a working buffer
for active context management. Enables reviewing what happened, detecting patterns,
and suggesting next actions based on mood, time, and history.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
import os
from collections import defaultdict, Counter

# Get the script directory for relative paths
SCRIPT_DIR = Path(__file__).parent
WAL_DIR = SCRIPT_DIR / "wal"
BUFFER_FILE = SCRIPT_DIR / "buffer" / "working_buffer.json"

# Ensure directories exist
WAL_DIR.mkdir(exist_ok=True)
BUFFER_FILE.parent.mkdir(exist_ok=True)

class ProactiveAgent:
    """Main class for the Proactive Agent Protocol"""
    
    def __init__(self):
        self.wal_dir = WAL_DIR
        self.buffer_file = BUFFER_FILE
        
    def _get_current_wal_file(self) -> Path:
        """Get current month's WAL file (rotate monthly)"""
        now = datetime.now()
        filename = f"wal-{now.year}-{now.month:02d}.json"
        return self.wal_dir / filename
        
    def _load_wal_entries(self, wal_file: Path) -> List[Dict]:
        """Load WAL entries from file"""
        if not wal_file.exists():
            return []
        try:
            with open(wal_file, 'r') as f:
                return [json.loads(line.strip()) for line in f if line.strip()]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
    def _append_wal_entry(self, entry: Dict) -> None:
        """Append entry to WAL (append-only)"""
        wal_file = self._get_current_wal_file()
        with open(wal_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            
    def _load_buffer(self) -> Dict:
        """Load working buffer"""
        if not self.buffer_file.exists():
            return {"active_items": [], "completed": [], "expired": []}
        try:
            with open(self.buffer_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"active_items": [], "completed": [], "expired": []}
            
    def _save_buffer(self, buffer_data: Dict) -> None:
        """Save working buffer"""
        with open(self.buffer_file, 'w') as f:
            json.dump(buffer_data, f, indent=2)
            
    def wal_log(self, type_: str, category: str, content: str, mood: str, 
                outcome: str = "pending", energy_cost: float = 0.0, 
                value_generated: float = 0.0, tags: List[str] = None,
                related_to: List[str] = None) -> str:
        """
        Append entry to Write-Ahead Log
        
        Args:
            type_: action|plan|observation|reflection
            category: build|explore|social|organize|learn
            content: Description of what happened/planned
            mood: Current mood during action
            outcome: success|failure|pending|skipped
            energy_cost: 0-1 how much effort required
            value_generated: 0-1 estimated value created
            tags: List of tags for categorization
            related_to: List of related WAL entry IDs
            
        Returns:
            Entry ID (UUID)
        """
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "type": type_,
            "category": category,
            "mood": mood,
            "content": content,
            "outcome": outcome,
            "energy_cost": energy_cost,
            "value_generated": value_generated,
            "tags": tags or [],
            "related_to": related_to or []
        }
        
        self._append_wal_entry(entry)
        return entry_id
        
    def wal_update_outcome(self, entry_id: str, outcome: str, 
                          value_generated: float = None) -> bool:
        """
        Update outcome of existing WAL entry
        
        Args:
            entry_id: Entry ID to update
            outcome: New outcome (success|failure|skipped)
            value_generated: Updated value estimate
            
        Returns:
            True if entry was found and updated
        """
        # Create new entry with outcome update (append-only principle)
        update_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "type": "reflection",
            "category": "organize",
            "mood": "neutral",
            "content": f"Updated outcome for {entry_id}: {outcome}",
            "outcome": "success",
            "energy_cost": 0.1,
            "value_generated": 0.1,
            "tags": ["meta", "outcome_update"],
            "related_to": [entry_id]
        }
        
        if value_generated is not None:
            update_entry["content"] += f" (value: {value_generated})"
            
        self._append_wal_entry(update_entry)
        return True
        
    def wal_search(self, query: str = None, category: str = None, 
                   mood: str = None, since: str = None, limit: int = 20) -> List[Dict]:
        """
        Search WAL entries with filters
        
        Args:
            query: Text search in content
            category: Filter by category
            mood: Filter by mood
            since: ISO date string or relative (e.g., "7d", "1h")
            limit: Maximum results to return
            
        Returns:
            List of matching WAL entries
        """
        # Parse since parameter
        since_dt = None
        if since:
            if since.endswith('d'):
                days = int(since[:-1])
                since_dt = datetime.now() - timedelta(days=days)
            elif since.endswith('h'):
                hours = int(since[:-1])
                since_dt = datetime.now() - timedelta(hours=hours)
            else:
                try:
                    since_dt = datetime.fromisoformat(since)
                except:
                    pass
                    
        # Load all WAL files for search (could be optimized)
        all_entries = []
        for wal_file in sorted(self.wal_dir.glob("wal-*.json")):
            all_entries.extend(self._load_wal_entries(wal_file))
            
        # Apply filters
        results = []
        for entry in reversed(all_entries):  # Most recent first
            # Time filter
            if since_dt:
                entry_dt = datetime.fromisoformat(entry["timestamp"])
                if entry_dt < since_dt:
                    continue
                    
            # Category filter
            if category and entry.get("category") != category:
                continue
                
            # Mood filter
            if mood and entry.get("mood") != mood:
                continue
                
            # Text search
            if query and query.lower() not in entry.get("content", "").lower():
                continue
                
            results.append(entry)
            if len(results) >= limit:
                break
                
        return results
        
    def wal_stats(self) -> Dict:
        """
        Generate statistics from WAL entries
        
        Returns:
            Dictionary with various statistics
        """
        # Load all entries
        all_entries = []
        for wal_file in sorted(self.wal_dir.glob("wal-*.json")):
            all_entries.extend(self._load_wal_entries(wal_file))
            
        if not all_entries:
            return {"total_entries": 0}
            
        # Calculate statistics
        total = len(all_entries)
        by_type = Counter(entry.get("type") for entry in all_entries)
        by_category = Counter(entry.get("category") for entry in all_entries)
        by_mood = Counter(entry.get("mood") for entry in all_entries)
        by_outcome = Counter(entry.get("outcome") for entry in all_entries)
        
        # Success rates by mood
        mood_outcomes = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
        for entry in all_entries:
            mood = entry.get("mood", "unknown")
            outcome = entry.get("outcome", "pending")
            mood_outcomes[mood][outcome] = mood_outcomes[mood].get(outcome, 0) + 1
            mood_outcomes[mood]["total"] += 1
            
        mood_success_rates = {}
        for mood, outcomes in mood_outcomes.items():
            if outcomes["total"] > 0:
                success_rate = outcomes.get("success", 0) / outcomes["total"]
                mood_success_rates[mood] = round(success_rate, 2)
                
        # Average energy and value
        energies = [entry.get("energy_cost", 0) for entry in all_entries 
                   if entry.get("energy_cost") is not None]
        values = [entry.get("value_generated", 0) for entry in all_entries 
                 if entry.get("value_generated") is not None]
        
        avg_energy = round(sum(energies) / len(energies), 2) if energies else 0
        avg_value = round(sum(values) / len(values), 2) if values else 0
        
        return {
            "total_entries": total,
            "by_type": dict(by_type),
            "by_category": dict(by_category),
            "by_mood": dict(by_mood),
            "by_outcome": dict(by_outcome),
            "mood_success_rates": mood_success_rates,
            "avg_energy_cost": avg_energy,
            "avg_value_generated": avg_value,
            "most_productive_mood": max(mood_success_rates, key=mood_success_rates.get) if mood_success_rates else None
        }
        
    def buffer_add(self, content: str, priority: str = "medium", 
                   category: str = "reminder", expires_hours: int = 24,
                   mood_relevant: List[str] = None) -> str:
        """
        Add item to working buffer
        
        Args:
            content: Description of what needs attention
            priority: high|medium|low
            category: project|reminder|observation|goal
            expires_hours: Hours until auto-expiry
            mood_relevant: List of moods that should pay attention to this
            
        Returns:
            Item ID (UUID)
        """
        buffer_data = self._load_buffer()
        
        item_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(hours=expires_hours)
        
        item = {
            "id": item_id,
            "created": now.isoformat(),
            "expires": expires_at.isoformat(),
            "priority": priority,
            "content": content,
            "category": category,
            "mood_relevant": mood_relevant or []
        }
        
        buffer_data["active_items"].append(item)
        self._save_buffer(buffer_data)
        
        return item_id
        
    def buffer_get(self, mood: str = None, priority: str = None) -> List[Dict]:
        """
        Get active buffer items with optional filters
        
        Args:
            mood: Filter items relevant to this mood
            priority: Filter by priority level
            
        Returns:
            List of active buffer items
        """
        buffer_data = self._load_buffer()
        self._prune_expired_items(buffer_data)
        
        items = buffer_data["active_items"]
        
        # Apply filters
        if mood:
            items = [item for item in items 
                    if not item.get("mood_relevant") or mood in item.get("mood_relevant", [])]
                    
        if priority:
            items = [item for item in items if item.get("priority") == priority]
            
        # Sort by priority and creation time
        priority_order = {"high": 0, "medium": 1, "low": 2}
        items.sort(key=lambda x: (
            priority_order.get(x.get("priority", "medium"), 1),
            x.get("created", "")
        ))
        
        return items
        
    def buffer_complete(self, item_id: str) -> bool:
        """
        Mark buffer item as completed
        
        Args:
            item_id: Item ID to complete
            
        Returns:
            True if item was found and completed
        """
        buffer_data = self._load_buffer()
        
        for i, item in enumerate(buffer_data["active_items"]):
            if item["id"] == item_id:
                item["completed_at"] = datetime.now().isoformat()
                completed_item = buffer_data["active_items"].pop(i)
                buffer_data["completed"].append(completed_item)
                
                # Keep only recent completed items
                buffer_data["completed"] = buffer_data["completed"][-50:]
                
                self._save_buffer(buffer_data)
                return True
                
        return False
        
    def buffer_prune(self) -> int:
        """
        Remove expired items from buffer
        
        Returns:
            Number of items pruned
        """
        buffer_data = self._load_buffer()
        return self._prune_expired_items(buffer_data)
        
    def _prune_expired_items(self, buffer_data: Dict) -> int:
        """Internal method to prune expired items"""
        now = datetime.now()
        pruned_count = 0
        
        # Move expired items
        active_items = []
        for item in buffer_data["active_items"]:
            expires_at = datetime.fromisoformat(item["expires"])
            if expires_at <= now:
                item["expired_at"] = now.isoformat()
                buffer_data["expired"].append(item)
                pruned_count += 1
            else:
                active_items.append(item)
                
        buffer_data["active_items"] = active_items
        
        # Keep only recent expired items
        buffer_data["expired"] = buffer_data["expired"][-50:]
        
        if pruned_count > 0:
            self._save_buffer(buffer_data)
            
        return pruned_count
        
    def suggest_next_action(self, current_mood: str, time_of_day: str = None) -> List[Dict]:
        """
        Suggest next actions based on context
        
        Args:
            current_mood: Current agent mood
            time_of_day: morning|day|evening|night (auto-detected if None)
            
        Returns:
            List of suggested actions with reasoning
        """
        if time_of_day is None:
            hour = datetime.now().hour
            if 6 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 18:
                time_of_day = "day"
            elif 18 <= hour < 23:
                time_of_day = "evening"
            else:
                time_of_day = "night"
                
        suggestions = []
        
        # Check buffer for high-priority items
        buffer_items = self.buffer_get(mood=current_mood, priority="high")
        for item in buffer_items[:3]:  # Top 3 high-priority items
            suggestions.append({
                "type": "buffer_item",
                "priority": 100,
                "action": item["content"],
                "reasoning": f"High-priority {item['category']} item in buffer",
                "source": "working_buffer",
                "item_id": item["id"]
            })
            
        # Look at WAL patterns for this mood
        recent_entries = self.wal_search(mood=current_mood, since="7d", limit=50)
        if recent_entries:
            mood_categories = Counter(entry.get("category") for entry in recent_entries)
            successful_categories = [entry.get("category") for entry in recent_entries 
                                   if entry.get("outcome") == "success"]
            
            if successful_categories:
                best_category = Counter(successful_categories).most_common(1)[0][0]
                suggestions.append({
                    "type": "mood_pattern",
                    "priority": 80,
                    "action": f"Continue {best_category} work - you've been successful at this in {current_mood} mood",
                    "reasoning": f"Recent success pattern in {current_mood} mood",
                    "source": "wal_analysis",
                    "category": best_category
                })
                
        # Time-of-day suggestions
        time_suggestions = {
            "night": {
                "action": "Start a focused build or exploration session",
                "reasoning": "Night time is ideal for deep work and building",
                "category": "build"
            },
            "morning": {
                "action": "Plan the day and organize tasks",
                "reasoning": "Morning energy is good for organizing and planning",
                "category": "organize"
            },
            "day": {
                "action": "Social activities or collaborative work",
                "reasoning": "Daytime is ideal for social engagement",
                "category": "social"
            },
            "evening": {
                "action": "Reflect on the day and journal learnings",
                "reasoning": "Evening is good for reflection and synthesis",
                "category": "learn"
            }
        }
        
        if time_of_day in time_suggestions:
            suggestions.append({
                "type": "time_based",
                "priority": 60,
                "action": time_suggestions[time_of_day]["action"],
                "reasoning": time_suggestions[time_of_day]["reasoning"],
                "source": "time_heuristic",
                "category": time_suggestions[time_of_day]["category"]
            })
            
        # Medium priority buffer items
        medium_buffer = self.buffer_get(mood=current_mood, priority="medium")
        for item in medium_buffer[:2]:
            suggestions.append({
                "type": "buffer_item",
                "priority": 40,
                "action": item["content"],
                "reasoning": f"Medium-priority {item['category']} in buffer",
                "source": "working_buffer",
                "item_id": item["id"]
            })
            
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions


def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 proactive.py <command> [args...]")
        print("Commands: log, search, stats, buffer-add, buffer-list, suggest")
        return
        
    agent = ProactiveAgent()
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 6:
            print("Usage: log <type> <category> <mood> <content>")
            return
        entry_id = agent.wal_log(sys.argv[2], sys.argv[3], sys.argv[5], sys.argv[4])
        print(f"Logged: {entry_id}")
        
    elif command == "search":
        results = agent.wal_search(query=sys.argv[2] if len(sys.argv) > 2 else None)
        for entry in results:
            print(f"{entry['timestamp'][:19]} [{entry['mood']}] {entry['content']}")
            
    elif command == "stats":
        stats = agent.wal_stats()
        print(json.dumps(stats, indent=2))
        
    elif command == "buffer-add":
        if len(sys.argv) < 3:
            print("Usage: buffer-add <content>")
            return
        item_id = agent.buffer_add(sys.argv[2])
        print(f"Added to buffer: {item_id}")
        
    elif command == "buffer-list":
        items = agent.buffer_get()
        for item in items:
            print(f"[{item['priority']}] {item['content']}")
            
    elif command == "suggest":
        mood = sys.argv[2] if len(sys.argv) > 2 else "curious"
        suggestions = agent.suggest_next_action(mood)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion['action']}")
            print(f"   Reasoning: {suggestion['reasoning']}")
            print()


if __name__ == "__main__":
    main()