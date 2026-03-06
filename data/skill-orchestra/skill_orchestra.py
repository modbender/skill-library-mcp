"""
SkillOrchestra - Intelligent Skill Routing

Research Source: arXiv 2024 - Skill-aware routing
Performance: +22.5% over RL-based, 700x less training cost
Created: 2026-02-26
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class TaskFeatures:
    """Features extracted from task"""
    type: str
    domain: str
    complexity: float
    constraints: List[str]


@dataclass
class SkillMatch:
    """Skill match with scores"""
    skill_name: str
    relevance: float
    performance: float
    cost: float
    score: float = 0.0


@dataclass
class ExecutionResult:
    """Result from skill execution"""
    success: bool
    quality: float
    duration: float
    cost: float


class SkillCatalog:
    """Catalog of available skills"""

    def __init__(self):
        self.skills = {
            # Meta-Cognition
            "self-reflection": {"type": "meta", "domain": "general", "performance": 0.85, "cost": 0.1},
            "self-criticism": {"type": "meta", "domain": "general", "performance": 0.88, "cost": 0.15},
            "self-evolution": {"type": "meta", "domain": "general", "performance": 0.90, "cost": 0.2},
            "meta-meta-learning": {"type": "meta", "domain": "learning", "performance": 0.92, "cost": 0.25},
            "self-consistency": {"type": "reasoning", "domain": "general", "performance": 0.87, "cost": 0.3},

            # Reasoning
            "tree-of-thoughts": {"type": "reasoning", "domain": "planning", "performance": 0.85, "cost": 0.4},
            "graph-of-thoughts": {"type": "reasoning", "domain": "synthesis", "performance": 0.88, "cost": 0.45},
            "multi-step-planning": {"type": "planning", "domain": "general", "performance": 0.82, "cost": 0.3},
            "task-decomposition": {"type": "planning", "domain": "general", "performance": 0.84, "cost": 0.25},

            # Learning
            "few-shot-learning": {"type": "learning", "domain": "general", "performance": 0.86, "cost": 0.2},
            "active-learning": {"type": "learning", "domain": "general", "performance": 0.83, "cost": 0.15},
            "transfer-learning": {"type": "learning", "domain": "general", "performance": 0.81, "cost": 0.3},

            # Content
            "quick-summarizer": {"type": "content", "domain": "text", "performance": 0.90, "cost": 0.1},
            "content-generation": {"type": "content", "domain": "text", "performance": 0.85, "cost": 0.2},
            "email-writer": {"type": "content", "domain": "email", "performance": 0.88, "cost": 0.15},
            "twitter-thread": {"type": "content", "domain": "social", "performance": 0.87, "cost": 0.15},

            # Memory
            "mirix-memory": {"type": "memory", "domain": "general", "performance": 0.92, "cost": 0.05},
            "semantic-cache": {"type": "memory", "domain": "general", "performance": 0.95, "cost": 0.02},
            "prompt-compressor": {"type": "optimization", "domain": "general", "performance": 0.94, "cost": 0.08},

            # Agents
            "mar-orchestrator": {"type": "agent", "domain": "reflexion", "performance": 0.90, "cost": 0.4},
            "aggregator-agent": {"type": "agent", "domain": "synthesis", "performance": 0.88, "cost": 0.35},

            # Automation
            "desktop-control": {"type": "automation", "domain": "desktop", "performance": 0.82, "cost": 0.1},
            "error-recovery": {"type": "resilience", "domain": "general", "performance": 0.90, "cost": 0.15},
            "rate-limiter": {"type": "resilience", "domain": "api", "performance": 0.95, "cost": 0.01},
        }

    def get_skill(self, name: str) -> Optional[Dict]:
        """Get skill by name"""
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        """List all skill names"""
        return list(self.skills.keys())

    def get_by_type(self, skill_type: str) -> List[str]:
        """Get skills by type"""
        return [name for name, data in self.skills.items() if data["type"] == skill_type]


class PerformanceTracker:
    """Track skill performance for routing decisions"""

    def __init__(self):
        self.history: Dict[str, List[Dict]] = {}

    def record(self, skill_name: str, result: ExecutionResult):
        """Record skill execution result"""
        if skill_name not in self.history:
            self.history[skill_name] = []

        self.history[skill_name].append({
            "timestamp": datetime.now().isoformat(),
            "success": result.success,
            "quality": result.quality,
            "duration": result.duration,
            "cost": result.cost
        })

    def get_performance(self, skill_name: str, window: int = 10) -> float:
        """Get skill performance score (0-1)"""
        if skill_name not in self.history or len(self.history[skill_name]) == 0:
            return 0.5  # Default for new skills

        recent = self.history[skill_name][-window:]
        success_rate = sum(r["success"] for r in recent) / len(recent)
        avg_quality = sum(r["quality"] for r in recent) / len(recent)

        return success_rate * 0.5 + avg_quality * 0.5


class SkillOrchestra:
    """
    Intelligent skill routing for agents.

    Features:
    - Task-based skill matching
    - Performance tracking
    - Collapse prevention
    - Transparent routing
    """

    def __init__(
        self,
        strategy: str = "performance",
        collapse_prevention: bool = True,
        exploration_rate: float = 0.2
    ):
        self.catalog = SkillCatalog()
        self.tracker = PerformanceTracker()
        self.strategy = strategy
        self.collapse_prevention = collapse_prevention
        self.exploration_rate = exploration_rate
        self.min_relevance = 0.3

    def route(
        self,
        task: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Route task to best skill.

        Args:
            task: Task description
            context: Optional context (domain, priority, etc.)

        Returns:
            Selected skill name
        """
        if context is None:
            context = {}

        # Analyze task
        features = self._analyze_task(task, context)

        # Match skills
        matches = self._match_skills(features)

        if not matches:
            return "self-reflection"  # Default fallback

        # Rank skills
        ranked = self._rank_skills(matches)

        # Select best (with collapse prevention)
        selected = self._select_skill(ranked)

        return selected

    def _analyze_task(self, task: str, context: Dict) -> TaskFeatures:
        """Extract features from task"""
        task_lower = task.lower()

        # Classify type
        if any(word in task_lower for word in ["summarize", "summary"]):
            task_type = "content"
        elif any(word in task_lower for word in ["plan", "planning"]):
            task_type = "planning"
        elif any(word in task_lower for word in ["learn", "learning"]):
            task_type = "learning"
        elif any(word in task_lower for word in ["reflect", "critique", "evaluate"]):
            task_type = "meta"
        elif any(word in task_lower for word in ["automate", "control"]):
            task_type = "automation"
        elif any(word in task_lower for word in ["memory", "remember", "query"]):
            task_type = "memory"
        else:
            task_type = "reasoning"

        # Detect domain
        domain = context.get("domain", "general")

        # Assess complexity
        complexity = len(task.split()) / 50  # Simple heuristic
        complexity = min(max(complexity, 0.1), 1.0)

        # Extract constraints
        constraints = context.get("constraints", [])

        return TaskFeatures(
            type=task_type,
            domain=domain,
            complexity=complexity,
            constraints=constraints
        )

    def _match_skills(self, features: TaskFeatures) -> List[SkillMatch]:
        """Find matching skills"""
        matches = []

        for skill_name, skill_data in self.catalog.skills.items():
            # Calculate relevance
            type_match = 1.0 if skill_data["type"] == features.type else 0.3
            domain_match = 1.0 if skill_data["domain"] == features.domain or skill_data["domain"] == "general" else 0.5

            relevance = type_match * 0.6 + domain_match * 0.4

            if relevance >= self.min_relevance:
                # Get performance from tracker
                performance = self.tracker.get_performance(skill_name)

                # Use catalog performance if no history
                if performance == 0.5 and skill_name in self.catalog.skills:
                    performance = self.catalog.skills[skill_name]["performance"]

                matches.append(SkillMatch(
                    skill_name=skill_name,
                    relevance=relevance,
                    performance=performance,
                    cost=skill_data["cost"]
                ))

        return matches

    def _rank_skills(self, matches: List[SkillMatch]) -> List[SkillMatch]:
        """Rank skills by score"""
        for match in matches:
            # Calculate score based on strategy
            if self.strategy == "performance":
                score = match.relevance * match.performance
            elif self.strategy == "cost_optimized":
                score = match.relevance * match.performance * (1 - match.cost)
            elif self.strategy == "exploration":
                score = match.relevance * match.performance * 0.8 + random.random() * 0.2
            else:  # balanced
                score = match.relevance * 0.4 + match.performance * 0.4 + (1 - match.cost) * 0.2

            match.score = score

        return sorted(matches, key=lambda x: x.score, reverse=True)

    def _select_skill(self, ranked: List[SkillMatch]) -> str:
        """Select best skill with collapse prevention"""
        if not ranked:
            return "self-reflection"

        # Check for collapse
        if self.collapse_prevention and len(ranked) >= 2:
            top_score = ranked[0].score
            second_score = ranked[1].score

            # Collapse if gap too large
            if (top_score - second_score) / top_score > 0.5:
                # Inject exploration
                if random.random() < self.exploration_rate:
                    return ranked[1].skill_name

        return ranked[0].skill_name

    def record_result(
        self,
        skill_name: str,
        success: bool,
        quality: float,
        duration: float = 0.0,
        cost: float = 0.0
    ):
        """Record skill execution result"""
        result = ExecutionResult(
            success=success,
            quality=quality,
            duration=duration,
            cost=cost
        )
        self.tracker.record(skill_name, result)

    def explain_routing(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Explain routing decision"""
        features = self._analyze_task(task, context or {})
        matches = self._match_skills(features)
        ranked = self._rank_skills(matches)

        return {
            "task": task,
            "features": {
                "type": features.type,
                "domain": features.domain,
                "complexity": features.complexity
            },
            "candidates": [
                {
                    "skill": m.skill_name,
                    "relevance": m.relevance,
                    "performance": m.performance,
                    "cost": m.cost,
                    "score": m.score
                }
                for m in ranked[:5]
            ],
            "selected": ranked[0].skill_name if ranked else None,
            "strategy": self.strategy
        }


# Convenience function
def create_orchestra(strategy: str = "performance") -> SkillOrchestra:
    """Create SkillOrchestra with specified strategy"""
    return SkillOrchestra(strategy=strategy)
