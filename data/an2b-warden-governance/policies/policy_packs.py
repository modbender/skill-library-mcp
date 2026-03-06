"""War/Den Policy Packs -- pre-built governance policies ready to load.

Available packs:
- basic_safety:    Block code execution in prod, monitor writes and API calls
- phi_guard:       Deny PHI access in dev, require review for memory export
- payments_guard:  Deny payment actions in dev, require review in prod

Usage:
    Set WARDEN_POLICY_PACKS=basic_safety,phi_guard in your skill config.
"""

# This module re-exports the pack definitions from the policy engine
# for documentation and direct import purposes.

from warden_governance.policy_engine import (
    BASIC_SAFETY_PACK,
    PACKS,
    PAYMENTS_GUARD_PACK,
    PHI_GUARD_PACK,
)

__all__ = [
    "BASIC_SAFETY_PACK",
    "PHI_GUARD_PACK",
    "PAYMENTS_GUARD_PACK",
    "PACKS",
]
