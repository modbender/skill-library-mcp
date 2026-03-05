#!/usr/bin/env python3
"""
Adaptive Learning Agent v1.0.0
A Claude agent that learns from errors, corrections, and successful patterns.

Free and open-source (MIT Licensed)
No external dependencies. Works locally with any Claude model.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path


@dataclass
class Learning:
    """A captured learning or insight"""
    id: str
    timestamp: str
    content: str
    category: str  # technique, bug-fix, api-endpoint, constraint, best-practice, error-handling
    source: str  # "user-correction", "error-discovery", "successful-pattern", "user-feedback"
    context: Optional[str] = None
    related_learnings: List[str] = None
    usefulness_score: float = 5.0  # 0-10 scale

    def __post_init__(self):
        if self.related_learnings is None:
            self.related_learnings = []


@dataclass
class Error:
    """A captured error or failure"""
    id: str
    timestamp: str
    error_description: str
    context: str
    attempted_solution: Optional[str] = None
    resolved: bool = False
    solution: Optional[str] = None
    prevention_tip: Optional[str] = None


class AdaptiveLearningAgent:
    """
    Captures and learns from errors, corrections, and successful patterns.

    Features:
    - Record errors and their solutions
    - Capture successful techniques and insights
    - Search learnings by keyword or category
    - Get summaries of accumulated knowledge
    - All data stored locally (no external APIs)
    """

    def __init__(self, storage_path: str = ".adaptive_learning"):
        """Initialize the learning agent"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.learnings_file = self.storage_path / "learnings.json"
        self.errors_file = self.storage_path / "errors.json"

        # Load existing data
        self.learnings: List[Learning] = self._load_learnings()
        self.errors: List[Error] = self._load_errors()

    def record_learning(
        self,
        content: str,
        category: str = "technique",
        source: str = "user-feedback",
        context: Optional[str] = None
    ) -> Learning:
        """Record a learning or insight"""
        learning = Learning(
            id=self._generate_id("learning"),
            timestamp=datetime.now().isoformat(),
            content=content,
            category=category,
            source=source,
            context=context
        )

        self.learnings.append(learning)
        self._save_learnings()

        print(f"✅ Learning recorded: {learning.id}")
        return learning

    def record_error(
        self,
        error_description: str,
        context: str,
        attempted_solution: Optional[str] = None,
        solution: Optional[str] = None,
        prevention_tip: Optional[str] = None
    ) -> Error:
        """Record an error and optionally its solution"""
        error = Error(
            id=self._generate_id("error"),
            timestamp=datetime.now().isoformat(),
            error_description=error_description,
            context=context,
            attempted_solution=attempted_solution,
            resolved=solution is not None,
            solution=solution,
            prevention_tip=prevention_tip
        )

        self.errors.append(error)
        self._save_errors()

        # If there's a solution, also record it as a learning
        if solution:
            self.record_learning(
                content=f"Fixed: {error_description} → {solution}",
                category="bug-fix",
                source="error-discovery",
                context=context
            )

        print(f"⚠️  Error recorded: {error.id}")
        return error

    def get_recent_learnings(self, limit: int = 10) -> List[Learning]:
        """Get the most recent learnings"""
        return sorted(
            self.learnings,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]

    def search_learnings(self, query: str) -> List[Learning]:
        """Search learnings by keyword or category"""
        query_lower = query.lower()
        results = []

        for learning in self.learnings:
            if (query_lower in learning.content.lower() or
                query_lower in learning.category.lower() or
                (learning.context and query_lower in learning.context.lower())):
                results.append(learning)

        return sorted(results, key=lambda x: x.usefulness_score, reverse=True)

    def get_learnings_by_category(self, category: str) -> List[Learning]:
        """Get all learnings of a specific category"""
        return [l for l in self.learnings if l.category == category]

    def get_unresolved_errors(self) -> List[Error]:
        """Get all unresolved errors"""
        return [e for e in self.errors if not e.resolved]

    def mark_error_resolved(self, error_id: str, solution: str) -> Optional[Error]:
        """Mark an error as resolved with a solution"""
        for error in self.errors:
            if error.id == error_id:
                error.resolved = True
                error.solution = solution
                self._save_errors()

                # Record as learning
                self.record_learning(
                    content=f"Resolved: {error.error_description} → {solution}",
                    category="bug-fix",
                    source="error-discovery"
                )
                return error
        return None

    def get_learning_summary(self) -> Dict:
        """Get a summary of all learnings"""
        by_category = {}
        for learning in self.learnings:
            if learning.category not in by_category:
                by_category[learning.category] = []
            by_category[learning.category].append(learning)

        error_stats = {
            "total_errors": len(self.errors),
            "resolved": sum(1 for e in self.errors if e.resolved),
            "unresolved": sum(1 for e in self.errors if not e.resolved),
        }

        return {
            "total_learnings": len(self.learnings),
            "learnings_by_category": {
                cat: len(items) for cat, items in by_category.items()
            },
            "recent_learnings": [
                asdict(l) for l in self.get_recent_learnings(5)
            ],
            "error_statistics": error_stats,
            "unresolved_errors": [
                asdict(e) for e in self.get_unresolved_errors()[:5]
            ]
        }

    def export_learnings(self, output_file: str = "learnings_export.json"):
        """Export all learnings to a JSON file"""
        data = {
            "learnings": [asdict(l) for l in self.learnings],
            "errors": [asdict(e) for e in self.errors],
            "exported_at": datetime.now().isoformat()
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"📁 Learnings exported to {output_file}")

    def _load_learnings(self) -> List[Learning]:
        """Load learnings from disk"""
        if not self.learnings_file.exists():
            return []

        try:
            with open(self.learnings_file, 'r') as f:
                data = json.load(f)
                return [Learning(**item) for item in data]
        except Exception as e:
            print(f"Warning: Could not load learnings: {e}")
            return []

    def _load_errors(self) -> List[Error]:
        """Load errors from disk"""
        if not self.errors_file.exists():
            return []

        try:
            with open(self.errors_file, 'r') as f:
                data = json.load(f)
                return [Error(**item) for item in data]
        except Exception as e:
            print(f"Warning: Could not load errors: {e}")
            return []

    def _save_learnings(self):
        """Save learnings to disk"""
        with open(self.learnings_file, 'w') as f:
            json.dump([asdict(l) for l in self.learnings], f, indent=2)

    def _save_errors(self):
        """Save errors to disk"""
        with open(self.errors_file, 'w') as f:
            json.dump([asdict(e) for e in self.errors], f, indent=2)

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID"""
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def format_learning_summary(self) -> str:
        """Format learning summary as readable string"""
        summary = self.get_learning_summary()

        output = f"""
╔═══════════════════════════════════════════════════════════╗
║         ADAPTIVE LEARNING AGENT - SUMMARY                 ║
╚═══════════════════════════════════════════════════════════╝

📊 Total Learnings: {summary['total_learnings']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

By Category:
"""
        for category, count in summary['learnings_by_category'].items():
            output += f"  • {category}: {count}\n"

        output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ ERROR STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Errors: {summary['error_statistics']['total_errors']}
✅ Resolved: {summary['error_statistics']['resolved']}
⏳ Unresolved: {summary['error_statistics']['unresolved']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 RECENT LEARNINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for i, learning in enumerate(summary['recent_learnings'], 1):
            output += f"\n{i}. [{learning['category']}] {learning['content'][:60]}...\n"
            output += f"   Source: {learning['source']} | {learning['timestamp'][:10]}\n"

        return output


if __name__ == "__main__":
    # Example usage
    agent = AdaptiveLearningAgent()

    # Record some learnings
    agent.record_learning(
        "Use claude-sonnet for faster API responses when latency matters",
        category="technique",
        context="API optimization"
    )

    agent.record_learning(
        "Always validate JSON before parsing to avoid silent failures",
        category="best-practice"
    )

    # Record an error
    agent.record_error(
        error_description="JSON parsing failed on empty input",
        context="Processing API response",
        solution="Add validation check before JSON.parse()"
    )

    # Print summary
    print(agent.format_learning_summary())

    # Search learnings
    results = agent.search_learnings("JSON")
    print(f"\n🔍 Found {len(results)} learnings matching 'JSON'")
