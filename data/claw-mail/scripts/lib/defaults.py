"""Default paths and configuration helpers.

Provides the default config file path so that ``--config`` can be
optional across all scripts.  When ``--config`` is not supplied the
scripts look for ``config.yaml`` in the skill root directory
(one level above ``scripts/``).
"""

from __future__ import annotations

import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))   # .../scripts/lib/
SCRIPTS_DIR = os.path.dirname(_THIS_DIR)                  # .../scripts/
SKILL_ROOT = os.path.dirname(SCRIPTS_DIR)                  # .../claw-mail/
DEFAULT_CONFIG_PATH = os.path.join(SKILL_ROOT, "config.yaml")


def resolve_config_path(explicit_path: str = "") -> str:
    """Return *explicit_path* if given, else the default config if it exists.

    Returns an empty string when neither is available so callers can
    still require ``--config`` or ``--imap-host`` as before.
    """
    if explicit_path:
        return explicit_path
    if os.path.isfile(DEFAULT_CONFIG_PATH):
        return DEFAULT_CONFIG_PATH
    return ""
