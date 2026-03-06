#!/usr/bin/env python3
"""
AI/Tech Pulse module for daily briefing.
Fetches recent AI and tech developments from various sources.
"""

import sys
import json
import urllib.request
import urllib.parse
import re
import html


def fetch_openai_blog():
    """Fetch latest from OpenAI blog/news."""
    try:
        # OpenAI blog RSS
        url = "https://openai.com/blog/rss.xml"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; DailyBriefing/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        # Extract titles
        items = content.split('<item>')[1:3]  # Top 2
        results = []
        for item in items:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', item)
            if title_match:
                title = title_match.group(1)
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                results.append({'title': f"OpenAI: {title}", 'source': 'OpenAI'})
        return results
    except Exception as e:
        return []


def fetch_anthropic_news():
    """Fetch latest from Anthropic."""
    try:
        url = "https://www.anthropic.com/news/rss.xml"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; DailyBriefing/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        items = content.split('<item>')[1:2]  # Top 1
        results = []
        for item in items:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', item)
            if title_match:
                title = title_match.group(1)
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                results.append({'title': f"Anthropic: {title}", 'source': 'Anthropic'})
        return results
    except Exception as e:
        return []


def fetch_techcrunch_ai():
    """Fetch AI-related news from TechCrunch."""
    try:
        url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; DailyBriefing/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        items = content.split('<item>')[1:2]  # Top 1
        results = []
        for item in items:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', item)
            if title_match:
                title = title_match.group(1)
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                results.append({'title': f"Tech: {title}", 'source': 'TechCrunch'})
        return results
    except Exception as e:
        return []


def fetch_hackernews_tech():
    """Fetch top tech stories from Hacker News."""
    try:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(top_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            story_ids = json.loads(response.read().decode('utf-8'))[:5]
        
        # Fetch details for each story
        tech_keywords = ['AI', 'machine learning', 'LLM', 'GPT', 'Claude', 'neural', 
                        'open source', 'launch', 'release', 'github', 'python', 
                        'javascript', 'rust', 'go', 'api', 'startup']
        
        stories = []
        for story_id in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url)
            with urllib.request.urlopen(req, timeout=5) as response:
                story = json.loads(response.read().decode('utf-8'))
                if story and 'title' in story:
                    title = story['title']
                    # Check if tech-related
                    if any(kw.lower() in title.lower() for kw in tech_keywords):
                        stories.append({
                            'title': f"HN: {title}",
                            'source': 'Hacker News'
                        })
                        if len(stories) >= 2:
                            break
        return stories
    except Exception as e:
        return []


def fetch_ai_jobs():
    """Fetch from AI jobs/newsletter sources."""
    # Placeholder for future newsletter/RSS integrations
    # Could include: Import AI, The Batch, TLDR, etc.
    return []


def get_ai_pulse(limit=4):
    """Get AI/Tech pulse headlines."""
    all_items = []
    
    # Fetch from various sources
    all_items.extend(fetch_openai_blog())
    all_items.extend(fetch_anthropic_news())
    all_items.extend(fetch_techcrunch_ai())
    all_items.extend(fetch_hackernews_tech())
    
    # Remove duplicates (simple check)
    seen = set()
    unique_items = []
    for item in all_items:
        title_key = item['title'].lower()[:40]
        if title_key not in seen and len(unique_items) < limit:
            seen.add(title_key)
            unique_items.append(item)
    
    if not unique_items:
        # Fallback message
        return "   • Check Hacker News and TechCrunch for latest AI updates"
    
    output = []
    for item in unique_items[:limit]:
        title = item['title']
        # Truncate if too long
        if len(title) > 90:
            title = title[:87] + '...'
        output.append(f"   • {title}")
    
    return '\n'.join(output)


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    print(get_ai_pulse(limit=limit))
