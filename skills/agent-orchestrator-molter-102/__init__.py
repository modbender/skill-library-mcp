"""
agent-orchestrator: Multi-agent orchestration for OpenClaw

Implements proven patterns for coordinating multiple AI agents:
- Work Crew: Parallel execution from multiple angles
- Supervisor: Dynamic task decomposition and delegation
- Pipeline: Sequential staged processing
- Council: Multi-expert deliberation and consensus
- Route: Automatic task classification and routing
"""

__version__ = "0.1.0"
__author__ = "OpenClaw Community"

from .crew import WorkCrew, ConvergenceMethod
from .utils import spawn_agent, collect_results, SessionManager

__all__ = [
    "WorkCrew",
    "ConvergenceMethod",
    "spawn_agent",
    "collect_results",
    "SessionManager",
]
