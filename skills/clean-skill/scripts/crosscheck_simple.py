#!/usr/bin/env python3
"""
Server-friendly restaurant cross-check using requests + BeautifulSoup.
No browser required, works in headless environments.
"""

import sys
from typing import List, Dict

from config import DEFAULT_THRESHOLDS
from fetch_dianping import DianpingRestaurant, fetch_dianping
from fetch_xiaohongshu import XiaohongshuPost, fetch_xiaohongshu
from match_restaurants import match_and_score
from crosscheck_base import CrossCheckBase, RecommendationResult


class SimpleCrossChecker(CrossCheckBase):
    """Simple cross-checker for server environments."""

    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or DEFAULT_THRESHOLDS

    def search_mock(self, location: str, cuisine: str) -> List[RecommendationResult]:
        """
        Search using mock data (for testing without real scraping).

        Args:
            location: Geographic area
            cuisine: Cuisine type

        Returns:
            List of recommendation results
        """
        # Generate mock data
        dp_restaurants = [
            DianpingRestaurant(
                name=f"{cuisine}推荐店A",
                rating=4.7,
                review_count=1800 + hash(location) % 500,
                price_range="¥180-250",
                address=f"{location}某某路88号",
                tags=["美味", "环境好", "服务热情"],
                url="https://www.dianping.com/shop/111"
            ),
            DianpingRestaurant(
                name=f"{cuisine}推荐店B",
                rating=4.4,
                review_count=900 + hash(location) % 300,
                price_range="¥120-180",
                address=f"{location}某某路168号",
                tags=["性价比高", "分量足", "实惠"],
                url="https://www.dianping.com/shop/222"
            ),
            DianpingRestaurant(
                name=f"{cuisine}特色店C",
                rating=4.2,
                review_count=600 + hash(location) % 200,
                price_range="¥100-150",
                address=f"{location}某某路258号",
                tags=["特色", "正宗", "值得一试"],
                url="https://www.dianping.com/shop/333"
            ),
        ]

        # Mock XHS data
        xhs_posts = [
            XiaohongshuPost(
                restaurant_name=f"{cuisine}推荐店A",
                likes=300 + hash(cuisine) % 100,
                saves=80,
                comments=45,
                sentiment_score=0.75,
                keywords=["好吃", "推荐", "环境"],
                url="https://www.xiaohongshu.com/explore/111"
            ),
            XiaohongshuPost(
                restaurant_name=f"{cuisine}推荐店B",
                likes=150 + hash(cuisine) % 80,
                saves=40,
                comments=22,
                sentiment_score=0.60,
                keywords=["性价比", "实惠"],
                url="https://www.xiaohongshu.com/explore/222"
            ),
            XiaohongshuPost(
                restaurant_name=f"{cuisine}特色店C",
                likes=100 + hash(cuisine) % 60,
                saves=30,
                comments=15,
                sentiment_score=0.50,
                keywords=["特色", "正宗"],
                url="https://www.xiaohongshu.com/explore/333"
            ),
        ]

        # Match and score
        matches = match_and_score(dp_restaurants, xhs_posts, self.config)

        return self.build_results(matches)


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: crosscheck-simple <location> <cuisine>")
        print("Example: crosscheck-simple '深圳市南山区' '美食'")
        print()
        print("Note: This version uses mock data for server environments.")
        print("For real data, use crosscheck-real.py on a system with browser.")
        sys.exit(1)

    location = sys.argv[1]
    cuisine = sys.argv[2]

    print(f"\n🔍 搜索: {location} - {cuisine}")
    print("⚠️ 使用模拟数据（服务器版本）\n")

    checker = SimpleCrossChecker()
    results = checker.search_mock(location, cuisine)
    output = checker.format_output(results, location, cuisine)

    print(output)


if __name__ == "__main__":
    main()
