"""
Load FASTFOLD_API_KEY (and other vars) from a .env file so scripts work without
exporting the key in the shell. Searches current directory and parent directories
for .env; only sets variables that are not already in os.environ.

Usage: Call load_dotenv() at the start of main() before reading os.environ.
"""

import os


def load_dotenv() -> None:
    """Load .env from current directory or any parent directory. Does not override existing env vars."""
    search_dirs = []
    d = os.getcwd()
    while d and d != os.path.dirname(d):
        search_dirs.append(d)
        d = os.path.dirname(d)
    for dirpath in search_dirs:
        env_path = os.path.join(dirpath, ".env")
        if os.path.isfile(env_path):
            _parse_and_set(env_path)
            return


def _parse_and_set(env_path: str) -> None:
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key.startswith("export "):
                key = key[7:].strip()
            if not key:
                continue
            # Remove surrounding quotes
            if len(value) >= 2 and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            # Only set if not already in environment (env wins)
            if key not in os.environ and value:
                os.environ[key] = value
