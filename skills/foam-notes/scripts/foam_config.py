#!/usr/bin/env python3
"""
Configuration loader for Foam notes skill.

Usage:
    from foam_config import load_config, get_foam_root

    config = load_config()
    foam_root = get_foam_root(cli_path=None, config=config)
"""

import json
import os
import re
import unicodedata
from pathlib import Path


def slugify(text: str) -> str:
    """
    Convert title to file-safe slug.

    Rules:
    - Unicode characters transliterated to ASCII (e.g., café → cafe)
    - Lowercase only
    - Spaces replaced with dashes
    - Special characters removed (', &, etc.)
    - Multiple dashes/spaces collapsed to single dash
    """
    # First, transliterate Unicode to ASCII using NFKD normalization
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    text = text.lower().strip()
    text = re.sub(
        r"[^\w\s-]", "", text
    )  # Remove special chars except word chars, whitespace, and dashes
    text = re.sub(
        r"[-\s]+", "-", text
    )  # Replace spaces and multiple dashes with single dash
    text = text.strip("-")  # Remove leading/trailing dashes
    return text


def get_skill_dir() -> Path:
    """Get the skill directory path."""
    # This script is in scripts/, skill root is parent
    return Path(__file__).parent.parent


def load_config() -> dict:
    """Load config.json from skill directory."""
    skill_dir = get_skill_dir()
    config_path = skill_dir / "config.json"

    default_config = {
        "foam_root": "",
        "default_template": "",
        "default_notes_folder": "",
        "daily_note_folder": "journals",
        "author": "",
        "editor": "code",
        "wikilinks": {
            "title_stopwords": [],
            "suffixes": [],
            "min_length": 3,
        },
        "tags": {
            "editorial_stopwords": [],
        },
    }

    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
            # Deep merge: nested dicts are merged, not replaced
            merged = {**default_config}
            for k, v in user_config.items():
                if isinstance(v, dict) and isinstance(merged.get(k), dict):
                    merged[k] = {**merged[k], **v}
                else:
                    merged[k] = v
            return merged
        except (json.JSONDecodeError, IOError) as e:
            print(
                f"Warning: Could not load config.json: {e}",
                file=__import__("sys").stderr,
            )
            return default_config

    return default_config


def save_config(config: dict) -> None:
    """Save config to config.json."""
    skill_dir = get_skill_dir()
    config_path = skill_dir / "config.json"

    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Error: Could not save config.json: {e}", file=__import__("sys").stderr)


def find_foam_root_auto(start_dir: Path = None) -> Path:
    """Auto-detect Foam workspace by looking for .foam or .vscode."""
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()
    while current != current.parent:
        if (current / ".foam").exists() or (current / ".vscode").exists():
            return current
        current = current.parent

    return None


def get_foam_root(cli_path: str = None, config: dict = None) -> Path:
    """
    Get Foam workspace root using priority order:
    1. CLI argument
    2. FOAM_WORKSPACE env var
    3. config.json foam_root
    4. Auto-detect
    5. Current directory (fallback)
    """
    # 1. CLI argument
    if cli_path:
        path = Path(cli_path).expanduser().resolve()
        if path.exists():
            return path
        else:
            print(
                f"Warning: Specified foam_root does not exist: {path}",
                file=__import__("sys").stderr,
            )

    # 2. Environment variable
    env_path = os.environ.get("FOAM_WORKSPACE")
    if env_path:
        path = Path(env_path).expanduser().resolve()
        if path.exists():
            return path

    # 3. Config file
    if config is None:
        config = load_config()

    if config.get("foam_root"):
        path = Path(config["foam_root"]).expanduser().resolve()
        if path.exists():
            return path

    # 4. Auto-detect
    auto = find_foam_root_auto()
    if auto:
        return auto

    # 5. Current directory
    return Path.cwd()


def get_daily_note_folder(config: dict = None) -> str:
    """Get daily notes folder name."""
    if config is None:
        config = load_config()

    return config.get("daily_note_folder", "journals")


def get_default_notes_folder(config: dict = None) -> str:
    """Get default notes folder for new notes (empty = root)."""
    if config is None:
        config = load_config()

    return config.get("default_notes_folder", "")


def get_default_template(config: dict = None) -> str:
    """Get default template name."""
    if config is None:
        config = load_config()

    return config.get("default_template", "")


def get_author(config: dict = None) -> str:
    """Get author name for note creation."""
    if config is None:
        config = load_config()

    return config.get("author", "")


def get_wikilink_config(config: dict = None) -> dict:
    """Get wikilink-related configuration.

    Returns dict with keys:
        title_stopwords: list[str] — note titles to never match as wikilinks
        suffixes: list[str] — filename suffixes whose base stem should also
            be registered as a match key (e.g. ["-hub"] means icedrive-hub.md
            also matches "icedrive" in prose)
        min_length: int — minimum key length to consider
    """
    if config is None:
        config = load_config()

    wl = config.get("wikilinks", {})
    return {
        "title_stopwords": wl.get("title_stopwords", []),
        "suffixes": wl.get("suffixes", []),
        "min_length": wl.get("min_length", 3),
    }


def get_tags_config(config: dict = None) -> dict:
    """Get tag-related configuration.

    Returns dict with keys:
        editorial_stopwords: list[str] — domain-specific words to exclude
            from tag suggestions (in addition to NLP stopwords)
    """
    if config is None:
        config = load_config()

    tc = config.get("tags", {})
    return {
        "editorial_stopwords": tc.get("editorial_stopwords", []),
    }


# ============================================================================
# Error Handling and YAML Validation Helpers
# ============================================================================


def validate_yaml(content: str) -> tuple[bool, str]:
    """
    Validate YAML syntax without loading it.

    Args:
        content: YAML content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        import yaml

        yaml.safe_load(content)
        return True, ""
    except yaml.YAMLError as e:
        return False, str(e)
    except ImportError:
        # yaml not installed, skip validation
        return True, ""


def safe_extract_frontmatter(content: str) -> tuple[dict, str]:
    """
    Safely extract YAML frontmatter from markdown content.

    Args:
        content: Markdown content

    Returns:
        Tuple of (frontmatter_dict, error_message)
        If error occurs, returns ({}, error_message)
    """
    if not content.startswith("---"):
        return {}, "No frontmatter found"

    try:
        # Find the end of frontmatter
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return {}, "Invalid frontmatter: no closing '---'"

        fm_content = content[3:end_idx].strip()

        # Validate YAML syntax first
        is_valid, error = validate_yaml(fm_content)
        if not is_valid:
            return {}, f"Invalid YAML syntax: {error}"

        # Parse the YAML
        import yaml

        data = yaml.safe_load(fm_content)

        if data is None:
            return {}, ""

        if not isinstance(data, dict):
            return {}, f"Frontmatter must be a dictionary, got {type(data).__name__}"

        return data, ""

    except Exception as e:
        return {}, f"Error extracting frontmatter: {e}"


def log_error(msg: str, verbose: bool = False) -> None:
    """
    Log an error message to stderr.

    Args:
        msg: Error message
        verbose: If True, include stack trace info
    """
    import sys

    print(f"Error: {msg}", file=sys.stderr)

    if verbose:
        import traceback

        traceback.print_exc()


def safe_read_file(filepath: Path, verbose: bool = False) -> tuple[str, str]:
    """
    Safely read a file with error handling.

    Args:
        filepath: Path to file
        verbose: If True, print detailed error info

    Returns:
        Tuple of (content, error_message)
        If error occurs, returns ("", error_message)
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        return content, ""
    except FileNotFoundError:
        error = f"File not found: {filepath}"
        if verbose:
            log_error(error, verbose)
        return "", error
    except PermissionError:
        error = f"Permission denied: {filepath}"
        if verbose:
            log_error(error, verbose)
        return "", error
    except Exception as e:
        error = f"Error reading {filepath}: {e}"
        if verbose:
            log_error(error, verbose)
        return "", error


def safe_write_file(
    filepath: Path, content: str, verbose: bool = False
) -> tuple[bool, str]:
    """
    Safely write a file with error handling.

    Args:
        filepath: Path to file
        content: Content to write
        verbose: If True, print detailed error info

    Returns:
        Tuple of (success, error_message)
    """
    try:
        filepath.write_text(content, encoding="utf-8")
        return True, ""
    except PermissionError:
        error = f"Permission denied: {filepath}"
        if verbose:
            log_error(error, verbose)
        return False, error
    except Exception as e:
        error = f"Error writing {filepath}: {e}"
        if verbose:
            log_error(error, verbose)
        return False, error


if __name__ == "__main__":
    # Test config loading
    config = load_config()
    print(f"Config loaded from: {get_skill_dir() / 'config.json'}")
    print(f"foam_root: {config.get('foam_root') or '(auto-detect)'}")
    print(f"daily_note_folder: {config.get('daily_note_folder')}")
    print(f"default_notes_folder: {config.get('default_notes_folder') or '(root)'}")

    foam_root = get_foam_root(config=config)
    print(f"Resolved foam_root: {foam_root}")
