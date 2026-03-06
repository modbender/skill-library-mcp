# Overkill Token Optimizer - Configuration

import os
import subprocess
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent
WORKSPACE_DIR = Path(os.path.expanduser("~/.openclaw/workspace-memory-builder"))
SESSION_INDEX_DIR = WORKSPACE_DIR / ".session_index"
OKTK_BIN = os.environ.get("OKTK_BIN", "/usr/local/bin/oktk")

# Token optimization settings
DEFAULT_COMPRESSION_LEVEL = "high"  # low, medium, high, extreme
MAX_CONTEXT_TOKENS = 200000
TARGET_CONTEXT_TOKENS = 150000

# Token optimization settings
DEFAULT_COMPRESSION_LEVEL = "high"  # low, medium, high, extreme
MAX_CONTEXT_TOKENS = 200000
TARGET_CONTEXT_TOKENS = 150000

# Indexing settings
INDEX_SESSION_DAYS = 30  # How many days of sessions to index
INDEX_BATCH_SIZE = 100

# Search settings
DEFAULT_SEARCH_LIMIT = 10
HYBRID_SEARCH_WEIGHT = 0.7  # semantic weight (1 - weight = keyword weight)

# Session storage
SESSION_DIR = WORKSPACE_DIR / "memory"
SESSION_PATTERN = "*.md"

# Colors for CLI output
COLORS = {
    "reset": "\033[0m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "bold": "\033[1m",
}
