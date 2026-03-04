"""
Module for generating quarterly content schedules.

This module provides functionality to:
- Generate quarterly content plans (90 days x 2 posts/day = 180 posts)
- Distribute posts across categories based on frequency rules
- Schedule posts at peak engagement hours
- Integrate trending topics and hashtags
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
import random

from .research import TrendData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PostPlan:
    """
    Plan for a single post to be generated.

    Attributes:
        date: Date when the post should be published
        time: Time (hour in UTC) when the post should be published
        category: Post category (e.g., "market_analysis", "educational")
        topic: Specific topic to cover from trending data
        hashtags: List of hashtags to include in the post
    """
    date: datetime
    time: int
    category: str
    topic: str
    hashtags: List[str] = field(default_factory=list)


class QuarterlyScheduler:
    """
    Generate quarterly content schedules based on trend data.

    This class creates a 90-day content plan with 2 posts per day,
    distributed across different categories and scheduled at peak hours.
    """

    # Category distribution per week (must sum to 14 posts/week for 2 posts/day)
    CATEGORY_DISTRIBUTION = {
        "market_analysis": 3,    # 3x per week
        "educational": 2,        # 2x per week
        "news": 2,              # 2x per week
        "tips": 2,              # 2x per week
        "opinion": 2,           # 2x per week
        "thread": 1,            # 1x per week
        "meme": 2               # 2x per week (14 total)
    }

    # Default peak hours (UTC) if trend data doesn't provide them
    DEFAULT_PEAK_HOURS = [13, 14, 17, 18, 21, 22]

    # Planning horizon presets
    FULL_PLAN_DAYS = 90
    FULL_PLAN_POSTS_PER_DAY = 2
    STARTER_PLAN_DAYS = 14
    STARTER_PLAN_POSTS_PER_DAY = 1

    def __init__(self):
        """Initialize the QuarterlyScheduler."""
        logger.info("QuarterlyScheduler initialized")

    def generate_quarterly_plan(
        self,
        trend_data: TrendData,
        start_date: Optional[datetime] = None,
        *,
        days: Optional[int] = None,
        posts_per_day: Optional[int] = None,
        starter_mode: bool = True,
        avoid_topics: Optional[List[str]] = None,
    ) -> List[PostPlan]:
        """
        Generate a content plan.

        Default behavior is starter-friendly to avoid token/cost frustration for
        first-time users. For the full quarterly plan, call with
        `starter_mode=False` or provide explicit days/posts_per_day values.

        Args:
            trend_data: TrendData object from research module
            start_date: Start date for the plan. If not provided, uses today.
            days: Optional explicit number of days to generate.
            posts_per_day: Optional explicit number of posts per day.
            starter_mode: If True, use a smaller initial plan by default.

        Returns:
            List of PostPlan objects.
        """
        logger.info("Generating content plan...")

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date is None:
            start_date = today_start
        else:
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            allow_past_start = os.getenv("SOCICLAW_ALLOW_PAST_PLAN_START", "").strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }
            if start_date < today_start and not allow_past_start:
                logger.info(
                    "Provided start_date %s is in the past; clamping to today (%s).",
                    start_date.date(),
                    today_start.date(),
                )
                start_date = today_start

        if days is None:
            days = self.STARTER_PLAN_DAYS if starter_mode else self.FULL_PLAN_DAYS
        if posts_per_day is None:
            posts_per_day = self.STARTER_PLAN_POSTS_PER_DAY if starter_mode else self.FULL_PLAN_POSTS_PER_DAY

        days = max(1, int(days))
        posts_per_day = max(1, int(posts_per_day))

        # Determine peak hours to use
        peak_hours = self._determine_peak_hours(trend_data)

        # Prepare topics and hashtags pools
        topics_pool = self._prepare_topics_pool(trend_data)
        hashtags_pool = trend_data.hashtags if trend_data.hashtags else []

        # Build the schedule
        post_plans = []
        category_schedule = self._build_weekly_category_schedule()

        total_posts = days * posts_per_day
        for day_index in range(days):
            post_date = start_date + timedelta(days=day_index)

            for post_slot in range(posts_per_day):
                post_index = day_index * posts_per_day + post_slot

                # Select category based on weekly distribution
                category = category_schedule[post_index % len(category_schedule)]

                # Select time from peak hours
                time_index = post_index % len(peak_hours)
                post_time = peak_hours[time_index]

                # Select topic (cycle through pool)
                topic = self._pick_topic(
                    topics_pool=topics_pool,
                    post_index=post_index,
                    avoid_topics=avoid_topics,
                )

                # Select hashtags (3-5 random hashtags)
                num_hashtags = random.randint(3, 5)
                if hashtags_pool:
                    selected_hashtags = random.sample(
                        hashtags_pool,
                        min(num_hashtags, len(hashtags_pool))
                    )
                else:
                    # Default hashtags if none available
                    selected_hashtags = ["Crypto", "Web3", "Blockchain"]

                post_plan = PostPlan(
                    date=post_date,
                    time=post_time,
                    category=category,
                    topic=topic,
                    hashtags=selected_hashtags
                )
                post_plans.append(post_plan)

        if len(post_plans) != total_posts:
            logger.warning(f"Expected {total_posts} posts, generated {len(post_plans)}")

        logger.info(f"Generated {len(post_plans)} posts for quarterly plan")
        return post_plans

    def _pick_topic(
        self,
        topics_pool: List[str],
        post_index: int,
        avoid_topics: Optional[List[str]] = None,
    ) -> str:
        if not topics_pool:
            return "SociClaw update"

        if not avoid_topics:
            return topics_pool[post_index % len(topics_pool)]

        avoid = {t.strip().lower() for t in avoid_topics if t.strip()}
        base_index = post_index % len(topics_pool)
        for offset in range(len(topics_pool)):
            idx = (base_index + offset) % len(topics_pool)
            topic = topics_pool[idx]
            if topic.strip().lower() not in avoid:
                return topic

        return topics_pool[base_index]

    def _determine_peak_hours(self, trend_data: TrendData) -> List[int]:
        """
        Determine which hours to use for posting based on trend data.

        Args:
            trend_data: TrendData object with peak hours

        Returns:
            List of hour values (0-23 UTC)
        """
        if trend_data.peak_hours and len(trend_data.peak_hours) >= 3:
            # Use trend data peak hours, expanded to 6 slots
            # (each peak hour gets both the hour and hour+1 for variety)
            expanded = []
            for hour in trend_data.peak_hours:
                expanded.extend([hour, (hour + 1) % 24])
            return expanded[:6]
        else:
            # Fall back to default peak hours
            logger.warning("Using default peak hours as trend data insufficient")
            return self.DEFAULT_PEAK_HOURS

    def _prepare_topics_pool(self, trend_data: TrendData) -> List[str]:
        """
        Prepare a pool of topics to cycle through.

        Args:
            trend_data: TrendData object with trending topics

        Returns:
            List of topic strings
        """
        if trend_data.topics:
            # Repeat topics to have enough for 180 posts
            # With 10 topics, we need to cycle through them 18 times
            topics = trend_data.topics * 20
        else:
            # Default crypto/web3 topics if no trend data
            logger.warning("No trending topics found, using defaults")
            topics = [
                "Bitcoin", "Ethereum", "DeFi", "NFTs", "Base",
                "Blockchain", "Smart Contracts", "Web3", "Crypto Trading",
                "Altcoins", "Stablecoins", "Layer 2"
            ] * 15

        return topics

    def _build_weekly_category_schedule(self) -> List[str]:
        """
        Build a 14-item schedule that represents the weekly category distribution.

        Returns:
            List of category strings (length 14)
        """
        week_schedule = []
        for category, count in self.CATEGORY_DISTRIBUTION.items():
            week_schedule.extend([category] * count)

        random.shuffle(week_schedule)
        return week_schedule

    def get_plans_by_date(
        self,
        plans: List[PostPlan],
        target_date: datetime
    ) -> List[PostPlan]:
        """
        Get all post plans for a specific date.

        Args:
            plans: List of all PostPlan objects
            target_date: Date to filter by

        Returns:
            List of PostPlan objects for the target date
        """
        target_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return [
            plan for plan in plans
            if plan.date.replace(hour=0, minute=0, second=0, microsecond=0) == target_day
        ]

    def get_plans_by_category(
        self,
        plans: List[PostPlan],
        category: str
    ) -> List[PostPlan]:
        """
        Get all post plans for a specific category.

        Args:
            plans: List of all PostPlan objects
            category: Category to filter by

        Returns:
            List of PostPlan objects for the category
        """
        return [plan for plan in plans if plan.category == category]
