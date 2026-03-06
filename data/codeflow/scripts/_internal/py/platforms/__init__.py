"""Platform adapters for posting messages to chat services."""

import os
import sys

from py_compat import require_python310

require_python310(prog="codeflow")

def get_platform(name=None):
    """Return a platform adapter by name. Defaults to PLATFORM env var or 'discord'."""
    name = (name or os.environ.get("PLATFORM", "discord")).strip().lower()
    if name == "discord":
        from . import discord
        return discord
    if name == "telegram":
        from . import telegram
        return telegram
    if name == "test":
        from . import test
        return test
    # Add slack.py, teams.py etc here
    raise RuntimeError(f"Platform '{name}' not yet supported")
