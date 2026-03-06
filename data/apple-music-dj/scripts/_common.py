#!/usr/bin/env python3
"""
_common.py — Shared utilities for Apple Music DJ scripts.

Provides call_api(), load_profile(), search helpers, and token utilities
used across all scripts.
"""

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Union

# ── Python version guard ──────────────────────────────────────────
_MIN_PYTHON = (3, 9)
if sys.version_info < _MIN_PYTHON:
    sys.exit(
        f"ERROR: Python {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]}+ is required "
        f"(you have {sys.version_info.major}.{sys.version_info.minor}). "
        f"Please upgrade Python."
    )

# Genres that Apple Music puts on everything — filter these out of scoring
GENERIC_GENRES = {"music"}

SCRIPT_DIR = Path(__file__).parent
API_SCRIPT = SCRIPT_DIR / "apple_music_api.sh"

DEFAULT_CONFIG_PATH = Path.home() / ".apple-music-dj" / "config.json"

DEFAULT_CONFIG = {
    "default_storefront": "auto",
    "preferred_genres": [],
    "excluded_artists": [],
    "playlist_size": 30,
    "cache_ttl_hours": 168,
}


def load_config(path: Optional[str] = None) -> dict:
    """Load user configuration from JSON, falling back to defaults.

    If no path is given, looks at ~/.apple-music-dj/config.json.
    Missing keys are filled with defaults; missing file returns all defaults.
    """
    config = dict(DEFAULT_CONFIG)
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return config
    try:
        with open(config_path) as f:
            user_config = json.load(f)
        if not isinstance(user_config, dict):
            print(f"WARN: Config is not a JSON object: {config_path}", file=sys.stderr)
            return config
        config.update(user_config)
        return config
    except json.JSONDecodeError as e:
        print(f"WARN: Invalid JSON in config: {config_path} (line {e.lineno})", file=sys.stderr)
        return config
    except OSError as e:
        print(f"WARN: Could not read config: {e}", file=sys.stderr)
        return config


def save_config(config: dict, path: Optional[str] = None):
    """Write config to JSON with restrictive permissions."""
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(config_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")


def require_env_tokens():
    """Verify Apple Music tokens are set. Call before any API usage."""
    import os
    missing = []
    if not os.environ.get("APPLE_MUSIC_DEV_TOKEN"):
        missing.append("APPLE_MUSIC_DEV_TOKEN")
    if not os.environ.get("APPLE_MUSIC_USER_TOKEN"):
        missing.append("APPLE_MUSIC_USER_TOKEN")
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        print("  See references/auth-setup.md for configuration steps.", file=sys.stderr)
        sys.exit(1)


def call_api(command: str, *args, raw: bool = False) -> Union[dict, list, str, None]:
    """Call apple_music_api.sh and parse JSON output.

    If raw=True, return stdout as a stripped string instead of parsing JSON.
    """
    cmd = [str(API_SCRIPT), command] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            stderr_msg = result.stderr.strip()
            if stderr_msg:
                print(f"WARN: API call '{command}' failed: {stderr_msg}", file=sys.stderr)
            return None
        if raw:
            return result.stdout.strip()
        return json.loads(result.stdout)
    except FileNotFoundError:
        print(f"ERROR: API script not found: {API_SCRIPT}", file=sys.stderr)
        print("  Ensure apple_music_api.sh is in the scripts/ directory.", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print(f"WARN: API call timed out: {command} {' '.join(args)}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"WARN: Malformed JSON from API call: {command}", file=sys.stderr)
        return None


def load_profile(path: str) -> dict:
    """Load a taste profile JSON with user-friendly error handling."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Profile not found: {path}", file=sys.stderr)
        print("  Run the taste profiler first: python3 scripts/taste_profiler.py", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in profile: {path}", file=sys.stderr)
        print(f"  Parse error at line {e.lineno}, column {e.colno}", file=sys.stderr)
        print("  Try regenerating: python3 scripts/taste_profiler.py --max-age 0", file=sys.stderr)
        sys.exit(1)


def search_artist(sf: str, name: str) -> Optional[dict]:
    """Search for an artist by name and return the top match."""
    result = call_api("search", sf, name, "artists")
    if not result:
        return None
    artists = result.get("results", {}).get("artists", {}).get("data", [])
    return artists[0] if artists else None


def search_album(sf: str, query: str) -> Optional[dict]:
    """Search for an album by name and return the top match."""
    result = call_api("search", sf, query, "albums")
    if not result:
        return None
    albums = result.get("results", {}).get("albums", {}).get("data", [])
    return albums[0] if albums else None


def filter_generic_genres(genres: list[str]) -> list[str]:
    """Remove generic genres like 'Music' that Apple puts on everything."""
    return [g for g in genres if g.lower() not in GENERIC_GENRES]


def check_token_expiry(warn_days: int = 14) -> Optional[dict]:
    """Check the dev token JWT exp claim and return status.

    Returns a dict with keys: expired (bool), days_remaining (int|None),
    warning (bool), message (str). Returns None if token is not set or
    cannot be decoded.
    """
    token = os.environ.get("APPLE_MUSIC_DEV_TOKEN", "")
    if not token:
        return None

    try:
        # JWT is header.payload.signature — decode the payload (middle segment)
        parts = token.split(".")
        if len(parts) != 3:
            return None
        # Add padding for base64
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        exp = payload.get("exp")
        if exp is None:
            return None

        now = time.time()
        remaining_secs = exp - now
        days_remaining = int(remaining_secs / 86400)

        if remaining_secs <= 0:
            return {
                "expired": True,
                "days_remaining": 0,
                "warning": True,
                "message": "⛔ Dev token has EXPIRED. Regenerate with: python3 scripts/generate_dev_token.py",
            }
        elif days_remaining <= warn_days:
            return {
                "expired": False,
                "days_remaining": days_remaining,
                "warning": True,
                "message": f"⚠️  Dev token expires in {days_remaining} day(s). Consider regenerating soon.",
            }
        else:
            return {
                "expired": False,
                "days_remaining": days_remaining,
                "warning": False,
                "message": f"✅ Dev token valid for {days_remaining} more day(s).",
            }
    except Exception:
        return None


STOREFRONT_CACHE = Path.home() / ".apple-music-dj" / "storefront.cache"


def get_storefront(override: Optional[str] = None) -> str:
    """Get storefront code with auto-detection and caching.

    Priority: explicit override > env var > cache > API detection > 'us' fallback.
    """
    if override and override != "auto":
        return override

    # Check env var
    env_sf = os.environ.get("APPLE_MUSIC_STOREFRONT", "")
    if env_sf:
        return env_sf

    # Check cache
    try:
        if STOREFRONT_CACHE.exists():
            cached = STOREFRONT_CACHE.read_text().strip()
            if len(cached) == 2 and cached.isalpha():
                return cached
    except OSError:
        pass

    # Auto-detect from API
    result = call_api("user-storefront", raw=True)
    if isinstance(result, str) and len(result) == 2 and result.isalpha():
        # Cache the result
        try:
            STOREFRONT_CACHE.parent.mkdir(parents=True, exist_ok=True)
            STOREFRONT_CACHE.write_text(result + "\n")
        except OSError:
            pass
        return result

    print(
        "⚠ Could not detect storefront, defaulting to 'us'. "
        "Set APPLE_MUSIC_STOREFRONT or use --storefront to override.",
        file=sys.stderr,
    )
    return "us"


def get_album_tracks(sf: str, album_id: str) -> list:
    """Fetch tracks for an album, returning a flat list of track dicts."""
    detail = call_api("album-tracks", sf, album_id)
    if not detail or "data" not in detail:
        return []
    tracks = []
    for album_data in detail.get("data", []):
        track_rel = album_data.get("relationships", {}).get("tracks", {}).get("data", [])
        tracks.extend(track_rel)
    return tracks
