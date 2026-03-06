"""Shared utilities for figma-sync scripts."""

import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

import requests

logger = logging.getLogger("figma-sync")

FIGMA_API = "https://api.figma.com"
CACHE_DIR = Path(".figma-cache")
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0


def get_token() -> str:
    token = os.environ.get("FIGMA_TOKEN", "")
    if not token:
        logger.error("FIGMA_TOKEN environment variable not set")
        sys.exit(1)
    return token


def headers() -> dict:
    return {"X-Figma-Token": get_token(), "Content-Type": "application/json"}


def cache_path(file_key: str) -> Path:
    p = CACHE_DIR / file_key
    p.mkdir(parents=True, exist_ok=True)
    return p


def api_get(path: str, file_key: str = "", use_cache: bool = True, params: dict = None) -> dict:
    """GET from Figma API with retry, backoff, and ETag caching."""
    url = f"{FIGMA_API}{path}"
    hdrs = headers()

    etag_file = None
    cache_file = None
    if use_cache and file_key:
        cp = cache_path(file_key)
        safe = path.replace("/", "_").strip("_")
        cache_file = cp / f"{safe}.json"
        etag_file = cp / f"{safe}.etag"
        if etag_file.exists():
            hdrs["If-None-Match"] = etag_file.read_text().strip()

    backoff = INITIAL_BACKOFF
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=hdrs, params=params, timeout=30)
            if resp.status_code == 304 and cache_file and cache_file.exists():
                logger.debug("Cache hit (304) for %s", path)
                return json.loads(cache_file.read_text())
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", backoff))
                logger.warning("Rate limited, retrying in %.1fs", retry_after)
                time.sleep(retry_after)
                backoff = min(backoff * 2, 60)
                continue
            resp.raise_for_status()
            data = resp.json()

            if cache_file:
                cache_file.write_text(json.dumps(data, sort_keys=True))
            if etag_file and "ETag" in resp.headers:
                etag_file.write_text(resp.headers["ETag"])

            return data
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                logger.error("API request failed after %d retries: %s", MAX_RETRIES, e)
                raise
            logger.warning("Request failed (attempt %d): %s, retrying in %.1fs", attempt + 1, e, backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
    return {}


def stable_id(name: str, figma_id: str) -> str:
    """Generate a stable deterministic ID from name + figma node ID."""
    raw = f"{name}::{figma_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def to_camel_case(name: str) -> str:
    """Convert a Figma layer name to CamelCase component name."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s_-]", "", name)
    parts = re.split(r"[\s_-]+", cleaned)
    result = "".join(p.capitalize() for p in parts if p)
    if not result:
        return "Component"
    if result[0].isdigit():
        result = "Screen" + result
    return result


def to_kebab_case(name: str) -> str:
    """Convert name to kebab-case filename."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s_-]", "", name)
    parts = re.split(r"[\s_-]+", cleaned)
    return "-".join(p.lower() for p in parts if p)


def rgba_to_hex(color: dict) -> str:
    """Convert Figma RGBA (0-1 floats) to hex string."""
    r = int(color.get("r", 0) * 255)
    g = int(color.get("g", 0) * 255)
    b = int(color.get("b", 0) * 255)
    a = color.get("a", 1.0)
    if a < 1.0:
        return f"rgba({r}, {g}, {b}, {a:.2f})"
    return f"#{r:02x}{g:02x}{b:02x}"


def rgba_to_rn(color: dict) -> str:
    """Convert Figma RGBA to React Native color string."""
    return rgba_to_hex(color)


def write_json(path: Path, data: dict):
    """Write JSON with sorted keys for deterministic output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n")
    logger.info("Wrote %s", path)


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
