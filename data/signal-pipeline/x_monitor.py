"""
X/Twitter Account Monitor for RSSdeck-MCP

Monitors X accounts via manual tweet URL fetching.
Since X API is paid, we use FxTwitter for individual tweets.

Features:
- SQLite persistence for compounding knowledge
- Track engagement over time (likes, retweets, views)
- Generate reports and detect trends

Usage:
  - Run: python x_monitor.py
  - Or import and call functions directly
"""

import json
import os
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass

DB_PATH = os.path.join(os.path.dirname(__file__), "x_monitor.db")

@dataclass
class Tweet:
    id: str
    author: str
    handle: str
    content: str
    created_at: str
    likes: int
    retweets: int
    views: int
    url: str
    fetched_at: str = None

# URLs to monitor (add any X URLs here)
MONITOR_URLS = [
    "https://x.com/karpathy/status/1896866532301783062",  # Claws
    "https://x.com/simonwillison/status/1896861234567890",
]

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            handle TEXT PRIMARY KEY,
            display_name TEXT,
            last_checked TIMESTAMP,
            tweet_count INTEGER DEFAULT 0
        )
    """)
    
    # Tweets table - stores each fetch with timestamp
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id TEXT,
            url TEXT,
            handle TEXT,
            author TEXT,
            content TEXT,
            created_at TIMESTAMP,
            likes INTEGER,
            retweets INTEGER,
            views INTEGER,
            fetched_at TIMESTAMP,
            PRIMARY KEY (id, fetched_at)
        )
    """)
    
    # Monitored URLs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitored_urls (
            url TEXT PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def add_account(handle: str, display_name: str = None):
    """Track an account"""
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO accounts (handle, display_name, last_checked)
        VALUES (?, ?, ?)
    """, (handle, display_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def add_monitored_url(url: str):
    """Add URL to monitoring list"""
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO monitored_urls (url) VALUES (?)
    """, (url,))
    conn.commit()
    conn.close()

def store_tweet(tweet: Tweet) -> bool:
    """Store tweet in database, return True if new"""
    conn = get_connection()
    fetched_at = datetime.now().isoformat()
    
    try:
        conn.execute("""
            INSERT OR IGNORE INTO tweets 
            (id, url, handle, author, content, created_at, likes, retweets, views, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tweet.id, tweet.url, tweet.handle, tweet.author,
            tweet.content, tweet.created_at, tweet.likes,
            tweet.retweets, tweet.views, fetched_at
        ))
        conn.commit()
        new = conn.total_changes > 0
        conn.close()
        return new
    except Exception as e:
        conn.close()
        print(f"Error storing tweet: {e}")
        return False

def get_tweet_history(tweet_id: str) -> List[Dict]:
    """Get all fetched records for a tweet (for trend analysis)"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT * FROM tweets WHERE id = ? ORDER BY fetched_at DESC
    """, (tweet_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_latest_tweets(limit: int = 50) -> List[Dict]:
    """Get most recently fetched tweets"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT DISTINCT id, url, handle, author, content, created_at, 
               likes, retweets, views, fetched_at
        FROM tweets 
        GROUP BY id 
        ORDER BY fetched_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_tweets_by_handle(handle: str, limit: int = 20) -> List[Dict]:
    """Get tweets from specific handle"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT DISTINCT id, url, handle, author, content, created_at,
               likes, retweets, views, fetched_at
        FROM tweets WHERE handle = ? 
        GROUP BY id ORDER BY fetched_at DESC LIMIT ?
    """, (handle, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_engagement_trends(handle: str = None, days: int = 7) -> Dict:
    """Analyze engagement trends"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    query = """
        SELECT handle, 
               AVG(likes) as avg_likes,
               AVG(retweets) as avg_retweets,
               AVG(views) as avg_views,
               COUNT(DISTINCT id) as tweet_count
        FROM tweets 
        WHERE fetched_at >= datetime('now', '-{} days')
        {}
        GROUP BY handle
    """.format(days, "AND handle = ?" if handle else "")
    
    params = [handle] if handle else []
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"trends": [dict(row) for row in rows], "days": days}

def fetch_tweet(url: str, store: bool = True) -> Optional[Tweet]:
    """Fetch a single tweet using FxTwitter API"""
    try:
        # Extract handle and ID from URL
        parts = url.split("/")
        handle = parts[-2] if len(parts) >= 2 else ""
        tweet_id = parts[-1] if parts else ""
        
        api_url = f"https://api.fxtwitter.com/{handle}/status/{tweet_id}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        if data.get("code") != 200:
            print(f"Error: {data.get('message', 'Unknown')}")
            return None
        
        tweet_data = data.get("tweet", {})
        author_data = tweet_data.get("author", {})
        
        tweet = Tweet(
            id=str(tweet_data.get("id", "")),
            author=author_data.get("name", ""),
            handle=author_data.get("screen_name", ""),
            content=tweet_data.get("text", ""),
            created_at=tweet_data.get("created_at", ""),
            likes=tweet_data.get("like_count", 0),
            retweets=tweet_data.get("retweet_count", 0),
            views=tweet_data.get("views", {}).get("count", 0) if "views" in tweet_data else 0,
            url=url,
        )
        
        if store:
            store_tweet(tweet)
            add_account(tweet.handle, tweet.author)
            add_monitored_url(url)
        
        return tweet
        
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def fetch_all(urls: List[str], store: bool = True) -> List[Tweet]:
    """Fetch multiple tweets"""
    tweets = []
    for url in urls:
        tweet = fetch_tweet(url, store=store)
        if tweet:
            tweets.append(tweet)
    return tweets

def generate_report(days: int = 7) -> str:
    """Generate intelligence report"""
    trends = get_engagement_trends(days=days)
    latest = get_latest_tweets(limit=20)
    
    report = f"X Monitor Report (Last {days} days)\n"
    report += "=" * 40 + "\n\n"
    
    # Top accounts by engagement
    if trends["trends"]:
        report += "Top Accounts by Average Engagement:\n"
        sorted_trends = sorted(trends["trends"], 
                               key=lambda x: x["avg_likes"] + x["avg_retweets"] * 2, 
                               reverse=True)
        for t in sorted_trends[:5]:
            report += f"  @{t['handle']}: ❤️{t['avg_likes']:.0f} 🔁{t['avg_retweets']:.0f} 👁️{t['avg_views']:.0f}\n"
        report += "\n"
    
    # Recent tweets
    report += f"Recent Tweets ({len(latest)}):\n"
    for t in latest[:10]:
        content = t["content"][:80] + "..." if len(t["content"]) > 80 else t["content"]
        report += f"  @{t['handle']}: {content}\n"
        report += f"    ❤️{t['likes']} 🔁{t['retweets']} 👁️{t['views']}\n"
    
    return report

def summarize(tweets: List[Tweet]) -> str:
    """Generate token-efficient summary"""
    if not tweets:
        return "No tweets to summarize"
    
    result = f"X/Twitter Monitor ({len(tweets)} tweets):\n\n"
    for i, t in enumerate(tweets, 1):
        content = t.content[:100] + "..." if len(t.content) > 100 else t.content
        result += f"{i}. @{t.handle}: {content}\n"
        result += f"   ❤️{t.likes} 🔁{t.retweets} 👁️{t.views}\n\n"
    
    return result

# Initialize DB on import
init_db()

# Test
if __name__ == "__main__":
    print("=== X Account Monitor ===\n")
    print(f"Database: {DB_PATH}\n")
    
    # Test with a known tweet
    test_url = "https://x.com/karpathy/status/1896866532301783062"
    print(f"Fetching: {test_url}")
    
    tweet = fetch_tweet(test_url, store=True)
    if tweet:
        print(f"\n@{tweet.handle}: {tweet.content[:150]}...")
        print(f"Likes: {tweet.likes}, Retweets: {tweet.retweets}, Views: {tweet.views}")
        print("\nStored in database ✓")
    
    print("\n" + "=" * 40)
    print("Report:")
    print(generate_report(days=7))
