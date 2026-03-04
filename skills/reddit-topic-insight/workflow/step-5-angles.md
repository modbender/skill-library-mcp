# Step 5: 角度规划

## 目标
由单个 SubAgent 统一规划 10 个不重复的内容角度，每个角度匹配一种文章类型。

## 前置条件
- Step 4 已完成
- `runs/<slug>/posts_detail.json` 已生成

## 设计原则

> **为什么用单个 SubAgent？**
> 角度规划需要全局视角：确保 10 个角度互不重复、覆盖多元视角。拆成多个 SubAgent 会导致角度重叠。

## 执行步骤

### 5.1 准备帖子摘要

主 Agent 从 `posts_detail.json` 构建精简摘要（**不传递完整内容，保护上下文**）：

```json
[
  {
    "rank": 1,
    "title": "帖子标题",
    "subreddit": "子版块",
    "heat_score": 1960,
    "selftext_summary": "正文前 300 字符...",
    "top_comments_summary": [
      "高票评论 1 摘要（100 字符）",
      "高票评论 2 摘要（100 字符）",
      "高票评论 3 摘要（100 字符）"
    ]
  }
]
```

### 5.2 调用 SubAgent

使用以下 Prompt 调用 SubAgent：

```
你是一个内容策略专家。基于以下 Reddit 讨论数据，为主题「{topic}」规划 10 个不重复的内容角度。

## 10 种文章类型（必须各用一次）

1. 热点解读    2. 工具测评    3. 经验分享    4. 痛点解决    5. 趋势预测
6. 对比分析    7. 新手指南    8. 深度案例    9. 争议讨论    10. 资源合集

## Reddit 讨论摘要

{posts_summary_json}

## 要求

1. 10 个角度必须互不重复，覆盖不同侧面
2. 每个角度必须匹配一种文章类型（10 种类型各用一次）
3. 每个角度需标明灵感来源（哪几个帖子启发了这个角度）
4. 角度表述要具体，不要空泛（错：「关于 XX 的讨论」；对：「为什么资深开发者正在从 VS Code 转向 Cursor」）
5. 优先选择 Reddit 上热度高、讨论激烈的方向

## 输出格式（严格 JSON）

{
  "angles": [
    {
      "id": 1,
      "angle": "具体角度描述",
      "article_type": "热点解读",
      "inspiration_posts": [1, 3, 7],
      "brief": "30 字以内的一句话概述"
    }
  ]
}
```

### 5.3 保存结果

将 SubAgent 返回的 JSON 保存到 `runs/<slug>/angles.json`。

### 5.4 更新 progress.json

Step 5 标记为 `completed`，`current_step` 设为 `6`。

## 输出文件

`angles.json` 示例：
```json
{
  "topic": "Cursor IDE",
  "angles": [
    {
      "id": 1,
      "angle": "为什么资深开发者正在从 VS Code 转向 Cursor",
      "article_type": "热点解读",
      "inspiration_posts": [1, 3, 7],
      "brief": "VS Code 老用户迁移 Cursor 的真实原因"
    },
    {
      "id": 2,
      "angle": "Cursor vs GitHub Copilot：AI 编程助手终极对决",
      "article_type": "对比分析",
      "inspiration_posts": [2, 5],
      "brief": "两大 AI 编程工具全方位横评"
    }
  ]
}
```

## 下一步

→ [Step 6: 成品生产](step-6-produce.md)
