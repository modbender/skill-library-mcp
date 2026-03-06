---
name: reddit-topic-insight
description: 输入研究主题，自动采集 Reddit 讨论，提炼爆款角度，产出 X 推文、小红书笔记、公众号文章三平台成品。7 步流水线：需求收集 → 关键词设计 → 数据采集 → 详情获取 → 角度规划 → 成品生产 → 合并输出。
---

# Reddit 主题洞察 Skill

从 Reddit 社区讨论中挖掘爆款内容角度，自动产出三平台（X / 小红书 / 公众号）成品内容。

## 触发条件

当用户：
- 提及「Reddit 研究」「Reddit 洞察」「Reddit 话题」
- 想从 Reddit 挖掘内容角度或爆款灵感
- 需要基于 Reddit 讨论产出多平台内容
- 使用类似「分析 Reddit 上关于 XX 的讨论」的表述

## 设计原则

| 原则 | 说明 |
|------|------|
| 确定性 → 脚本 | 数据采集、排序去重、内容合并等确定性操作使用 Python 脚本 |
| 创造性 → AI | 关键词设计、角度规划、内容创作等创造性操作由 AI SubAgent 完成 |
| 上下文隔离 | SubAgent 只接收必要信息、只返回极简结果 |
| 主 Agent 保护 | 主 Agent 不读 piece 文件，避免上下文膨胀 |
| 断点恢复 | `progress.json` 记录流水线进度，支持随时中断恢复 |

## 7 步流水线

```
┌─────────────────────────────────────────────────────┐
│  Step 1: 需求收集                                    │
│  初始化运行目录 + progress.json 断点恢复               │
├─────────────────────────────────────────────────────┤
│  Step 2: 关键词设计                    [AI 创造性]     │
│  5 个英文关键词：核心/同义/教程/经验/痛点               │
├─────────────────────────────────────────────────────┤
│  Step 3: 数据采集                      [Python 脚本]  │
│  reddit_collector.py → posts_raw.json               │
├─────────────────────────────────────────────────────┤
│  Step 4: 详情获取                      [Python 脚本]  │
│  reddit_detail_fetcher.py → posts_detail.json       │
├─────────────────────────────────────────────────────┤
│  Step 5: 角度规划                      [AI 创造性]     │
│  单 SubAgent → 10 个角度 × 10 种文章类型              │
├─────────────────────────────────────────────────────┤
│  Step 6: 成品生产                      [AI 创造性]     │
│  5 SubAgent × 3 轮（2+2+1）并行                      │
│  每角度 → X 推文 + 小红书笔记 + 公众号文章             │
├─────────────────────────────────────────────────────┤
│  Step 7: 合并输出                      [Python 脚本]  │
│  content_merger.py → content.md + 来源表格            │
└─────────────────────────────────────────────────────┘
```

## 执行流程

### Step 1: 需求收集
详见 [step-1-requirement.md](workflow/step-1-requirement.md)

1. 检查运行目录下是否存在 `progress.json`
2. 若存在：读取进度，从中断步骤恢复
3. 若不存在：向用户确认研究主题和目标受众
4. 创建 `runs/<topic-slug>/` 目录
5. 初始化 `progress.json`

### Step 2: 关键词设计
详见 [step-2-keywords.md](workflow/step-2-keywords.md)

AI 生成 5 个英文搜索关键词，覆盖：
- 🎯 核心词（锚定词，必须保留）
- 🔄 同义词 / 近义词
- 📚 教程 / How-to 类
- 💡 经验 / 最佳实践类
- 😫 痛点 / 问题类

输出 → `keywords.json`

### Step 3: 数据采集
详见 [step-3-collect.md](workflow/step-3-collect.md)

```bash
python3 scripts/python/reddit_collector.py \
  --keywords-file runs/<slug>/keywords.json \
  --output runs/<slug>/posts_raw.json \
  --config config/default.json
```

### Step 4: 详情获取
详见 [step-4-details.md](workflow/step-4-details.md)

```bash
python3 scripts/python/reddit_detail_fetcher.py \
  --input runs/<slug>/posts_raw.json \
  --output runs/<slug>/posts_detail.json \
  --config config/default.json
```

### Step 5: 角度规划
详见 [step-5-angles.md](workflow/step-5-angles.md)

单 SubAgent 读取帖子摘要 → 规划 10 个不重复角度 → 匹配文章类型 → `angles.json`

### Step 6: 成品生产
详见 [step-6-produce.md](workflow/step-6-produce.md)

5 个 SubAgent 分 3 轮并行（2+2+1），每角度产出三平台成品 → `pieces/angle-{n}.md`

### Step 7: 合并输出
详见 [step-7-merge.md](workflow/step-7-merge.md)

```bash
python3 scripts/python/content_merger.py \
  --pieces-dir runs/<slug>/pieces \
  --posts-file runs/<slug>/posts_detail.json \
  --output runs/<slug>/content.md
```

## 运行目录结构

每次运行产生以下文件：
```
runs/<topic-slug>/
├── progress.json         # 流水线进度
├── keywords.json         # 5 个关键词
├── posts_raw.json        # 原始帖子列表
├── posts_detail.json     # 帖子详情 + 评论
├── angles.json           # 10 个角度规划
├── pieces/               # 各角度成品
│   ├── angle-01.md
│   ├── angle-02.md
│   └── ...
└── content.md            # 最终合并输出
```

## 配置

默认配置文件：`config/default.json`

可选环境变量（用于 Reddit API 认证，提高速率限制）：
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

## 脚本依赖

仅需 `requests` 库：
```bash
pip install requests
```

## 参考模板

- [10 种文章类型](reference/article-types.md)
- [X 推文模板](reference/x-tweet-template.md)
- [小红书笔记模板](reference/xiaohongshu-template.md)
- [公众号文章模板](reference/wechat-template.md)
