"""ClawSkillShield package API
"""
from .skill import scan_local, quarantine, generate_report

__version__ = "0.1.1"
__all__ = ["scan_local", "quarantine", "generate_report"]
