#!/usr/bin/env python3
"""Skill Comparator — compare installed skills against ClawHub catalog.

Usage: python3 skill_comparator.py [workspace_path]

For each installed skill, checks if a better alternative exists on ClawHub
(higher stars, more downloads). Uses description-based category matching
instead of naive keyword overlap.
"""

import os, sys, json, time, re
from pathlib import Path
from urllib.request import Request, urlopen

ws = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".openclaw" / "workspace"
API = "https://clawhub.ai/api/v1"

# Category definitions for semantic matching
# Keywords are checked as substrings against slug+summary
# Higher-weight keywords (tuples with weight) get priority
CATEGORIES = {
    "stock-analysis": {
        "keywords": {"stock", "equity", "portfolio tracker", "trading", "valuation", "ticker", "shares", "invest", "yfinance", "yahoo finance"},
        "exclude": {"crypto", "blockchain", "nft", "defi", "polymarket", "academic", "research paper", "literature"}
    },
    "ai-news": {
        "keywords": {"ai news", "ai 新闻", "llm news", "ai briefing", "ai daily", "大模型日报", "ai 动态"},
        "exclude": set()
    },
    "academic": {
        "keywords": {"academic", "research paper", "paper writer", "literature review", "citation", "scholarly", "论文", "ieee", "arxiv"},
        "exclude": {"stock", "market"}
    },
    "productivity": {
        "keywords": {"productivity", "focus", "todo", "task management", "time management", "pomodoro", "deep work", "energy management"},
        "exclude": {"stock", "ai news", "agent"}
    },
    "weather": {
        "keywords": {"weather", "forecast", "temperature", "天气"},
        "exclude": set()
    },
    "web-search": {
        "keywords": {"web search", "search engine", "brave search", "tavily", "multi search"},
        "exclude": {"ai news"}
    },
    "browser": {
        "keywords": {"browser automat", "headless browser", "puppeteer", "playwright", "selenium"},
        "exclude": set()
    },
    "social": {
        "keywords": {"social network", "moltbook", "twitter", "reddit", "community post"},
        "exclude": set()
    },
    "tts-stt": {
        "keywords": {"speech-to-text", "text-to-speech", "voice", "whisper", "tts", "transcri", "speech recogni"},
        "exclude": set()
    },
    "git-github": {
        "keywords": {"github", "git repo", "pull request", "gh cli", "git commit"},
        "exclude": set()
    },
    "image-video": {
        "keywords": {"image generat", "video generat", "photo edit", "image edit", "visual", "ffmpeg", "imagemagick"},
        "exclude": {"summarize"}
    },
    "calendar": {
        "keywords": {"calendar", "caldav", "ical", "google calendar"},
        "exclude": {"market", "stock", "news"}
    },
    "note-taking": {
        "keywords": {"obsidian", "notion", "knowledge base", "vault", "wiki", "note-taking"},
        "exclude": set()
    },
    "agent-meta": {
        "keywords": {"self-improving agent", "proactive agent", "agent architecture", "skill manager", "heartbeat", "agent memory"},
        "exclude": {"stock", "news", "weather", "calendar"}
    },
    "summarize": {
        "keywords": {"summarize", "summary", "tldr", "digest"},
        "exclude": {"stock", "news"}
    },
    "market-news": {
        "keywords": {"market news", "stock news", "financial news", "earnings report", "市场新闻", "stock digest"},
        "exclude": {"self-improving", "proactive", "agent memory", "correction", "error"}
    },
    "speed-network": {
        "keywords": {"speedtest", "bandwidth", "latency", "network speed", "internet speed"},
        "exclude": set()
    },
}

def fetch_skill_stats(slug):
    """Fetch skill stats from ClawHub API."""
    try:
        req = Request(f"{API}/skills/{slug}")
        with urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
            sk = data.get("skill", {})
            stats = sk.get("stats", {})
            return {
                "slug": slug,
                "name": sk.get("displayName", slug),
                "summary": sk.get("summary", ""),
                "stars": stats.get("stars", 0),
                "downloads": stats.get("downloads", 0),
                "installs": stats.get("installsCurrent", 0),
                "comments": stats.get("comments", 0),
            }
    except:
        return None

def fetch_catalog(sort="stars", limit=50):
    """Fetch skill catalog from ClawHub."""
    try:
        req = Request(f"{API}/skills?sort={sort}&limit={limit}")
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return [item["slug"] for item in data.get("items", [])]
    except:
        return []

def categorize_skill(slug, summary):
    """Assign a skill to categories based on its slug and summary.
    
    Slug matches get 3x weight (more reliable than summary text).
    Excludes are checked against full text to prevent miscategorization.
    """
    slug_lower = slug.lower()
    summary_lower = summary.lower()
    full_text = f"{slug_lower} {summary_lower}"
    
    matched = []
    for cat, spec in CATEGORIES.items():
        # Check excludes against full text
        if any(ex in full_text for ex in spec["exclude"]):
            continue
        
        # Score: slug matches worth 3x, summary matches worth 1x
        score = 0
        for kw in spec["keywords"]:
            if kw in slug_lower:
                score += 3
            elif kw in summary_lower:
                score += 1
        
        if score >= 1:
            matched.append((cat, score))
    
    matched.sort(key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in matched[:2]]  # Top 2 categories

def get_installed_skills():
    """Get list of installed skills with descriptions."""
    skills_dir = ws / "skills"
    if not skills_dir.exists():
        return {}
    
    installed = {}
    for d in skills_dir.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists():
            content = (d / "SKILL.md").read_text()
            desc_match = re.search(r'description:\s*["\']?(.+?)["\']?\s*\n', content)
            desc = desc_match.group(1) if desc_match else ""
            installed[d.name] = {"description": desc}
    return installed

def main():
    print("\n📦 Skill Comparator — Checking installed skills against ClawHub")
    print("=" * 60)
    
    installed = get_installed_skills()
    if not installed:
        print("No skills installed.")
        return
    
    print(f"Found {len(installed)} installed skills. Fetching stats...\n")
    
    # Fetch stats for installed skills
    installed_stats = {}
    for slug in installed:
        stats = fetch_skill_stats(slug)
        if stats:
            installed_stats[slug] = stats
            installed_stats[slug]["categories"] = categorize_skill(slug, stats.get("summary", ""))
        time.sleep(0.3)
    
    # Fetch top catalog
    print("Fetching ClawHub catalog...")
    top_slugs = fetch_catalog("stars", 50)
    catalog_stats = {}
    for slug in top_slugs:
        if slug not in installed_stats:
            stats = fetch_skill_stats(slug)
            if stats:
                stats["categories"] = categorize_skill(slug, stats.get("summary", ""))
                catalog_stats[slug] = stats
            time.sleep(0.3)
    
    # Report installed skills
    print(f"\n📊 Installed Skills ({len(installed_stats)} with ClawHub data):")
    print("-" * 60)
    
    sorted_installed = sorted(installed_stats.values(), key=lambda x: x["stars"], reverse=True)
    for s in sorted_installed:
        cats = ", ".join(s.get("categories", [])) or "uncategorized"
        print(f"  ⭐{s['stars']:>4} 📥{s['downloads']:>6} | {s['slug']} [{cats}]")
    
    # Find missing top skills
    print(f"\n🏆 Top ClawHub Skills NOT Installed:")
    print("-" * 60)
    missing_top = [(slug, catalog_stats[slug]) for slug in top_slugs 
                   if slug in catalog_stats and slug not in installed]
    
    for slug, stats in missing_top[:15]:
        cats = ", ".join(stats.get("categories", [])) or "general"
        print(f"  ⭐{stats['stars']:>4} 📥{stats['downloads']:>6} | {slug} [{cats}] — {stats['summary'][:50]}")
    
    # Find potential upgrades (same category, higher stars)
    print(f"\n🔄 Potential Upgrades (same category, higher rated):")
    print("-" * 60)
    
    upgrades_found = False
    seen_suggestions = set()
    
    for slug, info in installed_stats.items():
        my_cats = set(info.get("categories", []))
        if not my_cats:
            continue
        
        my_stars = info["stars"]
        
        # Find catalog skills in same category with more stars
        candidates = []
        for cat_slug, cat_info in catalog_stats.items():
            cat_cats = set(cat_info.get("categories", []))
            shared_cats = my_cats & cat_cats
            
            if shared_cats and cat_info["stars"] > my_stars * 1.5 and cat_info["stars"] >= 10:
                key = f"{slug}->{cat_slug}"
                if key not in seen_suggestions:
                    seen_suggestions.add(key)
                    candidates.append(cat_info)
        
        candidates.sort(key=lambda x: x["stars"], reverse=True)
        
        if candidates:
            upgrades_found = True
            cats_str = ", ".join(my_cats)
            print(f"\n  {slug} (⭐{my_stars}) [{cats_str}] — consider:")
            for c in candidates[:2]:
                c_cats = ", ".join(c.get("categories", []))
                print(f"    → {c['slug']} (⭐{c['stars']} 📥{c['downloads']}) [{c_cats}]")
                print(f"      {c['summary'][:80]}")

    if not upgrades_found:
        print("  ✅ No obvious upgrades found — your skills are well-chosen!")

    # Category coverage analysis
    print(f"\n📋 Category Coverage:")
    print("-" * 60)
    
    covered_cats = set()
    for info in installed_stats.values():
        covered_cats.update(info.get("categories", []))
    
    uncovered = set(CATEGORIES.keys()) - covered_cats
    if uncovered:
        print(f"  Covered: {', '.join(sorted(covered_cats))}")
        print(f"  Not covered: {', '.join(sorted(uncovered))}")
    else:
        print(f"  ✅ All categories covered!")

    # Save report
    report = {
        "installed": sorted_installed,
        "missing_top": [{"slug": s, **st} for s, st in missing_top[:15]],
        "covered_categories": sorted(covered_cats),
        "uncovered_categories": sorted(uncovered) if uncovered else [],
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }
    report_path = ws / "memory" / "skill-comparator.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n📊 Report saved: {report_path}")

if __name__ == "__main__":
    main()
