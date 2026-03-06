---
name: Instagram Analyzer
description: A comprehensive Instagram profile and post analysis tool with
  engagement metrics, view tracking, and Reels-focused analytics.
---

# Instagram Analyzer

A comprehensive Instagram profile and post analysis tool with engagement metrics, view tracking, and Reels-focused analytics.

```yaml
---
name: instagram-analyzer
description: Analyze Instagram profiles and posts with engagement metrics, view counts, follower ratios, and Reels analytics.
emoji: 📊
version: 1.0.0
author: Sencer
tags:
  - instagram
  - analytics
  - engagement
  - reels
  - influencer
metadata:
  clawdbot:
    requires:
      bins:
        - python3
        - chromium
      pip:
        - playwright
        - beautifulsoup4
        - lxml
    config:
      stateDirs:
        - data/output
        - data/profiles
        - data/posts
      outputFormats:
        - json
        - csv
---
```

## 🎯 Features

### 📊 Single Post Analysis
- ✅ Like count
- ✅ Comment count  
- ✅ Save count
- ✅ View count (Reels)
- ✅ Follower count
- ✅ **View-to-Follower ratio (%)**
- ✅ Time posted (hours/days ago)

### 👤 Profile Analysis
- ✅ Minimum **60 posts** analyzed
- ✅ **Reels-focused** analytics
- ✅ All Reels links extraction
- ✅ Engagement rate calculations
- ✅ JSON/CSV export

### 🔧 Technical
- 🌐 Browser simulation with Playwright
- 🛡️ Stealth mode (human behavior)
- 📁 Structured JSON/CSV output
- ⚡ Batch processing support

---

## 🚀 Usage

### Profile Analysis (Default: Reels Only! 🎯)
```bash
# Full profile analysis - REELS FOCUS (default behavior)
analyze-profile "username"

# With custom post count
analyze-profile "username" --posts 60

# All posts (including regular posts)
analyze-profile "username" --include-posts
```

### Single Post Analysis
```bash
# Analyze a Reel/post URL
analyze-post "https://www.instagram.com/reel/ABC123xyz/"

# With JSON output
analyze-post "https://www.instagram.com/reel/ABC123xyz/" --output json
```

---

## 📊 Output Examples

### Single Post Response
```json
{
  "post_type": "reel",
  "url": "https://www.instagram.com/reel/ABC123xyz/",
  "username": "example_user",
  "metrics": {
    "views": 125000,
    "likes": 8542,
    "comments": 312,
    "saves": 892,
    "followers": 125000,
    "shares": 156
  },
  "ratios": {
    "view_to_follower_percent": 100.0,
    "like_to_view_percent": 6.83,
    "comment_to_view_percent": 0.25,
    "save_to_view_percent": 0.71
  },
  "timing": {
    "posted_at": "2026-02-11T14:30:00",
    "time_ago": "6 hours ago",
    "age_hours": 6
  }
}
```

### Profile Analysis Response
```json
{
  "profile": {
    "username": "example_user",
    "full_name": "Example User",
    "followers": 125000,
    "following": 1500,
    "posts_count": 450,
    "is_verified": false
  },
  "analysis_summary": {
    "total_posts_analyzed": 60,
    "reels_analyzed": 45,
    "analysis_mode": "reels_only",
    "total_views": 5420000,
    "average_views": 120444,
    "average_engagement_rate": 8.2,
    "top_reels": [...],
    "reels_links": [
      "https://www.instagram.com/reel/ABC123/",
      "https://www.instagram.com/reel/DEF456/",
      ...
    ]
  },
  "engagement_breakdown": {
    "avg_likes": 8542,
    "avg_comments": 312,
    "avg_saves": 892,
    "engagement_rate": 7.8
  }
}
```

---

## 📈 Engagement Metrics Explained

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **View Rate** | (Views / Followers) × 100 | How many followers actually watched |
| **Engagement Rate** | ((Likes + Comments + Saves) / Views) × 100 | Overall audience interaction |
| **Like Rate** | (Likes / Views) × 100 | Content appreciation |
| **Save Rate** | (Saves / Views) × 100 | Content value indicator |

---

## ⚙️ Configuration

Edit `config/analyzer_config.json`:

```json
{
  "scraper": {
    "headless": false,
    "min_followers": 1000,
    "posts_to_analyze": 60,
    "scroll_pause": 2,
    "timeout": 30000
  },
  "browser": {
    "stealth_mode": true,
    "human_behavior": true,
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
  },
  "output": {
    "default_format": "json",
    "save_reels_links": true,
    "export_csv": true
  }
}
```

---

## 📁 File Outputs

- **Profile data**: `data/profiles/{username}.json`
- **Post analysis**: `data/posts/{post_id}.json`
- **Batch results**: `data/output/batch_{timestamp}.json`
- **Reels links**: `data/output/{username}_reels.txt`

---

## 🔧 Troubleshooting

### Login Required
- Some metrics require login (view count, saves)
- Configure Instagram credentials in `.env`

### Rate Limiting
- Increase `scroll_pause` in config
- Reduce batch size
- Use multiple accounts

### Missing Data
- Check if account is private
- Verify post exists and is accessible
- Instagram may hide some metrics

---

## 📝 Requirements

- Python 3.8+
- Playwright
- Chromium browser
- BeautifulSoup4
- lxml parser
