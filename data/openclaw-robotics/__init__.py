"""Unitree Robot Controller Skill for OpenClaw

Control robots via IM platforms with natural language commands.
"""

from .skill import (
    RoboticsSkill,
    initialize,
    execute,
    start_slam,
    navigate,
    get_status,
    list_robots
)
from .robot_adapters import RobotFactory, RobotAdapter, RobotState, TaskResult
from .sensor_adapters import Insight9Adapter

__version__ = "2.0.0"
__author__ = "LooperRobotics"

__all__ = [
    "RoboticsSkill",
    "initialize",
    "execute", 
    "start_slam",
    "navigate",
    "get_status",
    "list_robots",
    "RobotFactory",
    "RobotAdapter",
    "RobotState",
    "TaskResult",
    "Insight9Adapter",
    "__version__",
]
