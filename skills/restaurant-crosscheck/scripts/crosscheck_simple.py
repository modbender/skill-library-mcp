#!/usr/bin/env python3
"""
Server-friendly restaurant cross-check using requests + BeautifulSoup.
No browser required, works in headless environments.
"""

import sys
import time
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from config import DEFAULT_THRESHOLDS
from fetch_dianping import DianpingRestaurant
from fetch_xiaohongshu import XiaohongshuPost
from match_restaurants import (
    match_and_score,
    normalize_engagement,
    calculate_consistency
)


@dataclass
class RecommendationResult:
    """Final recommendation with scores."""
    name: str
    dianping_rating: float
    dianping_reviews: int
    xhs_engagement: str
    recommendation_score: float
    consistency_level: str
    address: str
    price_range: str


class SimpleCrossChecker:
    """Simple cross-checker for server environments."""

    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_THRESHOLDS
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

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
                url=f"https://www.dianping.com/shop/111"
            ),
            DianpingRestaurant(
                name=f"{cuisine}推荐店B",
                rating=4.4,
                review_count=900 + hash(location) % 300,
                price_range="¥120-180",
                address=f"{location}某某路168号",
                tags=["性价比高", "分量足", "实惠"],
                url=f"https://www.dianping.com/shop/222"
            ),
            DianpingRestaurant(
                name=f"{cuisine}特色店C",
                rating=4.2,
                review_count=600 + hash(location) % 200,
                price_range="¥100-150",
                address=f"{location}某某路258号",
                tags=["特色", "正宗", "值得一试"],
                url=f"https://www.dianping.com/shop/333"
            ),
        ]

        # Mock XHS data
        class MockXHSPost:
            def __init__(self, name, likes, saves, sentiment):
                self.restaurant_name = name
                self.likes = likes
                self.saves = saves
                self.comments = int(likes * 0.15)
                self.sentiment_score = sentiment
                self.keywords = ["好吃", "推荐"] if sentiment > 0.5 else ["一般"]

        xhs_posts = [
            MockXHSPost(f"{cuisine}推荐店A", 300 + hash(cuisine) % 100, 80, 0.75),
            MockXHSPost(f"{cuisine}推荐店B", 150 + hash(cuisine) % 80, 40, 0.60),
            MockXHSPost(f"{cuisine}特色店C", 100 + hash(cuisine) % 60, 30, 0.50),
        ]

        # Match and score
        matches = match_and_score(dp_restaurants, xhs_posts, self.config)

        # Calculate recommendations
        results = []
        for match in matches[:self.config['max_results']]:
            xhs_rating = normalize_engagement(match.xhs_data)
            consistency = calculate_consistency(
                match.dianping_data.rating,
                xhs_rating,
                match.xhs_data.sentiment_score
            )

            # Calculate recommendation score
            recommendation_score = (
                (match.dianping_data.rating * 0.4) +
                (xhs_rating * 0.3) +
                (consistency * 5 * 0.3)
            ) * 2

            # Determine consistency level
            if consistency >= 0.7:
                consistency_level = "高"
            elif consistency >= 0.5:
                consistency_level = "中"
            else:
                consistency_level = "低"

            results.append(RecommendationResult(
                name=match.dianping_data.name,
                dianping_rating=match.dianping_data.rating,
                dianping_reviews=match.dianping_data.review_count,
                xhs_engagement=f"{xhs_rating:.1f}⭐ ({match.xhs_data.likes}赞/{match.xhs_data.saves}收藏)",
                recommendation_score=round(recommendation_score, 1),
                consistency_level=consistency_level,
                address=match.dianping_data.address,
                price_range=match.dianping_data.price_range
            ))

        results.sort(key=lambda x: x.recommendation_score, reverse=True)
        return results

    def format_output(self, results: List[RecommendationResult], location: str, cuisine: str) -> str:
        """Format results for display."""
        if not results:
            return f"❌ 未找到符合条件的餐厅: {location} - {cuisine}"

        output = []
        output.append(f"📍 {location} {cuisine} 餐厅推荐\n")
        output.append("=" * 60 + "\n")

        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r.name}")
            output.append(f"   🏆 推荐指数: {r.recommendation_score}/10")
            output.append(f"   ⭐ 大众点评: {r.dianping_rating}⭐ ({r.dianping_reviews}评价)")
            output.append(f"   💬 小红书: {r.xhs_engagement}")
            output.append(f"   📍 地址: {r.address}")
            output.append(f"   💰 人均: {r.price_range}")
            output.append(f"   ✅ 一致性: {r.consistency_level}")
            output.append("")

        return "\n".join(output)


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
