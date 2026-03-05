# Data Schema Documentation

## Dianping Restaurant Schema

```python
@dataclass
class DianpingRestaurant:
    name: str              # Restaurant name
    rating: float          # 0-5 scale
    review_count: int      # Number of reviews
    price_range: str       # e.g., "¥200-300"
    address: str           # Full address
    tags: List[str]        # User tags, e.g., ["美味", "环境好"]
    url: str              # Dianping URL
```

## Xiaohongshu Post Schema

```python
@dataclass
class XiaohongshuPost:
    restaurant_name: str   # Extracted from post content
    likes: int            # Number of likes
    saves: int            # Number of saves (收藏)
    comments: int         # Number of comments
    sentiment_score: float # -1.0 (negative) to 1.0 (positive)
    keywords: List[str]   # Extracted keywords, e.g., ["好吃", "环境"]
    url: str             # Post URL
```

## Matched Restaurant Schema

```python
@dataclass
class MatchedRestaurant:
    name: str                    # Matched restaurant name
    dianping_data: DianpingRestaurant
    xhs_data: XiaohongshuPost
    similarity_score: float      # 0-1, matching confidence
    consistency_score: float     # 0-1, cross-platform consistency
```

## Recommendation Result Schema

```python
@dataclass
class RecommendationResult:
    restaurant: MatchedRestaurant
    recommendation_score: float  # 0-10, final score
    consistency_level: str       # "高", "中", "低"
```

## Scoring Algorithm

### 1. Engagement Normalization (Xiaohongshu to 0-5 scale)

```
engagement_score = (likes × 1.0) + (saves × 2.0) + (comments × 1.5)
normalized_rating = (engagement_score / (max_expected × 4.5)) × 5
```

### 2. Consistency Score (0-1)

```
rating_correlation = max(0, 1 - (|rating_dp - rating_xhs| / 2))
sentiment_alignment = (sentiment_score + 1) / 2
consistency = (rating_correlation × 0.6) + (sentiment_alignment × 0.4)
```

### 3. Final Recommendation Score (0-10)

```
recommendation = (
    (dianping_rating × 0.4) +
    (xhs_engagement_normalized × 0.3) +
    (consistency × 5 × 0.3)
) × 2
```

## Consistency Levels

- **高 (High)**: Consistency ≥ 0.7
  - Both platforms agree on quality
  - High confidence recommendation

- **中 (Medium)**: Consistency 0.5 - 0.7
  - Generally consistent with minor differences
  - Moderate confidence

- **低 (Low)**: Consistency < 0.5
  - Significant disagreement between platforms
  - Manual review recommended

## Data Quality Thresholds

| Metric | Minimum | Rationale |
|--------|---------|-----------|
| Dianping rating | 4.0/5.0 | Filter out low-rated restaurants |
| Dianping reviews | 50 | Ensure statistically significant data |
| Xiaohongshu notes | 20 | Minimum social proof |
| Name similarity | 0.7 | Confident fuzzy match threshold |
