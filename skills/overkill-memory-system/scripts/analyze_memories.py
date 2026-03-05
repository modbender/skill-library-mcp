#!/usr/bin/env python3
"""
Neuroscience Memory Analyzer
Analyzes existing memories and adds neuroscience tags (importance, emotions, value)
"""
import sys
import json
from pathlib import Path

# Add parent to path
cli_path = Path(__file__).parent.parent
sys.path.insert(0, str(cli_path))

# Import from cli module
import importlib.util
spec = importlib.util.spec_from_file_location("cli", cli_path / "cli.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)

DAILY_DIR = cli.DAILY_DIR
DIARY_DIR = cli.DIARY_DIR
MEMORY_BASE = cli.MEMORY_BASE
analyze_existing_memories = cli.analyze_existing_memories
add_neuroscience_metadata = cli.add_neuroscience_metadata
tag_memory_with_neuroscience = cli.tag_memory_with_neuroscience
get_importance_from_index = cli.get_importance_from_index
detect_emotions = cli.detect_emotions
VALID_EMOTIONS = cli.VALID_EMOTIONS
VALID_REWARDS = cli.VALID_REWARDS


def main():
    """Analyze and tag existing memories."""
    print("🧠 Neuroscience Memory Analyzer")
    print("=" * 50)
    
    # Check what memories exist
    print("\n📂 Scanning memory directories...")
    
    daily_files = list(DAILY_DIR.glob("*.md"))
    diary_files = list(DIARY_DIR.glob("*.md"))
    
    print(f"   Daily files: {len(daily_files)}")
    print(f"   Diary files: {len(diary_files)}")
    
    # Run analysis
    print("\n🔍 Analyzing memories...")
    results = analyze_existing_memories()
    
    print(f"\n✅ Analysis complete!")
    print(f"   Analyzed: {results['analyzed']}")
    print(f"   Tagged: {results['tagged']}")
    print(f"   Errors: {results['errors']}")
    
    # Show breakdown
    for tier, data in results.get("by_tier", {}).items():
        print(f"   {tier}: {data.get('analyzed', 0)} analyzed, {data.get('tagged', 0)} tagged")
    
    print("\n📊 Valid neuroscience values:")
    print(f"   Emotions: {', '.join(VALID_EMOTIONS)}")
    print(f"   Rewards: {', '.join(VALID_REWARDS)}")


if __name__ == "__main__":
    main()
