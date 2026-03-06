# Content Ops 数据库使用指南

## 快速开始

### 1. 安装依赖
```bash
cd /home/admin/.openclaw/workspace/skills/content-ops
npm install
```

### 2. 初始化数据库
```bash
# 创建工作目录和数据库文件
npm run db:init

# 生成迁移文件
npm run db:generate

# 执行迁移（创建表结构）
npm run db:migrate
```

### 3. 启动数据管理界面（可选）
```bash
npm run db:studio
```

---

## 表结构速查

### 表1: target_accounts (被运营账号)
**用途**: 管理 Reddit/Pinterest/Discord 等发布目标账号

| 核心字段 | 说明 | 示例值 |
|----------|------|--------|
| platform | 平台名称 | 'reddit', 'pinterest', 'discord' |
| account_name | 账号名称 | 'MyBrandUS' |
| status | 状态 | 'active', 'paused', 'banned' |
| api_config | API密钥(加密) | {client_id, client_secret} |
| positioning | 账号定位 | "分享亚洲时尚穿搭" |

**常用查询**:
```typescript
// 获取所有活跃账号
const accounts = await queries.getActiveTargetAccounts();

// 按平台筛选
const redditAccounts = await queries.getTargetAccountsByPlatform('reddit');
```

---

### 表2: source_accounts (信息源账号)
**用途**: 管理小红书等抓取源账号的登录态和配额

| 核心字段 | 说明 | 示例值 |
|----------|------|--------|
| platform | 平台名称 | 'xiaohongshu', 'douyin' |
| login_status | 登录状态 | 'active', 'expired', 'rate_limited' |
| daily_quota | 每日限额 | 100 |
| quota_used_today | 今日已用 | 50 |
| quota_reset_at | 重置时间 | 2024-01-16 00:00:00 |
| crawl_config | 抓取配置 | {search_limit, request_interval} |

**常用查询**:
```typescript
// 获取有可用配额的账号
const accounts = await queries.getSourceAccountsWithQuota();

// 检查是否需要重新登录
if (account.loginStatus === 'expired') {
  // 触发重新登录流程
}
```

---

### 表3: crawl_tasks (抓取任务)
**用途**: 管理内容抓取任务的创建、调度、执行状态

| 核心字段 | 说明 | 示例值 |
|----------|------|--------|
| task_name | 任务名称 | "春季穿搭-第1批" |
| status | 状态 | 'pending', 'running', 'completed' |
| query_list | 搜索关键词 | ["穿搭", "OOTD", "春季"] |
| target_count | 目标数量 | 50 |
| crawled_count | 已抓取 | 35 |
| scheduled_at | 计划时间 | 2024-01-15 10:00:00 |

**常用查询**:
```typescript
// 获取待执行的任务
const tasks = await queries.getPendingCrawlTasks();

// 查看任务统计
const stats = await queries.getCrawlTaskStats(taskId);
console.log(`已抓取: ${stats.stats.approved}/${stats.task.target_count}`);
```

---

### 表4: crawl_results (抓取结果)
**用途**: 存储抓取到的原始内容，包含完整数据和元信息

| 核心字段 | 说明 | 示例值 |
|----------|------|--------|
| source_url | 原始链接 | "https://xiaohongshu.com/..." |
| title | 标题 | "春季简约穿搭分享" |
| content | 正文 | 完整文字内容 |
| media_urls | 媒体URL | ["https://.../img1.jpg"] |
| engagement | 互动数据 | {likes: 1000, saves: 500} |
| curation_status | 审核状态 | 'raw', 'approved', 'rejected' |
| quality_score | 质量分 | 8 |
| is_available | 可用状态 | true/false |
| usage_count | 使用次数 | 3 |

**常用查询**:
```typescript
// 获取待审核内容
const pending = await queries.getPendingCrawlResults(20);

// 获取可用语料（质量分>7）
const corpus = await queries.getAvailableCorpus('穿搭', 7);

// 搜索语料
const results = await queries.searchCorpus(['春季', '简约']);
```

---

### 表5: publish_tasks (发布任务)
**用途**: 管理内容从草稿到发布的完整流程

| 核心字段 | 说明 | 示例值 |
|----------|------|--------|
| target_account_id | 发布账号 | uuid |
| source_corpus_ids | 来源语料 | ["uuid1", "uuid2"] |
| status | 状态 | 'draft', 'pending_review', 'published' |
| content | 发布内容 | {title, body, media, tags} |
| content_type | 内容类型 | 'translated', 'adapted' |
| scheduled_at | 计划时间 | 2024-01-15 14:00:00 |
| review_notes | 审核意见 | "标题可以更有吸引力" |

**常用查询**:
```typescript
// 获取今日待发布
const tasks = await queries.getTodayScheduledTasks();

// 获取待审核
const pending = await queries.getPendingReviewTasks();

// 获取发布历史
const history = await queries.getAccountPublishHistory(accountId, 10);
```

---

### 表6: publish_metrics_daily (发布内容每日数据)
**用途**: 追踪每篇已发布内容的每日数据表现

| 核心字段 | 说明 | 平台 |
|----------|------|------|
| metric_date | 数据日期 | 通用 |
| impressions | 曝光量 | 通用 |
| reddit_score | 帖子得分 | Reddit |
| reddit_upvotes | 赞成票 | Reddit |
| reddit_comments | 评论数 | Reddit |
| pinterest_saves | 保存数 | Pinterest |
| discord_reactions | 表情反应 | Discord |

**常用查询**:
```typescript
// 查看某篇内容的数据趋势
const metrics = await db.query.publishMetricsDaily.findMany({
  where: eq(publishMetricsDaily.publishTaskId, taskId),
  orderBy: [asc(publishMetricsDaily.metricDate)]
});
```

---

### 表7: target_accounts_metrics_daily (账号每日数据)
**用途**: 追踪被运营账号的整体每日数据表现

| 核心字段 | 说明 | 计算方式 |
|----------|------|----------|
| followers | 粉丝数 | 平台API获取 |
| followers_change | 粉丝变化 | 今日 - 昨日 |
| reddit_total_karma | 总Karma | Reddit特有 |
| reddit_karma_change | Karma变化 | 今日 - 昨日 |
| growth_rate | 增长率 | 变化量 / 昨日基数 |
| engagement_rate | 互动率 | 总互动 / 总曝光 |

**常用查询**:
```typescript
// 获取7天趋势
const trend = await queries.getAccountTrend(accountId, 7);

// 多账号对比
const comparison = await queries.getMultiAccountComparison(
  ['account-uuid-1', 'account-uuid-2'],
  '2024-01-15'
);
```

---

## 常用查询场景

### 场景1: 首页看板数据
```typescript
const stats = await queries.getOverviewStats();
// 返回:
// {
//   activeAccounts: 5,          // 活跃账号数
//   todayScheduledTasks: 3,     // 今日待发布
//   pendingCorpus: 20,          // 待审核语料
//   availableCorpus: 150,       // 可用语料
//   weeklyPublished: 21         // 近7天发布
// }
```

### 场景2: 内容运营周报
```typescript
// 获取上周发布的内容排行
const topContent = await queries.getTopPerformingContent(accountId, 7, 10);

// 获取本周vs上周数据对比
const thisWeek = await queries.getAccountTrend(accountId, 7);
const lastWeek = await queries.getAccountTrend(accountId, 14);
// 计算增长率
```

### 场景3: 语料库管理
```typescript
// 统计各主题语料数量
const topicStats = await db.select({
  topic: sql`json_extract(${crawlResults.tags}, '$[0]')`,
  count: sql<number>`COUNT(*)`,
  avgQuality: sql<number>`AVG(${crawlResults.qualityScore})`
})
.from(crawlResults)
.where(eq(crawlResults.curationStatus, 'approved'))
.groupBy(sql`json_extract(${crawlResults.tags}, '$[0]')`);

// 找出高质量未使用的语料
const unusedHighQuality = await db.query.crawlResults.findMany({
  where: and(
    eq(crawlResults.curationStatus, 'approved'),
    eq(crawlResults.usageCount, 0),
    sql`${crawlResults.qualityScore} >= 8`
  )
});
```

### 场景4: 异常监控
```typescript
// 检查抓取失败率高的任务
const failedTasks = await db.select({
  taskId: crawlTasks.id,
  taskName: crawlTasks.taskName,
  total: sql<number>`COUNT(*)`,
  failed: sql<number>`SUM(CASE WHEN ${crawlResults.curationStatus} = 'rejected' THEN 1 ELSE 0 END)`
})
.from(crawlTasks)
.leftJoin(crawlResults, eq(crawlTasks.id, crawlResults.taskId))
.where(sql`${crawlTasks.createdAt} >= date('now', '-7 days')`)
.groupBy(crawlTasks.id)
.having(sql`failed > total * 0.5`); // 失败率>50%

// 检查长时间未登录的账号
const staleAccounts = await db.query.sourceAccounts.findMany({
  where: sql`${sourceAccounts.lastLoginAt} < date('now', '-7 days')`
});
```

---

## 数据看板SQL示例

### 每日数据汇总
```sql
-- 今日各账号粉丝增长
SELECT 
  t.platform,
  t.account_name,
  m.followers,
  m.followers_change,
  m.growth_rate
FROM target_accounts_metrics_daily m
JOIN target_accounts t ON m.target_account_id = t.id
WHERE m.metric_date = date('now')
ORDER BY m.followers_change DESC;

-- 今日发布内容表现
SELECT 
  pt.task_name,
  t.account_name,
  pm.reddit_score,
  pm.reddit_comments,
  pm.pinterest_saves
FROM publish_tasks pt
JOIN target_accounts t ON pt.target_account_id = t.id
LEFT JOIN publish_metrics_daily pm ON pt.id = pm.publish_task_id
WHERE date(pt.published_at) = date('now')
  AND pt.status = 'published';
```

### 周/月趋势
```sql
-- 近7天发布数量趋势
SELECT 
  date(published_at) as date,
  COUNT(*) as publish_count
FROM publish_tasks
WHERE published_at >= date('now', '-7 days')
  AND status = 'published'
GROUP BY date(published_at)
ORDER BY date;

-- 近30天账号增长趋势
SELECT 
  metric_date,
  SUM(followers_change) as total_growth,
  AVG(growth_rate) as avg_growth_rate
FROM target_accounts_metrics_daily
WHERE metric_date >= date('now', '-30 days')
GROUP BY metric_date
ORDER BY metric_date;
```

---

## 数据维护

### 定期清理（可选）
```typescript
// 清理已拒绝且超过30天的抓取结果
await db.delete(crawlResults)
  .where(and(
    eq(crawlResults.curationStatus, 'rejected'),
    sql`${crawlResults.crawlTime} < date('now', '-30 days')`
  ));

// 归档已发布超过1年的内容数据
// （迁移到历史表或导出为文件）
```

### 备份数据库
```bash
# SQLite数据库备份就是复制文件
cp ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db \
   ~/.openclaw/workspace/content-ops-workspace/data/content-ops-backup-$(date +%Y%m%d).db
```
