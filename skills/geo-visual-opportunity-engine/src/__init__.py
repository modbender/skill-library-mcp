# GEO Visual Opportunity Engine
# Author: Tim (sales@dageno.ai)
# Version: 3.0.0

"""GEO Visual Opportunity Engine - Main Entry Point"""

from .analyzer import OpportunityAnalyzer
from .nano_banana_2 import NanoBanana2
from .config import AUTHOR_INFO, SKILL_CONFIG

__version__ = "3.0.0"
__author__ = AUTHOR_INFO["name"]
__email__ = AUTHOR_INFO["email"]
__website__ = AUTHOR_INFO["website"]

__all__ = [
    "OpportunityAnalyzer",
    "NanoBanana2",
    "AUTHOR_INFO",
    "SKILL_CONFIG"
]
