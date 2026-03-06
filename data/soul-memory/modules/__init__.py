#!/usr/bin/env python3
"""
Soul Memory System v2.1 - Modules Package
Modules:
- priority_parser: Tag parsing and priority detection
- vector_search: Semantic keyword search (local)
- dynamic_classifier: Auto-learning categories
- version_control: Git integration
- memory_decay: Time-based decay and cleanup
- auto_trigger: Pre-response memory retrieval
"""

__version__ = "2.1.0"

# Make modules available
from .priority_parser import PriorityParser, Priority, ParsedMemory
from .vector_search import VectorSearch, SearchResult
from .dynamic_classifier import DynamicClassifier
from .version_control import VersionControl
from .memory_decay import MemoryDecay
from .auto_trigger import AutoTrigger

__all__ = [
    'PriorityParser', 'Priority', 'ParsedMemory',
    'VectorSearch', 'SearchResult',
    'DynamicClassifier',
    'VersionControl',
    'MemoryDecay',
    'AutoTrigger'
]
