#!/usr/bin/env python3
"""
Jarvis Diary Module
Personal diary with full-text search, entry management, and statistics.
Integrates with the overkill-memory-system for parallel querying.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Path configuration
DIARY_DIR = Path.home() / ".openclaw" / "memory" / "diary"
DIARY_DIR.mkdir(parents=True, exist_ok=True)

# Strategy notes path
STRATEGY_NOTES_FILE = Path.home() / ".openclaw" / "memory" / "strategy-notes.md"

# Valid emotions for metadata
VALID_EMOTIONS = ["joy", "sadness", "anger", "fear", "surprise", "disgust", 
                  "anticipation", "trust", "accomplishment", "frustration",
                  "excitement", "anxiety", "gratitude", "love", "loneliness",
                  "confidence", "confusion", "hope", "nostalgia", "serenity"]


def _get_today_filename() -> Path:
    """Get today's diary file path."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return DIARY_DIR / f"{date_str}.neuro.json"


def _get_all_diary_files() -> list:
    """Get all diary files sorted by date (newest first)."""
    files = sorted(DIARY_DIR.glob("*.neuro.json"), reverse=True)
    return files


def search_diary(query: str, max_results: int = 10) -> dict:
    """
    Search all diary entries for matching content.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary with search results and metadata
    """
    results = []
    query_lower = query.lower()
    
    for diary_file in _get_all_diary_files():
        try:
            with open(diary_file, 'r') as f:
                data = json.load(f)
            
            date_str = diary_file.stem.replace(".neuro", "")  # e.g., "2026-02-25"
            
            for memory in data.get("memories", []):
                content = memory.get("content_preview", "")
                full_content = memory.get("content", "")
                
                # Search in both preview and full content
                if query_lower in content.lower() or query_lower in full_content.lower():
                    results.append({
                        "date": date_str,
                        "timestamp": memory.get("timestamp", ""),
                        "importance": memory.get("importance", 0.5),
                        "emotions": memory.get("emotions", []),
                        "content_preview": content[:200] if content else full_content[:200],
                        "full_content": full_content,
                        "source": "diary"
                    })
                    
                    if len(results) >= max_results:
                        break
        except (json.JSONDecodeError, IOError) as e:
            continue
        
        if len(results) >= max_results:
            break
    
    return {
        "query": query,
        "total_matches": len(results),
        "results": results
    }


def get_today_entry() -> dict:
    """
    Get today's diary entry.
    
    Returns:
        Dictionary with today's entry content and metadata
    """
    today_file = _get_today_filename()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    if today_file.exists():
        try:
            with open(today_file, 'r') as f:
                data = json.load(f)
            
            return {
                "date": date_str,
                "exists": True,
                "memories": data.get("memories", []),
                "entry_count": len(data.get("memories", [])),
                "lastUpdated": data.get("lastUpdated", "")
            }
        except (json.JSONDecodeError, IOError) as e:
            return {
                "date": date_str,
                "exists": False,
                "error": str(e)
            }
    
    return {
        "date": date_str,
        "exists": False,
        "entry_count": 0,
        "memories": []
    }


def add_entry(content: str, importance: float = 0.5, emotions: list = None) -> dict:
    """
    Add a new entry to today's diary.
    
    Args:
        content: The diary content text
        importance: Importance score 0.0-1.0
        emotions: List of emotions associated with this entry
    
    Returns:
        Dictionary with entry creation status
    """
    today_file = _get_today_filename()
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().isoformat()
    
    # Load existing data or create new structure
    if today_file.exists():
        try:
            with open(today_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {"memories": [], "lastUpdated": ""}
    else:
        data = {"memories": [], "lastUpdated": ""}
    
    # Create new memory entry
    memory_entry = {
        "content_preview": f"# Diary - {date_str}\n\n## {timestamp} *importance: {importance:.2f}* *emotions: {', '.join(emotions or [])}*\n\n{content[:100]}...",
        "timestamp": timestamp,
        "importance": importance,
        "emotions": emotions or [],
        "value": {
            "type": "social",
            "score": 0.4,
            "intensity": 0.5,
            "auto_detected": True
        },
        "source": "jarvis_diary"
    }
    
    # Add full content
    memory_entry["content"] = content
    
    # Append to memories
    data["memories"].append(memory_entry)
    data["lastUpdated"] = timestamp
    
    # Save back
    with open(today_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return {
        "success": True,
        "date": date_str,
        "timestamp": timestamp,
        "entry_count": len(data["memories"])
    }


def get_diary_stats() -> dict:
    """
    Get diary statistics including entry counts and date range.
    
    Returns:
        Dictionary with diary statistics
    """
    files = _get_all_diary_files()
    
    total_entries = 0
    date_range = {"earliest": None, "latest": None}
    emotion_counts = {}
    importance_sum = 0.0
    importance_count = 0
    
    for diary_file in files:
        date_str = diary_file.stem.replace(".neuro", "")
        
        if date_range["earliest"] is None:
            date_range["earliest"] = date_str
        date_range["latest"] = date_str
        
        try:
            with open(diary_file, 'r') as f:
                data = json.load(f)
            
            memories = data.get("memories", [])
            total_entries += len(memories)
            
            for memory in memories:
                # Track importance
                importance = memory.get("importance", 0.5)
                importance_sum += importance
                importance_count += 1
                
                # Track emotions
                emotions = memory.get("emotions", [])
                for emotion in emotions:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    
        except (json.JSONDecodeError, IOError):
            continue
    
    # Calculate averages
    avg_importance = importance_sum / importance_count if importance_count > 0 else 0.5
    
    # Get top emotions
    top_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_entries": total_entries,
        "total_days": len(files),
        "date_range": date_range,
        "average_importance": round(avg_importance, 2),
        "emotion_distribution": dict(top_emotions),
        "entries_per_day": round(total_entries / len(files), 1) if len(files) > 0 else 0
    }


def format_entry_for_display(entry: dict, show_full: bool = False) -> str:
    """
    Format a diary entry for CLI display.
    
    Args:
        entry: Entry dictionary from get_today_entry or search
        show_full: Whether to show full content
    
    Returns:
        Formatted string for display
    """
    lines = []
    
    if "date" in entry:
        lines.append(f"📔 **Diary - {entry['date']}**")
    
    if entry.get("exists") == False:
        return "No diary entry for today yet."
    
    if "memories" in entry:
        for i, memory in enumerate(entry["memories"], 1):
            lines.append(f"\n### Entry {i}")
            
            if memory.get("timestamp"):
                ts = memory["timestamp"]
                lines.append(f"🕐 {ts}")
            
            if memory.get("importance"):
                lines.append(f"⭐ Importance: {memory['importance']:.2f}")
            
            if memory.get("emotions"):
                emotions_str = ", ".join(memory["emotions"])
                lines.append(f"💭 Emotions: {emotions_str}")
            
            content = memory.get("full_content") or memory.get("content_preview", "")
            if show_full:
                lines.append(f"\n{content}")
            else:
                lines.append(f"\n{content[:200]}...")
    
    return "\n".join(lines)


# ============================================================================
# STRATEGY NOTES FUNCTIONS
# ============================================================================

def search_strategy(query: str, max_results: int = 10) -> dict:
    """
    Search strategy notes for matching content.
    
    Args:
        string
        max query: Search query_results: Maximum number of results to return
    
    Returns:
        Dictionary with search results and metadata
    """
    if not STRATEGY_NOTES_FILE.exists():
        return {
            "query": query,
            "total_matches": 0,
            "results": []
        }
    
    try:
        content = STRATEGY_NOTES_FILE.read_text()
    except IOError:
        return {
            "query": query,
            "total_matches": 0,
            "results": [],
            "error": "Could not read strategy notes file"
        }
    
    query_lower = query.lower()
    results = []
    
    # Split content into sections (## headings)
    lines = content.split("\n")
    current_section = ""
    current_content = []
    
    for line in lines:
        if line.startswith("## "):
            # Save previous section if it matches
            if current_section and query_lower in current_section.lower():
                section_text = "\n".join(current_content)
                results.append({
                    "section": current_section,
                    "content": section_text,
                    "preview": section_text[:200] if section_text else ""
                })
            current_section = line[3:].strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    # Check last section
    if current_section and query_lower in current_section.lower():
        section_text = "\n".join(current_content)
        results.append({
            "section": current_section,
            "content": section_text,
            "preview": section_text[:200] if section_text else ""
        })
    
    # Also check if query matches any content
    if not results:
        for line_num, line in enumerate(lines, 1):
            if query_lower in line.lower():
                # Find the section this line belongs to
                section_name = "Overview"
                for i in range(line_num - 2, -1, -1):
                    if lines[i].startswith("## "):
                        section_name = lines[i][3:].strip()
                        break
                
                results.append({
                    "section": section_name,
                    "content": content,
                    "preview": lines[line_num - 1][:200]
                })
                break
    
    return {
        "query": query,
        "total_matches": len(results),
        "results": results[:max_results]
    }


def get_strategy() -> dict:
    """
    Get all strategy notes.
    
    Returns:
        Dictionary with strategy notes content
    """
    if not STRATEGY_NOTES_FILE.exists():
        return {
            "exists": False,
            "content": "",
            "sections": []
        }
    
    try:
        content = STRATEGY_NOTES_FILE.read_text()
    except IOError:
        return {
            "exists": False,
            "content": "",
            "error": "Could not read strategy notes file"
        }
    
    # Parse sections
    sections = []
    lines = content.split("\n")
    current_section = None
    
    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections.append(current_section)
            current_section = {"title": line[3:].strip(), "content": []}
        elif current_section is not None:
            current_section["content"].append(line)
    
    if current_section:
        sections.append(current_section)
    
    return {
        "exists": True,
        "content": content,
        "sections": sections,
        "file_path": str(STRATEGY_NOTES_FILE)
    }


def add_strategy(content: str, section: str = None) -> dict:
    """
    Add a new entry to strategy notes.
    
    Args:
        content: The strategy note content to add
        section: Optional section title (creates if doesn't exist)
    
    Returns:
        Dictionary with addition status
    """
    timestamp = datetime.now().isoformat()
    
    # Read existing content or create new
    if STRATEGY_NOTES_FILE.exists():
        try:
            existing_content = STRATEGY_NOTES_FILE.read_text()
        except IOError:
            existing_content = "# Strategy Notes\n"
    else:
        existing_content = "# Strategy Notes\n"
    
    # Determine where to add the new content
    if section:
        # Check if section exists
        section_header = f"## {section}"
        if section_header in existing_content:
            # Append to existing section
            new_entry = f"\n- {content} _{timestamp}_\n"
            lines = existing_content.split("\n")
            in_section = False
            result_lines = []
            
            for line in lines:
                result_lines.append(line)
                if line.strip() == section_header:
                    in_section = True
                elif in_section and line.startswith("## "):
                    # Insert before next section
                    result_lines.insert(-1, new_entry)
                    in_section = False
            
            if in_section:
                result_lines.append(new_entry)
            
            final_content = "\n".join(result_lines)
        else:
            # Create new section
            final_content = existing_content.rstrip() + f"\n\n{section_header}\n\n- {content} _{timestamp}_\n"
    else:
        # Add to end of file (or create Overview section)
        if "# Strategy Notes" in existing_content:
            final_content = existing_content.rstrip() + f"\n\n- {content} _{timestamp}_\n"
        else:
            final_content = f"# Strategy Notes\n\n## Overview\n\n- {content} _{timestamp}_\n"
    
    # Write back
    try:
        STRATEGY_NOTES_FILE.write_text(final_content)
        return {
            "success": True,
            "timestamp": timestamp,
            "section": section or "Overview"
        }
    except IOError as e:
        return {
            "success": False,
            "error": str(e)
        }


# CLI functions for direct command-line usage
def cli_search(query: str):
    """CLI interface for searching diary."""
    results = search_diary(query)
    
    if results["total_matches"] == 0:
        print(f"No diary entries found matching: {query}")
        return
    
    print(f"📔 Found {results['total_matches']} matching entries:\n")
    for i, entry in enumerate(results["results"], 1):
        print(f"{i}. [{entry['date']}] {entry['timestamp']}")
        print(f"   {entry['content_preview'][:150]}...")
        if entry.get("emotions"):
            print(f"   💭 {', '.join(entry['emotions'])}")
        print()


def cli_today():
    """CLI interface for getting today's entry."""
    entry = get_today_entry()
    print(format_entry_for_display(entry, show_full=True))


def cli_add(content: str, importance: float = 0.5, emotions: list = None):
    """CLI interface for adding a diary entry."""
    result = add_entry(content, importance, emotions)
    
    if result["success"]:
        print(f"✅ Added diary entry for {result['date']}")
        print(f"   Timestamp: {result['timestamp']}")
        print(f"   Total entries today: {result['entry_count']}")
    else:
        print(f"❌ Failed to add entry: {result.get('error', 'Unknown error')}")


def cli_stats():
    """CLI interface for showing diary statistics."""
    stats = get_diary_stats()
    
    print("📔 **Diary Statistics**\n")
    print(f"📅 Total Days: {stats['total_days']}")
    print(f"📝 Total Entries: {stats['total_entries']}")
    print(f"📊 Avg Entries/Day: {stats['entries_per_day']}")
    print(f"⭐ Avg Importance: {stats['average_importance']}")
    print(f"📆 Date Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    
    if stats["emotion_distribution"]:
        print(f"\n💭 Top Emotions:")
        for emotion, count in stats["emotion_distribution"].items():
            print(f"   {emotion}: {count}")


def cli_strategy_search(query: str):
    """CLI interface for searching strategy notes."""
    results = search_strategy(query)
    
    if results["total_matches"] == 0:
        print(f"No strategy notes found matching: {query}")
        return
    
    print(f"📋 Found {results['total_matches']} matching sections:\n")
    for i, entry in enumerate(results["results"], 1):
        print(f"{i}. [{entry['section']}]")
        print(f"   {entry['preview'][:150]}...")
        print()


def cli_strategy_list():
    """CLI interface for listing all strategy notes."""
    strategy = get_strategy()
    
    if not strategy["exists"]:
        print("No strategy notes file found.")
        return
    
    print("📋 **Strategy Notes**\n")
    print(strategy["content"])


def cli_strategy_add(content: str, section: str = None):
    """CLI interface for adding a strategy note."""
    result = add_strategy(content, section)
    
    if result["success"]:
        print(f"✅ Added strategy note")
        if result.get("section"):
            print(f"   Section: {result['section']}")
        print(f"   Timestamp: {result['timestamp']}")
    else:
        print(f"❌ Failed to add strategy note: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Jarvis Diary CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search diary entries")
    search_parser.add_argument("query", help="Search query")
    
    # today
    subparsers.add_parser("today", help="Show today's diary entry")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add diary entry")
    add_parser.add_argument("--content", required=True, help="Entry content")
    add_parser.add_argument("--importance", type=float, default=0.5, help="Importance 0-1")
    add_parser.add_argument("--emotions", type=str, help="Comma-separated emotions")
    
    # stats
    subparsers.add_parser("stats", help="Show diary statistics")
    
    # strategy
    strategy_parser = subparsers.add_parser("strategy", help="Strategy notes commands")
    strategy_subparsers = strategy_parser.add_subparsers(dest="strategy_command", help="Strategy subcommands")
    
    # strategy search
    strategy_search_parser = strategy_subparsers.add_parser("search", help="Search strategy notes")
    strategy_search_parser.add_argument("query", help="Search query")
    
    # strategy list
    strategy_subparsers.add_parser("list", help="List all strategy notes")
    
    # strategy add
    strategy_add_parser = strategy_subparsers.add_parser("add", help="Add strategy note")
    strategy_add_parser.add_argument("--content", required=True, help="Note content")
    strategy_add_parser.add_argument("--section", type=str, help="Section name")
    
    args = parser.parse_args()
    
    if args.command == "search":
        cli_search(args.query)
    elif args.command == "today":
        cli_today()
    elif args.command == "add":
        emotions = args.emotions.split(",") if args.emotions else None
        cli_add(args.content, args.importance, emotions)
    elif args.command == "stats":
        cli_stats()
    elif args.command == "strategy":
        if args.strategy_command == "search":
            cli_strategy_search(args.query)
        elif args.strategy_command == "list":
            cli_strategy_list()
        elif args.strategy_command == "add":
            cli_strategy_add(args.content, args.section)
        else:
            strategy_parser.print_help()
    else:
        parser.print_help()
