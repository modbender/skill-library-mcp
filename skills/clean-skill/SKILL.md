---
name: restaurant-crosscheck-v2
description: Cross-reference restaurant recommendations from Xiaohongshu (小红书) and Dianping (大众点评) to validate restaurant quality and consistency. Use when querying restaurant recommendations by geographic location (city/district) to get validated insights from both platforms. Automatically fetches ratings, review counts, and analyzes consistency across platforms to provide trustworthy recommendations with confidence scores.
---

# Restaurant Review Cross-Check

Cross-reference restaurant data from Xiaohongshu and Dianping to provide validated recommendations.

## Quick Start

Query restaurants by location and cuisine type:

```bash
# Basic query
crosscheck-restaurants "上海静安区" "日式料理"

# With filters
crosscheck-restaurants "北京朝阳区" "火锅" --min-rating 4.5 --min-reviews 100
```

## Workflow

### 1. Data Collection

Query both platforms simultaneously:

**Dianping:**
- Fetch restaurants matching location + cuisine
- Extract: name, rating, review_count, price_range, address, tags

**Xiaohongshu:**
- Search notes/posts matching location + cuisine
- Extract: restaurant_name, engagement_metrics (likes/saves), sentiment_score
- Note: Xiaohongshu data requires scraping as no public API

### 2. Data Matching

Match restaurants across platforms using fuzzy matching:

- Restaurant name similarity (Levenshtein distance)
- Location proximity (address matching)
- Handle name variations (e.g., "银座寿司" vs "银座寿司静安店")

See [scripts/match_restaurants.py](scripts/match_restaurants.py) for matching logic.

### 3. Consistency Analysis

Calculate consistency score based on:

- **Rating correlation** (0-1): Correlation between platform ratings
- **Engagement validation** (0-1): Do high ratings correlate with high engagement?
- **Sentiment alignment** (0-1): Do user sentiments align across platforms?

Formula: `consistency_score = (rating_corr * 0.5) + (engagement_val * 0.3) + (sentiment_align * 0.2)`

### 4. Recommendation Score

Calculate final recommendation score:

```
recommendation_score = (
    (dianping_rating * 0.4) +
    (xhs_engagement_normalized * 0.3) +
    (consistency_score * 0.3)
) * 10
```

Output: 0-10 scale, where >8.0 = high confidence recommendation

## Output Format

```
📍 [Location] [Cuisine Type] 餐厅推荐

1. [Restaurant Name]
   🏆 推荐指数: X.X/10
   ⭐ 大众点评: X.X (Xk评价)
   💬 小红书: X.X⭐ (X笔记)
   📍 地址: [Address]
   💰 人均: ¥[Price]
   ✅ 一致性: [高/中/低] - [Brief explanation]
   
   📊 平台对比:
   - 大众点评标签: [Tags]
   - 小红书热词: [Keywords]
   
   ⚠️ 注意: [Any discrepancies or warnings]

[Continue for top 5-10 restaurants...]
```

## Thresholds

- **Min rating**: 4.0/5.0 (configurable)
- **Min reviews**: 50 on Dianping, 20 notes on Xiaohongshu (configurable)
- **Max results**: Top 10 restaurants by recommendation score
- **High consistency**: Score > 0.7
- **Medium consistency**: Score 0.5-0.7
- **Low consistency**: Score < 0.5 (flag for manual review)

## API & Data Sources

### Dianping
- **Method**: Web scraping (Dianping API requires business partnership)
- **Base URL**: https://www.dianping.com
- **Rate limiting**: 1 request/2 seconds minimum
- **Anti-scraping**: Use residential proxies, rotate user agents

See [scripts/fetch_dianping.py](scripts/fetch_dianping.py) for implementation.

### Xiaohongshu
- **Method**: Web scraping (no public API)
- **Base URL**: https://www.xiaohongshu.com
- **Rate limiting**: 1 request/3 seconds minimum
- **Authentication**: Cookies required for full access

See [scripts/fetch_xiaohongshu.py](scripts/fetch_xiaohongshu.py) for implementation.

## Configuration

Edit `scripts/config.py` to set:

```python
DEFAULT_THRESHOLDS = {
    "min_rating": 4.0,
    "min_dianping_reviews": 50,
    "min_xhs_notes": 20,
    "max_results": 10
}

PROXY_CONFIG = {
    "use_proxy": True,
    "proxy_list": ["http://proxy1:port", "http://proxy2:port"]
}
```

## Error Handling

- **No matches found**: Suggest broader search terms or nearby areas
- **Platform timeout**: Retry with exponential backoff, max 3 attempts
- **Rate limiting detected**: Pause for 60 seconds, rotate proxy
- **Low confidence results**: Flag results with consistency < 0.5 for manual review

## Advanced Features

### Sentiment Analysis
Xiaohongshu posts use NLP to extract:
- Food quality mentions
- Service quality mentions
- Atmosphere mentions
- Price/value mentions

See [references/sentiment_analysis.md](references/sentiment_analysis.md) for methodology.

### Fuzzy Matching
Handle restaurant name variations:
- Chain stores (e.g., "海底捞火锅" vs "海底捞静安店")
- Abbreviations (e.g., "鼎泰丰" vs "鼎泰丰上海店")
- Translation differences

Uses `thefuzz` library for similarity scoring.

## Dependencies

```bash
pip install requests beautifulsoup4 pandas numpy thefuzz selenium lxml
```

See [scripts/requirements.txt](scripts/requirements.txt) for complete list.

## Troubleshooting

**Issue**: Xiaohongshu returns empty results
- **Solution**: Check if cookies expired, re-authenticate

**Issue**: Dianping blocks requests
- **Solution**: Reduce request rate, rotate proxies

**Issue**: Poor matching between platforms
- **Solution**: Adjust similarity threshold in `match_restaurants.py`

## References

- [Data schema documentation](references/data_schema.md)
- [Sentiment analysis guide](references/sentiment_analysis.md)
- [API limitations](references/api_limitations.md)
