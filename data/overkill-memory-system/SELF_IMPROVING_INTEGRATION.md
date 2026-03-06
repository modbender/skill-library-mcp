# Integration: self-improving-agent

## Overview

self-improving-agent captures learnings, errors, and corrections for continuous improvement. Perfect complement to our memory system!

---

## What It Does

| Situation | Log File |
|-----------|----------|
| Command fails | `.learnings/ERRORS.md` |
| User corrects you | `.learnings/LEARNINGS.md` |
| Missing feature | `.learnings/FEATURE_REQUESTS.md` |
| Knowledge gap | `.learnings/LEARNINGS.md` |
| Better approach | `.learnings/LEARNINGS.md` (best_practice) |

---

## Integration with Overkill Memory System

### Current Coverage

| Feature | What it tracks |
|---------|---------------|
| acc-error | Error patterns |
| habits | Repeated actions |
| neuro | Corrections importance |
| kg | Atomic facts |

### What self-improving-agent Adds

| New | Benefit |
|-----|---------|
| ERROR logging | Command failures |
| FEATURE_REQUESTS | Missing capabilities |
| Best practices | Better approaches |
| Knowledge gaps | Outdated knowledge |

---

## Implementation

### 1. Create self_improving.py

```python
from pathlib import Path
from datetime import datetime

LEARNINGS_PATH = Path("~/.openclaw/memory/.learnings").expanduser()

class SelfImprover:
    def __init__(self):
        self.learnings_path = LEARNINGS_PATH
        self.errors_path = self.learnings_path / "ERRORS.md"
        self.features_path = self.learnings_path / "FEATURE_REQUESTS.md"
    
    def log_error(self, error: str, context: str = ""):
        """Log command/operation failure"""
        content = f"""## {datetime.now().isoformat()}
### Error
{error}
### Context
{context}
---
"""
        self.errors_path.append(content)
    
    def log_correction(self, correction: str, context: str = ""):
        """Log user correction"""
        content = f"""## {datetime.now().isoformat()}
### Correction
{correction}
### Context
{context}
### Category
correction
---
"""
        (self.learnings_path / "LEARNINGS.md").append(content)
    
    def log_feature_request(self, feature: str, reason: str = ""):
        """Log missing capability"""
        content = f"""## {datetime.now().isoformat()}
### Feature
{feature}
### Reason
{reason}
---
"""
        self.features_path.append(content)
    
    def log_best_practice(self, practice: str, context: str = ""):
        """Log better approach discovered"""
        content = f"""## {datetime.now().isoformat()}
### Practice
{practice}
### Context
{context}
### Category
best_practice
---
"""
        (self.learnings_path / "LEARNINGS.md").append(content)
    
    def get_learnings(self) -> dict:
        """Get all learnings"""
        return {
            "errors": self.errors_path.read() if self.errors_path.exists() else "",
            "learnings": (self.learnings_path / "LEARNINGS.md").read() if (self.learnings_path / "LEARNINGS.md").exists() else "",
            "features": self.features_path.read() if self.features_path.exists() else ""
        }
```

### 2. CLI Commands

```bash
# Log an error
overkill improve error "Command failed" --context "tried to install package"

# Log a correction
overkill improve correct "No, that's wrong" --context "user corrected my answer"

# Log feature request
overkill improve request "Need markdown support" --reason "user wants to export to md"

# Log best practice
overkill improve better "Use async for I/O" --context "found during refactoring"

# Get all learnings
overkill improve list

# Promote to memory
overkill improve promote <learning_id>
```

### 3. Integration Points

```python
# In hybrid_search - after results
if user_correction_detected:
    improver.log_correction(correction, query)

# In error handling
except Exception as e:
    improver.log_error(str(e), context)

# Before complex tasks
learnings = improver.get_learnings()
if relevant := filter(learnings, task):
    inject_into_context(relevant)
```

---

## Summary

| Feature | File | Integration |
|---------|------|-------------|
| Error logging | ERRORS.md | Auto-capture failures |
| Corrections | LEARNINGS.md | User feedback capture |
| Feature requests | FEATURE_REQUESTS.md | Missing capabilities |
| Best practices | LEARNINGS.md | Better approaches |

**Perfect complement to our acc-error and habits!**

---

*self-improving-agent integration for overkill-memory-system*
