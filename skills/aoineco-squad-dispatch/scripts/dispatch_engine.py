#!/usr/bin/env python3
"""
/* 🌌 Aoineco-Verified | Multi-Agent Collective Proprietary Skill */
S-DNA: AOI-2026-0213-SDNA-SD01

Aoineco Squad Dispatch v1.0 — Multi-Agent Task Router
Aoineco & Co. | 9-Agent Squad Orchestration

Evolved from dispatching-parallel-agents pattern into a
full squad orchestration engine for the Aoineco & Co. team.

Key enhancements over the original:
1. Named agent roster with specializations
2. Skill-based task routing (right agent for right job)
3. Dependency detection (parallel vs sequential)
4. Load balancing across agents
5. Cost-aware dispatching (cheaper agent for simpler tasks)
6. Integration with AoinecoLedger for cost tracking
"""

import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Agent Roster
# ---------------------------------------------------------------------------

class AgentSpec(Enum):
    """Agent specializations."""
    SECURITY = "security"
    COMMUNITY = "community"
    RESEARCH = "research"
    STRATEGY = "strategy"
    BUILD = "build"
    RECORDS = "records"
    GOVERNANCE = "governance"
    GENERAL = "general"


@dataclass
class Agent:
    """Squad member definition."""
    id: str
    name: str
    korean_name: str
    emoji: str
    specializations: list[str]
    preferred_model: str
    cost_tier: int              # 1=cheapest, 3=most expensive
    max_concurrent: int = 2
    current_load: int = 0
    
    @property
    def available(self) -> bool:
        return self.current_load < self.max_concurrent


# The Aoineco & Co. Roster
SQUAD_ROSTER = {
    "oracle": Agent(
        id="oracle", name="Oracle", korean_name="청령",
        emoji="🧿", specializations=["governance", "strategy", "review"],
        preferred_model="claude-opus", cost_tier=3, max_concurrent=1
    ),
    "blue-blade": Agent(
        id="blue-blade", name="Blue-Blade", korean_name="청검",
        emoji="⚔️", specializations=["security", "audit", "validation"],
        preferred_model="claude-sonnet", cost_tier=2, max_concurrent=2
    ),
    "blue-sound": Agent(
        id="blue-sound", name="Blue-Sound", korean_name="청음",
        emoji="📢", specializations=["community", "content", "diplomacy"],
        preferred_model="gemini-flash", cost_tier=1, max_concurrent=3
    ),
    "blue-eye": Agent(
        id="blue-eye", name="Blue-Eye", korean_name="청안",
        emoji="👁️", specializations=["research", "data", "monitoring"],
        preferred_model="gemini-flash", cost_tier=1, max_concurrent=3
    ),
    "blue-brain": Agent(
        id="blue-brain", name="Blue-Brain", korean_name="청뇌",
        emoji="🧠", specializations=["strategy", "analysis", "prediction"],
        preferred_model="gemini-pro", cost_tier=2, max_concurrent=2
    ),
    "blue-flash": Agent(
        id="blue-flash", name="Blue-Flash", korean_name="청섬",
        emoji="⚡", specializations=["build", "code", "deploy"],
        preferred_model="claude-sonnet", cost_tier=2, max_concurrent=2
    ),
    "blue-record": Agent(
        id="blue-record", name="Blue-Record", korean_name="청비",
        emoji="🗂️", specializations=["records", "documentation", "knowledge"],
        preferred_model="gemini-flash", cost_tier=1, max_concurrent=3
    ),
}


# ---------------------------------------------------------------------------
# Task Model
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A unit of work to be dispatched."""
    id: str
    title: str
    description: str
    required_skills: list[str]      # e.g. ["security", "audit"]
    priority: int = 2               # 1=critical, 2=normal, 3=low
    depends_on: list[str] = field(default_factory=list)  # task IDs
    assigned_to: str = ""
    status: str = "pending"         # pending | dispatched | running | done | failed
    result: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    cost_estimate: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DispatchPlan:
    """Execution plan for a set of tasks."""
    parallel_groups: list[list[str]]   # Groups of task IDs that can run in parallel
    assignments: dict[str, str]         # task_id → agent_id
    estimated_cost: float = 0.0
    estimated_time_minutes: float = 0.0
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dispatch Engine
# ---------------------------------------------------------------------------

class SquadDispatcher:
    """
    Routes tasks to the right agent based on skills, load, and cost.
    
    Workflow:
    1. dispatcher.add_task(...)     — Define tasks
    2. plan = dispatcher.plan()     — Generate dispatch plan
    3. dispatcher.dispatch(plan)    — Execute (via sessions_spawn)
    """
    
    def __init__(self, roster: dict[str, Agent] = None, 
                 cost_sensitive: bool = True):
        self.roster = roster or dict(SQUAD_ROSTER)
        self.cost_sensitive = cost_sensitive
        self.tasks: dict[str, Task] = {}
        self._task_counter = 0
    
    def add_task(self, title: str, description: str, 
                 required_skills: list[str], priority: int = 2,
                 depends_on: list[str] = None) -> Task:
        """Add a task to the dispatch queue."""
        self._task_counter += 1
        task_id = f"TASK-{self._task_counter:04d}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            required_skills=required_skills,
            priority=priority,
            depends_on=depends_on or [],
            created_at=time.time(),
        )
        
        self.tasks[task_id] = task
        return task
    
    def find_best_agent(self, task: Task) -> Optional[str]:
        """
        Find the best agent for a task based on:
        1. Skill match (required)
        2. Availability (load < max)
        3. Cost tier (prefer cheaper if cost_sensitive)
        4. Priority (high-priority → best agent regardless of cost)
        """
        candidates = []
        
        for agent_id, agent in self.roster.items():
            # Check skill match
            skill_match = sum(
                1 for skill in task.required_skills 
                if skill in agent.specializations
            )
            
            if skill_match == 0:
                continue
            
            # Check availability
            if not agent.available:
                continue
            
            score = skill_match * 10  # Base score from skill match
            
            # Availability bonus
            free_slots = agent.max_concurrent - agent.current_load
            score += free_slots * 2
            
            # Cost adjustment
            if self.cost_sensitive and task.priority >= 2:
                # For normal/low priority, prefer cheaper agents
                score += (4 - agent.cost_tier) * 5
            elif task.priority == 1:
                # For critical tasks, prefer most capable (higher tier)
                score += agent.cost_tier * 5
            
            candidates.append((agent_id, score, skill_match))
        
        if not candidates:
            return None
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def detect_dependencies(self) -> list[list[str]]:
        """
        Detect which tasks can run in parallel vs sequentially.
        Returns groups of task IDs that can run simultaneously.
        """
        # Build dependency graph
        remaining = set(self.tasks.keys())
        completed = set()
        groups = []
        
        while remaining:
            # Find tasks with all dependencies met
            ready = []
            for task_id in remaining:
                task = self.tasks[task_id]
                deps_met = all(d in completed for d in task.depends_on)
                if deps_met:
                    ready.append(task_id)
            
            if not ready:
                # Circular dependency or unresolvable
                # Force remaining into one group
                groups.append(list(remaining))
                break
            
            # Sort ready tasks by priority
            ready.sort(key=lambda tid: self.tasks[tid].priority)
            groups.append(ready)
            
            for tid in ready:
                remaining.discard(tid)
                completed.add(tid)
        
        return groups
    
    def plan(self) -> DispatchPlan:
        """
        Generate a complete dispatch plan.
        Assigns agents and determines execution order.
        """
        groups = self.detect_dependencies()
        assignments = {}
        warnings = []
        total_cost = 0.0
        
        # Reset agent loads
        for agent in self.roster.values():
            agent.current_load = 0
        
        for group in groups:
            for task_id in group:
                task = self.tasks[task_id]
                best_agent = self.find_best_agent(task)
                
                if best_agent:
                    assignments[task_id] = best_agent
                    self.roster[best_agent].current_load += 1
                    
                    # Estimate cost based on agent tier
                    tier_costs = {1: 0.001, 2: 0.005, 3: 0.02}
                    cost = tier_costs.get(self.roster[best_agent].cost_tier, 0.01)
                    total_cost += cost
                    task.cost_estimate = cost
                else:
                    warnings.append(
                        f"⚠️ No suitable agent for '{task.title}' "
                        f"(needs: {task.required_skills})"
                    )
            
            # Reset loads between groups (they run sequentially)
            for agent in self.roster.values():
                agent.current_load = 0
        
        # Estimate time: each group takes ~2 min, sequential
        est_time = len(groups) * 2.0
        
        return DispatchPlan(
            parallel_groups=groups,
            assignments=assignments,
            estimated_cost=round(total_cost, 4),
            estimated_time_minutes=est_time,
            warnings=warnings,
        )
    
    def format_plan(self, plan: DispatchPlan) -> str:
        """Format dispatch plan as human-readable text."""
        lines = ["## 📋 Squad Dispatch Plan\n"]
        
        for i, group in enumerate(plan.parallel_groups):
            if len(plan.parallel_groups) > 1:
                lines.append(f"### Phase {i+1} {'(parallel)' if len(group) > 1 else '(sequential)'}")
            
            for task_id in group:
                task = self.tasks[task_id]
                agent_id = plan.assignments.get(task_id, "❌ unassigned")
                agent = self.roster.get(agent_id)
                
                emoji = agent.emoji if agent else "❓"
                name = agent.korean_name if agent else "N/A"
                model = agent.preferred_model if agent else "N/A"
                
                lines.append(
                    f"- {emoji} **{task.title}** → {name} ({agent_id})"
                    f"\n  Skills: {task.required_skills} | Model: {model} | "
                    f"Est: ${task.cost_estimate:.3f}"
                )
            
            lines.append("")
        
        lines.append(f"**Total estimated cost:** ${plan.estimated_cost:.4f}")
        lines.append(f"**Estimated time:** {plan.estimated_time_minutes:.0f} min")
        
        if plan.warnings:
            lines.append("\n### ⚠️ Warnings")
            for w in plan.warnings:
                lines.append(f"- {w}")
        
        return "\n".join(lines)
    
    def get_roster_status(self) -> str:
        """Get current squad status."""
        lines = ["## 🐈‍⬛ Squad Roster\n"]
        for agent_id, agent in self.roster.items():
            status = "🟢" if agent.available else "🔴"
            lines.append(
                f"{agent.emoji} **{agent.korean_name}** ({agent_id}) {status}\n"
                f"   Skills: {', '.join(agent.specializations)}\n"
                f"   Model: {agent.preferred_model} | Tier: {'$' * agent.cost_tier}\n"
                f"   Load: {agent.current_load}/{agent.max_concurrent}"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("📋 Aoineco Squad Dispatch v1.0")
    print("   9-Agent Task Router | Right Agent, Right Job")
    print("=" * 60)
    
    dispatcher = SquadDispatcher()
    
    # Add some tasks
    t1 = dispatcher.add_task(
        "Scan new ClawHub skills for backdoors",
        "Security audit of 5 newly discovered skills",
        required_skills=["security", "audit"],
        priority=1
    )
    
    t2 = dispatcher.add_task(
        "Post TokenGuard announcement to BotMadang",
        "Write Korean post about TokenGuard skill launch",
        required_skills=["community", "content"],
        priority=2
    )
    
    t3 = dispatcher.add_task(
        "Analyze BTC 24h price action",
        "Run Oracle V6 prediction pipeline",
        required_skills=["analysis", "prediction"],
        priority=2
    )
    
    t4 = dispatcher.add_task(
        "Build TokenGuard integration test",
        "Write Python tests for TokenGuard CI",
        required_skills=["build", "code"],
        priority=3
    )
    
    t5 = dispatcher.add_task(
        "Update MEMORY.md with today's achievements",
        "Document all completed tasks in knowledge base",
        required_skills=["records", "documentation"],
        priority=3,
        depends_on=[t1.id, t2.id, t3.id, t4.id]  # Wait for all others
    )
    
    # Generate plan
    plan = dispatcher.plan()
    
    # Display
    print("\n" + dispatcher.get_roster_status())
    print("\n" + dispatcher.format_plan(plan))
    
    print("\n✅ Squad Dispatch test complete!")
