"""
Sentiment Analyzer -- news and social media sentiment analysis.

Scrapes crypto news from RSS feeds, CryptoPanic, Reddit, and Twitter,
then scores sentiment using VADER (fast, rule-based) and optionally
FinBERT (transformer-based, more accurate). Aggregates scores per asset
and generates trading signals based on extreme sentiment shifts.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("crypto-trader.sentiment")


class SentimentAnalyzer:
    """Multi-source crypto sentiment analyzer."""

    def __init__(self) -> None:
        self._vader = None
        self._cryptopanic_key = os.environ.get("CRYPTOPANIC_API_KEY", "")
        self._twitter_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
        self._reddit_client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self._reddit_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        self._reddit_agent = os.environ.get("REDDIT_USER_AGENT", "crypto-trader-skill/1.0")

        self._init_vader()

    def _init_vader(self) -> None:
        """Initialize VADER sentiment analyzer."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._vader = SentimentIntensityAnalyzer()
        except ImportError:
            logger.warning("vaderSentiment not installed. Sentiment scoring limited.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, symbol: str) -> Dict[str, Any]:
        """Run full sentiment analysis for a cryptocurrency symbol.

        Returns aggregated sentiment with breakdown by source.
        """
        results: Dict[str, Any] = {
            "status": "ok",
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources": {},
            "aggregate": {},
        }

        news_sentiment = self._analyze_news(symbol)
        results["sources"]["news"] = news_sentiment

        reddit_sentiment = self._analyze_reddit(symbol)
        results["sources"]["reddit"] = reddit_sentiment

        twitter_sentiment = self._analyze_twitter(symbol)
        results["sources"]["twitter"] = twitter_sentiment

        cryptopanic_sentiment = self._analyze_cryptopanic(symbol)
        results["sources"]["cryptopanic"] = cryptopanic_sentiment

        results["aggregate"] = self._aggregate_scores(results["sources"])

        return results

    def get_quick_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Fast sentiment check using only news RSS (no API keys needed)."""
        news = self._analyze_news(symbol)
        return {
            "symbol": symbol,
            "score": news.get("avg_score", 0),
            "label": news.get("label", "neutral"),
            "articles_analyzed": news.get("count", 0),
        }

    # ------------------------------------------------------------------
    # News RSS Feeds
    # ------------------------------------------------------------------

    def _analyze_news(self, symbol: str) -> Dict[str, Any]:
        """Analyze crypto news RSS feeds for sentiment."""
        feeds = [
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cryptonews.com/news/feed/",
        ]

        articles: List[Dict[str, Any]] = []

        try:
            import feedparser
        except ImportError:
            return {"error": "feedparser not installed", "count": 0, "avg_score": 0}

        symbol_lower = symbol.lower()
        symbol_names = self._get_symbol_names(symbol)

        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:20]:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    text = f"{title} {summary}"

                    if any(name.lower() in text.lower() for name in symbol_names):
                        score = self._score_text(text)
                        articles.append({
                            "title": title[:120],
                            "score": score,
                            "source": feed_url.split("//")[1].split("/")[0],
                            "published": entry.get("published", ""),
                        })
            except Exception as exc:
                logger.warning("Failed to parse feed %s: %s", feed_url, exc)

        if not articles:
            return {"count": 0, "avg_score": 0, "label": "neutral", "articles": []}

        avg_score = sum(a["score"] for a in articles) / len(articles)
        label = self._score_to_label(avg_score)

        return {
            "count": len(articles),
            "avg_score": round(avg_score, 4),
            "label": label,
            "articles": articles[:10],
        }

    # ------------------------------------------------------------------
    # CryptoPanic
    # ------------------------------------------------------------------

    def _analyze_cryptopanic(self, symbol: str) -> Dict[str, Any]:
        """Analyze CryptoPanic news for sentiment."""
        if not self._cryptopanic_key:
            return {"error": "CRYPTOPANIC_API_KEY not set", "count": 0, "avg_score": 0}

        try:
            import requests
        except ImportError:
            return {"error": "requests not installed", "count": 0, "avg_score": 0}

        try:
            url = f"https://cryptopanic.com/api/v1/posts/?auth_token={self._cryptopanic_key}&currencies={symbol}&kind=news"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            return {"error": str(exc), "count": 0, "avg_score": 0}

        articles: List[Dict[str, Any]] = []
        for post in data.get("results", [])[:20]:
            title = post.get("title", "")
            score = self._score_text(title)

            votes = post.get("votes", {})
            if votes:
                positive = votes.get("positive", 0) + votes.get("important", 0)
                negative = votes.get("negative", 0) + votes.get("toxic", 0)
                if positive + negative > 0:
                    vote_score = (positive - negative) / (positive + negative)
                    score = (score + vote_score) / 2

            articles.append({
                "title": title[:120],
                "score": round(score, 4),
                "source": post.get("source", {}).get("title", "unknown"),
            })

        avg_score = sum(a["score"] for a in articles) / len(articles) if articles else 0
        return {
            "count": len(articles),
            "avg_score": round(avg_score, 4),
            "label": self._score_to_label(avg_score),
            "articles": articles[:10],
        }

    # ------------------------------------------------------------------
    # Reddit
    # ------------------------------------------------------------------

    def _analyze_reddit(self, symbol: str) -> Dict[str, Any]:
        """Analyze Reddit posts for sentiment."""
        if not self._reddit_client_id or not self._reddit_secret:
            return {"error": "Reddit API credentials not set", "count": 0, "avg_score": 0}

        try:
            import praw
        except ImportError:
            return {"error": "praw not installed", "count": 0, "avg_score": 0}

        try:
            reddit = praw.Reddit(
                client_id=self._reddit_client_id,
                client_secret=self._reddit_secret,
                user_agent=self._reddit_agent,
            )

            subreddits = ["cryptocurrency", "bitcoin", "ethtrader", "CryptoMarkets"]
            symbol_names = self._get_symbol_names(symbol)
            posts: List[Dict[str, Any]] = []

            for sub_name in subreddits:
                try:
                    subreddit = reddit.subreddit(sub_name)
                    for post in subreddit.hot(limit=25):
                        text = f"{post.title} {post.selftext[:500]}"
                        if any(name.lower() in text.lower() for name in symbol_names):
                            score = self._score_text(text)
                            upvote_ratio = getattr(post, "upvote_ratio", 0.5)
                            adjusted_score = score * (0.5 + upvote_ratio)

                            posts.append({
                                "title": post.title[:120],
                                "score": round(adjusted_score, 4),
                                "subreddit": sub_name,
                                "upvotes": getattr(post, "score", 0),
                            })
                except Exception as exc:
                    logger.warning("Failed to fetch r/%s: %s", sub_name, exc)

            avg_score = sum(p["score"] for p in posts) / len(posts) if posts else 0
            return {
                "count": len(posts),
                "avg_score": round(avg_score, 4),
                "label": self._score_to_label(avg_score),
                "posts": posts[:10],
            }
        except Exception as exc:
            return {"error": str(exc), "count": 0, "avg_score": 0}

    # ------------------------------------------------------------------
    # Twitter
    # ------------------------------------------------------------------

    def _analyze_twitter(self, symbol: str) -> Dict[str, Any]:
        """Analyze recent tweets for sentiment."""
        if not self._twitter_token:
            return {"error": "TWITTER_BEARER_TOKEN not set", "count": 0, "avg_score": 0}

        try:
            import requests
        except ImportError:
            return {"error": "requests not installed", "count": 0, "avg_score": 0}

        symbol_names = self._get_symbol_names(symbol)
        query = " OR ".join(f'"{name}"' for name in symbol_names[:3])
        query += " -is:retweet lang:en"

        try:
            headers = {"Authorization": f"Bearer {self._twitter_token}"}
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                "query": query,
                "max_results": 50,
                "tweet.fields": "public_metrics,created_at",
            }
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            return {"error": str(exc), "count": 0, "avg_score": 0}

        tweets: List[Dict[str, Any]] = []
        for tweet in data.get("data", []):
            text = tweet.get("text", "")
            score = self._score_text(text)

            metrics = tweet.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            retweets = metrics.get("retweet_count", 0)
            engagement = likes + retweets
            if engagement > 10:
                score *= 1.2

            tweets.append({
                "text": text[:120],
                "score": round(score, 4),
                "engagement": engagement,
            })

        avg_score = sum(t["score"] for t in tweets) / len(tweets) if tweets else 0
        return {
            "count": len(tweets),
            "avg_score": round(avg_score, 4),
            "label": self._score_to_label(avg_score),
            "tweets": tweets[:10],
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_text(self, text: str) -> float:
        """Score text sentiment using VADER. Returns -1.0 to 1.0."""
        if self._vader is None:
            return 0.0

        scores = self._vader.polarity_scores(text)
        return scores.get("compound", 0.0)

    @staticmethod
    def _score_to_label(score: float) -> str:
        """Convert a numeric score to a human-readable label."""
        if score >= 0.3:
            return "very_bullish"
        elif score >= 0.1:
            return "bullish"
        elif score <= -0.3:
            return "very_bearish"
        elif score <= -0.1:
            return "bearish"
        return "neutral"

    @staticmethod
    def _get_symbol_names(symbol: str) -> List[str]:
        """Map a ticker symbol to searchable names."""
        name_map = {
            "BTC": ["Bitcoin", "BTC", "#Bitcoin"],
            "ETH": ["Ethereum", "ETH", "#Ethereum"],
            "SOL": ["Solana", "SOL", "#Solana"],
            "XRP": ["Ripple", "XRP", "#XRP"],
            "ADA": ["Cardano", "ADA", "#Cardano"],
            "DOGE": ["Dogecoin", "DOGE", "#Dogecoin"],
            "DOT": ["Polkadot", "DOT", "#Polkadot"],
            "AVAX": ["Avalanche", "AVAX", "#Avalanche"],
            "LINK": ["Chainlink", "LINK", "#Chainlink"],
            "MATIC": ["Polygon", "MATIC", "#Polygon"],
        }
        clean_symbol = symbol.upper().split("/")[0]
        return name_map.get(clean_symbol, [clean_symbol])

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    @staticmethod
    def _aggregate_scores(sources: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate sentiment scores from all sources."""
        weights = {
            "news": 0.30,
            "cryptopanic": 0.25,
            "reddit": 0.25,
            "twitter": 0.20,
        }

        total_weight = 0.0
        weighted_sum = 0.0
        total_count = 0

        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and "avg_score" in source_data:
                count = source_data.get("count", 0)
                if count > 0:
                    weight = weights.get(source_name, 0.1)
                    weighted_sum += source_data["avg_score"] * weight
                    total_weight += weight
                    total_count += count

        if total_weight > 0:
            aggregate_score = weighted_sum / total_weight
        else:
            aggregate_score = 0.0

        label = "neutral"
        if aggregate_score >= 0.3:
            label = "very_bullish"
        elif aggregate_score >= 0.1:
            label = "bullish"
        elif aggregate_score <= -0.3:
            label = "very_bearish"
        elif aggregate_score <= -0.1:
            label = "bearish"

        return {
            "score": round(aggregate_score, 4),
            "label": label,
            "total_items_analyzed": total_count,
            "confidence": "high" if total_count > 20 else "medium" if total_count > 5 else "low",
        }
