"""Platform adapters for posting messages to chat services."""

import os

def get_platform(name=None):
    """Return a platform adapter by name. Defaults to PLATFORM env var or 'discord'."""
    name = name or os.environ.get("PLATFORM", "discord")
    if name == "discord":
        from . import discord
        return discord
    # Add slack.py, teams.py etc here
    raise RuntimeError(f"Platform '{name}' not yet supported")
