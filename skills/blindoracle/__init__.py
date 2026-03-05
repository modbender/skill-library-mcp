"""
BlindOracle OpenClaw Skill Package (Brand A: Privacy-First)

Privacy-first infrastructure services for AI agents - forecasting,
private settlement, credential verification, and cross-rail transfers.

All protected by CaMel 4-layer security and powered by guardian federation
for zero-identity-linkage privacy.

Brand A: Sanitized terminology for general-purpose platforms.
No cryptocurrency-specific language. Suitable for all distribution channels.

@author: Craig M. Brown
@version: 1.0.0
@license: Proprietary
"""

from .handler import handle_request, BlindOracleSkillHandler

__version__ = "1.0.0"
__all__ = ["handle_request", "BlindOracleSkillHandler"]
