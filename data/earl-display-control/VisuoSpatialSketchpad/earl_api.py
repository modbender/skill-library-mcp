"""
Earl's Mind API — Simple helpers for an AI agent to update the visuospatial sketchpad.

Usage (from an AI agent or script):

    from earl_api import EarlMind

    mind = EarlMind()

    # Update Earl's mood and vibe
    mind.set_mood("happy", energy=0.9, vibe="Just noticed the sunset through the window. Beautiful.")

    # Set Earl's photo
    mind.set_photo("earl_selfie.jpg", caption="Looking good today.")

    # Post important house stuff
    mind.post_house_stuff("Bins go out tonight", detail="It's Wednesday again.", priority="high", category="chores", icon="🗑️")

    # Update a room's status
    mind.update_room("kitchen", status="occupied", notes="Someone's cooking pasta. Smells great.")

    # Drop a hot take (Earl Unplugged)
    mind.hot_take("Pineapple on pizza", "Controversial but I respect the audacity.", heat=0.6, emoji="🍕")

    # Doodle on the sketchpad
    mind.doodle("🌧️", x=0.3, y=0.2, size=30, note="Rain starting")
    mind.sketch_note("todo: remind about umbrellas", x=0.5, y=0.8, color="#fbbf24")

    # Record a long-term pattern
    mind.learn_pattern("The cat always sits by the window at 3pm", confidence=0.7, observations=5)

    # Save all changes (each method auto-saves, but you can batch too)
    mind.save()
"""

import json
import os
import uuid
from datetime import datetime, timezone

MIND_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "earl_mind.json")


class EarlMind:
    """Read and write Earl's visuospatial sketchpad state."""

    def __init__(self, path=None):
        self.path = path or MIND_FILE
        self.mind = self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        """Write current mind state to disk. The HTML viewer auto-refreshes."""
        self.mind["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.mind["meta"]["update_count"] = self.mind["meta"].get("update_count", 0) + 1
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.mind, f, indent=2, ensure_ascii=False)
        return self

    # ── Identity & Mood ──────────────────────────────────────────────

    def set_mood(self, mood, energy=None, vibe=None, expression=None):
        """Update Earl's current mood, energy level, and inner monologue."""
        self.mind["identity"]["mood"] = mood
        if energy is not None:
            self.mind["identity"]["energy"] = max(0, min(1, energy))
        if vibe is not None:
            self.mind["identity"]["current_vibe"] = vibe
        if expression is not None:
            self.mind["identity"]["avatar_expression"] = expression
        return self.save()

    def set_photo(self, url, caption=None):
        """Set Earl's photo (URL or local file path) shown in the header."""
        self.mind["identity"]["photo"] = url
        if caption is not None:
            self.mind["identity"]["photo_caption"] = caption
        return self.save()

    # ── Important House Stuff ────────────────────────────────────────

    def post_house_stuff(self, title, detail="", priority="medium", category="general", icon="📌"):
        """Add an item to the Important House Stuff noticeboard."""
        items = self.mind["house_stuff"]["items"]
        items.insert(0, {
            "id": f"hs_{uuid.uuid4().hex[:6]}",
            "title": title,
            "detail": detail,
            "priority": priority,
            "category": category,
            "icon": icon
        })
        return self.save()

    def resolve_house_stuff(self, item_id):
        """Remove a resolved item from Important House Stuff by ID."""
        self.mind["house_stuff"]["items"] = [
            i for i in self.mind["house_stuff"]["items"] if i["id"] != item_id
        ]
        return self.save()

    def clear_house_stuff(self):
        """Clear all house stuff items."""
        self.mind["house_stuff"]["items"] = []
        return self.save()

    # ── Spatial Awareness ────────────────────────────────────────────

    def update_room(self, room_id, status=None, notes=None, attention=None):
        """Update a room's status, notes, or attention level."""
        for room in self.mind["spatial_awareness"]["rooms"]:
            if room["id"] == room_id:
                if status is not None:
                    room["status"] = status
                if notes is not None:
                    room["notes"] = notes
                if attention is not None:
                    room["attention_level"] = max(0, min(1, attention))
                break
        return self.save()

    def add_room(self, room_id, name, x, y, icon="default", status="all_good", notes="", attention=0.3):
        """Add a new room to Earl's spatial awareness."""
        self.mind["spatial_awareness"]["rooms"].append({
            "id": room_id,
            "name": name,
            "x": max(0, min(1, x)),
            "y": max(0, min(1, y)),
            "status": status,
            "attention_level": max(0, min(1, attention)),
            "notes": notes,
            "icon": icon
        })
        return self.save()

    def sweep(self):
        """Mark that Earl just did a full house sweep."""
        self.mind["spatial_awareness"]["last_sweep"] = datetime.now(timezone.utc).isoformat()
        return self.save()

    # ── Earl Unplugged (Hot Takes) ───────────────────────────────────

    def hot_take(self, topic, take, heat=0.5, emoji="💭"):
        """Add or update a hot take. If topic exists, update it."""
        for t in self.mind["earl_unplugged"]:
            if t["topic"].lower() == topic.lower():
                t["take"] = take
                t["heat"] = max(0, min(1, heat))
                t["emoji"] = emoji
                t["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                return self.save()

        self.mind["earl_unplugged"].append({
            "id": f"eu_{uuid.uuid4().hex[:6]}",
            "topic": topic,
            "take": take,
            "heat": max(0, min(1, heat)),
            "emoji": emoji,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        })
        return self.save()

    def drop_take(self, topic):
        """Remove a hot take by topic."""
        self.mind["earl_unplugged"] = [
            t for t in self.mind["earl_unplugged"]
            if t["topic"].lower() != topic.lower()
        ]
        return self.save()

    # ── Earl's Sketchpad ─────────────────────────────────────────────

    def doodle(self, label, x=0.5, y=0.5, size=30, color="#FFD700", note=""):
        """Place an emoji doodle on the sketchpad."""
        self.mind["sketchpad"]["canvas"].append({
            "id": f"sk_{uuid.uuid4().hex[:6]}",
            "type": "doodle",
            "label": label,
            "x": max(0, min(1, x)),
            "y": max(0, min(1, y)),
            "size": size,
            "color": color,
            "note": note
        })
        return self.save()

    def sketch_note(self, text, x=0.5, y=0.5, size=12, color="#88CCFF"):
        """Place a text note on the sketchpad."""
        self.mind["sketchpad"]["canvas"].append({
            "id": f"sk_{uuid.uuid4().hex[:6]}",
            "type": "note",
            "label": text,
            "x": max(0, min(1, x)),
            "y": max(0, min(1, y)),
            "size": size,
            "color": color,
            "note": ""
        })
        return self.save()

    def clear_sketchpad(self):
        """Wipe the sketchpad clean."""
        self.mind["sketchpad"]["canvas"] = []
        return self.save()

    # ── Long-Term Patterns ───────────────────────────────────────────

    def learn_pattern(self, pattern, confidence=0.5, observations=1):
        """Record or update a long-term behavioral pattern."""
        for p in self.mind["long_term_patterns"]:
            if p["pattern"].lower() == pattern.lower():
                p["confidence"] = max(0, min(1, confidence))
                p["observations"] = observations
                return self.save()

        self.mind["long_term_patterns"].append({
            "pattern": pattern,
            "confidence": max(0, min(1, confidence)),
            "observations": observations
        })
        return self.save()

    # ── Convenience ──────────────────────────────────────────────────

    def snapshot(self):
        """Return the current mind state as a dict (useful for AI context)."""
        return self.mind

    def summary(self):
        """Return a human-readable summary of Earl's current state."""
        m = self.mind
        lines = [
            f"🧙🏻 {m['identity']['name']} — {m['identity']['mood']} (energy: {int(m['identity']['energy']*100)}%)",
            f"💭 \"{m['identity']['current_vibe']}\"",
            f"",
            f"📋 Important House Stuff:"
        ]
        for item in m.get('house_stuff', {}).get('items', []):
            prio = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(item['priority'], '⚪')
            lines.append(f"  {prio} {item['icon']} {item['title']}: {item['detail']}")
        lines.append("")
        lines.append(f"🏠 Rooms:")
        for r in m['spatial_awareness']['rooms']:
            lines.append(f"  {r['name']}: {r['status']} — {r['notes']}")
        lines.append("")
        lines.append(f"🎤 Earl Unplugged ({len(m.get('earl_unplugged', []))}):")
        for t in m.get('earl_unplugged', []):
            lines.append(f"  {t['emoji']} {t['topic']}: \"{t['take']}\"")
        return "\n".join(lines)


if __name__ == "__main__":
    mind = EarlMind()
    print(mind.summary())
