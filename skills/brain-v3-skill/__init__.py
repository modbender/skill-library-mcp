"""
Claw Brain v3 - Personal AI Memory System for AI Agents

A sophisticated memory and learning system that enables truly personalized AI-human communication.

Features:
- 🎭 Soul/Personality - Evolving personality traits
- 👤 User Profile - Learns preferences, interests, communication style
- 💭 Conversation State - Real-time mood/intent detection
- 📚 Learning Insights - Continuous improvement from interactions
- � Encrypted Secrets - Securely store API keys and credentials
- 🔄 Auto-Refresh - Automatic memory refresh on OpenClaw restart

Install: pip install clawbrain[all]
Setup:   clawbrain setup

OpenClaw/ClawdBot Integration:
    pip install clawbrain[all]
    clawbrain setup
    sudo systemctl restart clawdbot  # or openclaw
"""

__version__ = "3.1.0"
__author__ = "ClawColab"

# Core exports
from clawbrain import (
    Brain,
    Memory,
    UserProfile,
    Embedder
)

__all__ = ["Brain", "Memory", "UserProfile", "Embedder"]
