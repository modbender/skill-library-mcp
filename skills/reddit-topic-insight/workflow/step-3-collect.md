# Step 3: 数据采集

## 目标
使用 Python 脚本调用 Reddit JSON API，采集与关键词相关的帖子，按热度排序并去重。

## 前置条件
- Step 2 已完成
- `runs/<slug>/keywords.json` 已生成

## 执行命令

```bash
python3 skills/reddit-topic-insight/scripts/python/reddit_collector.py \
  --keywords-file runs/<slug>/keywords.json \
  --output runs/<slug>/posts_raw.json \
  --config skills/reddit-topic-insight/config/default.json
```

## 脚本行为

### 3.1 读取关键词
从 `keywords.json` 提取 5 个关键词。

### 3.2 搜索 Reddit
对每个关键词调用 Reddit 搜索 API：
```
GET https://www.reddit.com/search.json?q={keyword}&sort=relevance&t=year&limit=50
```

- 请求间隔：2 秒（遵守 Reddit 速率限制）
- 携带 User-Agent 头（必须，否则 Reddit 返回 429）

### 3.3 热度计算与排序
对所有帖子按以下公式计算热度分：
```
热度分 = score + num_comments × 2
```

### 3.4 跨关键词去重
以 `post_id` 为主键，合并多个关键词搜索到的重复帖子。
重复帖子只保留一条，但记录其命中的所有关键词。

### 3.5 输出
按热度分降序排列，输出 `posts_raw.json`。

## 输出文件格式

```json
{
  "metadata": {
    "topic": "Cursor IDE",
    "keywords_used": ["Cursor IDE", "Cursor AI code editor", ...],
    "total_searched": 250,
    "total_after_dedup": 187,
    "collected_at": "2025-01-01T00:00:00Z"
  },
  "posts": [
    {
      "post_id": "abc123",
      "title": "Post title",
      "subreddit": "programming",
      "author": "username",
      "url": "https://reddit.com/r/...",
      "score": 1500,
      "num_comments": 230,
      "heat_score": 1960,
      "created_utc": 1700000000,
      "selftext_preview": "前 200 字...",
      "matched_keywords": ["Cursor IDE", "Cursor AI code editor"]
    }
  ]
}
```

## 更新 progress.json

Step 3 标记为 `completed`，`current_step` 设为 `4`。

## 错误处理

| 情况 | 处理 |
|------|------|
| 网络超时 | 重试 3 次，间隔 5 秒 |
| 429 Too Many Requests | 等待 60 秒后重试 |
| 某个关键词无结果 | 跳过，继续下一个关键词 |
| 全部关键词无结果 | 报错退出，提示用户检查关键词 |

## 下一步

→ [Step 4: 详情获取](step-4-details.md)
