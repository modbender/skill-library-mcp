"""
RSS Feed Database for RSSdeck-MCP

SQLite persistence for RSS feeds and articles.
Enables compounding knowledge, trend analysis, and reporting.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "rss_db.db")

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Feeds table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            url TEXT UNIQUE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_fetched TIMESTAMP,
            article_count INTEGER DEFAULT 0
        )
    """)
    
    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT,
            title TEXT,
            link TEXT UNIQUE,
            summary TEXT,
            content TEXT,
            published TIMESTAMP,
            source TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sentiment TEXT DEFAULT 'neutral',
            relevance_score REAL DEFAULT 0.0,
            PRIMARY KEY (id, fetched_at)
        )
    """)
    
    # Feed topics/categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feed_topics (
            feed_id INTEGER,
            topic TEXT,
            FOREIGN KEY (feed_id) REFERENCES feeds(id)
        )
    """)
    
    conn.commit()
    return conn

def get_connection():
    return sqlite3.connect(DB_PATH)

# ============ FEEDS ============

def add_feed(name: str, url: str) -> int:
    """Add a feed, return feed_id"""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO feeds (name, url) VALUES (?, ?)
        """, (name, url))
        conn.commit()
        if cursor.lastrowid:
            feed_id = cursor.lastrowid
        else:
            # Already exists, get the ID
            row = conn.execute("SELECT id FROM feeds WHERE url = ?", (url,)).fetchone()
            feed_id = row[0] if row else None
        conn.close()
        return feed_id
    except Exception as e:
        conn.close()
        print(f"Error adding feed: {e}")
        return None

def get_all_feeds() -> List[Dict]:
    """Get all feeds"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM feeds ORDER BY last_fetched DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_feed_fetched(url: str):
    """Mark feed as fetched"""
    conn = get_connection()
    conn.execute("""
        UPDATE feeds SET last_fetched = ?, article_count = article_count + 1 
        WHERE url = ?
    """, (datetime.now().isoformat(), url))
    conn.commit()
    conn.close()

# ============ ARTICLES ============

def store_article(article: Dict) -> bool:
    """Store article in database, return True if new"""
    conn = get_connection()
    fetched_at = datetime.now().isoformat()
    
    try:
        conn.execute("""
            INSERT OR IGNORE INTO articles 
            (id, title, link, summary, content, published, source, fetched_at, sentiment, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.get("id"),
            article.get("title"),
            article.get("link"),
            article.get("summary", ""),
            article.get("content", ""),
            article.get("published"),
            article.get("source"),
            fetched_at,
            article.get("sentiment", "neutral"),
            article.get("relevance_score", 0.0)
        ))
        conn.commit()
        new = conn.total_changes > 0
        conn.close()
        return new
    except Exception as e:
        conn.close()
        print(f"Error storing article: {e}")
        return False

def store_articles(articles: List[Dict]) -> int:
    """Store multiple articles, return count of new ones"""
    new_count = 0
    for article in articles:
        if store_article(article):
            new_count += 1
    return new_count

def get_articles(limit: int = 50, hours: int = None) -> List[Dict]:
    """Get articles, optionally filtered by hours"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    if hours:
        query = """
            SELECT DISTINCT id, title, link, summary, published, source, fetched_at, sentiment, relevance_score
            FROM articles 
            WHERE fetched_at >= datetime('now', '-{} hours')
            ORDER BY relevance_score DESC, published DESC
            LIMIT ?
        """.format(hours)
        cursor = conn.execute(query, (limit,))
    else:
        query = """
            SELECT DISTINCT id, title, link, summary, published, source, fetched_at, sentiment, relevance_score
            FROM articles 
            ORDER BY fetched_at DESC LIMIT ?
        """
        cursor = conn.execute(query, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_articles_by_source(source: str, limit: int = 20) -> List[Dict]:
    """Get articles from specific source"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT DISTINCT id, title, link, summary, published, source, fetched_at, sentiment, relevance_score
        FROM articles WHERE source = ? 
        ORDER BY published DESC LIMIT ?
    """, (source, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_articles(query: str, limit: int = 20) -> List[Dict]:
    """Search articles by title or summary"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    search = f"%{query}%"
    cursor = conn.execute("""
        SELECT DISTINCT id, title, link, summary, published, source, fetched_at, sentiment, relevance_score
        FROM articles 
        WHERE title LIKE ? OR summary LIKE ?
        ORDER BY relevance_score DESC, published DESC
        LIMIT ?
    """, (search, search, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_sentiment_breakdown(hours: int = 24) -> Dict:
    """Get sentiment distribution"""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT sentiment, COUNT(*) as count 
        FROM articles 
        WHERE fetched_at >= datetime('now', '-{} hours')
        GROUP BY sentiment
    """.format(hours))
    rows = cursor.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}

def get_top_sources(hours: int = 24, limit: int = 10) -> List[Dict]:
    """Get top sources by article count"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT source, COUNT(*) as count, AVG(relevance_score) as avg_relevance
        FROM articles 
        WHERE fetched_at >= datetime('now', '-{} hours')
        GROUP BY source
        ORDER BY count DESC
        LIMIT ?
    """.format(hours), (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_trending_topics(hours: int = 24, limit: int = 10) -> List[Dict]:
    """Extract trending topics/keywords from recent articles"""
    # Simple keyword extraction - in production, use NLP
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    # Get recent articles and extract keywords
    cursor = conn.execute("""
        SELECT title, summary FROM articles 
        WHERE fetched_at >= datetime('now', '-{} hours')
    """.format(hours))
    rows = cursor.fetchall()
    conn.close()
    
    # Simple word frequency (skip common words)
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                 "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
                 "this", "that", "these", "those", "it", "its", "new", "how", "what",
                 "why", "when", "where", "who", "can", "will", "your", "you", "our"}
    
    word_freq = {}
    for row in rows:
        text = (row["title"] + " " + row["summary"]).lower()
        words = text.split()
        for w in words:
            w = w.strip(".,!?;:\"'()[]")
            if len(w) > 3 and w not in stopwords:
                word_freq[w] = word_freq.get(w, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [{"keyword": w, "count": c} for w, c in sorted_words[:limit]]

def generate_rss_report(days: int = 7) -> str:
    """Generate RSS intelligence report"""
    hours = days * 24
    
    articles = get_articles(limit=50, hours=hours)
    sources = get_top_sources(hours=hours)
    sentiment = get_sentiment_breakdown(hours=hours)
    trending = get_trending_topics(hours=hours)
    
    report = f"RSS Intelligence Report (Last {days} days)\n"
    report += "=" * 45 + "\n\n"
    
    # Stats
    report += f"Total Articles: {len(articles)}\n"
    report += f"Sentiment: "
    for s, c in sentiment.items():
        report += f"{s}={c} "
    report += "\n\n"
    
    # Top sources
    if sources:
        report += "Top Sources:\n"
        for s in sources[:5]:
            report += f"  {s['source']}: {s['count']} articles (relevance: {s['avg_relevance']:.2f})\n"
        report += "\n"
    
    # Trending topics
    if trending:
        report += "Trending Topics:\n  "
        report += ", ".join([f"{t['keyword']} ({t['count']})" for t in trending[:8]])
        report += "\n\n"
    
    # Top articles
    if articles:
        report += "Top Articles by Relevance:\n"
        for a in articles[:10]:
            title = a["title"][:60] + "..." if len(a["title"]) > 60 else a["title"]
            report += f"  [{a['sentiment'][:3]}] {title}\n"
            report += f"    Source: {a['source']}\n"
    
    return report

# Initialize on import
init_db()

if __name__ == "__main__":
    print(f"RSS Database: {DB_PATH}")
    
    # Test
    feeds = get_all_feeds()
    print(f"Feeds tracked: {len(feeds)}")
    
    articles = get_articles(limit=5)
    print(f"Articles in DB: {len(articles)}")
    
    print("\n" + "=" * 45)
    print(generate_rss_report(days=7))
