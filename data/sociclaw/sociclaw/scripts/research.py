"""
Module for researching trends on X (Twitter) using the X API v2.

This module provides functionality to:
- Connect to X API v2 using tweepy
- Search for posts about specific topics/niches
- Extract engagement metrics
- Identify trending topics and formats
- Determine peak posting hours
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import Counter, defaultdict
import os

try:
    import tweepy
except ImportError:  # pragma: no cover - handled during initialization
    tweepy = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrendData:
    """
    Structured data representing trends discovered from X API research.

    Attributes:
        topics: Top 10 topics currently being discussed
        formats: Most engaging post formats (thread, image, carousel, etc.)
        peak_hours: Hours with highest engagement (in UTC)
        hashtags: Relevant hashtags with high engagement
        sample_posts: Sample posts with high engagement for reference
    """
    topics: List[str] = field(default_factory=list)
    formats: Dict[str, int] = field(default_factory=dict)
    peak_hours: List[int] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    sample_posts: List[Dict[str, Any]] = field(default_factory=list)


class TrendResearcher:
    """
    Research trends on X (Twitter) to inform content generation.

    This class connects to the X API v2 and analyzes posts to identify
    trending topics, formats, optimal posting times, and relevant hashtags.
    """

    def __init__(self, api_key: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize the TrendResearcher with X API credentials.

        Args:
            api_key: X API key (Bearer token). If not provided, reads from
                    XAI_API_KEY environment variable.
            client: Optional tweepy client instance for testing/mocking.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.client = client

        if self.client is None:
            if not self.api_key:
                raise ValueError("XAI_API_KEY must be provided or set in environment")
            if tweepy is None:
                raise ImportError("tweepy is required for trend research")
            # Initialize tweepy client with bearer token
            self.client = tweepy.Client(bearer_token=self.api_key)
        
        # Rate limiting state
        self._last_request_time = 0.0
        self._min_request_interval = 1.0  # 1 second between API requests
        
        logger.info("TrendResearcher initialized successfully")

    async def research_trends(self, topic: str, days: int = 30) -> TrendData:
        """
        Research trends on X for a given topic over the specified time period.

        Args:
            topic: The topic/niche to research (e.g., "crypto", "web3")
            days: Number of days to look back (default: 30)

        Returns:
            TrendData object containing analysis results

        Raises:
            ValueError: If topic is empty or invalid
            tweepy.TweepyException: If API request fails
        """
        # Input validation
        if not topic or not topic.strip():
            raise ValueError("topic cannot be empty")
        topic = topic.strip()[:100]  # Sanitize and limit length
        
        logger.info(f"Starting trend research for topic: {topic}, days: {days}")

        # Calculate start time
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Search for tweets
        posts = await self._search_posts(topic, start_time, end_time)

        # Analyze the posts
        topics = self._identify_topics(posts)
        formats = self._identify_formats(posts)
        peak_hours = self._identify_peak_hours(posts)
        hashtags = self._extract_hashtags(posts)
        sample_posts = self._select_sample_posts(posts)

        trend_data = TrendData(
            topics=topics,
            formats=formats,
            peak_hours=peak_hours,
            hashtags=hashtags,
            sample_posts=sample_posts
        )

        logger.info(f"Trend research completed: {len(topics)} topics, {len(hashtags)} hashtags")
        return trend_data

    async def _search_posts(
        self,
        topic: str,
        start_time: datetime,
        end_time: datetime,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Search for posts about a topic using X API v2.

        Args:
            topic: Search query
            start_time: Start of search window
            end_time: End of search window
            max_results: Maximum number of tweets to retrieve per page

        Returns:
            List of tweet dictionaries with engagement metrics
        """
        posts = []

        try:
            # Rate limiting: ensure minimum interval between requests
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                time.sleep(self._min_request_interval - elapsed)
            self._last_request_time = time.time()
            
            # Search recent tweets with engagement metrics
            # Using search_recent_tweets with tweet.fields for metrics
            response = self.client.search_recent_tweets(
                query=topic,
                start_time=start_time.isoformat() + "Z",
                end_time=end_time.isoformat() + "Z",
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "entities", "referenced_tweets"],
                expansions=["attachments.media_keys"],
                media_fields=["type"]
            )

            if not response.data:
                logger.warning(f"No tweets found for topic: {topic}")
                return posts

            # Process tweets
            for tweet in response.data:
                post_data = {
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                    "engagement": (
                        tweet.public_metrics.get("like_count", 0) +
                        tweet.public_metrics.get("retweet_count", 0) * 2 +
                        tweet.public_metrics.get("reply_count", 0) * 1.5
                    ),
                    "entities": tweet.entities if hasattr(tweet, "entities") else {},
                    "referenced_tweets": tweet.referenced_tweets if hasattr(tweet, "referenced_tweets") else []
                }
                posts.append(post_data)

            # Sort by engagement
            posts.sort(key=lambda x: x["engagement"], reverse=True)
            logger.info(f"Retrieved {len(posts)} posts for analysis")

        except tweepy.TweepyException as e:
            logger.error(f"Error searching posts: {e}")
            raise

        return posts

    def _identify_topics(self, posts: List[Dict], top_n: int = 10) -> List[str]:
        """
        Identify top topics being discussed based on post content.

        Args:
            posts: List of post dictionaries
            top_n: Number of top topics to return

        Returns:
            List of top topic strings
        """
        # Extract keywords from high-engagement posts
        # Simple approach: extract hashtags and common words
        topic_counter = Counter()

        for post in posts[:50]:  # Focus on top 50 posts
            # Extract hashtags as topics
            entities = post.get("entities", {})
            if entities and "hashtags" in entities:
                for tag in entities["hashtags"]:
                    topic_counter[tag["tag"].lower()] += post["engagement"]

        # Get top topics
        top_topics = [topic for topic, _ in topic_counter.most_common(top_n)]
        return top_topics

    def _identify_formats(self, posts: List[Dict]) -> Dict[str, int]:
        """
        Identify the most engaging post formats.

        Args:
            posts: List of post dictionaries

        Returns:
            Dictionary mapping format types to engagement counts
        """
        format_engagement = defaultdict(int)

        for post in posts:
            # Determine format based on tweet characteristics
            referenced = post.get("referenced_tweets", [])
            text = post.get("text", "")
            engagement = post.get("engagement", 0)

            # Thread detection (has replies to same author)
            is_thread = any(ref.get("type") == "replied_to" for ref in referenced)

            # Check if it's a single tweet or has media
            # Note: Full media detection would require checking includes in response
            has_media = "media" in post.get("entities", {})

            if is_thread:
                format_engagement["thread"] += engagement
            elif has_media:
                format_engagement["image"] += engagement
            elif len(text) > 200:
                format_engagement["long_form"] += engagement
            else:
                format_engagement["short_form"] += engagement

        return dict(format_engagement)

    def _identify_peak_hours(self, posts: List[Dict]) -> List[int]:
        """
        Identify peak hours for engagement based on post timestamps.

        Args:
            posts: List of post dictionaries

        Returns:
            List of hour values (0-23 UTC) with highest engagement
        """
        hour_engagement = defaultdict(int)

        for post in posts:
            created_at = post.get("created_at")
            if created_at:
                hour = created_at.hour
                hour_engagement[hour] += post.get("engagement", 0)

        # Get top 3 peak hours
        sorted_hours = sorted(hour_engagement.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, _ in sorted_hours[:3]]

        return sorted(peak_hours)

    def _extract_hashtags(self, posts: List[Dict], top_n: int = 20) -> List[str]:
        """
        Extract the most relevant hashtags with high engagement.

        Args:
            posts: List of post dictionaries
            top_n: Number of top hashtags to return

        Returns:
            List of hashtag strings (without #)
        """
        hashtag_engagement = Counter()

        for post in posts:
            entities = post.get("entities", {})
            if entities and "hashtags" in entities:
                for tag in entities["hashtags"]:
                    hashtag_engagement[tag["tag"]] += post.get("engagement", 0)

        # Get top hashtags
        top_hashtags = [tag for tag, _ in hashtag_engagement.most_common(top_n)]
        return top_hashtags

    def _select_sample_posts(self, posts: List[Dict], count: int = 10) -> List[Dict[str, Any]]:
        """
        Select sample posts with high engagement for reference.

        Args:
            posts: List of post dictionaries
            count: Number of sample posts to return

        Returns:
            List of dictionaries with post text, engagement, and format
        """
        samples = []

        for post in posts[:count]:
            sample = {
                "text": post.get("text", ""),
                "likes": post.get("likes", 0),
                "retweets": post.get("retweets", 0),
                "replies": post.get("replies", 0),
                "engagement": post.get("engagement", 0),
                "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
            }
            samples.append(sample)

        return samples
