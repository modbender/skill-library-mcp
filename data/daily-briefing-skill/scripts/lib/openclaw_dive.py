#!/usr/bin/env python3
"""
OpenClaw Deep Dive module for daily briefing.
Generates insights about OpenClaw news, skills, community, and suggestions.
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta


# OpenClaw skills directory
SKILLS_DIR = "/Users/nudge/openclaw/skills"
WORKSPACE_DIR = "/Users/nudge/.openclaw/workspace-codey"


def get_recent_skills(days=7):
    """Get list of recently modified skills."""
    try:
        skills = []
        cutoff = datetime.now() - timedelta(days=days)
        
        skill_dirs = glob.glob(os.path.join(SKILLS_DIR, "*/"))
        for skill_dir in skill_dirs:
            skill_name = os.path.basename(os.path.dirname(skill_dir))
            skill_md = os.path.join(skill_dir, "SKILL.md")
            
            if os.path.exists(skill_md):
                mtime = datetime.fromtimestamp(os.path.getmtime(skill_md))
                if mtime > cutoff:
                    # Try to read description from frontmatter
                    description = ""
                    try:
                        with open(skill_md, 'r') as f:
                            lines = f.readlines()[:20]
                            for line in lines:
                                if line.startswith("description:"):
                                    description = line.split(":", 1)[1].strip().strip('"').strip("'")
                                    break
                    except:
                        pass
                    
                    skills.append({
                        'name': skill_name,
                        'description': description or 'New skill',
                        'date': mtime.strftime('%Y-%m-%d')
                    })
        
        # Sort by date, newest first
        skills.sort(key=lambda x: x['date'], reverse=True)
        return skills[:3]  # Top 3 recent
    except Exception as e:
        return []


def count_skills():
    """Count total skills."""
    try:
        skill_dirs = glob.glob(os.path.join(SKILLS_DIR, "*/"))
        return len([d for d in skill_dirs if os.path.exists(os.path.join(d, "SKILL.md"))])
    except:
        return "many"


def get_skill_suggestions():
    """Generate skill suggestions based on common patterns."""
    suggestions = [
        "Try the 'coding-agent' skill for automated coding tasks",
        "Check out 'model-usage' to track your AI usage",
        "Use 'nano-pdf' for quick PDF operations",
        "Explore 'sag' for high-quality text-to-speech",
        "The 'canvas' skill helps with visual presentations",
        "Try 'peekaboo' for system monitoring",
        "Use 'discord' skill for server management",
    ]
    
    # Return 2 random suggestions
    import random
    return random.sample(suggestions, min(2, len(suggestions)))


def get_openclaw_news():
    """Generate OpenClaw-related news/updates section."""
    sections = []
    
    # New skills
    recent_skills = get_recent_skills(days=14)
    if recent_skills:
        skill_text = f"📦 Skills ({count_skills()} total): Recent additions include "
        skill_names = [f"{s['name']}" for s in recent_skills[:2]]
        skill_text += " and ".join(skill_names)
        sections.append(skill_text)
    else:
        sections.append(f"📦 Skills: You have {count_skills()} skills installed")
    
    # Community highlight (rotating content)
    highlights = [
        "💡 Tip: Use '/reasoning' to toggle deep reasoning mode for complex tasks",
        "💡 Tip: Heartbeats are great for periodic checks; cron for exact timing",
        "💡 Tip: Skills use progressive disclosure - metadata is always loaded, details on demand",
        "💡 Tip: The 'web_search' tool supports freshness filters like 'pd' (past day)",
        "💡 Tip: Canvas snapshots can capture rendered UI for documentation",
    ]
    import random
    sections.append(random.choice(highlights))
    
    return '\n'.join(sections)


def get_deep_dive():
    """Generate the full OpenClaw Deep Dive section."""
    lines = []
    
    # News section
    lines.append(get_openclaw_news())
    
    # Suggestions
    lines.append("")
    lines.append("🎯 Worth exploring:")
    for suggestion in get_skill_suggestions():
        lines.append(f"   • {suggestion}")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    print(get_deep_dive())
