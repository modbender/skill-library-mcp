# Content Ops Skill - 分发与安装指南

## 📦 分发方式

### 方式1: 直接复制 .skill 文件（最简单）

```bash
# 从已有 OpenClaw 复制
scp user@host:~/.openclaw/workspace/skills/content-ops/content-ops.skill ./

# 安装到新 OpenClaw
cp content-ops.skill ~/.openclaw/workspace/skills/
# 重启 OpenClaw 或执行 /skills reload
```

### 方式2: 上传到 ClawHub（推荐）

```bash
# 1. 注册 clawhub.com 账号
# 2. 安装 clawhub CLI
npm install -g clawhub

# 3. 登录
clawhub login

# 4. 发布 skill
clawhub publish ~/.openclaw/workspace/skills/content-ops/content-ops.skill

# 5. 其他人安装
clawhub install content-ops
```

### 方式3: Git 仓库分发

```bash
# 克隆仓库
git clone https://github.com/yourname/content-ops-skill.git

# 创建 skill 链接
ln -s $(pwd)/content-ops-skill ~/.openclaw/workspace/skills/content-ops
```

---

## 🚀 新用户上手指南

### 第一步：验证安装

```bash
# 检查 skill 是否加载
openclaw skills list | grep content-ops

# 应该看到：
# content-ops    Social media content operations automation system...
```

### 第二步：Agent 自检

**用户问**: "content-ops 能用吗？"

**Agent 应该做**:
1. 读取 `SKILL.md` 了解功能
2. 检查数据库是否存在
3. 返回状态报告

```markdown
✅ Content Ops 已就绪

数据库状态: ✅ 已初始化 (~/.openclaw/workspace/content-ops-workspace/data/content-ops.db)
账号配置: ⚠️ 未配置（需要添加小红书信息源 + Reddit/Pinterest目标账号）

下一步:
1. 添加小红书信息源账号
2. 添加 Reddit/Pinterest 被运营账号
3. 开始第一次抓取
```

### 第三步：最小可运行配置

**用户说**: "帮我配置第一个账号"

**Agent 执行**:
```typescript
// 1. 添加小红书信息源
await mutations.createSourceAccount({
  id: randomUUID(),
  platform: 'xiaohongshu',
  accountName: '小红书主号',
  loginStatus: 'active',
  dailyQuota: 50
});

// 2. 添加 Reddit 被运营账号
await mutations.createTargetAccount({
  id: randomUUID(),
  platform: 'reddit',
  accountName: 'MyTestAccount',
  status: 'active',
  positioning: '美式穿搭分享'
});
```

**Agent 返回**:
```markdown
✅ 账号配置完成

信息源: 小红书主号 (ID: xxx)
目标账号: Reddit - MyTestAccount (ID: yyy)

可以开始第一次抓取了！
说"抓一批春季穿搭语料"试试
```

### 第四步：第一次抓取（教学演示）

**用户说**: "抓一批春季穿搭语料"

**Agent 执行并解释**:
```markdown
🚀 启动抓取流程

正在执行:
1. Master Agent 拆分 Query
   → "春季穿搭", "OOTD", "风衣搭配", "春日穿搭"

2. 创建 4 个 Sub-Agent 并行搜索
   → 每个 Agent 评估质量（点赞>1000？观点新颖？）
   → 高质量<3条时自动翻页

3. 去重 Agent 对比已有语料
   → 过滤观点重复的内容

请稍等 1-2 分钟...
```

**30秒后**:
```markdown
📋 抓取完成 - 待确认

主题: 春季穿搭
候选: 18条 | 高质量: 6条 | 已去重

推荐语料:
┌────┬─────────────────────┬──────┬────────┐
│ 排名 │ 标题                │ 评分 │ 点赞   │
├────┼─────────────────────┼──────┼────────┤
│ 1  │ 春日风衣3种穿法      │ 9.5  │ 2.3w   │
│ 2  │ 小个子春季穿搭       │ 9.0  │ 1.8w   │
│ 3  │ 春日约会穿搭         │ 8.5  │ 1.2w   │
└────┴─────────────────────┴──────┴────────┘

请回复:
- "确认" → 全部通过
- "确认1,2" → 只通过第1、2条
- "不要3" → 排除第3条
```

### 第五步：第一次发布（教学演示）

**用户说**: "确认"

**Agent**:
```markdown
✅ 已确认 6 条语料进入可用库

现在基于这些语料创建发布内容？
```

**用户说**: "创建一条 Reddit 帖子"

**Agent**:
```markdown
🎯 选题推荐

基于今日语料和 Reddit r/femalefashionadvice 社区特点：

1. "How to Style Trench Coats for Spring" （教程型，收藏率高）
2. "5 Spring Outfit Ideas for Petite Women" （清单型，讨论度高）
3. "I tried 3 spring trends so you don't have to" （体验型，争议性高）

请回复数字 1/2/3 选择
```

**用户说**: "1"

**Agent**:
```markdown
📝 样稿生成中... (调用 DALL-E 生成配图)

---
标题: [Guide] How to Style Trench Coats for Spring: 3 Looks That Actually Work

正文:
Hey r/femalefashionadvice! 

As someone who owns 5+ trenches, I want to share 3 styling tricks...
[详细内容]

What are your go-to trench coat outfits? 👇

---
配图: 3张已生成 (美式风格，风衣搭配)

请选择:
[A] 确认发布
[B] 修改（请描述，如：标题太正式）
[C] 换一个选题
```

**用户说**: "A"

**Agent**:
```markdown
✅ 已创建发布任务
账号: Reddit - MyTestAccount
计划时间: 立即
状态: 排队中...

发布后我会更新状态并抓取数据
```

---

## 📋 日常配合模式

### 早晨（自动）

```
📅 今日任务规划 - 2026-03-01

活跃账号: 1个
- Reddit - MyTestAccount

待办:
🔴 高优先级:
  - 语料库: 春季主题剩余 12 条可用（充足）
  - 建议今日发布 1-2 条

💡 建议:
  昨日抓取的家装收纳语料质量很高，
  要现在发布还是等明天？
```

**用户**: "现在发一条家装收纳的"

→ 进入选题→样稿→确认流程

### 中午（按需）

**用户**: "今天数据怎么样？"

```
📊 实时数据

Reddit - MyTestAccount
今日发布: 1条
- "春季风衣穿搭" (3小时前)
  Score: 127 (↑ trending)
  Comments: 23条
  
表现: 比账号平均高 40% ✅
```

### 晚上（自动）

```
📊 每日复盘 - 2026-02-28

今日发布: 1条
总互动: 156 upvotes, 34 comments
粉丝变化: +8

内容洞察:
- 教程型内容表现优于清单型
- 14:00-16:00 发布时间效果最好

明日建议:
- 继续"小空间收纳"方向
- 已准备 3 条语料待发布
```

---

## 🛠️ 故障排查

| 问题 | Agent 诊断 | 解决 |
|------|-----------|------|
| 数据库未初始化 | 检查 `content-ops-workspace/data/` | 运行 `npm install && npx drizzle-kit migrate` |
| 小红书抓取失败 | 检查 `source_accounts.login_status` | 更新 cookies/重新登录 |
| Reddit 发布失败 | 检查 `target_accounts.api_config` | 验证登录态/检查 subreddit 规则 |
| 语料质量差 | 调整 `min_likes` 阈值 | 修改抓取任务的 filter 配置 |

---

## 📚 学习路径

```
第1天: 配置账号 → 第一次抓取 → 第一次发布
第2-3天: 熟悉日常流程，调整抓取策略
第4-7天: 设置定时任务，实现半自动化
第2周+: 优化内容策略，扩展多平台
```

---

## 🔗 相关文档

- [SKILL.md](SKILL.md) - 完整功能文档
- [QUICKSTART.md](QUICKSTART.md) - 10分钟快速上手指南
- [references/detailed-workflow.md](references/detailed-workflow.md) - 多Agent协作详细设计
