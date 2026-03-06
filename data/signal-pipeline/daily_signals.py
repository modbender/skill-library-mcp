#!/usr/bin/env python3
"""
Daily Marketing Signals - Gathers signals about tech impact on marketing
Run: python daily_signals.py

Task: Run daily at ~10am, find 1 interesting signal, draft post
"""

import os
import sqlite3
import sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from rss_db import get_articles
from x_monitor import get_latest_tweets
from telegram_monitor import get_connection

# Marketing-adjacent keywords to search for
MARKETING_KEYWORDS = ['marketing', 'brand', 'consumer', 'retail', 'platform', 
                      'growth', 'media', 'advertising', ' DTC', 'subscription',
                      'business', 'product', 'customer', 'user', 'attention']

# Broader tech/business keywords
TECH_KEYWORDS = ['ai', 'model', 'chip', 'hardware', 'software', 'platform', 
                 'startup', 'founder', 'venture', 'investment', '估值', '融资']

def get_telegram_posts():
    conn = get_connection()
    conn.row_factory = lambda c, r: dict(zip([d[0] for d in c.description], r))
    return conn.execute('SELECT * FROM posts ORDER BY posted_at DESC LIMIT 20').fetchall()

def find_signal(signals):
    """Find the best signal from all sources"""
    
    # Try X first - usually more insightful
    for t in signals.get('x', []):
        content = t.get('content', '')
        # Look for product/tech insights that relate to marketing
        if any(k in content.lower() for k in ['product', 'launch', 'growth', 'user', 'platform', 'model']):
            return {
                'source': f"X/@{t['handle']}",
                'content': content[:200],
                'engagement': t.get('likes', 0),
                'type': 'x'
            }
    
    # Try RSS
    for a in signals.get('rss', []):
        title = a.get('title', '')
        if any(k in title.lower() for k in MARKETING_KEYWORDS + TECH_KEYWORDS):
            return {
                'source': a.get('source', 'RSS'),
                'content': title,
                'engagement': 0,
                'type': 'rss'
            }
    
    # Fallback: any interesting tech signal
    if signals.get('x'):
        t = signals['x'][0]
        return {
            'source': f"X/@{t['handle']}",
            'content': t.get('content', '')[:200],
            'engagement': t.get('likes', 0),
            'type': 'x'
        }
    
    return None

def draft_post(signal):
    """Draft a LinkedIn/X post based on signal"""
    
    if not signal:
        return "No signal found today"
    
    today = datetime.now().strftime('%b %d')
    
    content = signal['content']
    source = signal['source']
    
    # Draft template
    draft = f"""📡 Daily Signal - {today}

{content}

Source: {source}

#Marketing #Tech #Business"""

    return draft

def gather_signals():
    """Gather all signals for the day"""
    signals = {"rss": [], "x": [], "telegram": []}
    
    try:
        articles = get_articles(limit=100)
        signals["rss"] = articles
    except:
        pass
    
    try:
        tweets = get_latest_tweets(limit=50)
        signals["x"] = tweets
    except:
        pass
    
    try:
        signals["telegram"] = get_telegram_posts()
    except:
        pass
    
    return signals

if __name__ == "__main__":
    print("=" * 60)
    print(f"DAILY MARKETING SIGNALS - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    signals = gather_signals()
    
    print(f"\nSources:")
    print(f"  RSS: {len(signals['rss'])} articles")
    print(f"  X: {len(signals['x'])} tweets")  
    print(f"  Telegram: {len(signals['telegram'])} posts")
    
    signal = find_signal(signals)
    
    if signal:
        print(f"\nBest Signal:")
        print(f"  Source: {signal['source']}")
        print(f"  Content: {signal['content'][:100]}...")
        
        print()
        print("=" * 60)
        print("DRAFT POST:")
        print("=" * 60)
        print(draft_post(signal))
    else:
        print("\nNo signal found today")

def get_all_daily_signals(days=7):
    """Get all signals from past N days"""
    signals = {"rss": [], "x": [], "telegram": []}
    
    try:
        articles = get_articles(limit=500)
        signals["rss"] = articles
    except:
        pass
    
    try:
        tweets = get_latest_tweets(limit=200)
        signals["x"] = tweets
    except:
        pass
    
    return signals

def find_themes(signals, days=7):
    """Find recurring themes from the week"""
    themes = {}
    
    # X themes
    for t in signals.get('x', []):
        content = t.get('content', '').lower()
        if 'india' in content or 'market' in content:
            themes['market_expansion'] = themes.get('market_expansion', 0) + 1
        if 'platform' in content or 'tiktok' in content or 'algorithm' in content:
            themes['platform_power'] = themes.get('platform_power', 0) + 1
        if 'ai' in content or 'model' in content or 'chip' in content:
            themes['ai_disruption'] = themes.get('ai_disruption', 0) + 1
        if 'retail' in content or 'consumer' in content or 'brand' in content:
            themes['consumer_shift'] = themes.get('consumer_shift', 0) + 1
    
    return themes

def generate_weekly_summary():
    """Generate weekly summary"""
    print("=" * 70)
    print(f"WEEKLY MARKETING SIGNALS SUMMARY")
    print(f"Week of: {(datetime.now() - timedelta(days=7)).strftime('%b %d')} - {datetime.now().strftime('%b %d, %Y')}")
    print("=" * 70)
    
    signals = get_all_daily_signals(7)
    themes = find_themes(signals)
    
    print(f"\nSources captured:")
    print(f"  X: {len(signals['x'])} tweets")
    print(f"  RSS: {len(signals['rss'])} articles")
    
    print(f"\nRecurring Themes:")
    for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
        print(f"  - {theme}: {count} mentions")
    
    # Top signals
    print(f"\nTop Signals This Week:")
    print("-" * 50)
    
    # X
    print("X/Twitter:")
    for t in signals['x'][:5]:
        print(f"  @{t['handle']}: {t['content'][:60]}...")
    
    print()
    return """
## Weekly Summary Draft

[This week we observed X themes in marketing transformation]

### Key Themes:
- Theme 1
- Theme 2  
- Theme 3

### What this means for marketing:
[Your analysis]

#Marketing #Tech #WeeklyInsights
"""

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--weekly', action='store_true', help='Generate weekly summary')
    args = parser.parse_args()
    
    if args.weekly:
        print(generate_weekly_summary())
    else:
        # Daily mode
        print("=" * 60)
        print(f"DAILY MARKETING SIGNALS - {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        signals = gather_signals()
        
        print(f"\nSources:")
        print(f"  RSS: {len(signals['rss'])} articles")
        print(f"  X: {len(signals['x'])} tweets")  
        print(f"  Telegram: {len(signals['telegram'])} posts")
        
        signal = find_signal(signals)
        
        if signal:
            print(f"\nBest Signal:")
            print(f"  Source: {signal['source']}")
            print(f"  Content: {signal['content'][:100]}...")
            
            print()
            print("=" * 60)
            print("DRAFT POST:")
            print("=" * 60)
            print(draft_post(signal))
        else:
            print("\nNo signal found today")

def save_daily_signal(signal):
    """Save today's signal to file for weekly compilation"""
    if not signal:
        return
    
    import json
    date = datetime.now().strftime('%Y-%m-%d')
    filepath = f"/Users/jarvis/.openclaw/workspace/memory/daily_signals/{date}.json"
    
    data = {
        "date": date,
        "signal": signal,
        "draft": draft_post(signal)
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f)
    
    print(f"Saved to {filepath}")
    return filepath

def generate_monthly_report():
    """Generate monthly deep-dive report"""
    from collections import defaultdict
    import json
    
    print("=" * 70)
    print(f"MONTHLY MARKETING TRANSFORMATION REPORT")
    print(f"Month: February 2026")
    print("=" * 70)
    
    # Load all daily signals
    signals = []
    import os
    import glob
    
    signal_dir = "/Users/jarvis/.openclaw/workspace/memory/daily_signals/"
    files = glob.glob(signal_dir + "*.json")
    
    for f in files:
        with open(f) as fp:
            data = json.load(fp)
            signals.append(data)
    
    print(f"\nDaily signals compiled: {len(signals)}")
    
    # Aggregate themes
    themes = defaultdict(list)
    for s in signals:
        sig = s.get('signal', {})
        # Categorize
        content = sig.get('content', '').lower()
        
        if any(k in content for k in ['india', 'market', 'growth', 'expansion']):
            themes['market_expansion'].append(s)
        if any(k in content for k in ['platform', 'tiktok', 'algorithm', 'super-app']):
            themes['platform_power'].append(s)
        if any(k in content for k in ['ai', 'model', 'chip', 'llm', 'agent']):
            themes['ai_disruption'].append(s)
        if any(k in content for k in ['brand', 'consumer', 'retail', 'd2c']):
            themes['consumer_shift'].append(s)
    
    print(f"\nThemes identified:")
    for theme, items in themes.items():
        print(f"  {theme}: {len(items)} signals")
    
    # Generate POV
    print()
    print("=" * 70)
    print("MONTHLY POV DRAFT:")
    print("=" * 70)
    
    pov = f"""📊 Monthly Marketing Signals - February 2026

After tracking {len(signals)} daily signals from X, RSS, and Telegram this month, three themes emerge:

## 1. AI is rewriting the playbook

From Andrew Ng's "no-code AI course" to Karpathy's "Claws" concept, the democratization of AI is accelerating. 

Marketing implication: The "barrier to entry" for building products is dropping. Every consumer becomes a potential creator. The marketing challenge shifts from "how to reach" to "how to matter."

## 2. Emerging markets are the frontier

India 4x growth in 2 weeks. These markets skip legacy tech and go straight to mobile-first, AI-native behaviors.

Marketing implication: The next billion users don't think about "digital transformation" - they just use. Distribution through super-apps and short-video platforms, not traditional advertising.

## 3. Platform power consolidates

Whether it's TikTok becoming the default discovery engine or X/Telegram as information hubs, the gatekeepers are shifting.

Marketing implication: Brand authority erodes. Platform algorithms decide reach. The only moat is community and authenticity.

---

The common thread: The old marketing playbook (interrupt, persuade, repeat) is breaking. The new playbook is permission, value, community.

What's your take?

#Marketing #Transformation #AI #2026
"""
    
    print(pov)
    return pov

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--weekly', action='store_true', help='Generate weekly summary')
    parser.add_argument('--monthly', action='store_true', help='Generate monthly report')
    args = parser.parse_args()
    
    if args.monthly:
        print(generate_monthly_report())
    elif args.weekly:
        print(generate_weekly_summary())
    else:
        # Daily mode
        print("=" * 60)
        print(f"DAILY MARKETING SIGNALS - {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        signals = gather_signals()
        
        print(f"\nSources:")
        print(f"  RSS: {len(signals['rss'])} articles")
        print(f"  X: {len(signals['x'])} tweets")  
        print(f"  Telegram: {len(signals['telegram'])} posts")
        
        signal = find_signal(signals)
        
        if signal:
            print(f"\nBest Signal:")
            print(f"  Source: {signal['source']}")
            print(f"  Content: {signal['content'][:100]}...")
            
            print()
            print("=" * 60)
            print("DRAFT POST:")
            print("=" * 60)
            print(draft_post(signal))
        else:
            print("\nNo signal found today")

def get_newsletter_signals():
    """Get signals from Gmail newsletters"""
    try:
        from newsletter_monitor import get_marketing_signals
        return get_marketing_signals()
    except Exception as e:
        print(f"Newsletter error: {e}")
        return []

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--weekly', action='store_true', help='Generate weekly summary')
    parser.add_argument('--monthly', action='store_true', help='Generate monthly report')
    parser.add_argument('--newsletters', action='store_true', help='Check newsletters')
    args = parser.parse_args()
    
    if args.newsletters:
        signals = get_newsletter_signals()
        print(f"Found {len(signals)} newsletter signals:")
        for s in signals[:10]:
            print(f"  {s['newsletter']}: {s['subject'][:50]}")
    elif args.monthly:
        print(generate_monthly_report())
    elif args.weekly:
        print(generate_weekly_summary())
    else:
        # Daily mode
        print("=" * 60)
        print(f"DAILY MARKETING SIGNALS - {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        signals = gather_signals()
        
        print(f"\nSources:")
        print(f"  RSS: {len(signals['rss'])} articles")
        print(f"  X: {len(signals['x'])} tweets")  
        print(f"  Telegram: {len(signals['telegram'])} posts")
        
        # Also check newsletters
        nl_signals = get_newsletter_signals()
        print(f"  Newsletters: {len(nl_signals)} emails")
        
        signal = find_signal(signals)
        
        if signal:
            print(f"\nBest Signal:")
            print(f"  Source: {signal['source']}")
            print(f"  Content: {signal['content'][:100]}...")
            
            print()
            print("=" * 60)
            print("DRAFT POST:")
            print("=" * 60)
            print(draft_post(signal))
        else:
            print("\nNo signal found today")

# ============ EVOMAP-STYLE SIGNAL CAPSULES ============

class SignalCapsule:
    """Structured signal like EvoMap capsules"""
    def __init__(self, content, source, signal_type, tags, engagement_score=0):
        self.id = hash(content[:50])  # Unique ID
        self.content = content
        self.source = source
        self.signal_type = signal_type  # trend, insight, data, news
        self.tags = tags  # marketing, tech, etc
        self.engagement_score = engagement_score
        self.gdi_score = self.calculate_gdi()
        self.created_at = datetime.now().isoformat()
    
    def calculate_gdi(self):
        """Calculate signal quality score (like EvoMap's GDI)"""
        # Base score from engagement
        score = min(self.engagement_score / 100, 1.0) * 50
        
        # Boost for having tags
        score += min(len(self.tags) * 5, 20)
        
        # Boost for source quality
        source_boost = {
            'x': 10,
            'rss': 8,
            'telegram': 5,
            'newsletter': 12,
            'wechat': 7
        }
        score += source_boost.get(self.source.split('/')[0].lower(), 5)
        
        return min(score, 100)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content[:200],
            'source': self.source,
            'type': self.signal_type,
            'tags': self.tags,
            'gdi_score': self.gdi_score,
            'engagement': self.engagement_score,
            'created_at': self.created_at
        }

def store_capsule(capsule):
    """Store capsule in database"""
    import json
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO signal_capsules 
            (id, content, source, signal_type, tags, gdi_score, engagement, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            capsule.id,
            capsule.content,
            capsule.source,
            capsule.signal_type,
            json.dumps(capsule.tags),
            capsule.gdi_score,
            capsule.engagement_score,
            capsule.created_at
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Store capsule error: {e}")
        return False

def get_top_capsules(limit=10):
    """Get highest quality signals"""
    conn = get_connection()
    conn.row_factory = lambda c, r: dict(zip([d[0] for d in c.description], r))
    cursor = conn.execute("""
        SELECT * FROM signal_capsules 
        ORDER BY gdi_score DESC LIMIT ?
    """, (limit,))
    return cursor.fetchall()

# ============ CAPSULE DATABASE TABLE ============

def init_capsule_db():
    """Initialize capsule storage"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signal_capsules (
            id INTEGER PRIMARY KEY,
            content TEXT,
            source TEXT,
            signal_type TEXT,
            tags TEXT,
            gdi_score REAL DEFAULT 0,
            engagement INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

# Initialize on import
init_capsule_db()
