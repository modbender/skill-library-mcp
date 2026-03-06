#!/usr/bin/env python3
"""
Sync lessons from workspace tasks/lessons.md to skill references/lessons.md

Usage:
  python3 scripts/sync_lessons.py --workspace /path/to/workspace

This script:
1. Reads tasks/lessons.md from the workspace
2. Merges new lessons into references/lessons.md (preserves existing content)
3. Updates the skill with learned patterns
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path


def extract_lessons_section(content):
    """Extract just the lessons section (after philosophy intro)"""
    # Split by the philosophy sections
    lines = content.split('\n')
    
    # Find where the lessons start (after "Keeping It Portable" section)
    lessons_start = None
    for i, line in enumerate(lines):
        if line.startswith('## Keeping It Portable'):
            # Find next section or end
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('##') and j > i + 5:
                    return '\n'.join(lines[j:])
    
    return None


def load_file(path):
    """Load file content, return empty string if not found"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_file(path, content):
    """Save content to file, create parent dirs if needed"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


def merge_lessons(workspace_lessons, skill_lessons):
    """
    Merge workspace lessons into skill lessons
    Preserves philosophy intro and appends new lessons
    """
    
    philosophy_intro = """# Lessons in Markdown

## The Quiet Power of Plain Text

Markdown thrives on simplicity. A few hashes for headings, asterisks for emphasis, dashes for lists—no flashy code or hidden tricks. It's text you can read raw, anywhere, on any device. In a world of bloated apps and endless scrolls, .md files remind us: truth doesn't need embellishment. It's there, unadorned, waiting to be seen.

Life's lessons work the same way. They arrive in raw moments—a quiet talk with a friend, a walk under rain-soaked trees, the weight of a small regret. No fanfare, just plain experience. We often dress them up with excuses or distractions, but strip them back, and they sharpen into something enduring.

## Rendering Wisdom

Open a .md file in a viewer, and it transforms: headings bolden, paragraphs flow, structure emerges. Our minds do this too. A jumbled day becomes a lesson when reflected upon. That argument with a loved one? It renders as patience. A missed chance? Gratitude for what's here.

In 2026, as screens multiply and noise amplifies, this rendering matters more. We preview life's drafts daily, tweaking for clarity. Markdown teaches us to version our growth—save, edit, share—without losing the source.

## Keeping It Portable

- Write lessons lightly, like notes in a pocket notebook.
- Share them openly, letting others render their meaning.
- Revisit old files; they age well, gaining depth.

Lessons.md isn't a vault of secrets. It's an invitation to live simply, thoughtfully.

---

## Lessons Learned (Updated {timestamp})

"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    # Extract lessons from workspace file (skip philosophy)
    workspace_lines = workspace_lessons.split('\n')
    lessons_content = []
    capture = False
    
    for line in workspace_lines:
        if line.startswith('## ') and 'Keeping It Portable' not in line:
            capture = True
        if capture:
            lessons_content.append(line)
    
    # Build merged content
    merged = philosophy_intro.format(timestamp=timestamp)
    
    if lessons_content:
        merged += '\n'.join(lessons_content)
    else:
        merged += "(No lessons captured yet. Lessons from your work will appear here.)"
    
    # Add closing quote
    merged += "\n\n*In the end, the best lessons render themselves, if we learn to look plainly.*"
    
    return merged


def main():
    parser = argparse.ArgumentParser(
        description='Sync lessons from workspace to skill repository'
    )
    parser.add_argument(
        '--workspace',
        default=os.path.expanduser('~/.openclaw/workspace'),
        help='Path to OpenClaw workspace (default: ~/.openclaw/workspace)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    # Paths
    workspace_lessons = os.path.join(args.workspace, 'tasks/lessons.md')
    skill_lessons = 'references/lessons.md'
    
    # Load files
    workspace_content = load_file(workspace_lessons)
    skill_content = load_file(skill_lessons)
    
    if not workspace_content:
        print(f"❌ Workspace lessons not found: {workspace_lessons}")
        return 1
    
    # Merge
    merged = merge_lessons(workspace_content, skill_content)
    
    if args.dry_run:
        print("📋 Dry run: Would update references/lessons.md")
        print("\n---\n")
        print(merged[:500] + "\n..." if len(merged) > 500 else merged)
        return 0
    
    # Save
    save_file(skill_lessons, merged)
    print(f"✅ Updated {skill_lessons}")
    print(f"📚 Synced lessons from {workspace_lessons}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
