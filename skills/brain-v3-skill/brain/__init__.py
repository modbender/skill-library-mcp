"""Claw Brain - Brain module

This package re-exports from the main clawbrain module for backward compatibility.
"""

__version__ = "0.1.10"
__author__ = "ClawColab"

# Re-export from the main module (clawbrain.py at package root)
from clawbrain import Brain, Memory, UserProfile, Embedder, get_bridge_script_path

__all__ = ["Brain", "Memory", "UserProfile", "Embedder", "get_bridge_script_path", "__version__"]
