"""
Telegram Channel Monitor

Scrapes public Telegram channel posts via web.
Stores in SQLite for compounding knowledge.

Usage:
  python telegram_monitor.py
"""

import os
import sqlite3
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict

CHANNEL = "jike_collection"
DB_PATH = os.path.join(os.path.dirname(__file__), "telegram_db.db")

def init_db():
    """Initialize SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            message_id TEXT UNIQUE,
            text TEXT,
            author TEXT,
            channel TEXT,
            posted_at TIMESTAMP,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_posts(count: int = 10) -> List[Dict]:
    """Fetch latest posts from channel via web"""
    url = f"https://t.me/s/{CHANNEL}"
    
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        posts = []
        messages = soup.select("div.tgme_widget_message")
        
        for msg in messages[:count]:
            try:
                # Get message ID
                msg_link = msg.select_one("a.tgme_widget_message_date")
                if not msg_link:
                    continue
                
                # Extract message text
                text_elem = msg.select_one("div.tgme_widget_message_text")
                text = text_elem.get_text(strip=True) if text_elem else ""
                
                # Get author
                author_elem = msg.select_one("a.tgme_widget_message_owner_name")
                author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                
                # Get date
                time_elem = msg.select_one("time")
                posted_at = time_elem.get("datetime") if time_elem else datetime.now().isoformat()
                
                if text:
                    posts.append({
                        "text": text[:2000],  # Limit length
                        "author": author,
                        "posted_at": posted_at
                    })
            except Exception as e:
                print(f"Error parsing message: {e}")
                continue
        
        return posts
        
    except Exception as e:
        print(f"Error fetching channel: {e}")
        return []

def store_post(post: Dict) -> bool:
    """Store post, return True if new"""
    conn = get_connection()
    channel = post.get("channel", "unknown")
    try:
        conn.execute("""
            INSERT OR IGNORE INTO posts (message_id, text, author, channel, posted_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            hash(post["text"][:100]),  # Use hash as pseudo-ID
            post["text"],
            post["author"],
            channel,
            post["posted_at"]
        ))
        conn.commit()
        new = conn.total_changes > 0
        conn.close()
        return new
    except Exception as e:
        conn.close()
        print(f"Error storing: {e}")
        return False

def get_posts(limit: int = 20) -> List[Dict]:
    """Get stored posts"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT * FROM posts ORDER BY posted_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def generate_report() -> str:
    """Generate briefing from channel"""
    posts = get_posts(limit=10)
    
    if not posts:
        return "No posts yet"
    
    report = "📱 TELEGRAM CHANNEL: 即刻精选\n"
    report += "=" * 45 + "\n\n"
    
    for i, p in enumerate(posts[:5], 1):
        text = p["text"][:150] + "..." if len(p["text"]) > 150 else p["text"]
        report += f"{i}. {text}\n"
        report += f"   by @{p['author']} | {p['posted_at'][:10]}\n\n"
    
    return report

# Initialize
init_db()

if __name__ == "__main__":
    print("Fetching posts from @jike_collection...")
    posts = fetch_posts(10)
    print(f"Found {len(posts)} posts")
    
    new_count = 0
    for p in posts:
        if store_post(p):
            new_count += 1
    
    print(f"Stored {new_count} new posts")
    print("\n" + generate_report())

# WeChat via Sogou search
def search_wechat(keyword, limit=5):
    """Search WeChat articles via Sogou"""
    import requests
    from bs4 import BeautifulSoup
    
    url = f"https://weixin.sogou.com/weixin?type=2&query={keyword}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        results = []
        articles = soup.select("div.txt-box")[:limit]
        
        for art in articles:
            try:
                title = art.select_one("h3")
                if title:
                    title = title.get_text(strip=True)
                    
                # Get article link
                link = art.select_one("a")
                if link and link.get("href"):
                    article_url = "https://weixin.sogou.com" + link["href"]
                    
                    results.append({
                        "title": title,
                        "url": article_url,
                        "source": "WeChat"
                    })
            except:
                pass
        
        return results
    except Exception as e:
        print(f"WeChat search error: {e}")
        return []

if __name__ == "__main__":
    # Test
    results = search_wechat("品牌营销")
    print(f"Found {len(results)} WeChat articles")
    for r in results:
        print(f"  - {r['title'][:40]}")
