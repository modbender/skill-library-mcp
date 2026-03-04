# Step 4: 详情获取

## 目标
获取 Top 10 帖子的完整内容和评论，使用分层采样策略提取高质量评论。

## 前置条件
- Step 3 已完成
- `runs/<slug>/posts_raw.json` 已生成

## 执行命令

```bash
python3 skills/reddit-topic-insight/scripts/python/reddit_detail_fetcher.py \
  --input runs/<slug>/posts_raw.json \
  --output runs/<slug>/posts_detail.json \
  --config skills/reddit-topic-insight/config/default.json
```

## 脚本行为

### 4.1 选取 Top N 帖子
从 `posts_raw.json` 中按 `heat_score` 取前 10 条帖子。

### 4.2 获取帖子详情
对每个帖子请求完整内容：
```
GET https://www.reddit.com/comments/{post_id}.json
```

### 4.3 正文截断
帖子正文（`selftext`）截断到 **3000 字符**。超出部分以 `...（已截断）` 结尾。

### 4.4 评论分层采样

对每个帖子的评论进行三层采样，共采集 **15 条评论**：

| 层级 | 排序方式 | 数量 | 说明 |
|------|---------|------|------|
| 高票评论 | `sort=top` | 8 条 | 社区最认可的观点 |
| 热门评论 | `sort=hot` | 4 条 | 当前热议的内容 |
| 最新评论 | `sort=new` | 3 条 | 最新动态和趋势 |

**去重规则**：跨排序方式以 `comment_id` 去重。若某层采样不足，不补充。

### 4.5 评论截断
每条评论的 `body` 截断到 **200 字符**。

### 4.6 输出
保存到 `posts_detail.json`。

## 输出文件格式

```json
{
  "metadata": {
    "topic": "Cursor IDE",
    "top_n": 10,
    "fetched_at": "2025-01-01T00:00:00Z"
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
      "selftext": "完整正文（最多 3000 字符）...",
      "comments": [
        {
          "comment_id": "xyz789",
          "author": "commenter",
          "body": "评论内容（最多 200 字符）...",
          "score": 450,
          "sampling_layer": "high_vote"
        }
      ]
    }
  ]
}
```

## 更新 progress.json

Step 4 标记为 `completed`，`current_step` 设为 `5`。

## 错误处理

| 情况 | 处理 |
|------|------|
| 帖子已删除 | 跳过，尝试下一个帖子（保证获取 10 条有效帖子） |
| 评论为空 | 标记 `comments: []`，继续 |
| 网络超时 | 重试 3 次，间隔 5 秒 |

## 下一步

→ [Step 5: 角度规划](step-5-angles.md)
