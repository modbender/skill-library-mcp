# Content Ops - 快速上手指南

> 让其他 OpenClaw 在 10 分钟内跑起来的最小化文档

---

## 1. 安装 Skill

```bash
# 将 .skill 文件放入 OpenClaw skills 目录
cp content-ops.skill ~/.openclaw/workspace/skills/

# 或使用 clawhub 安装（如果已配置）
clawhub install content-ops
```

---

## 2. 初始化数据库

```bash
cd ~/.openclaw/workspace/skills/content-ops

# 安装依赖
npm install

# 生成并执行数据库迁移
npx drizzle-kit generate
npx drizzle-kit migrate

# 验证数据库
npx drizzle-kit studio  # 可选：打开管理界面
```

**数据库文件位置**: `~/.openclaw/workspace/content-ops-workspace/data/content-ops.db`

---

## 3. 配置第一个账号

### 3.1 添加信息源账号（小红书）

```typescript
import { mutations } from './src/db/index.js';
import { randomUUID } from 'crypto';

await mutations.createSourceAccount({
  id: randomUUID(),
  accountType: 'source',
  platform: 'xiaohongshu',
  accountName: '小红书主号',
  loginStatus: 'active',  // 需要先手动登录获取cookies
  sessionData: {},        // 登录会话信息
  dailyQuota: 50,
  quotaUsedToday: 0
});
```

### 3.2 添加被运营账号（Reddit）

```typescript
await mutations.createTargetAccount({
  id: randomUUID(),
  accountType: 'target',
  platform: 'reddit',
  accountName: 'MyBrandUS',
  status: 'active',
  homepageUrl: 'https://reddit.com/user/MyBrandUS',
  positioning: '美式简约穿搭分享',
  targetAudience: '18-35岁美国女性',
  contentDirection: '日常穿搭、搭配技巧'
});
```

---

## 4. 第一次抓取（人工确认流程）

### Step 1: 用户发起

**用户说**: "抓一批春季穿搭的语料"

### Step 2: Agent 执行

```typescript
import { mutations } from './src/db/index.js';
import { randomUUID } from 'crypto';

// 创建抓取任务
const task = await mutations.createCrawlTask({
  id: randomUUID(),
  taskName: '春季穿搭语料抓取',
  sourceAccountId: '你的小红书账号ID',
  status: 'pending',
  queryList: ['春季穿搭', 'OOTD', '风衣搭配', '春日穿搭'],
  targetCount: 20
});

// 启动 Master Agent 执行抓取
// （这里调用你的多Agent协作脚本）
```

### Step 3: Agent 返回结果给用户确认

```markdown
📋 语料抓取完成 - 待确认

主题: 春季穿搭
搜索Query: 4个
候选帖子: 18条
高质量（8-10分）: 6条 ✅

前3推荐:
1. [9.5分] 春日风衣3种穿法 | 点赞2.3w
2. [9.0分] 小个子春季穿搭 | 点赞1.8w
3. [8.5分] 春日约会穿搭 | 点赞1.2w

请回复"确认"通过，或标记"不要第2条"
```

### Step 4: 用户确认后归档

**用户说**: "确认"

```typescript
import { mutations } from './src/db/index.js';

// 将选中的语料标记为 approved
await mutations.updateCrawlResultCuration(
  'result-id',
  'approved',
  '用户确认通过',
  9
);
```

---

## 5. 第一次发布（样稿确认流程）

### Step 1: 选题推荐

**Agent 返回**: 
```markdown
基于语料库，推荐3个选题:

1. "How to Style Trench Coats for Spring"
2. "5 Spring Outfit Ideas for Petite Women"
3. "Spring Date Night Looks: Romantic vs Cool"

请回复数字选选题
```

### Step 2: 用户确认选题

**用户说**: "选1"

### Step 3: 生成样稿

**Agent 返回**:
```markdown
📝 样稿已生成

标题: [Guide] How to Style Trench Coats for Spring: 3 Easy Looks

正文:
Hey r/femalefashionadvice! Spring is here and I want to share...
[详细内容]

配图: 3张（DALL-E生成）

请确认：
[A] 确认发布
[B] 修改（请描述）
```

### Step 4: 用户确认并发布

**用户说**: "A"

```typescript
import { mutations } from './src/db/index.js';

// 创建发布任务
await mutations.createPublishTask({
  id: randomUUID(),
  taskName: '春季风衣穿搭指南',
  targetAccountId: '你的Reddit账号ID',
  status: 'scheduled',
  scheduledAt: new Date()  // 立即发布
});

// 执行发布（浏览器自动化）
// ...
```

---

## 6. 每日自动化流程

### 设置定时任务

```bash
# 每天早上 9:00 执行
0 9 * * * cd ~/.openclaw/workspace/skills/content-ops && node scripts/daily-plan.js

# 每小时检查待发布任务
0 * * * * cd ~/.openclaw/workspace/skills/content-ops && node scripts/check-publish.js

# 每天晚上 18:00 数据复盘
0 18 * * * cd ~/.openclaw/workspace/skills/content-ops && node scripts/daily-report.js
```

### 定时任务做什么

| 时间 | 任务 | 是否需要用户确认 |
|------|------|-----------------|
| 9:00 | 生成今日任务规划 | ❌ 自动通知 |
| 10:00 | 检查语料库，不足则建议抓取 | ✅ 需确认主题 |
| 14:00 | 发布已排期内容 | ❌ 自动执行 |
| 18:00 | 生成数据复盘报告 | ❌ 自动通知 |

---

## 7. 常用查询（Agent 使用）

```typescript
import { queries } from './src/db/index.js';

// 看板数据
const stats = await queries.getOverviewStats();

// 可用语料
const corpus = await queries.getAvailableCorpus('穿搭', 7);

// 今日待发布
const tasks = await queries.getTodayScheduledTasks();

// 账号趋势
const trend = await queries.getAccountTrend('account-id', 7);
```

---

## 8. 人机配合要点

**用户需要做的**:
1. 确认抓取主题（每天1-2次）
2. 确认选题方向（每次发布前）
3. 确认样稿内容（每次发布前）
4. 查看复盘报告（可选）

**Agent 自动做的**:
1. 拆分Query、并行搜索、质量评估
2. 去重、排序、生成候选列表
3. 生成样稿、配图
4. 定时发布、数据抓取、报告生成

---

## 9. 故障排查

| 问题 | 解决 |
|------|------|
| 数据库连接失败 | 检查 `~/.openclaw/workspace/content-ops-workspace/data/` 是否存在 |
| 抓取失败 | 检查小红书登录态，可能需要更新 cookies |
| 发布失败 | 检查目标平台登录态，Reddit/Pinterest 需要浏览器自动化 |
| 质量问题 | 调整 `quality_score` 阈值 |

---

**完整文档**: 见 `references/` 目录
- `detailed-workflow.md` - 完整工序设计
- `database-schema.md` - 数据库表结构
- `sop-workflows.md` - 7个SOP流程
