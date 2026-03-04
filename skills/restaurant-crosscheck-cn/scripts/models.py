"""
数据模型 — 整合自原始 fetch_dianping.py / fetch_xiaohongshu.py / crosscheck_base.py
"""
from typing import List
from dataclasses import dataclass, field


@dataclass
class DianpingRestaurant:
    """大众点评餐厅数据（来自原始 fetch_dianping.py）"""
    name: str
    rating: float = 0.0
    review_count: int = 0
    price_range: str = ""
    address: str = ""
    tags: List[str] = field(default_factory=list)
    url: str = ""


@dataclass
class XiaohongshuPost:
    """小红书帖子数据（来自原始 fetch_xiaohongshu.py）"""
    restaurant_name: str
    likes: int = 0
    saves: int = 0
    comments: int = 0
    sentiment_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    url: str = ""
    mention_count: int = 1


@dataclass
class MatchedRestaurant:
    """跨平台匹配结果（来自原始 match_restaurants.py）"""
    name: str
    dianping_data: DianpingRestaurant
    xhs_data: XiaohongshuPost
    similarity_score: float = 0.0
    consistency_score: float = 0.0


@dataclass
class RecommendationResult:
    """最终推荐结果（来自原始 crosscheck_base.py）"""
    name: str
    dianping_rating: float = 0.0
    dianping_reviews: int = 0
    dianping_tags: List[str] = field(default_factory=list)
    dianping_address: str = ""
    dianping_price: str = ""
    xhs_engagement_display: str = ""
    xhs_keywords: List[str] = field(default_factory=list)
    recommendation_score: float = 0.0  # 0-10
    consistency_level: str = ""        # "高", "中", "低"
    consistency_score: float = 0.0     # 0-1
    similarity_score: float = 0.0      # 0-1
