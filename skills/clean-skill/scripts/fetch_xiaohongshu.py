"""Fetch restaurant data from Xiaohongshu (小红书)."""

import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class XiaohongshuPost:
    """Post data from Xiaohongshu."""
    restaurant_name: str
    likes: int
    saves: int
    comments: int
    sentiment_score: float  # -1.0 to 1.0 (negative to positive)
    keywords: List[str]
    url: str


class XiaohongshuFetcher:
    """Fetch restaurant data from Xiaohongshu."""

    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.xiaohongshu.com"
        self.session = requests.Session()
        self._setup_headers()

    def _setup_headers(self):
        """Setup request headers to mimic browser."""
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36',
        ]
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.xiaohongshu.com/',
        })

    def search(self, location: str, cuisine: str, min_notes: int = 20) -> List[XiaohongshuPost]:
        """
        Search for restaurant posts by location and cuisine.

        Args:
            location: Geographic area (e.g., "上海静安区")
            cuisine: Cuisine type (e.g., "日式料理")
            min_notes: Minimum number of notes/posts to include

        Returns:
            List of XiaohongshuPost objects
        """
        # Note: This is a simplified implementation
        # Actual implementation needs to handle:
        # - Cookie authentication (required for most searches)
        # - Anti-scraping measures (very strict)
        # - Dynamic content (JavaScript rendering)
        # - API endpoint discovery
        # - Pagination

        search_query = f"{location} {cuisine}"
        print(f"🔍 Searching Xiaohongshu for: {search_query}")

        # Simulated data for demonstration
        # In production, this would scrape actual Xiaohongshu pages
        posts = self._fetch_mock_data(location, cuisine)

        # Aggregate posts by restaurant name
        aggregated = self._aggregate_by_restaurant(posts)

        # Filter by minimum notes
        filtered = {name: data for name, data in aggregated.items()
                   if len(data['posts']) >= min_notes}

        # Convert to list of aggregated posts
        result = []
        for name, data in filtered.items():
            avg_post = self._aggregate_post_data(data['posts'])
            avg_post.restaurant_name = name
            result.append(avg_post)

        # Rate limiting
        time.sleep(self.config.get('xhs_delay', 3))

        return result

    def _aggregate_by_restaurant(self, posts: List[XiaohongshuPost]) -> Dict[str, Dict]:
        """Group posts by restaurant name."""
        aggregated = {}
        for post in posts:
            if post.restaurant_name not in aggregated:
                aggregated[post.restaurant_name] = {'posts': []}
            aggregated[post.restaurant_name]['posts'].append(post)
        return aggregated

    def _aggregate_post_data(self, posts: List[XiaohongshuPost]) -> XiaohongshuPost:
        """Calculate average metrics from multiple posts."""
        if not posts:
            return XiaohongshuPost(
                restaurant_name="",
                likes=0, saves=0, comments=0,
                sentiment_score=0.0, keywords=[], url=""
            )

        total_posts = len(posts)
        avg_likes = sum(p.likes for p in posts) // total_posts
        avg_saves = sum(p.saves for p in posts) // total_posts
        avg_comments = sum(p.comments for p in posts) // total_posts
        avg_sentiment = sum(p.sentiment_score for p in posts) / total_posts

        # Combine keywords
        all_keywords = []
        for post in posts:
            all_keywords.extend(post.keywords)
        # Get top keywords
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_keywords_list = [kw for kw, count in top_keywords]

        return XiaohongshuPost(
            restaurant_name="",  # Will be set by caller
            likes=avg_likes,
            saves=avg_saves,
            comments=avg_comments,
            sentiment_score=avg_sentiment,
            keywords=top_keywords_list,
            url=posts[0].url  # First post URL
        )

    def _fetch_mock_data(self, location: str, cuisine: str) -> List[XiaohongshuPost]:
        """Generate mock data for testing (replace with actual scraping)."""
        import random

        mock_data = []

        # Restaurant A - Generate 25 mock posts
        for i in range(25):
            mock_data.append(XiaohongshuPost(
                restaurant_name=f"{cuisine}店A",
                likes=random.randint(200, 500),
                saves=random.randint(50, 150),
                comments=random.randint(20, 80),
                sentiment_score=random.uniform(0.6, 0.95),
                keywords=["好吃", "环境", "值得", "正宗", "新鲜"],
                url=f"{self.base_url}/explore/12345{i}"
            ))

        # Restaurant B - Generate 30 mock posts
        for i in range(30):
            mock_data.append(XiaohongshuPost(
                restaurant_name=f"{cuisine}店B",
                likes=random.randint(100, 300),
                saves=random.randint(30, 100),
                comments=random.randint(10, 50),
                sentiment_score=random.uniform(0.5, 0.85),
                keywords=["性价比", "分量", "实惠", "性价比高"],
                url=f"{self.base_url}/explore/67890{i}"
            ))

        return mock_data


def fetch_xiaohongshu(location: str, cuisine: str, config: Dict) -> List[XiaohongshuPost]:
    """Convenience function to fetch Xiaohongshu data."""
    fetcher = XiaohongshuFetcher(config)
    return fetcher.search(location, cuisine)
