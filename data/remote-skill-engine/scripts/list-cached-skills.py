#!/usr/bin/env python3
"""List all cached remote skills with their status."""
import json
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / ".openclaw" / "workspace" / "remote-skills-cache"

def get_cache_stats(skill_path):
    """Get stats for a cached skill."""
    metadata_file = skill_path / "cache-metadata.json"
    
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        return {
            "name": metadata.get('name', skill_path.name),
            "source": metadata.get('source', 'Unknown'),
            "cached_at": metadata.get('cached_at', 'Unknown'),
            "version": metadata.get('version', 'N/A')
        }
    else:
        return {
            "name": skill_path.name,
            "source": "Unknown",
            "cached_at": "Unknown",
            "version": "N/A"
        }

def main():
    if not CACHE_DIR.exists():
        print("📭 No cached skills found.")
        print(f"Cache directory: {CACHE_DIR}")
        return
    
    cached_skills = list(CACHE_DIR.iterdir())
    cached_skills = [d for d in cached_skills if d.is_dir()]
    
    if not cached_skills:
        print("📭 No cached skills found.")
        return
    
    print("=" * 80)
    print("💾 CACHED REMOTE SKILLS")
    print("=" * 80)
    print("")
    print(f"{'Name':<30} {'Source':<30} {'Cached At':<25} {'Version':<10}")
    print("-" * 80)
    
    for skill_path in sorted(cached_skills):
        stats = get_cache_stats(skill_path)
        name = stats['name'][:28]
        source = stats['source'][:28]
        cached_at = stats['cached_at'][:23] if stats['cached_at'] != 'Unknown' else 'Unknown'
        version = stats['version'][:8]
        
        print(f"{name:<30} {source:<30} {cached_at:<25} {version:<10}")
    
    print("-" * 80)
    print(f"Total: {len(cached_skills)} skill(s) cached")
    print("")
    print(f"Cache location: {CACHE_DIR}")
    print("Tip: Cached skills work like installed skills (symlinked to skills/ folder)")
    print("=" * 80)

if __name__ == "__main__":
    main()
