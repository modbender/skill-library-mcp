#!/usr/bin/env python3
"""
GTM Tracking System for Expanso/Prometheus
A lightweight founder-focused GTM tool.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse
import os
import re
from typing import Optional
import html
import ssl
import time
import subprocess

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "gtm.db"
CACHE_PATH = DATA_DIR / "crawl_cache.json"

# Ensure data dir exists
DATA_DIR.mkdir(exist_ok=True)

# Database schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    company TEXT,
    role TEXT,
    linkedin TEXT,
    github TEXT,
    twitter TEXT,
    notes TEXT,
    source TEXT,
    hubspot_id TEXT,
    last_engagement DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    company TEXT NOT NULL,
    stage TEXT DEFAULT 'awareness',
    value_estimate TEXT,
    description TEXT,
    next_action TEXT,
    due_date DATE,
    priority INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    opportunity_id INTEGER,
    type TEXT DEFAULT 'note',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    opportunity_id INTEGER,
    due_date DATE NOT NULL,
    message TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_id TEXT,
    title TEXT NOT NULL,
    url TEXT,
    content TEXT,
    relevance_score REAL DEFAULT 0.5,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, source_id)
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE,
    category TEXT DEFAULT 'general',
    weight REAL DEFAULT 1.0
);

-- Default keywords for Expanso/Bacalhau (weighted by LinkedIn CTR data)
INSERT OR IGNORE INTO keywords (keyword, category, weight) VALUES
    -- Compliance/sovereignty/on-prem keywords → weight 3.0 (7.23% CTR)
    ('compliance', 'compliance', 3.0),
    ('data sovereignty', 'compliance', 3.0),
    ('on-prem', 'compliance', 3.0),
    ('on-premises', 'compliance', 3.0),
    ('pipelines crumble', 'compliance', 3.0),
    ('regulatory', 'compliance', 3.0),
    ('governance', 'compliance', 3.0),
    
    -- Pipeline maintenance/ingestion/debugging keywords → weight 2.5 (5.64% CTR)
    ('debugging ingestion', 'pipeline', 2.5),
    ('pipeline maintenance', 'pipeline', 2.5),
    ('data pipeline', 'pipeline', 2.5),
    ('ingestion', 'pipeline', 2.5),
    ('debugging', 'pipeline', 2.5),
    ('data orchestration', 'pipeline', 2.5),
    
    -- Cloud cost/billing/egress keywords → weight 2.5 (4.84-4.86% CTR)
    ('aws billing', 'cost', 2.5),
    ('cloud cost', 'cost', 2.5),
    ('egress', 'cost', 2.5),
    ('data transfer', 'cost', 2.5),
    ('cloud bill', 'cost', 2.5),
    ('billing optimization', 'cost', 2.5),
    ('seven-figure budgets', 'cost', 2.5),
    ('cost optimization', 'cost', 2.5),
    
    -- Tool sprawl/unified platform keywords → weight 2.0 (4.60% CTR)
    ('tool sprawl', 'platform', 2.0),
    ('duct-taped together', 'platform', 2.0),
    ('unified platform', 'platform', 2.0),
    ('15 tools', 'platform', 2.0),
    ('modern data stack', 'platform', 2.0),
    
    -- AI readiness/agent keywords → weight 2.0 (4.16% CTR)
    ('ai-ready', 'ai', 2.0),
    ('ai readiness', 'ai', 2.0),
    ('ai agents', 'ai', 2.0),
    ('mlops', 'ai', 2.0),
    
    -- Existing Expanso-specific keywords
    ('bacalhau', 'product', 2.0),
    ('distributed computing', 'domain', 1.5),
    ('compute over data', 'domain', 1.5),
    ('edge computing', 'domain', 1.2),
    ('wasm', 'tech', 1.0),
    ('webassembly', 'tech', 1.0),
    ('ipfs', 'tech', 1.2),
    ('filecoin', 'tech', 1.2),
    ('kubernetes', 'tech', 0.8),
    ('data mesh', 'domain', 1.3),
    ('data lakehouse', 'domain', 1.0),
    ('dbt', 'tech', 0.9),
    ('airflow', 'tech', 0.9),
    ('dagster', 'tech', 0.9),
    ('prefect', 'tech', 0.9),
    ('data engineering', 'domain', 1.0);
"""

# Pipeline stages
STAGES = ['awareness', 'interest', 'evaluation', 'negotiation', 'closed_won', 'closed_lost']


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database."""
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")


def add_contact(name: str, email: str = None, company: str = None, 
                role: str = None, source: str = None, notes: str = None):
    """Add a new contact."""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO contacts (name, email, company, role, source, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, email, company, role, source, notes)
    )
    conn.commit()
    contact_id = cur.lastrowid
    conn.close()
    print(f"✅ Added contact #{contact_id}: {name}")
    return contact_id


def add_opportunity(company: str, contact_id: int = None, description: str = None,
                    next_action: str = None, priority: int = 5):
    """Create a new opportunity."""
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO opportunities (company, contact_id, description, next_action, priority)
           VALUES (?, ?, ?, ?, ?)""",
        (company, contact_id, description, next_action, priority)
    )
    conn.commit()
    opp_id = cur.lastrowid
    conn.close()
    print(f"✅ Created opportunity #{opp_id}: {company}")
    return opp_id


def log_interaction(contact_id: int = None, opp_id: int = None, 
                    content: str = "", interaction_type: str = "note"):
    """Log an interaction with a contact or opportunity."""
    conn = get_db()
    conn.execute(
        """INSERT INTO interactions (contact_id, opportunity_id, type, content)
           VALUES (?, ?, ?, ?)""",
        (contact_id, opp_id, interaction_type, content)
    )
    if contact_id:
        conn.execute("UPDATE contacts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (contact_id,))
    if opp_id:
        conn.execute("UPDATE opportunities SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (opp_id,))
    conn.commit()
    conn.close()
    print(f"✅ Logged interaction")


def move_stage(opp_id: int, new_stage: str):
    """Move an opportunity to a new stage."""
    if new_stage not in STAGES:
        print(f"❌ Invalid stage. Choose from: {', '.join(STAGES)}")
        return
    
    conn = get_db()
    closed_at = datetime.now().isoformat() if new_stage.startswith('closed') else None
    conn.execute(
        """UPDATE opportunities SET stage = ?, updated_at = CURRENT_TIMESTAMP, closed_at = ?
           WHERE id = ?""",
        (new_stage, closed_at, opp_id)
    )
    conn.commit()
    conn.close()
    print(f"✅ Moved opportunity #{opp_id} to {new_stage}")


def set_reminder(contact_id: int = None, opp_id: int = None, 
                 due_date: str = None, message: str = ""):
    """Set a follow-up reminder."""
    if not due_date:
        due_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    conn = get_db()
    conn.execute(
        """INSERT INTO reminders (contact_id, opportunity_id, due_date, message)
           VALUES (?, ?, ?, ?)""",
        (contact_id, opp_id, due_date, message)
    )
    conn.commit()
    conn.close()
    print(f"✅ Reminder set for {due_date}")


def get_pipeline():
    """Get pipeline summary."""
    conn = get_db()
    
    print("\n📊 PIPELINE SUMMARY")
    print("=" * 60)
    
    for stage in STAGES:
        if stage.startswith('closed'):
            continue
        opps = conn.execute(
            """SELECT o.*, c.name as contact_name 
               FROM opportunities o 
               LEFT JOIN contacts c ON o.contact_id = c.id
               WHERE o.stage = ? ORDER BY o.priority, o.updated_at DESC""",
            (stage,)
        ).fetchall()
        
        print(f"\n{stage.upper().replace('_', ' ')} ({len(opps)})")
        print("-" * 40)
        for opp in opps:
            contact = f" ({opp['contact_name']})" if opp['contact_name'] else ""
            action = f" → {opp['next_action']}" if opp['next_action'] else ""
            print(f"  #{opp['id']} {opp['company']}{contact}{action}")
    
    conn.close()


def get_actions():
    """Get today's action items."""
    conn = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("\n📋 TODAY'S ACTIONS")
    print("=" * 60)
    
    # Due reminders
    reminders = conn.execute(
        """SELECT r.*, c.name as contact_name, o.company
           FROM reminders r
           LEFT JOIN contacts c ON r.contact_id = c.id
           LEFT JOIN opportunities o ON r.opportunity_id = o.id
           WHERE r.due_date <= ? AND r.completed = FALSE
           ORDER BY r.due_date""",
        (today,)
    ).fetchall()
    
    if reminders:
        print("\n🔔 FOLLOW-UPS DUE")
        for r in reminders:
            target = r['contact_name'] or r['company'] or 'Unknown'
            if r['due_date'] < today:
                days_overdue = (datetime.now() - datetime.strptime(r['due_date'], '%Y-%m-%d')).days
                overdue = f" 🚨 URGENT - OVERDUE ({days_overdue}d)"
            else:
                overdue = ""
            print(f"  [{r['due_date']}] {target}: {r['message']}{overdue}")
    
    # Active opportunities needing attention
    stale_opps = conn.execute(
        """SELECT o.*, c.name as contact_name,
                  julianday('now') - julianday(o.updated_at) as days_stale
           FROM opportunities o
           LEFT JOIN contacts c ON o.contact_id = c.id
           WHERE o.stage NOT LIKE 'closed%'
           AND julianday('now') - julianday(o.updated_at) > 7
           ORDER BY days_stale DESC""",
    ).fetchall()
    
    if stale_opps:
        print("\n⏰ STALE OPPORTUNITIES (no activity in 7+ days)")
        for opp in stale_opps:
            days = int(opp['days_stale'])
            print(f"  #{opp['id']} {opp['company']} ({opp['stage']}) - {days} days since update")
    
    # New signals
    new_signals = conn.execute(
        """SELECT * FROM signals 
           WHERE processed = FALSE AND created_at > datetime('now', '-2 days')
           ORDER BY relevance_score DESC LIMIT 10"""
    ).fetchall()
    
    if new_signals:
        print("\n🎯 NEW OPPORTUNITIES DETECTED")
        for s in new_signals:
            score = f"[{s['relevance_score']:.1f}]" if s['relevance_score'] else ""
            print(f"  {score} [{s['source']}] {s['title'][:60]}")
            if s['url']:
                print(f"       {s['url']}")
    
    # HubSpot-sourced opportunities 
    hubspot_opps = conn.execute(
        """SELECT o.*, c.name as contact_name, c.last_engagement
           FROM opportunities o
           LEFT JOIN contacts c ON o.contact_id = c.id
           WHERE c.source = 'hubspot'
           AND o.stage NOT LIKE 'closed%'
           ORDER BY o.priority, o.updated_at DESC"""
    ).fetchall()
    
    if hubspot_opps:
        print("\n🤝 HUBSPOT OPPORTUNITIES")
        for opp in hubspot_opps:
            engagement = f" (engaged: {opp['last_engagement']})" if opp['last_engagement'] else ""
            print(f"  #{opp['id']} {opp['company']} ({opp['stage']}){engagement}")
            if opp['next_action']:
                print(f"       → {opp['next_action']}")
    
    # High priority opportunities
    hot_opps = conn.execute(
        """SELECT o.*, c.name as contact_name
           FROM opportunities o
           LEFT JOIN contacts c ON o.contact_id = c.id
           WHERE o.stage IN ('evaluation', 'negotiation')
           AND o.priority <= 3
           ORDER BY o.priority, o.updated_at DESC"""
    ).fetchall()
    
    if hot_opps:
        print("\n🔥 HIGH PRIORITY DEALS")
        for opp in hot_opps:
            action = f"→ {opp['next_action']}" if opp['next_action'] else "No next action defined!"
            print(f"  #{opp['id']} {opp['company']} ({opp['stage']})")
            print(f"       {action}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("💡 SUGGESTED FOCUS FOR TODAY:")
    print("  1. Handle overdue follow-ups first")
    print("  2. Review and process new signals")
    print("  3. Advance stale opportunities")
    print("  4. Check on high-priority deals")


def crawl_hn():
    """Crawl Hacker News for relevant discussions using Algolia search API."""
    conn = get_db()
    keywords = [row['keyword'] for row in conn.execute("SELECT keyword FROM keywords").fetchall()]
    
    print("🔍 Crawling Hacker News (Algolia)...")
    
    # Batch keywords into search queries (Algolia is fast — one request per query)
    # Group into chunks of 3-4 keywords per query using OR
    keyword_groups = []
    for i in range(0, len(keywords), 3):
        keyword_groups.append(keywords[i:i+3])
    
    found = 0
    try:
        for group in keyword_groups:
            query = ' OR '.join(f'"{kw}"' if ' ' in kw else kw for kw in group)
            encoded_query = urllib.parse.quote(query)
            url = f'https://hn.algolia.com/api/v1/search?query={encoded_query}&tags=story&hitsPerPage=50&numericFilters=created_at_i>{int(time.time()) - 86400 * 7}'
            
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'GTM-Tracker/1.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode())
            except (urllib.error.URLError, ConnectionResetError, ssl.SSLError) as e:
                print(f"  ⚠️ Algolia error for '{query[:40]}': {e}")
                continue
            
            for hit in data.get('hits', []):
                story_id = hit.get('objectID', '')
                
                existing = conn.execute(
                    "SELECT 1 FROM signals WHERE source = 'hn' AND source_id = ?",
                    (str(story_id),)
                ).fetchone()
                if existing:
                    continue
                
                title = hit.get('title', '')
                story_url = hit.get('url') or f"https://news.ycombinator.com/item?id={story_id}"
                
                # Score based on keyword matches
                content = title.lower()
                score = 0
                matched_keywords = []
                for kw in keywords:
                    if kw.lower() in content:
                        weight = conn.execute(
                            "SELECT weight FROM keywords WHERE keyword = ?", (kw,)
                        ).fetchone()
                        score += weight['weight'] if weight else 1.0
                        matched_keywords.append(kw)
                
                if score > 0:
                    conn.execute(
                        """INSERT OR IGNORE INTO signals (source, source_id, title, url, content, relevance_score)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        ('hn', str(story_id), title, story_url, f"Matched: {', '.join(matched_keywords)}", score)
                    )
                    found += 1
                    print(f"  📰 [{score:.1f}] {title[:60]}")
            
            time.sleep(0.5)  # Be polite to Algolia
        
        conn.commit()
        print(f"✅ HN crawl complete — {found} new signals")
        
    except Exception as e:
        print(f"❌ Error crawling HN: {e}")
    finally:
        conn.close()


def crawl_reddit():
    """Crawl Reddit for relevant posts."""
    conn = get_db()
    keywords = [row['keyword'] for row in conn.execute("SELECT keyword FROM keywords").fetchall()]
    
    subreddits = ['dataengineering', 'devops', 'mlops', 'selfhosted', 'kubernetes', 'datascience',
                   'snowflake', 'databricks', 'apachespark', 'cloudcomputing', 'aws', 'sysadmin',
                   'MachineLearning', 'artificial', 'LocalLLaMA']
    
    print("🔍 Crawling Reddit...")
    
    # Reddit blocks unauthenticated JSON API (403). Use Brave Search as fallback.
    brave_key = os.environ.get('BRAVE_API_KEY', '')
    if brave_key:
        try:
            pain_queries = [
                'site:reddit.com/r/dataengineering OR site:reddit.com/r/snowflake OR site:reddit.com/r/databricks "cost" OR "expensive" OR "bill" OR "pricing"',
                'site:reddit.com/r/dataengineering OR site:reddit.com/r/devops "pipeline" OR "ingestion" broken OR slow OR debugging',
                'site:reddit.com/r/aws OR site:reddit.com/r/cloudcomputing "egress" OR "data transfer" OR "cloud cost"',
                'site:reddit.com/r/dataengineering OR site:reddit.com/r/mlops "edge computing" OR "on-prem" OR "data sovereignty"',
                'site:reddit.com/r/Splunk OR site:reddit.com/r/sysadmin "splunk" cost OR expensive OR alternative OR migration',
            ]
            for query in pain_queries:
                encoded = urllib.parse.quote(query)
                req = urllib.request.Request(
                    f'https://api.search.brave.com/res/v1/web/search?q={encoded}&count=10&freshness=pm',
                    headers={'X-Subscription-Token': brave_key, 'Accept': 'application/json'}
                )
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        data = json.loads(response.read().decode())
                    for result in data.get('web', {}).get('results', []):
                        url = result.get('url', '')
                        if 'reddit.com' not in url:
                            continue
                        title = result.get('title', '')
                        snippet = result.get('description', '')
                        source_id = url.split('/')[-2] if '/comments/' in url else url
                        
                        existing = conn.execute(
                            "SELECT 1 FROM signals WHERE source = 'reddit' AND source_id = ?",
                            (source_id,)
                        ).fetchone()
                        if existing:
                            continue
                        
                        content = (title + ' ' + snippet).lower()
                        score = 0
                        matched = []
                        for kw in keywords:
                            if kw.lower() in content:
                                weight = conn.execute(
                                    "SELECT weight FROM keywords WHERE keyword = ?", (kw,)
                                ).fetchone()
                                score += weight['weight'] if weight else 1.0
                                matched.append(kw)
                        
                        if score > 0:
                            conn.execute(
                                """INSERT OR IGNORE INTO signals (source, source_id, title, url, content, relevance_score)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                ('reddit', source_id, title, url, f"Matched: {', '.join(matched)}", score)
                            )
                            print(f"  📰 [{score:.1f}] {title[:60]}")
                except (urllib.error.URLError, json.JSONDecodeError) as e:
                    continue
            conn.commit()
            print("✅ Reddit crawl complete (via Brave Search)")
            return
        except Exception as e:
            print(f"⚠️ Brave fallback failed: {e}")
    
    # Original Reddit JSON API (often blocked with 403)
    try:
        for subreddit in subreddits:
            req = urllib.request.Request(
                f'https://www.reddit.com/r/{subreddit}/hot.json?limit=50',
                headers={'User-Agent': 'GTM-Tracker/1.0'}
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
            except (urllib.error.URLError, json.JSONDecodeError):
                continue
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                post_id = post_data.get('id')
                
                # Check if already processed
                existing = conn.execute(
                    "SELECT 1 FROM signals WHERE source = 'reddit' AND source_id = ?",
                    (post_id,)
                ).fetchone()
                if existing:
                    continue
                
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                url = f"https://reddit.com{post_data.get('permalink', '')}"
                
                # Calculate relevance
                content = (title + ' ' + selftext).lower()
                score = 0
                matched = []
                for kw in keywords:
                    if kw.lower() in content:
                        weight = conn.execute(
                            "SELECT weight FROM keywords WHERE keyword = ?", (kw,)
                        ).fetchone()
                        score += weight['weight'] if weight else 1.0
                        matched.append(kw)
                
                if score > 0:
                    conn.execute(
                        """INSERT OR IGNORE INTO signals (source, source_id, title, url, content, relevance_score)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        ('reddit', post_id, f"[r/{subreddit}] {title}", url, f"Matched: {', '.join(matched)}", score)
                    )
                    print(f"  📰 [{score:.1f}] r/{subreddit}: {title[:50]}")
        
        conn.commit()
        print("✅ Reddit crawl complete")
        
    except Exception as e:
        print(f"❌ Error crawling Reddit: {e}")
    finally:
        conn.close()


def crawl_github():
    """Check GitHub for mentions and relevant repos."""
    conn = get_db()
    
    print("🔍 Checking GitHub trends...")
    
    # Search for repos mentioning key terms
    search_terms = ['bacalhau', 'distributed+computing', 'compute+over+data']
    
    try:
        for term in search_terms:
            req = urllib.request.Request(
                f'https://api.github.com/search/repositories?q={term}&sort=updated&per_page=20',
                headers={
                    'User-Agent': 'GTM-Tracker/1.0',
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
            except (urllib.error.URLError, json.JSONDecodeError):
                continue
            
            for repo in data.get('items', []):
                repo_id = str(repo.get('id'))
                
                existing = conn.execute(
                    "SELECT 1 FROM signals WHERE source = 'github' AND source_id = ?",
                    (repo_id,)
                ).fetchone()
                if existing:
                    continue
                
                name = repo.get('full_name', '')
                desc = repo.get('description', '') or ''
                url = repo.get('html_url', '')
                stars = repo.get('stargazers_count', 0)
                
                # Higher score for more stars
                score = 1.0 + min(stars / 100, 3.0)
                
                conn.execute(
                    """INSERT OR IGNORE INTO signals (source, source_id, title, url, content, relevance_score)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    ('github', repo_id, f"⭐{stars} {name}", url, desc[:200], score)
                )
                print(f"  📦 [{score:.1f}] {name} (⭐{stars})")
        
        conn.commit()
        print("✅ GitHub crawl complete")
        
    except Exception as e:
        print(f"❌ Error crawling GitHub: {e}")
    finally:
        conn.close()


def crawl_exa():
    """Search Exa.ai for semantically relevant GTM signals."""
    EXA_API_KEY = os.environ.get('EXA_API_KEY', '10b8459b-cbfe-42e4-9057-b541e10e671c')
    conn = get_db()
    keywords = [row['keyword'] for row in conn.execute("SELECT keyword FROM keywords").fetchall()]

    print("🔍 Searching Exa.ai for GTM signals...")

    queries = [
        "companies migrating from Snowflake or Databricks to reduce costs",
        "distributed compute orchestration for data pipelines",
        "edge computing data processing alternative to cloud",
        "Bacalhau distributed computing",
        "compute over data architecture",
        "AI agent data access security compliance",
        "pipeline debugging ingestion problems",
        "cloud cost optimization aws billing",
        "tool sprawl unified platform data stack",
    ]

    try:
        for query in queries:
            payload = json.dumps({
                "query": query,
                "type": "auto",
                "numResults": 10,
                "contents": {
                    "text": {"maxCharacters": 500}
                }
            }).encode()

            req = urllib.request.Request(
                'https://api.exa.ai/search',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': EXA_API_KEY,
                    'User-Agent': 'GTM-Tracker/1.0',
                    'Accept': 'application/json'
                },
                method='POST'
            )

            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode())
            except (urllib.error.URLError, json.JSONDecodeError) as e:
                print(f"  ⚠️ Exa query failed: {e}")
                continue

            for result in data.get('results', []):
                source_id = result.get('id', result.get('url', ''))
                existing = conn.execute(
                    "SELECT 1 FROM signals WHERE source = 'exa' AND source_id = ?",
                    (source_id,)
                ).fetchone()
                if existing:
                    continue

                title = result.get('title', '')[:200]
                url = result.get('url', '')
                text = result.get('text', '')[:500]
                
                # Score based on keyword matches and weights (same as other sources)
                content = (title + ' ' + text).lower()
                score = 0
                matched_keywords = []
                for kw in keywords:
                    if kw.lower() in content:
                        weight = conn.execute(
                            "SELECT weight FROM keywords WHERE keyword = ?", (kw,)
                        ).fetchone()
                        score += weight['weight'] if weight else 1.0
                        matched_keywords.append(kw)
                
                # Only store if we have keyword matches
                if score > 0:
                    conn.execute(
                        """INSERT OR IGNORE INTO signals (source, source_id, title, url, content, relevance_score)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        ('exa', source_id, title, url, f"Matched: {', '.join(matched_keywords)}", score)
                    )
                    print(f"  🧠 [{score:.1f}] {title[:80]}")

            time.sleep(0.5)  # rate limit courtesy

        conn.commit()
        print("✅ Exa crawl complete")

    except Exception as e:
        print(f"❌ Error crawling Exa: {e}")
    finally:
        conn.close()


def hubspot_sync():
    """Sync contacts from HubSpot and create opportunities for launch targets."""
    print("🔄 Syncing with HubSpot...")
    
    # Get HubSpot API token
    try:
        result = subprocess.run(
            ['doppler', 'secrets', 'get', 'HUBSPOT_API_TOKEN', '--plain', '--project', 'openclaw-server', '--config', 'prd'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print(f"❌ Failed to get HubSpot token: {result.stderr}")
            return
        
        hubspot_token = result.stdout.strip()
        if not hubspot_token.startswith('pat-na1-'):
            print(f"❌ Invalid HubSpot token format: {hubspot_token[:10]}...")
            return
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout getting HubSpot token")
        return
    except Exception as e:
        print(f"❌ Error getting HubSpot token: {e}")
        return
    
    conn = get_db()
    
    # Launch target companies for opportunity matching
    launch_companies = {
        'HSBC', 'Zededa', 'Baker Hughes', 'MotherDuck', 'Energy Transfer', 'NVIDIA',
        'SADA', 'ApertureData', 'NextEra Energy', 'PNC', 'IBM', 'Edge AI Foundation',
        'PhysicsX', 'Samsung Next', 'Waabi', 'Red Hat', 'Cisco', 'General Catalyst',
        'Exelon Corporation', 'Republic Services', 'Virtusa', 'Dell Technologies',
        'Sunified', 'Eversource', 'Permian Labs', 'Trilogy Search Partners',
        'Endeavor Health', 'AWS', 'Force Multiply', 'Astronomer'
    }
    
    try:
        # Get contacts with recent engagement (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # HubSpot contacts API with engagement filter
        contacts_url = f"https://api.hubapi.com/crm/v3/objects/contacts?limit=100&properties=firstname,lastname,email,company,jobtitle,lastmodifieddate,hs_latest_open_date,hs_latest_click_date"
        
        req = urllib.request.Request(
            contacts_url,
            headers={
                'Authorization': f'Bearer {hubspot_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'GTM-Tracker/1.0'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        
        contacts_synced = 0
        opportunities_created = 0
        
        for contact_data in data.get('results', []):
            props = contact_data.get('properties', {})
            hubspot_id = contact_data.get('id')
            
            # Basic contact info
            firstname = props.get('firstname', '')
            lastname = props.get('lastname', '')
            name = f"{firstname} {lastname}".strip()
            email = props.get('email', '')
            company = props.get('company', '')
            role = props.get('jobtitle', '')
            
            if not name or not email:
                continue
            
            # Check for recent engagement
            last_open = props.get('hs_latest_open_date')
            last_click = props.get('hs_latest_click_date')
            last_engagement = None
            
            if last_open or last_click:
                # Convert HubSpot timestamp (milliseconds) to date
                latest_ts = max(
                    int(last_open) if last_open else 0,
                    int(last_click) if last_click else 0
                )
                if latest_ts > 0:
                    last_engagement = datetime.fromtimestamp(latest_ts / 1000).strftime('%Y-%m-%d')
            
            # Only sync if recent engagement
            if not last_engagement or last_engagement < thirty_days_ago:
                continue
            
            # Check if contact already exists
            existing = conn.execute(
                "SELECT id FROM contacts WHERE hubspot_id = ? OR email = ?",
                (hubspot_id, email)
            ).fetchone()
            
            if existing:
                # Update existing contact
                conn.execute(
                    """UPDATE contacts SET name = ?, company = ?, role = ?, 
                       hubspot_id = ?, last_engagement = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (name, company, role, hubspot_id, last_engagement, existing['id'])
                )
            else:
                # Create new contact
                cur = conn.execute(
                    """INSERT INTO contacts (name, email, company, role, source, hubspot_id, last_engagement)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, email, company, role, 'hubspot', hubspot_id, last_engagement)
                )
                contact_id = cur.lastrowid
                contacts_synced += 1
                
                # Create opportunity if company matches launch targets
                if company and any(target.lower() in company.lower() for target in launch_companies):
                    existing_opp = conn.execute(
                        "SELECT 1 FROM opportunities WHERE company = ? AND contact_id = ?",
                        (company, contact_id)
                    ).fetchone()
                    
                    if not existing_opp:
                        conn.execute(
                            """INSERT INTO opportunities (contact_id, company, stage, description, next_action, priority)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (contact_id, company, 'interest', 
                             f'Launch target identified via HubSpot engagement: {name}',
                             'Review engagement patterns and reach out', 3)
                        )
                        opportunities_created += 1
                        print(f"  🎯 Created opportunity: {company} ({name})")
        
        conn.commit()
        print(f"✅ HubSpot sync complete: {contacts_synced} contacts, {opportunities_created} opportunities")
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if hasattr(e, 'read') else str(e)
        print(f"❌ HubSpot API error {e.code}: {error_body}")
    except Exception as e:
        print(f"❌ Error syncing HubSpot: {e}")
    finally:
        conn.close()


def list_contacts():
    """List all contacts."""
    conn = get_db()
    contacts = conn.execute(
        "SELECT * FROM contacts ORDER BY updated_at DESC"
    ).fetchall()
    
    print("\n👥 CONTACTS")
    print("=" * 60)
    for c in contacts:
        company = f" @ {c['company']}" if c['company'] else ""
        email = f" <{c['email']}>" if c['email'] else ""
        print(f"  #{c['id']} {c['name']}{company}{email}")
    
    conn.close()


def list_signals(unprocessed_only=True):
    """List detected signals."""
    conn = get_db()
    
    query = "SELECT * FROM signals"
    if unprocessed_only:
        query += " WHERE processed = FALSE"
    query += " ORDER BY relevance_score DESC, created_at DESC LIMIT 50"
    
    signals = conn.execute(query).fetchall()
    
    print("\n🎯 SIGNALS" + (" (unprocessed)" if unprocessed_only else ""))
    print("=" * 60)
    for s in signals:
        print(f"  [{s['relevance_score']:.1f}] [{s['source']}] {s['title'][:55]}")
        if s['url']:
            print(f"       {s['url']}")
    
    conn.close()


def mark_signal_processed(signal_id: int):
    """Mark a signal as processed."""
    conn = get_db()
    conn.execute("UPDATE signals SET processed = TRUE WHERE id = ?", (signal_id,))
    conn.commit()
    conn.close()
    print(f"✅ Signal #{signal_id} marked as processed")


def complete_reminder(reminder_id: int):
    """Mark a reminder as completed."""
    conn = get_db()
    conn.execute("UPDATE reminders SET completed = TRUE WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    print(f"✅ Reminder #{reminder_id} completed")


def add_keyword(keyword: str, category: str = 'custom', weight: float = 1.0):
    """Add a tracking keyword."""
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO keywords (keyword, category, weight) VALUES (?, ?, ?)",
        (keyword, category, weight)
    )
    conn.commit()
    conn.close()
    print(f"✅ Added keyword: {keyword} ({category}, weight={weight})")


def check_escalations():
    """Check for items needing immediate attention."""
    conn = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    
    escalations = []
    
    # 1. Overdue follow-ups
    overdue_reminders = conn.execute(
        """SELECT r.*, c.name as contact_name, o.company
           FROM reminders r
           LEFT JOIN contacts c ON r.contact_id = c.id
           LEFT JOIN opportunities o ON r.opportunity_id = o.id
           WHERE r.due_date < ? AND r.completed = FALSE
           ORDER BY r.due_date""",
        (today,)
    ).fetchall()
    
    for r in overdue_reminders:
        target = r['contact_name'] or r['company'] or 'Unknown'
        days_overdue = (datetime.now() - datetime.strptime(r['due_date'], '%Y-%m-%d')).days
        escalations.append({
            'type': 'overdue_followup',
            'priority': 'URGENT',
            'message': f"OVERDUE ({days_overdue}d): {target} - {r['message']}",
            'item_id': r['id']
        })
    
    # 2. High-score signals (>= 3.0) not processed after 48h
    stale_signals = conn.execute(
        """SELECT * FROM signals 
           WHERE processed = FALSE 
           AND relevance_score >= 3.0
           AND created_at < ?
           ORDER BY relevance_score DESC""",
        (two_days_ago,)
    ).fetchall()
    
    for s in stale_signals:
        hours_old = (datetime.now() - datetime.strptime(s['created_at'], '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600
        escalations.append({
            'type': 'stale_signal',
            'priority': 'URGENT',
            'message': f"HIGH-SCORE SIGNAL UNPROCESSED ({int(hours_old)}h): [{s['source']}] {s['title'][:50]}",
            'item_id': s['id']
        })
    
    # 3. Opportunities with no interaction in 7+ days
    stale_opportunities = conn.execute(
        """SELECT o.*, c.name as contact_name,
                  julianday('now') - julianday(o.updated_at) as days_stale
           FROM opportunities o
           LEFT JOIN contacts c ON o.contact_id = c.id
           WHERE o.stage NOT LIKE 'closed%'
           AND o.updated_at < ?
           ORDER BY days_stale DESC""",
        (seven_days_ago,)
    ).fetchall()
    
    for opp in stale_opportunities:
        days = int(opp['days_stale'])
        escalations.append({
            'type': 'stale_opportunity',
            'priority': 'HIGH',
            'message': f"STALE OPPORTUNITY ({days}d): #{opp['id']} {opp['company']} ({opp['stage']})",
            'item_id': opp['id']
        })
    
    conn.close()
    return escalations


def escalate():
    """Show escalation items requiring immediate attention."""
    escalations = check_escalations()
    
    print("\n🚨 ESCALATIONS")
    print("=" * 60)
    
    if not escalations:
        print("✅ No escalations - everything is on track!")
        return
    
    urgent_count = sum(1 for e in escalations if e['priority'] == 'URGENT')
    high_count = sum(1 for e in escalations if e['priority'] == 'HIGH')
    
    print(f"Total: {len(escalations)} items ({urgent_count} URGENT, {high_count} HIGH)")
    print()
    
    for escalation in escalations:
        priority_icon = "🚨" if escalation['priority'] == 'URGENT' else "⚠️"
        print(f"{priority_icon} {escalation['message']}")
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDED ACTIONS:")
    print("  1. Handle URGENT items immediately")
    print("  2. Process stale high-score signals")
    print("  3. Update stale opportunities")
    print("  4. Set follow-up reminders")


def generate_daily_digest():
    """Generate a daily digest suitable for sending via Telegram."""
    conn = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    
    output = []
    output.append(f"📊 **GTM Daily Digest - {today}**\n")
    
    # Due reminders
    reminders = conn.execute(
        """SELECT r.*, c.name as contact_name, o.company
           FROM reminders r
           LEFT JOIN contacts c ON r.contact_id = c.id
           LEFT JOIN opportunities o ON r.opportunity_id = o.id
           WHERE r.due_date <= ? AND r.completed = FALSE
           ORDER BY r.due_date""",
        (today,)
    ).fetchall()
    
    if reminders:
        output.append("🔔 **Follow-ups Due:**")
        for r in reminders:
            target = r['contact_name'] or r['company'] or 'Unknown'
            output.append(f"  • {target}: {r['message']}")
        output.append("")
    
    # Pipeline summary
    for stage in ['evaluation', 'negotiation']:
        opps = conn.execute(
            """SELECT COUNT(*) as count FROM opportunities WHERE stage = ?""",
            (stage,)
        ).fetchone()
        if opps['count'] > 0:
            output.append(f"📈 {stage.title()}: {opps['count']} opportunities")
    
    # New signals (top 5)
    signals = conn.execute(
        """SELECT * FROM signals 
           WHERE processed = FALSE 
           ORDER BY relevance_score DESC LIMIT 5"""
    ).fetchall()
    
    if signals:
        output.append("\n🎯 **New Signals:**")
        for s in signals:
            output.append(f"  • [{s['source']}] {s['title'][:50]}")
    
    # Add escalations
    escalations = check_escalations()
    if escalations:
        output.append("\n🚨 **ESCALATIONS**")
        urgent_items = [e for e in escalations if e['priority'] == 'URGENT']
        if urgent_items:
            output.append("**URGENT:**")
            for e in urgent_items:
                output.append(f"  • {e['message']}")
        
        high_items = [e for e in escalations if e['priority'] == 'HIGH']
        if high_items:
            output.append("**HIGH:**")
            for e in high_items[:3]:  # Limit to top 3 to avoid spam
                output.append(f"  • {e['message']}")
    
    conn.close()
    
    digest = "\n".join(output)
    print(digest)
    return digest


def main():
    parser = argparse.ArgumentParser(description='GTM Tracking System')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init
    subparsers.add_parser('init', help='Initialize database')
    
    # Add contact
    add_contact_parser = subparsers.add_parser('add-contact', help='Add a contact')
    add_contact_parser.add_argument('name')
    add_contact_parser.add_argument('email', nargs='?')
    add_contact_parser.add_argument('--company', '-c')
    add_contact_parser.add_argument('--role', '-r')
    add_contact_parser.add_argument('--source', '-s')
    add_contact_parser.add_argument('--notes', '-n')
    
    # Add opportunity
    add_opp_parser = subparsers.add_parser('add-opp', help='Add an opportunity')
    add_opp_parser.add_argument('company')
    add_opp_parser.add_argument('--contact', '-c', type=int)
    add_opp_parser.add_argument('--description', '-d')
    add_opp_parser.add_argument('--next-action', '-a')
    add_opp_parser.add_argument('--priority', '-p', type=int, default=5)
    
    # Log interaction
    log_parser = subparsers.add_parser('log', help='Log an interaction')
    log_parser.add_argument('content')
    log_parser.add_argument('--contact', '-c', type=int)
    log_parser.add_argument('--opp', '-o', type=int)
    log_parser.add_argument('--type', '-t', default='note')
    
    # Move stage
    move_parser = subparsers.add_parser('move-stage', help='Move opportunity stage')
    move_parser.add_argument('opp_id', type=int)
    move_parser.add_argument('stage', choices=STAGES)
    
    # Set reminder
    remind_parser = subparsers.add_parser('remind', help='Set a reminder')
    remind_parser.add_argument('message')
    remind_parser.add_argument('--contact', '-c', type=int)
    remind_parser.add_argument('--opp', '-o', type=int)
    remind_parser.add_argument('--date', '-d')
    
    # Complete reminder
    complete_parser = subparsers.add_parser('complete', help='Complete a reminder')
    complete_parser.add_argument('reminder_id', type=int)
    
    # Views
    subparsers.add_parser('pipeline', help='Show pipeline')
    subparsers.add_parser('actions', help='Show today\'s actions')
    subparsers.add_parser('contacts', help='List contacts')
    subparsers.add_parser('signals', help='List signals')
    subparsers.add_parser('digest', help='Generate daily digest')
    
    # Mark signal processed
    process_signal_parser = subparsers.add_parser('process-signal', help='Mark signal processed')
    process_signal_parser.add_argument('signal_id', type=int)
    
    # Crawl
    crawl_parser = subparsers.add_parser('crawl', help='Run crawlers')
    crawl_parser.add_argument('--sources', '-s', default='hn,reddit,github')
    
    # Add keyword
    keyword_parser = subparsers.add_parser('add-keyword', help='Add tracking keyword')
    keyword_parser.add_argument('keyword')
    keyword_parser.add_argument('--category', '-c', default='custom')
    keyword_parser.add_argument('--weight', '-w', type=float, default=1.0)
    
    # HubSpot sync
    subparsers.add_parser('hubspot-sync', help='Sync contacts and opportunities from HubSpot')
    
    # Escalations
    subparsers.add_parser('escalate', help='Show escalation items requiring immediate attention')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'init':
        init_db()
    elif args.command == 'add-contact':
        add_contact(args.name, args.email, args.company, args.role, args.source, args.notes)
    elif args.command == 'add-opp':
        add_opportunity(args.company, args.contact, args.description, args.next_action, args.priority)
    elif args.command == 'log':
        log_interaction(args.contact, args.opp, args.content, args.type)
    elif args.command == 'move-stage':
        move_stage(args.opp_id, args.stage)
    elif args.command == 'remind':
        set_reminder(args.contact, args.opp, args.date, args.message)
    elif args.command == 'complete':
        complete_reminder(args.reminder_id)
    elif args.command == 'pipeline':
        get_pipeline()
    elif args.command == 'actions':
        get_actions()
    elif args.command == 'contacts':
        list_contacts()
    elif args.command == 'signals':
        list_signals()
    elif args.command == 'digest':
        generate_daily_digest()
    elif args.command == 'process-signal':
        mark_signal_processed(args.signal_id)
    elif args.command == 'crawl':
        sources = args.sources.split(',')
        if 'hn' in sources:
            crawl_hn()
        if 'reddit' in sources:
            crawl_reddit()
        if 'github' in sources:
            crawl_github()
        if 'exa' in sources:
            crawl_exa()
    elif args.command == 'add-keyword':
        add_keyword(args.keyword, args.category, args.weight)
    elif args.command == 'hubspot-sync':
        hubspot_sync()
    elif args.command == 'escalate':
        escalate()


if __name__ == '__main__':
    main()
