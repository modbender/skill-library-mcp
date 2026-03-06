"""Main script for cross-referencing restaurant reviews from multiple platforms."""

import sys
from typing import List, Dict

from config import DEFAULT_THRESHOLDS
from fetch_dianping import fetch_dianping
from fetch_xiaohongshu import fetch_xiaohongshu
from match_restaurants import match_and_score
from crosscheck_base import CrossCheckBase, RecommendationResult


class RestaurantCrossChecker(CrossCheckBase):
    """Cross-reference restaurant data from multiple platforms."""

    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or DEFAULT_THRESHOLDS

    def search(self, location: str, cuisine: str) -> List[RecommendationResult]:
        """
        Search and cross-reference restaurants.

        Args:
            location: Geographic area (e.g., "上海静安区")
            cuisine: Cuisine type (e.g., "日式料理")

        Returns:
            List of recommendation results sorted by score
        """
        print(f"\n🔍 开始搜索: {location} - {cuisine}\n")

        # Fetch data from both platforms
        dp_restaurants = fetch_dianping(location, cuisine, self.config)
        xhs_posts = fetch_xiaohongshu(location, cuisine, self.config)

        print(f"✅ 大众点评: 找到 {len(dp_restaurants)} 家餐厅")
        print(f"✅ 小红书: 找到 {len(xhs_posts)} 家餐厅\n")

        if not dp_restaurants or not xhs_posts:
            print("⚠️ 数据不足，无法进行交叉验证")
            return []

        # Match restaurants across platforms
        matches = match_and_score(dp_restaurants, xhs_posts, self.config)

        print(f"🔗 匹配成功: {len(matches)} 家餐厅\n")

        return self.build_results(matches)


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python crosscheck.py <location> <cuisine>")
        print("Example: python crosscheck.py '上海静安区' '日式料理'")
        sys.exit(1)

    location = sys.argv[1]
    cuisine = sys.argv[2]

    checker = RestaurantCrossChecker()
    results = checker.search(location, cuisine)
    output = checker.format_output(results, location, cuisine)

    print(output)


if __name__ == "__main__":
    main()
