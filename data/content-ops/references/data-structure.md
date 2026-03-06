# Content Ops System - Data Structure

## 概念区分

### 信息源账号 (Source Accounts)
- **用途**: 抓取内容作为语料
- **需要**: 登录态才能访问
- **示例**: 小红书（需要登录后才能搜索浏览）
- **存储**: `accounts/source-平台-账号名.md`

### 被运营账号 (Target Accounts)
- **用途**: 发布内容、数据分析
- **需要**: API 或自动化发布
- **示例**: Reddit, Pinterest, Discord
- **存储**: `accounts/target-平台-账号名.md`

## 目录结构

```
content-ops-workspace/
├── accounts/                    # 账号管理
│   ├── source-xiaohongshu-账号名.md      # 信息源：小红书抓取账号
│   ├── target-reddit-账号名.md           # 发布目标：Reddit账号
│   └── target-pinterest-账号名.md        # 发布目标：Pinterest账号
├── strategies/                  # 运营策略
│   ├── target-reddit-账号名-strategy.md  # Reddit账号的运营策略
│   ├── target-pinterest-账号名-strategy.md
│   └── global-strategy.md       # 全局策略（跨平台内容规划）
├── corpus/                      # 语料库
│   ├── raw/                     # 原始抓取内容
│   │   └── 来源平台-日期-主题.md
│   ├── curated/                 # 人工确认后的语料
│   │   └── 主题名.md
│   └── published/               # 已发布内容
│       └── 目标平台-账号名-日期-标题.md
├── schedules/                   # 发布计划
│   └── YYYY-MM-发布计划.md
├── reports/                     # 数据报告
│   └── YYYY-MM-DD-目标平台-账号名-report.md
└── sessions/                    # 登录会话状态
    └── xiaohongshu-session.json # 小红书登录态存储
```

## 文件格式规范

### 信息源账号档案 (accounts/source-平台-账号名.md)
```yaml
---
account_type: source
platform: xiaohongshu
account_name: 账号名
account_id: xxx
login_status: active  # active / expired / needs_verification
last_login: 2024-01-15T10:00:00
---

# 小红书抓取账号

## 登录信息
- **账号**: xxx
- **状态**: 已登录
- **登录时间**: 2024-01-15

## 抓取限制
- 每日抓取限额: 100条笔记
- 当前已用: 0条

## 抓取历史
| 日期 | 主题 | 抓取数量 | 状态 |
|------|------|----------|------|
| 2024-01-15 | 穿搭 | 20 | 成功 |
```

### 被运营账号档案 (accounts/target-平台-账号名.md)
```yaml
---
account_type: target
platform: reddit
account_name: 账号名
account_id: xxx
homepage_url: https://www.reddit.com/user/xxx
api_config:
  client_id: xxx
  client_secret: xxx
  refresh_token: xxx
created_at: 2024-01-01
status: active
---

# Reddit 运营账号

## 账号信息
- **定位**: xxx
- **目标受众**: xxx
- **内容方向**: xxx
- **主要Subreddit**: r/xxx, r/yyy

## 运营数据追踪
### 2024-01
- Karma: 100 → 500 (+400)
- Posts: 10
- Comments: 50

## 关联策略文件
- [运营策略](../strategies/target-reddit-账号名-strategy.md)

## 已发布内容索引
- [2024-01-15-标题](../corpus/published/target-reddit-账号名-20240115-标题.md)
```

### 语料文件 (corpus/raw/ 和 corpus/curated/)
```yaml
---
topic: 主题名
source_platform: xiaohongshu
source_account: source-xiaohongshu-抓取账号名  # 记录是哪个账号抓取的
query_list:
  - 关键词1
  - 关键词2
crawled_at: 2024-01-15
curated: false  # 人工确认后为 true
curated_by: ""  # 确认人
---

# 抓取结果: {topic}

> 来源平台: 小红书
> 抓取时间: 2024-01-15
> 搜索Query: {关键词列表}

## 抓取到的内容

### 笔记1
- **标题**: [笔记标题]
- **作者**: [作者名]
- **链接**: https://www.xiaohongshu.com/explore/xxx
- **点赞数**: 1000
- **收藏数**: 500
- **内容摘要**: [内容文字摘要]
- **标签**: #标签1 #标签2
- **原图**: [图片链接，如有]

### 笔记2
...

---

## 人工确认区

- [ ] 内容1已审核 - 质量: [高/中/低] - 是否可用: [是/否] - 确认人: [名字]
- [ ] 内容2已审核 - 质量: [高/中/低] - 是否可用: [是/否] - 确认人: [名字]

确认后执行:
```bash
python3 scripts/curate_content.py corpus/raw/xiaohongshu-2024-01-15-主题.md
```
```

### 运营策略 (strategies/target-平台-账号名-strategy.md)
```markdown
---
account_type: target
platform: reddit
account: 账号名
created_at: 2024-01-01
updated_at: 2024-01-01
---

# Reddit 账号运营策略

## 账号定位
- **人设**: 
- **目标受众**: 
- **内容调性**: 
- **差异化卖点**: 

## 内容规划

### 发布频率
- 每日发布: 1 篇
- 最佳发布时间: 08:00 UTC (对应目标时区)

### 内容来源策略
- **信息源**: 小红书
- **内容类型**: 图片 + 文字改编
- **改编方向**: 
  - 中文 → 英文翻译
  - 添加文化背景解释
  - 适配 Reddit 社区风格

### 目标Subreddit
| Subreddit | 内容类型 | 频率 | 策略 |
|-----------|----------|------|------|
| r/xxx | 类型A | 每周2篇 | 策略说明 |
| r/yyy | 类型B | 每周1篇 | 策略说明 |

## 内容发布流程
1. 从 `corpus/curated/` 选择语料
2. 翻译/改编内容
3. 生成标题（符合Reddit风格）
4. 选择合适Subreddit
5. 发布并追踪数据

## KPI 目标
- 月度 Karma 增长: [ ] 
- 月度帖子数: [ ]
- 平均帖子得分: [ ]

## 备注
```

### 已发布内容 (corpus/published/target-平台-账号名-日期-标题.md)
```yaml
---
account_type: target
platform: reddit
account: 账号名
source_corpus: 主题名  # 来源语料
published_at: 2024-01-15T12:00:00
post_url: https://www.reddit.com/r/xxx/comments/xxx
target_subreddit: r/xxx
status: published
topics:
  - 主题1
engagement:
  score: 100
  comments: 20
  upvote_ratio: 0.95
---

# 发布内容

## 原文语料
- **来源**: [语料文件路径]
- **原平台**: 小红书
- **原作者**: xxx

## 改编说明
- 翻译策略: 
- 文化适配: 
- 标题优化: 

## 发布内容

### 标题
[Reddit标题]

### 正文
[正文内容]

### 图片
- [图片1描述](assets/xxx.jpg)

## 数据追踪
| 日期 | Score | Comments | Upvote Ratio |
|------|-------|----------|--------------|
| 2024-01-15 | 100 | 20 | 95% |
| 2024-01-16 | 200 | 35 | 94% |
```

### 每日复盘报告 (reports/日期-目标平台-账号名-report.md)
```markdown
# 每日数据复盘

## 账号: 账号名 (Reddit)

### 今日新增数据 (2024-01-15)
- 帖子得分增长: +100
- 新增评论: +15
- Karma增长: +50

### 昨日对比
| 指标 | 昨日 | 今日 | 变化 |
|------|------|------|------|
| 总Karma | 1000 | 1050 | +50 ↑ |
| 帖子数 | 10 | 11 | +1 ↑ |

### 内容表现
| 帖子 | Subreddit | Score | Comments | 趋势 |
|------|-----------|-------|----------|------|
| 帖子1 | r/xxx | 100 | 20 | ↑ |
| 帖子2 | r/yyy | 50 | 10 | → |

### 分析与建议
- 表现最佳: [帖子标题] (高互动率)
- 需要优化: [帖子标题] (得分较低，可能标题不够吸引人)
```

## 工作流程中的账号类型

### 1. 内容抓取流程
```
使用账号: source-xiaohongshu-xxx (信息源)
输出位置: corpus/raw/xiaohongshu-日期-主题.md
```

### 2. 内容发布流程
```
输入语料: corpus/curated/主题.md (来源: 小红书)
使用账号: target-reddit-xxx (发布目标)
输出位置: corpus/published/target-reddit-xxx-日期-标题.md
```

### 3. 数据复盘流程
```
目标账号: target-reddit-xxx
输出位置: reports/日期-target-reddit-xxx-report.md
```

## 多信息源扩展

未来可支持多个信息源：
- `source-xiaohongshu-账号A` - 小红书账号A
- `source-xiaohongshu-账号B` - 小红书账号B  
- `source-douyin-账号C` - 抖音账号
- `source-instagram-账号D` - Instagram账号

每个信息源独立管理登录态和抓取配额。
