"""War/Den Governance Skill for OpenClaw -- every action governed before execution.

Community mode: zero external dependencies. Local YAML policies, SQLite audit log.
Enterprise mode: Sentinel_OS cloud governance + EngramPort memory (MandelDB backend).

Install: openclaw skill install an2b/warden-governance
"""

from warden_governance.skill import WardenGovernanceSkill

__version__ = "1.0.0"
__all__ = ["WardenGovernanceSkill"]
