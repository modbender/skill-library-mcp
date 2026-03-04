"""
Migration configuration: paths and patterns for source bots (moltbot / clawdbot)
vs openclaw target layout. Works for any user's system; no machine-specific paths.
"""

# --- Source layouts (moltbot and clawdbot) ---
# Memory/identity files that may exist in either system
SOURCE_MEMORY_FILES = [
    "SOUL.md",      # Who the bot is
    "USER.md",      # Who the human is
    "TOOLS.md",     # Local notes, device names, env-specific
    "IDENTITY.md",  # Bot identity (if present)
    "AGENTS.md",    # Agent instructions (if present)
    "MEMORY.md",    # Long-term memory (if present)
]

# Config paths: union of moltbot and clawdbot locations (credentials, API keys)
SOURCE_CONFIG_PATHS = [
    # Clawdbot
    ".config/moltbook/credentials.json",
    ".config/moltbook/",
    # Moltbot
    ".config/moltbot/credentials.json",
    ".config/moltbot/",
    ".config/moltbook/",  # Moltbot may also use moltbook for Clawdbook
]

# Deduplicate while preserving order
SOURCE_CONFIG_PATHS = list(dict.fromkeys(SOURCE_CONFIG_PATHS))

# Extra paths: project docs and scripts (both systems)
SOURCE_EXTRA_DIRS = [
    "projects/",
]

# --- Openclaw (target) layout ---
OPENCLAW_MEMORY_DIR = "memory"
OPENCLAW_CONFIG_DIR = ".config/openclaw"
OPENCLAW_CLAWDBOOK_DIR = ".config/clawdbook"

# Backup (generic; no product name in prefix)
DEFAULT_BACKUP_DIR = "backups"
BACKUP_PREFIX = "openclaw_migrate_backup_"

# Backward compatibility: same names used by discover
CLAWDBOT_MEMORY_FILES = SOURCE_MEMORY_FILES
CLAWDBOT_CONFIG_PATHS = SOURCE_CONFIG_PATHS
CLAWDBOT_EXTRA_PATTERNS = SOURCE_EXTRA_DIRS
