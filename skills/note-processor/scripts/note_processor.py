#!/usr/bin/env python3
"""
Note Processor - Summarize and analyze research notes
Usage: python3 note_processor.py summarize <topic>
       python3 note_processor.py keywords <topic>
       python3 note_processor.py extract <topic> <keyword>
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

DB_PATH = Path.home() / ".openclaw" / "workspace" / "research_db.json"

def load_db():
    """Load research database"""
    if not DB_PATH.exists():
        return {}
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_topic_notes(topic):
    """Get all notes for a topic"""
    db = load_db()
    if topic not in db:
        return None
    return db[topic]

def summarize_topic(topic):
    """Generate summary of a research topic"""
    notes = get_topic_notes(topic)
    
    if not notes:
        print(f"Topic '{topic}' not found.")
        return
    
    # Collect all content
    all_content = " ".join([note["content"] for note in notes["notes"]])
    
    # Basic statistics
    word_count = len(all_content.split())
    note_count = len(notes["notes"])
    tags = []
    for note in notes["notes"]:
        tags.extend(note.get("tags", []))
    
    print(f"\n📊 Summary: {topic}")
    print("-" * 60)
    print(f"Notes: {note_count}")
    print(f"Words: {word_count}")
    print(f"Created: {notes['created'][:10]}")
    print(f"Last update: {notes['last_updated'][:10]}")
    print()
    
    # Tags summary
    if tags:
        tag_counts = Counter(tags)
        print("🏷️  Top Tags:")
        for tag, count in tag_counts.most_common(5):
            print(f"   {tag}: {count}")
        print()
    
    # Key points (sentences with important words)
    important_words = ['important', 'key', 'critical', 'essential', 'must', 'should', 
                     'note', 'remember', 'warning', 'critical', 'priority']
    key_points = []
    
    for note in notes["notes"]:
        sentences = re.split(r'[.!?]+', note["content"])
        for sentence in sentences:
            if any(word in sentence.lower() for word in important_words):
                key_points.append(sentence.strip())
    
    if key_points:
        print("💡 Key Points:")
        for i, point in enumerate(key_points[:5], 1):
            print(f"   {i}. {point[:100]}...")
        print()
    
    # Recent notes
    print("📝 Recent Notes:")
    for note in notes["notes"][-3:]:
        ts = note["timestamp"][:19].replace("T", " ")
        preview = note["content"][:80] + "..." if len(note["content"]) > 80 else note["content"]
        print(f"   [{ts}] {preview}")
    print()

def extract_keywords(topic):
    """Extract keywords from topic notes"""
    notes = get_topic_notes(topic)
    
    if not notes:
        print(f"Topic '{topic}' not found.")
        return
    
    # Collect all content
    all_content = " ".join([note["content"] for note in notes["notes"]])
    
    # Extract words (simple keyword extraction)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', all_content.lower())
    
    # Common stop words to filter
    stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'will', 'what',
                 'when', 'where', 'which', 'their', 'there', 'would', 'could',
                 'should', 'about', 'these', 'those', 'other', 'into', 'through'}
    
    keywords = [w for w in words if w not in stop_words]
    keyword_counts = Counter(keywords)
    
    print(f"\n🔤 Keywords: {topic}")
    print("-" * 60)
    print(f"Total unique keywords: {len(keyword_counts)}")
    print()
    
    print("Top 20 Keywords:")
    for i, (keyword, count) in enumerate(keyword_counts.most_common(20), 1):
        print(f"{i:3d}. {keyword:20s} ({count:2d}x)")
    print()

def search_topic(topic, keyword):
    """Search within a topic for keyword"""
    notes = get_topic_notes(topic)
    
    if not notes:
        print(f"Topic '{topic}' not found.")
        return
    
    matches = []
    for note in notes["notes"]:
        if keyword.lower() in note["content"].lower():
            matches.append(note)
    
    if not matches:
        print(f"No matches for '{keyword}' in topic '{topic}'")
        return
    
    print(f"\n🔍 Search Results: '{keyword}' in {topic}")
    print("-" * 60)
    print(f"Found {len(matches)} match(es)\n")
    
    for i, note in enumerate(matches, 1):
        ts = note["timestamp"][:19].replace("T", " ")
        # Highlight the keyword (case-insensitive using re)
        content = re.sub(
            re.escape(keyword),
            f"**{keyword.upper()}**",
            note["content"],
            flags=re.IGNORECASE
        )
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"{i}. [{ts}]")
        print(f"   Tags: {', '.join(note.get('tags', []))}")
        print(f"   {preview}\n")

def list_topics():
    """List all research topics with summaries"""
    db = load_db()
    
    if not db:
        print("No research topics yet.")
        return
    
    print(f"\n📚 Research Topics ({len(db)})")
    print("-" * 60)
    
    for topic, data in sorted(db.items(), key=lambda x: x[1]["last_updated"], reverse=True):
        note_count = len(data["notes"])
        word_count = sum(len(n["content"].split()) for n in data["notes"])
        last_update = data["last_updated"][:10]
        
        print(f"\n{topic}")
        print(f"   Notes: {note_count} | Words: {word_count} | Updated: {last_update}")
        
        # Show recent note preview
        if data["notes"]:
            preview = data["notes"][-1]["content"][:60] + "..."
            print(f"   Latest: {preview}")

def main():
    if len(sys.argv) < 2:
        print("Note Processor - Summarize and analyze research notes")
        print("\nCommands:")
        print("  summarize <topic>           - Generate summary of topic")
        print("  keywords <topic>            - Extract top keywords")
        print("  extract <topic> <keyword>    - Search within topic")
        print("  list                         - List all topics")
        print("\nExamples:")
        print("  note_processor.py summarize income-experiments")
        print("  note_processor.py keywords security-incident")
        print("  note_processor.py extract security-incident vulnerability")
        return
    
    command = sys.argv[1]
    
    if command == "summarize":
        if len(sys.argv) < 3:
            print("Usage: summarize <topic>")
            return
        summarize_topic(sys.argv[2])
    
    elif command == "keywords":
        if len(sys.argv) < 3:
            print("Usage: keywords <topic>")
            return
        extract_keywords(sys.argv[2])
    
    elif command == "extract":
        if len(sys.argv) < 4:
            print("Usage: extract <topic> <keyword>")
            return
        search_topic(sys.argv[2], sys.argv[3])
    
    elif command == "list":
        list_topics()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
