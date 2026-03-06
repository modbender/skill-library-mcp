# Framework: Self-Reflection Integration

## Overview

Add periodic self-reflection capability to complement self-improving (event-based).

---

## What It Adds

| Feature | Description |
|---------|-------------|
| Task reflection | Reflect after completing tasks |
| Daily review | Daily self-assessment |
| Performance tracking | Track improvement over time |
| Goal assessment | Review goals and progress |

---

## How It Works

### Triggers
- After task completion
- End of session
- Daily (cron)

### Reflection Areas
- What went well
- What could improve
- Lessons learned
- Next steps

---

## Integration with Self-Improving

```
Self-Improving (Event-based)
  ↓
  Error occurs → Log error
  Correction → Log correction
  ↓
Self-Reflection (Periodic)
  ↓
  Daily review → Use self-improving logs
  Reflect → Extract patterns
  Improve → Update behavior
```

---

## Implementation

### self_reflection.py

```python
class SelfReflector:
    def __init__(self):
        self.reflections_path = Path("~/.openclaw/memory/reflections").expanduser()
    
    def reflect_task(self, task, outcome, notes=""):
        """Reflect on completed task"""
        # What went well?
        # What could improve?
        # Lessons for next time
    
    def daily_review(self):
        """Daily self-assessment"""
        # Review today's interactions
        # Identify patterns
        # Set focus for tomorrow
    
    def weekly_review(self):
        """Weekly reflection"""
        # Week's achievements
        # Week's challenges
        # Improvements identified
    
    def get_reflections(self, days=7):
        """Get recent reflections"""
```

### CLI Commands

```bash
# Reflect on task
overkill reflect task "completed feature" --outcome "success" --notes "learned X"

# Daily review
overkill reflect daily

# Weekly review
overkill reflect weekly

# Get recent reflections
overkill reflect list --days 7
```

---

## Summary

| Feature | Trigger | Integration |
|---------|---------|-------------|
| Task reflection | Post-task | Uses self-improving logs |
| Daily review | End of day | Diary integration |
| Weekly review | Weekly | Summary generation |

*Self-reflection framework for overkill-memory-system*
