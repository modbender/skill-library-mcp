"""
CounterClaw - Defensive Security for AI Agents
"""

__version__ = "1.0.0"

from counterclaw.scanner import Scanner
from counterclaw.middleware import (
    CounterClawInterceptor, 
    _log_violation,
    _mask_pii,
    PII_MASK_PATTERNS
)

__all__ = [
    "Scanner", 
    "CounterClawInterceptor", 
    "_log_violation",
    "_mask_pii",
    "PII_MASK_PATTERNS",
    "__version__"
]
