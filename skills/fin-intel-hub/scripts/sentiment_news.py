import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import Counter
import re

@dataclass
class NewsArticle:
    title: str
    description: Optional[str]
    url: str
    published_at: str
    source: str
    sentiment_score: Optional[float] = None

class NewsSentimentClient:
    """Client for financial news sentiment analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with optional NewsAPI key.
        
        Args:
            api_key: NewsAPI key. If None, reads from NEWS_API_KEY env var.
                     If not provided, news features will be unavailable.
                     Get free key at: https://newsapi.org/register
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.has_api_key = bool(self.api_key)
        self.base_url = "https://newsapi.org/v2"
        
        # Simple sentiment word lists (lexicon-based)
        self.positive_words = {
            'surge', 'soar', 'jump', 'rally', 'gain', 'rise', 'boost', 'growth',
            'profit', 'beat', 'exceed', 'strong', 'bullish', 'optimistic',
            'recovery', 'outperform', 'upgrade', 'buy', 'opportunity'
        }
        self.negative_words = {
            'crash', 'plunge', 'drop', 'fall', 'decline', 'loss', 'bearish',
            'miss', 'weak', 'downgrade', 'sell', 'risk', 'concern', 'worry',
            'recession', 'inflation', 'debt', 'crisis', 'fraud', 'investigation'
        }
    
    def get_financial_news(
        self,
        query: Optional[str] = None,
        ticker: Optional[str] = None,
        days: int = 7,
        page_size: int = 20
    ) -> List[NewsArticle]:
        """
        Get financial news articles.
        
        Note: Requires NewsAPI key. Set NEWS_API_KEY environment variable
        or pass api_key to constructor.
        
        Args:
            query: Search query (e.g., "stock market", "inflation")
            ticker: Stock ticker to search for
            days: How many days back to search
            page_size: Number of articles (max 100)
        """
        if not self.has_api_key:
            print("NewsAPI key required for news features. "
                  "Set NEWS_API_KEY environment variable, "
                  "or get free key at: https://newsapi.org/register")
            return []
        
        # Build query
        search_query = query or ""
        if ticker:
            search_query = f"{search_query} {ticker}".strip() if search_query else ticker
        
        # Free tier only supports everything, not specific sources
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/everything"
        params = {
            "q": search_query or "finance OR stock OR market",
            "from": from_date,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(page_size, 100),
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"NewsAPI error: {data.get('message')}")
                return []
            
            articles = []
            for article in data.get("articles", []):
                news = NewsArticle(
                    title=article.get("title", ""),
                    description=article.get("description"),
                    url=article.get("url", ""),
                    published_at=article.get("publishedAt", ""),
                    source=article.get("source", {}).get("name", "Unknown")
                )
                # Calculate sentiment
                news.sentiment_score = self._calculate_sentiment(news.title, news.description)
                articles.append(news)
            
            return articles
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def _calculate_sentiment(self, title: str, description: Optional[str]) -> float:
        """
        Calculate sentiment score (-1 to +1) using simple lexicon.
        
        Returns:
            -1.0 = Very negative
             0.0 = Neutral
            +1.0 = Very positive
        """
        text = f"{title} {description or ''}".lower()
        words = set(re.findall(r'\b\w+\b', text))
        
        pos_count = len(words & self.positive_words)
        neg_count = len(words & self.negative_words)
        total = pos_count + neg_count
        
        if total == 0:
            return 0.0
        
        # Normalize to -1 to +1
        return (pos_count - neg_count) / total
    
    def get_sentiment_summary(
        self,
        ticker: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get aggregated sentiment summary for a ticker or market.
        
        Returns:
            Dictionary with overall sentiment, article counts, key topics
        """
        articles = self.get_financial_news(ticker=ticker, days=days, page_size=50)
        
        if not articles:
            return {
                "ticker": ticker,
                "article_count": 0,
                "average_sentiment": None,
                "sentiment_label": "No data",
                "articles": []
            }
        
        scores = [a.sentiment_score for a in articles if a.sentiment_score is not None]
        avg_sentiment = sum(scores) / len(scores) if scores else 0
        
        # Determine label
        if avg_sentiment > 0.2:
            label = "Bullish"
        elif avg_sentiment < -0.2:
            label = "Bearish"
        else:
            label = "Neutral"
        
        # Extract key topics (simple frequency)
        all_text = " ".join([a.title for a in articles]).lower()
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        common_words = Counter(words).most_common(10)
        
        return {
            "ticker": ticker,
            "article_count": len(articles),
            "average_sentiment": round(avg_sentiment, 3),
            "sentiment_label": label,
            "positive_articles": sum(1 for s in scores if s > 0.1),
            "negative_articles": sum(1 for s in scores if s < -0.1),
            "neutral_articles": sum(1 for s in scores if -0.1 <= s <= 0.1),
            "key_topics": [word for word, count in common_words],
            "latest_headlines": [
                {"title": a.title, "sentiment": a.sentiment_score, "source": a.source}
                for a in articles[:5]
            ],
            "articles": articles
        }


def get_financial_news(
    query: Optional[str] = None,
    ticker: Optional[str] = None,
    days: int = 7
) -> List[Dict]:
    """Convenience function to get news as dicts."""
    client = NewsSentimentClient()
    articles = client.get_financial_news(query, ticker, days)
    return [
        {
            "title": a.title,
            "description": a.description,
            "url": a.url,
            "published_at": a.published_at,
            "source": a.source,
            "sentiment_score": a.sentiment_score
        }
        for a in articles
    ]


def get_sentiment_summary(ticker: Optional[str] = None, days: int = 7) -> Dict:
    """Get sentiment summary for a ticker."""
    client = NewsSentimentClient()
    return client.get_sentiment_summary(ticker, days)


if __name__ == "__main__":
    # Test
    print("Testing news sentiment...")
    
    # This requires NEWS_API_KEY
    summary = get_sentiment_summary(ticker="AAPL", days=3)
    print(f"\nAAPL Sentiment: {summary['sentiment_label']} ({summary['average_sentiment']})")
    print(f"Articles analyzed: {summary['article_count']}")
    print(f"Key topics: {', '.join(summary['key_topics'][:5])}")
