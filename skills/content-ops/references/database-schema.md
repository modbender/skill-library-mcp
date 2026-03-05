# Content Ops System - Database Schema

## 表1: 被运营账号表 (target_accounts)

用于管理 Reddit/Pinterest/Discord 等发布目标账号

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| account_type | ENUM | 固定值: 'target' |
| platform | VARCHAR(50) | 平台: reddit, pinterest, discord |
| account_name | VARCHAR(100) | 账号名称/ID |
| account_id | VARCHAR(100) | 平台用户ID |
| homepage_url | TEXT | 主页链接 |
| status | ENUM | active, paused, banned, deleted |
| api_config | JSON | API认证信息(加密存储) |
| positioning | TEXT | 账号定位描述 |
| target_audience | TEXT | 目标受众描述 |
| content_direction | TEXT | 内容方向 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**平台特有字段 (存储在 platform_config JSON中)**

Reddit:
- `default_subreddits`: ["r/xxx", "r/yyy"] - 默认发布社区
- `posting_rules`: 各subreddit的规则摘要

Pinterest:
- `default_boards`: ["board1", "board2"] - 默认画板
- `content_categories`: 内容分类

Discord:
- `webhook_urls`: webhook地址列表
- `channel_mappings`: 频道映射

---

## 表2: 信息源账号表 (source_accounts)

用于管理小红书等抓取源账号

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| account_type | ENUM | 固定值: 'source' |
| platform | VARCHAR(50) | 平台: xiaohongshu, douyin, instagram |
| account_name | VARCHAR(100) | 账号标识名(自定义) |
| login_status | ENUM | active, expired, needs_verification, rate_limited |
| session_data | JSON | 登录会话信息(加密存储) |
| cookies | TEXT | 浏览器cookies(加密存储) |
| daily_quota | INT | 每日抓取限额 |
| quota_used_today | INT | 今日已使用配额 |
| quota_reset_at | TIMESTAMP | 配额重置时间 |
| last_login_at | TIMESTAMP | 最后登录时间 |
| last_crawl_at | TIMESTAMP | 最后抓取时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**抓取配置 (存储在 crawl_config JSON中)**

```json
{
  "search_limit": 50,           // 每次搜索最多抓取条数
  "request_interval": [2, 5],   // 请求间隔范围(秒)
  "retry_times": 3,             // 失败重试次数
  "user_agent": "...",          // 浏览器UA
  "proxy_config": null          // 代理配置
}
```

---

## 表3: 抓取任务表 (crawl_tasks)

管理内容抓取任务的创建、执行、状态追踪

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_name | VARCHAR(200) | 任务名称/主题 |
| source_account_id | UUID | 外键 -> source_accounts.id |
| status | ENUM | pending, running, completed, failed, cancelled |
| query_list | JSON | 搜索关键词列表 |
| target_count | INT | 目标抓取数量 |
| crawled_count | INT | 实际抓取数量 |
| scheduled_at | TIMESTAMP | 计划执行时间 |
| started_at | TIMESTAMP | 实际开始时间 |
| completed_at | TIMESTAMP | 完成时间 |
| created_by | VARCHAR(100) | 创建人 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**任务配置 (存储在 task_config JSON中)**

```json
{
  "filters": {
    "min_likes": 100,        // 最少点赞数
    "min_saves": 50,         // 最少收藏数
    "date_range": "7d",      // 发布时间范围
    "exclude_authors": []    // 排除的作者
  },
  "extract_fields": [        // 需要提取的字段
    "title", "content", "images", "tags", 
    "likes", "saves", "author", "publish_time"
  ]
}
```

---

## 表4: 抓取结果表 (crawl_results)

存储抓取到的原始内容

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_id | UUID | 外键 -> crawl_tasks.id |
| source_account_id | UUID | 外键 -> source_accounts.id |
| platform | VARCHAR(50) | 来源平台 |
| source_url | TEXT | 原始链接 |
| source_id | VARCHAR(100) | 平台内容ID |
| author_name | VARCHAR(100) | 原作者名称 |
| author_id | VARCHAR(100) | 原作者ID |
| title | TEXT | 标题 |
| content | LONGTEXT | 正文内容 |
| content_type | ENUM | text, image, video, mixed |
| media_urls | JSON | 媒体文件URL列表 |
| media_local_paths | JSON | 本地存储路径 |
| tags | JSON | 标签列表 |
| engagement | JSON | 互动数据 {likes, saves, comments, shares} |
| publish_time | TIMESTAMP | 原始发布时间 |
| crawl_time | TIMESTAMP | 抓取时间 |
| curation_status | ENUM | raw, reviewing, approved, rejected, expired |
| curation_notes | TEXT | 人工审核备注 |
| curated_by | VARCHAR(100) | 审核人 |
| curated_at | TIMESTAMP | 审核时间 |
| quality_score | INT | 质量评分(1-10) |
| is_available | BOOLEAN | 是否可用于二次创作 |
| usage_count | INT | 被使用次数 |
| last_used_at | TIMESTAMP | 最后使用时间 |

---

## 表5: 发布任务表 (publish_tasks)

管理内容发布任务的创建、审核、执行

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| task_name | VARCHAR(200) | 任务名称 |
| target_account_id | UUID | 外键 -> target_accounts.id |
| source_corpus_ids | JSON | 使用的语料ID列表 |
| status | ENUM | draft, pending_review, approved, scheduled, publishing, published, failed, cancelled |
| content_type | ENUM | original, translated, adapted, mixed |
| platform_specific | JSON | 平台特定配置 |
| scheduled_at | TIMESTAMP | 计划发布时间 |
| published_at | TIMESTAMP | 实际发布时间 |
| created_by | VARCHAR(100) | 创建人 |
| reviewed_by | VARCHAR(100) | 审核人 |
| reviewed_at | TIMESTAMP | 审核时间 |
| review_notes | TEXT | 审核意见 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**发布内容 (存储在 content JSON中)**

```json
{
  "title": "...",
  "body": "...",
  "media": ["path1", "path2"],
  "tags": ["tag1", "tag2"],
  "platform_specific": {
    "reddit": {
      "subreddit": "r/xxx",
      "flair": "..."
    },
    "pinterest": {
      "board": "...",
      "description": "..."
    }
  }
}
```

**内容改编记录 (存储在 adaptation JSON中)**

```json
{
  "source_platform": "xiaohongshu",
  "adaptation_type": "translation",
  "changes": [
    {"field": "title", "from": "...", "to": "..."},
    {"field": "body", "from": "...", "to": "..."}
  ],
  "cultural_notes": "...",
  "translator": "agent"
}
```

---

## 表6: 发布数据表 (每日) (publish_metrics_daily)

追踪每篇已发布内容的每日数据表现

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| publish_task_id | UUID | 外键 -> publish_tasks.id |
| target_account_id | UUID | 外键 -> target_accounts.id |
| metric_date | DATE | 数据日期 |
| platform | VARCHAR(50) | 平台 |
| post_url | TEXT | 帖子链接 |
| platform_post_id | VARCHAR(100) | 平台帖子ID |

**互动数据 (按平台存储)**

通用字段:
| impressions | INT | 曝光量/浏览量 |
| clicks | INT | 点击量 |
| engagement_rate | DECIMAL | 互动率 |

Reddit 特有:
| score | INT | 帖子得分(upvotes - downvotes) |
| upvotes | INT | 赞成票 |
| downvotes | INT | 反对票 |
| upvote_ratio | DECIMAL | 赞成比例 |
| comments | INT | 评论数 |
| awards | INT | 奖励数 |

Pinterest 特有:
| saves | INT | 保存数 |
| closeups | INT | 点击查看数 |
| outbound_clicks | INT |  outbound点击 |

Discord 特有:
| reactions | JSON | 表情反应统计 |
| replies | INT | 回复数 |

**数据质量**
| is_complete | BOOLEAN | 数据是否完整抓取 |
| fetch_error | TEXT | 抓取错误信息 |
| fetched_at | TIMESTAMP | 数据抓取时间 |
| created_at | TIMESTAMP | 记录创建时间 |

---

## 表7: 被运营账号数据表 (每日) (target_accounts_metrics_daily)

追踪被运营账号的整体每日数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| target_account_id | UUID | 外键 -> target_accounts.id |
| platform | VARCHAR(50) | 平台 |
| metric_date | DATE | 数据日期 |

**账号整体数据**
| followers | INT | 粉丝数 |
| followers_change | INT | 粉丝变化(较昨日) |
| total_posts | INT | 总帖子数 |
| posts_change | INT | 新增帖子数 |
| total_engagement | INT | 总互动数 |
| engagement_change | INT | 互动变化 |

**平台特有KPI**

Reddit:
| total_karma | INT | 总Karma |
| karma_change | INT | Karma变化 |
| link_karma | INT | 链接Karma |
| comment_karma | INT | 评论Karma |

Pinterest:
| monthly_views | INT | 月度浏览量 |
| total_pins | INT | 总Pin数 |
| total_boards | INT | 画板数 |
| followers | INT | 关注者数 |

**内容表现汇总**
| top_post_id | UUID | 当日最佳表现帖子 |
| top_post_engagement | INT | 最佳帖子互动数 |
| avg_post_engagement | DECIMAL | 平均帖子互动 |

**计算指标**
| growth_rate | DECIMAL | 增长率 |
| engagement_rate | DECIMAL | 互动率 |
| posting_consistency | DECIMAL | 发布一致性评分 |

**数据质量**
| is_complete | BOOLEAN | 数据是否完整 |
| fetch_error | TEXT | 抓取错误 |
| fetched_at | TIMESTAMP | 数据抓取时间 |
| created_at | TIMESTAMP | 记录创建时间 |

---

## 关联关系图

```
┌─────────────────┐     ┌─────────────────┐
│ source_accounts │     │ target_accounts │
│   (信息源账号)    │     │   (被运营账号)   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │ 1:N                   │ 1:N
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  crawl_tasks    │     │ publish_tasks   │
│   (抓取任务)      │     │   (发布任务)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │ 1:N                   │ 1:1
         ▼                       ▼
┌─────────────────┐     ┌─────────────────────────┐
│ crawl_results   │     │ publish_metrics_daily   │
│   (抓取结果)      │     │   (发布内容每日数据)      │
└─────────────────┘     └─────────────────────────┘
                                  │
                                  │ N:1
                                  ▼
                         ┌─────────────────────────┐
                         │ target_accounts_metrics │
                         │   (账号每日数据)          │
                         └─────────────────────────┘
```

---

## 索引建议

```sql
-- 加速查询常用索引
CREATE INDEX idx_crawl_results_status ON crawl_results(curation_status);
CREATE INDEX idx_crawl_results_available ON crawl_results(is_available, quality_score);
CREATE INDEX idx_publish_tasks_status ON publish_tasks(status);
CREATE INDEX idx_publish_tasks_scheduled ON publish_tasks(scheduled_at) WHERE status='scheduled';
CREATE INDEX idx_metrics_date ON publish_metrics_daily(metric_date);
CREATE INDEX idx_metrics_account_date ON target_accounts_metrics_daily(target_account_id, metric_date);
```
