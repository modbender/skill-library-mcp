"""
Self-Improving Integration for Overkill Memory System
Captures learnings, errors, and corrections for continuous improvement
"""

from pathlib import Path
from datetime import datetime
import json

LEARNINGS_PATH = Path("~/.openclaw/memory/.learnings").expanduser()

# Ensure the learnhgs directory exists
LEARNINGS_PATH.mkdir(parents=True, exist_ok=True)


class SelfImprover:
    """Self-improvement logging for continuous learning"""
    
    def __init__(self):
        self.learnings_path = LEARNINGS_PATH
        self.errors_path = self.learnings_path / "ERRORS.md"
        self.features_path = self.learnings_path / "FEATURE_REQUESTS.md"
        self.learnings_file = self.learnings_path / "LEARNINGS.md"
        
        # Ensure files exist
        for f in [self.errors_path, self.features_path, self.learnings_file]:
            if not f.exists():
                f.write_text("")
    
    def log_error(self, error: str, context: str = ""):
        """Log command/operation failure"""
        timestamp = datetime.now().isoformat()
        content = f"""## {timestamp}
### Error
{error}
### Context
{context}
---

"""
        existing = self.errors_path.read_text() if self.errors_path.exists() else ""
        self.errors_path.write_text(existing + content)
        return {"status": "logged", "type": "error", "timestamp": timestamp}
    
    def log_correction(self, correction: str, context: str = ""):
        """Log user correction"""
        timestamp = datetime.now().isoformat()
        content = f"""## {timestamp}
### Correction
{correction}
### Context
{context}
### Category
correction
---

"""
        self.learnings_file.append(content)
        return {"status": "logged", "type": "correction", "timestamp": timestamp}
    
    def log_feature_request(self, feature: str, reason: str = ""):
        """Log missing capability"""
        timestamp = datetime.now().isoformat()
        content = f"""## {timestamp}
### Feature
{feature}
### Reason
{reason}
---

"""
        self.features_path.append(content)
        return {"status": "logged", "type": "feature_request", "timestamp": timestamp}
    
    def log_best_practice(self, practice: str, context: str = ""):
        """Log better approach discovered"""
        timestamp = datetime.now().isoformat()
        content = f"""## {timestamp}
### Practice
{practice}
### Context
{context}
### Category
best_practice
---

"""
        self.learnings_file.append(content)
        return {"status": "logged", "type": "best_practice", "timestamp": timestamp}
    
    def get_learnings(self) -> dict:
        """Get all learnings"""
        return {
            "errors": self.errors_path.read_text() if self.errors_path.exists() else "",
            "learnings": self.learnings_file.read_text() if self.learnings_file.exists() else "",
            "features": self.features_path.read_text() if self.features_path.exists() else ""
        }
    
    def list_all(self) -> dict:
        """List all learnings in a structured format"""
        learnings = self.get_learnings()
        result = {"errors": [], "corrections": [], "best_practices": [], "feature_requests": []}
        
        # Parse errors
        if learnings["errors"]:
            entries = learnings["errors"].split("## ")
            for entry in entries[1:]:  # Skip empty first
                if entry.strip():
                    lines = entry.split("\n", 1)
                    timestamp = lines[0].strip() if lines else "unknown"
                    result["errors"].append({"timestamp": timestamp, "entry": entry.strip()})
        
        # Parse learnings (corrections + best practices)
        if learnings["learnings"]:
            entries = learnings["learnings"].split("## ")
            for entry in entries[1:]:
                if entry.strip():
                    lines = entry.split("\n", 1)
                    timestamp = lines[0].strip() if lines else "unknown"
                    content = entry.strip()
                    if "correction" in content.lower():
                        result["corrections"].append({"timestamp": timestamp, "entry": content})
                    elif "best_practice" in content.lower() or "practice" in content.lower():
                        result["best_practices"].append({"timestamp": timestamp, "entry": content})
        
        # Parse feature requests
        if learnings["features"]:
            entries = learnings["features"].split("## ")
            for entry in entries[1:]:
                if entry.strip():
                    lines = entry.split("\n", 1)
                    timestamp = lines[0].strip() if lines else "unknown"
                    result["feature_requests"].append({"timestamp": timestamp, "entry": entry.strip()})
        
        return result


# CLI helper functions
def cli_log_error(text: str, context: str = ""):
    """CLI: Log an error"""
    improver = SelfImprover()
    result = improver.log_error(text, context)
    print(json.dumps(result, indent=2))


def cli_log_correction(text: str, context: str = ""):
    """CLI: Log a correction"""
    improver = SelfImprover()
    result = improver.log_correction(text, context)
    print(json.dumps(result, indent=2))


def cli_log_feature_request(text: str, reason: str = ""):
    """CLI: Log a feature request"""
    improver = SelfImprover()
    result = improver.log_feature_request(text, reason)
    print(json.dumps(result, indent=2))


def cli_log_best_practice(text: str, context: str = ""):
    """CLI: Log a best practice"""
    improver = SelfImprover()
    result = improver.log_best_practice(text, context)
    print(json.dumps(result, indent=2))


def cli_list_learnings():
    """CLI: List all learnings"""
    improver = SelfImprover()
    result = improver.list_all()
    print(json.dumps(result, indent=2))
