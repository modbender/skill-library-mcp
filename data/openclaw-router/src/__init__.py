"""
OpenClaw Router Skill v3.0
通用智能路由系统 - 自动选择最佳模型，节省 60% 成本

Author: pepsiboy87
Version: 3.0.0
License: MIT
"""

from .detector import EnvironmentDetector
from .recommender import ConfigRecommender
from .router import ModelRouter
from .config_manager import ConfigManager

__version__ = "3.0.0"
__author__ = "pepsiboy87"
__all__ = [
    "EnvironmentDetector",
    "ConfigRecommender",
    "ModelRouter",
    "ConfigManager"
]
