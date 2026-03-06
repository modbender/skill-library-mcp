#!/usr/bin/env python3
"""Test with high consistency mock data."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from dataclasses import dataclass
from fetch_xiaohongshu import XiaohongshuFetcher, XiaohongshuPost
from fetch_dianping import DianpingFetcher, DianpingRestaurant
from match_restaurants import normalize_engagement, calculate_consistency

# Create high-quality mock data
def create_high_consistency_test():
    """Create test data where platforms agree."""
    
    # High-rated restaurant - both platforms agree
    high_restaurant = DianpingRestaurant(
        name="顶级日式料理",
        rating=4.8,
        review_count=2500,
        price_range="¥300-400",
        address="上海静安区南京西路888号",
        tags=["顶级", "新鲜", "服务好"],
        url="https://www.dianping.com/shop/111"
    )
    
    # High engagement XHS posts for the same restaurant
    high_xhs_posts = []
    for i in range(35):
        high_xhs_posts.append(XiaohongshuPost(
            restaurant_name="顶级日式料理",
            likes=400,  # High engagement
            saves=120,
            comments=60,
            sentiment_score=0.85,  # Very positive
            keywords=["顶级", "新鲜", "服务", "值得"],
            url=f"https://www.xiaohongshu.com/explore/high{i}"
        ))
    
    # Medium-rated restaurant - both platforms agree
    medium_restaurant = DianpingRestaurant(
        name="平价日料店",
        rating=4.2,
        review_count=800,
        price_range="¥100-150",
        address="上海静安区某某路456号",
        tags=["性价比", "实惠"],
        url="https://www.dianping.com/shop/222"
    )
    
    medium_xhs_posts = []
    for i in range(25):
        medium_xhs_posts.append(XiaohongshuPost(
            restaurant_name="平价日料店",
            likes=180,  # Medium engagement
            saves=50,
            comments=25,
            sentiment_score=0.65,  # Moderately positive
            keywords=["性价比", "实惠", "分量"],
            url=f"https://www.xiaohongshu.com/explore/med{i}"
        ))
    
    return [high_restaurant, medium_restaurant], [high_xhs_posts, medium_xhs_posts]

def main():
    print("=" * 70)
    print("高一致性测试案例")
    print("=" * 70)
    print()
    
    dp_restaurants, xhs_posts_lists = create_high_consistency_test()
    
    for i, (dp_restaurant, xhs_posts) in enumerate(zip(dp_restaurants, xhs_posts_lists), 1):
        # Aggregate XHS data
        from fetch_xiaohongshu import XiaohongshuFetcher
        fetcher = XiaohongshuFetcher({})
        aggregated = fetcher._aggregate_by_restaurant(xhs_posts)
        avg_post = fetcher._aggregate_post_data(aggregated[dp_restaurant.name]['posts'])
        
        # Calculate metrics
        xhs_rating = normalize_engagement(avg_post)
        consistency = calculate_consistency(dp_restaurant.rating, xhs_rating, avg_post.sentiment_score)
        
        # Determine consistency level
        if consistency >= 0.7:
            level = "高"
        elif consistency >= 0.5:
            level = "中"
        else:
            level = "低"
        
        print(f"{i}. {dp_restaurant.name}")
        print(f"   大众点评: {dp_restaurant.rating}⭐ ({dp_restaurant.review_count}评价)")
        print(f"   小红书: {xhs_rating:.1f}⭐ (avg {avg_post.likes}赞/{avg_post.saves}收藏)")
        print(f"   一致性: {level} ({consistency:.2f})")
        print(f"   大众点评标签: {', '.join(dp_restaurant.tags)}")
        print(f"   小红书热词: {', '.join(avg_post.keywords)}")
        print()

if __name__ == "__main__":
    main()
