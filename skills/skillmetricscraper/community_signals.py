"""
community_signals.py — Weekly X/Twitter community intel for the report

Loads curated signal data from a JSON file (data/weekly_signals.json).
Each week, you drop in the week's X threads, blog posts, and notable
discussions before running the pipeline. The report renders them as a
"Community Buzz" section.

File format (data/weekly_signals.json):
[
  {
    "date": "2026-02-28",
    "category": "tutorial",
    "title": "How to create a simple custom OpenClaw Skill",
    "url": "https://x.com/i/status/...",
    "summary": "Video walkthrough of building a custom skill from scratch.",
    "tags": ["custom-skills", "beginner"],
    "source": "x"
  },
  ...
]

Categories: tutorial, security, ecosystem, showcase, discussion, market
Sources: x, blog, docs, youtube, reddit, hackernews
"""

import json
from datetime import date, timedelta
from pathlib import Path

SIGNALS_PATH = Path(__file__).parent / "data" / "weekly_signals.json"

CATEGORY_EMOJI = {
    "tutorial": "📚",
    "security": "🔒",
    "ecosystem": "🌐",
    "showcase": "🎨",
    "discussion": "💬",
    "market": "📈",
}

SOURCE_ICON = {
    "x": "𝕏",
    "reddit": "🔴",
    "hackernews": "🟠",
    "blog": "📝",
    "docs": "📄",
    "youtube": "▶️",
}

CATEGORY_LABEL = {
    "tutorial": "Tutorial",
    "security": "Security",
    "ecosystem": "Ecosystem",
    "showcase": "Showcase",
    "discussion": "Discussion",
    "market": "Market Signal",
}


def load_signals() -> list[dict]:
    """Load weekly community signals from JSON file."""
    if not SIGNALS_PATH.exists():
        return []
    try:
        data = json.loads(SIGNALS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def render_community_section(signals: list[dict], ttl_days: int = 7) -> str:
    """Render the Community Buzz markdown section. Filters to last ttl_days only."""
    if not signals:
        return ""

    # Filter by TTL — only show signals from the last N days
    cutoff = (date.today() - timedelta(days=ttl_days)).isoformat()
    signals = [s for s in signals if s.get("date", "9999") >= cutoff]

    if not signals:
        return ""

    # Count signals by source for subtitle
    sources = {s.get("source", "x") for s in signals}
    source_labels = []
    if "x" in sources:
        source_labels.append("X")
    if "reddit" in sources:
        source_labels.append("Reddit")
    if "hackernews" in sources:
        source_labels.append("Hacker News")
    if "blog" in sources:
        source_labels.append("blogs")
    subtitle = ", ".join(source_labels) or "community discussions"

    lines = [
        "## Community Buzz This Week",
        "",
        f"*Curated from {subtitle}.*",
        "",
    ]

    # Group by category
    by_cat: dict[str, list[dict]] = {}
    for s in signals:
        cat = s.get("category", "discussion")
        by_cat.setdefault(cat, []).append(s)

    for cat in ["showcase", "tutorial", "security", "ecosystem", "discussion", "market"]:
        items = by_cat.get(cat, [])
        if not items:
            continue

        emoji = CATEGORY_EMOJI.get(cat, "")
        label = CATEGORY_LABEL.get(cat, cat.title())
        lines.append(f"### {emoji} {label}")
        lines.append("")

        for item in items:
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            summary = item.get("summary", "")
            item_date = item.get("date", "")
            tags = item.get("tags", [])
            source = item.get("source", "")

            link = f"[{title}]({url})" if url else title
            tag_str = " ".join(f"`#{t}`" for t in tags) if tags else ""
            date_str = f" ({item_date})" if item_date else ""
            source_icon = SOURCE_ICON.get(source, "")
            source_prefix = f"{source_icon} " if source_icon else ""

            lines.append(f"- {source_prefix}**{link}**{date_str}")
            if summary:
                lines.append(f"  {summary}")
            if tag_str:
                lines.append(f"  {tag_str}")
            lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)
