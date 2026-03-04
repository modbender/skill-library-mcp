"""Cache management for ClawHub skill data."""
from __future__ import annotations

import time

from .utils import DATA_DIR, load_json, save_json

CACHE_FILE = DATA_DIR / "clawhub-cache.json"
CACHE_MAX_AGE = 86400  # 24 hours in seconds
CACHE_VERSION = "2.0.0"


def is_cache_fresh(cache_data: dict) -> bool:
    """Check if cache is less than 24 hours old."""
    if not cache_data or "timestamp" not in cache_data:
        return False
    cache_age = time.time() - cache_data["timestamp"]
    return cache_age < CACHE_MAX_AGE


def load_cache() -> dict:
    """Load local cache file."""
    try:
        if CACHE_FILE.exists():
            data = load_json(CACHE_FILE)
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def enrich_cache_with_complementary(cache_data: dict) -> dict:
    """Enrich cache skills with complementary metadata.

    Args:
        cache_data: Raw cache data

    Returns:
        Enriched cache with complementary fields
    """
    comp_file = DATA_DIR / "complementary-skills.json"
    if not comp_file.exists():
        return cache_data

    comp_data = load_json(comp_file)
    if not comp_data:
        return cache_data

    # Build skill complementary mapping
    skill_map = {}

    for relationship in comp_data.get("relationships", []):
        for comp in relationship.get("complements", []):
            skill_slug = comp["skill_slug"]
            if skill_slug not in skill_map:
                skill_map[skill_slug] = {
                    "categories": [],
                    "priority": comp.get("priority", "MEDIUM"),
                    "integration_type": comp.get("integration_type", ""),
                    "complements": [],
                    "complemented_by": []
                }

            # Add category if not already present
            category = comp.get("category", "")
            if category and category not in skill_map[skill_slug]["categories"]:
                skill_map[skill_slug]["categories"].append(category)

            # Add bidirectional relationship
            base_skill = relationship.get("skill_slug", "")
            if base_skill:
                skill_map[skill_slug]["complements"].append(base_skill)

                # Add reverse relationship
                if base_skill not in skill_map:
                    skill_map[base_skill] = {
                        "categories": [],
                        "priority": "MEDIUM",
                        "integration_type": "",
                        "complements": [],
                        "complemented_by": []
                    }
                if skill_slug not in skill_map[base_skill]["complemented_by"]:
                    skill_map[base_skill]["complemented_by"].append(skill_slug)

    # Enrich skills in cache
    enriched_count = 0
    for skill in cache_data.get("skills", []):
        if skill["slug"] in skill_map:
            skill["complementary"] = skill_map[skill["slug"]]
            enriched_count += 1

    # Add metadata
    cache_data["version"] = CACHE_VERSION
    cache_data["metadata"] = {
        "total_skills": len(cache_data.get("skills", [])),
        "complementary_enriched": enriched_count,
        "last_enrichment": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    return cache_data


def save_cache(data: dict) -> dict:
    """Save cache file with enrichment and timestamp. Returns updated data."""
    enriched = enrich_cache_with_complementary(data)
    enriched["timestamp"] = time.time()
    save_json(CACHE_FILE, enriched)
    return enriched


def search_cache(cache_data: dict, query: str, limit: int) -> list[dict]:
    """Search cached skills by keyword matching.

    Args:
        cache_data: Loaded cache dict
        query: Search query
        limit: Maximum results

    Returns:
        Matching skill data dicts from cache
    """
    if "skills" not in cache_data:
        return []

    query_lower = query.lower()
    matches = []

    for skill_data in cache_data["skills"]:
        name = skill_data.get("name", "").lower()
        desc = skill_data.get("description", "").lower()
        tags = [t.lower() for t in skill_data.get("tags", [])]

        if (query_lower in name or
            query_lower in desc or
            any(query_lower in tag for tag in tags)):
            matches.append(skill_data)

    return matches[:limit]
