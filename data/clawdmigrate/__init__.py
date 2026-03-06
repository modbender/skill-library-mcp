"""
clawd_migrate - Migrate from moltbot or clawdbot to openclaw while preserving
configuration, memory, and clawdbook (Moltbook) data. Includes post-migration
verification and automatic openclaw reinstall. Works for any user's system.
"""

__version__ = "0.2.0"

from .backup import create_backup
from .discover import discover_source_assets, discover_clawdbot_assets
from .migrate import run_migration
from .verify import verify_migration

__all__ = [
    "create_backup",
    "discover_source_assets",
    "discover_clawdbot_assets",
    "run_migration",
    "verify_migration",
    "__version__",
]
