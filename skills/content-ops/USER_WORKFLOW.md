# Content Ops 使用流程手册

> 从安装到日常运营的完整操作指南

---

## 目录

1. [首次安装流程](#一首次安装流程)
2. [账号配置流程](#二账号配置流程)
3. [日常运营流程](#三日常运营流程)
4. [故障处理流程](#四故障处理流程)
5. [数据备份流程](#五数据备份流程)

---

## 一、首次安装流程

### Step 1: 安装 Skill (2分钟)

```bash
# 方式1: 直接复制
scp content-ops.skill ~/.openclaw/workspace/skills/

# 方式2: ClawHub
clawhub install content-ops

# 重启 OpenClaw 生效
# 或在聊天中输入: /skills reload
```

**验证安装**:
```
用户: content-ops 能用吗？

Agent 返回:
✅ Content Ops 已就绪
数据库: ✅ 已连接
配图生成: ⚠️ 未配置 (需要 OPENAI_API_KEY)
账号: ⚠️ 未配置 (需要信息源+目标账号)

下一步: 配置账号信息
```

### Step 2: 初始化数据库 (3分钟)

```bash
cd ~/.openclaw/workspace/skills/content-ops

# 1. 安装依赖
npm install

# 2. 生成迁移
npx drizzle-kit generate

# 3. 执行迁移
npx drizzle-kit migrate

# 4. 验证 (可选)
npx drizzle-kit studio  # 打开管理界面
```

**成功标志**:
```
✅ 数据库初始化完成
位置: ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db
表数量: 7张
```

### Step 3: 配置环境 (5分钟)

```bash
# 配置 OpenAI API Key (配图生成)
export OPENAI_API_KEY="sk-..."

# 添加到 ~/.bashrc 持久化
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

**验证配置**:
```bash
node scripts/test-image-generation.ts
# 应生成测试图片并保存
```

---

## 二、账号配置流程

### 流程图

```
开始
  │
  ▼
┌─────────────────┐
│ 添加信息源账号   │ ← 小红书账号
│ (source_accounts)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 添加目标账号     │ ← Reddit/Pinterest/Discord
│ (target_accounts)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 配置运营策略     │ ← 定位、受众、内容方向
│ (strategy.md)    │
└────────┬────────┘
         │
         ▼
       完成 ✅
```

### Step 1: 添加小红书信息源

**方式1: 通过 Agent 对话**

```
用户: 添加小红书账号

Agent: 请提供以下信息:
1. 账号标识名 (如: 小红书主号)
2. 登录状态 (active/expired)
3. 每日抓取限额 (建议: 50)

用户: 1. 小红书主号 2. active 3. 50

Agent: ✅ 已添加信息源账号
ID: xxx-xxx
状态: active
限额: 50条/天

⚠️ 注意: 需要配置登录信息才能抓取
请提供 cookies 或扫码登录
```

**方式2: 直接数据库操作**

```typescript
import { mutations } from './src/db/index.js';
import { randomUUID } from 'crypto';

await mutations.createSourceAccount({
  id: randomUUID(),
  accountType: 'source',
  platform: 'xiaohongshu',
  accountName: '小红书主号',
  loginStatus: 'active',
  sessionData: { /* cookies */ },
  dailyQuota: 50,
  quotaUsedToday: 0,
  crawlConfig: {
    search_limit: 50,
    request_interval: [2, 5],
    retry_times: 3
  }
});
```

### Step 2: 添加目标账号

**Reddit 账号**:

```
用户: 添加 Reddit 账号 MyBrandUS

Agent: 请提供:
1. 主页链接 (如: https://reddit.com/user/MyBrandUS)
2. 账号定位 (如: 美式简约穿搭分享)
3. 目标受众 (如: 18-35岁美国女性)

用户: 提供信息...

Agent: ✅ 已添加 Reddit 账号
是否创建运营策略文档？(是/否)
```

**Pinterest 账号**:

```
用户: 添加 Pinterest 账号 StyleInspo

Agent: ✅ 已添加
请配置默认画板:
- Spring Outfits
- Minimalist Style
- Daily Inspiration
```

**Discord Webhook**:

```
用户: 添加 Discord 频道

Agent: 请提供 Webhook URL:
(https://discord.com/api/webhooks/...)

用户: 提供 URL

Agent: ✅ 已添加
测试消息已发送，请确认收到
```

### Step 3: 创建运营策略

**自动生成 + 人工完善**:

```
Agent: 基于账号定位，生成策略草稿:

## MyBrandUS 运营策略 (草稿)

### 定位
美式简约穿搭分享

### 目标受众
18-35岁美国女性，喜欢minimalist风格

### 内容方向 (建议)
- 通勤穿搭 (40%)
- 周末休闲 (30%)
- 搭配技巧 (20%)
- 购物推荐 (10%)

### 发布频率
每日 1-2 条，最佳时间 14:00-16:00 (EST)

### 参考社区
- r/femalefashionadvice
- r/minimalism

请完善或确认保存
```

**用户确认后保存**: `strategies/reddit-mybrandus-strategy.md`

---

## 三、日常运营流程

### 标准工作日流程图

```
09:00  自动: 生成今日任务规划
       用户: 查看并确认/调整
       
10:00  按需: 语料抓取
       Agent: 通知"语料不足，建议抓取XX主题"
       用户: 确认主题
       Agent: 执行抓取 → 返回结果 → 用户审核
       
14:00  自动/确认: 内容发布
       Agent: 生成样稿 → 用户确认 → 定时发布
       
18:00  自动: 数据复盘
       Agent: 生成昨日数据报告
       用户: 查看洞察和建议
```

### 详细操作流程

#### 操作1: 语料抓取

**触发条件**: 
- 用户主动: "抓一批春季穿搭"
- Agent 建议: "语料库不足，建议抓取"

**完整流程**:

```
Step 1: 用户发起
─────────────────────────
用户: 抓一批春季穿搭语料


Step 2: Agent 确认
─────────────────────────
Agent: 🚀 启动抓取任务

主题: 春季穿搭
扩展Query: 春季穿搭, OOTD, 风衣搭配, 春日穿搭, 每日穿搭
搜索深度: 前3页 (高质量<3条时翻页)
预计时间: 2-3分钟

确认执行？(是/否)

用户: 是


Step 3: Agent 执行 (自动)
─────────────────────────
Master Agent
├── 拆分Query: 5个关键词
├── 创建5个Sub-Agent并行搜索
│   ├── Agent1: 搜索"春季穿搭" → 评估质量 → 翻页(如需要)
│   ├── Agent2: 搜索"OOTD" → 评估质量 → 翻页
│   ├── Agent3: 搜索"风衣搭配" → 评估质量
│   ├── Agent4: 搜索"春日穿搭" → 评估质量
│   └── Agent5: 搜索"每日穿搭" → 评估质量
├── 去重Agent: 对比已有语料
└── 汇总输出

评估标准:
- 数据好: 点赞>1000, 收藏>500
- 观点好: 新颖实用
- 时效高: 7天内发布
- 无重复: 观点重合度<70%


Step 4: Agent 返回结果
─────────────────────────
Agent: 📋 抓取完成 - 待确认

主题: 春季穿搭
候选帖子: 25条
高质量（8-10分）: 8条 ✅
中质量（5-7分）: 10条
重复/低质量: 7条 ❌

┌────┬─────────────────────┬──────┬────────┬─────────────────────┐
│ 排名 │ 标题                │ 评分 │ 点赞   │ 推荐理由            │
├────┼─────────────────────┼──────┼────────┼─────────────────────┤
│ 1  │ 春日风衣3种穿法      │ 9.5  │ 2.3w   │ 搭配思路实用        │
│ 2  │ 小个子春季穿搭       │ 9.0  │ 1.8w   │ 针对性强            │
│ 3  │ 春日约会穿搭         │ 8.5  │ 1.2w   │ 评论区互动高        │
│ 4  │ 韩系春季穿搭         │ 8.0  │ 1.5w   │ 风格独特            │
└────┴─────────────────────┴──────┴────────┴─────────────────────┘

建议:
- 语料1适合 Reddit (实用教程向)
- 语料2适合 Pinterest (图文向)
- 语料3适合 Discord (讨论向)

请回复:
- "确认" → 全部进入可用语料库
- "确认1,2,3" → 只选第1-3条
- "不要2" → 排除第2条
- "重新抓取" → 放弃这批，重新搜索


Step 5: 用户确认
─────────────────────────
用户: 确认

Agent: ✅ 已确认 8 条高质量语料
- 进入可用语料库
- 关联主题标签: ["春季穿搭", "风衣", "OOTD"]

是否立即基于这些语料创建发布内容？(是/否)

用户: 否 (稍后)

Agent: 好的，已保存到语料库。随时可以说"创建一条Reddit帖子"来使用。
```

#### 操作2: 内容创建与发布

**触发条件**:
- 用户主动: "创建一条帖子"
- 定时任务: 已到排期时间
- Agent 建议: "今日建议发布"

**完整流程**:

```
Step 1: 选题推荐
─────────────────────────
用户: 创建一条 Reddit 帖子

Agent: 🎯 选题推荐

基于今日语料库 (可用: 45条) 和 Reddit r/femalefashionadvice 社区:

┌────┬──────────────────────────────────┬──────────┬────────────────────┐
│ 选项 │ 选题                             │ 类型     │ 推荐理由           │
├────┼──────────────────────────────────┼──────────┼────────────────────┤
│ 1  │ How to Style Trench Coats for    │ 教程型   │ 语料1点赞2.3w,    │
│    │ Spring: 3 Looks That Work        │          │ 收藏率高          │
├────┼──────────────────────────────────┼──────────┼────────────────────┤
│ 2  │ 5 Spring Outfit Ideas for        │ 清单型   │ 适合合集形式,     │
│    │ Petite Women                     │          │ 讨论度高          │
├────┼──────────────────────────────────┼──────────┼────────────────────┤
│ 3  │ I Tried 3 Spring Trends So You   │ 体验型   │ 争议性强,         │
│    │ Don't Have To                    │          │ 评论通常较多      │
└────┴──────────────────────────────────┴──────────┴────────────────────┘

请回复数字 (1/2/3) 选择选题
或描述你的需求 (如: "想要适合小个子的")

用户: 1


Step 2: 样稿生成 (自动)
─────────────────────────
Agent: 📝 正在生成样稿...

执行中:
1. 分析参考语料 (春日风衣3种穿法)
2. 提取核心观点: 腰带系法、配色技巧、场合适配
3. 改编为英文 Reddit 风格
4. 生成标题选项 (3个)
5. 生成正文结构 (Hook + 主体 + CTA)
6. 生成配图 (DALL-E, 3张)
   - Prompt: "Minimalist spring trench coat outfit, ..."
   - 生成中...
   - 保存到: corpus/published/xxx/
7. 排版优化 (Markdown格式)

预计 1-2 分钟


Step 3: 样稿展示
─────────────────────────
Agent: 📝 样稿已生成 - 待审核

账号: Reddit - MyBrandUS
社区: r/femalefashionadvice
计划时间: 今日 14:00 (最佳发布时间)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
标题: [Guide] How to Style Trench Coats for Spring: 3 Looks That Actually Work

正文:
Hey r/femalefashionadvice! 👋

Spring is here and I know many of us are reaching for our trench 
coats. As a 5'4" gal who's struggled with looking overwhelmed in 
oversized trenches, I want to share 3 styling tricks that actually 
work for us regular folks...

[详细内容: 3种搭配方法]

What's your go-to trench coat outfit? Share below! 👇
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

配图预览:
[图片1: 主图-风衣全身照]
[图片2: 细节-腰带系法]
[图片3: 配色展示]

标签: #fashion #springoutfits #styletips #trenchcoat

参考语料: 春日风衣3种穿法 (点赞2.3w)
改编类型: 翻译 + 本土化

请选择:
[A] 确认，按计划 14:00 发布
[B] 修改 (请描述，如: "标题太正式，换个活泼点的")
[C] 看看其他版本 (生成备选版本)
[D] 换个选题

用户: B，标题太长了，简短一点


Step 4: 修改循环
─────────────────────────
Agent: 📝 重新生成中...

新标题选项:
1. "3 Spring Trench Coat Looks That Actually Work"
2. "How I Style My Trench Coat: 3 Easy Looks"
3. "Spring Trench Styling for Short Girls"

请选择 1/2/3

用户: 2

Agent: 已更新。新标题: "How I Style My Trench Coat: 3 Easy Looks"

确认发布？(是/否)

用户: 是


Step 5: 创建发布任务
─────────────────────────
Agent: ✅ 已创建发布任务

任务ID: xxx-xxx
状态: scheduled
计划时间: 2026-03-01 14:00
账号: Reddit - MyBrandUS

操作:
- 14:00 自动发布
- 发布后 24h 抓取数据
- 数据更新后通知你

是否现在预览发布效果？(是/否)
```

#### 操作3: 定时发布执行

```
14:00 自动执行
─────────────────────────
系统:
1. 检查 Reddit 登录态 ✅
2. 访问 r/femalefashionadvice
3. 填写标题、正文
4. 上传 3 张配图
5. 预览检查 (截图保存)
6. 点击 Post
7. 等待发布完成
8. 抓取发布后的 URL
9. 更新任务状态: published
10. 设置 24h 后数据抓取任务

Agent 通知用户:
📢 发布完成

账号: Reddit - MyBrandUS
帖子: How I Style My Trench Coat: 3 Easy Looks
链接: https://reddit.com/r/femalefashionadvice/comments/xxx
时间: 14:03 (计划14:00，延迟3分钟)
状态: ✅ 成功

预览截图: [查看]
数据追踪: 24小时后生成报告
```

#### 操作4: 数据复盘

```
18:00 自动生成
─────────────────────────
Agent: 📊 昨日复盘 - 2026-02-28

Reddit - MyBrandUS:
┌─────────────────┬─────────┬──────────┬────────┐
│ 指标            │ 昨日    │ 前日     │ 变化   │
├─────────────────┼─────────┼──────────┼────────┤
│ 粉丝数          │ 1,245   │ 1,233    │ +12 ⬆️ │
│ Karma 变化      │ +156    │ +128     │ +22% ⬆️│
│ 发布内容        │ 1       │ 1        │ -      │
│ 总互动          │ 156     │ 128      │ +22% ⬆️│
└─────────────────┴─────────┴──────────┴────────┘

内容表现详情:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"How I Style My Trench Coat..."
发布时间: 昨日 14:03
Score: 456 (比账号平均高 40%) ✅
Upvotes: 512
Comments: 34 (热度: 高)
Awards: 2

热评:
- "这方法救了我的衣柜" (127赞)
- "5'2" here, definitely trying #2" (89赞)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

洞察与建议:
✅ 教程型内容表现优于清单型 (+40%)
✅ 带身高标注的标题点击率高
✅ 14:00-16:00 发布时间效果最好
⚠️ 评论回复率可提高 (目前 0/34)

明日建议:
- 继续"小空间/小个子"方向
- 已准备 3 条相关语料待发布
- 建议今日 14:00 再发一条

查看完整报告: reports/2026-02-28-reddit-mybrandus.md
```

---

## 四、故障处理流程

### 故障1: 抓取失败

```
症状: Agent 返回"抓取失败"

排查流程:
1. 检查登录态
   → 用户: 检查小红书登录
   → 如过期: 重新扫码登录 → 更新 sessionData

2. 检查配额
   → Agent: 今日已用 45/50 条
   → 如超限: 明日再试或提高配额

3. 检查网络
   → 测试: curl https://xiaohongshu.com
   → 如 blocked: 检查代理/VPN

4. 重试
   → Agent: 3次重试后仍失败
   → 报告详细错误日志
```

### 故障2: 发布失败

```
症状: 定时发布未执行或报错

排查流程:
1. 检查账号状态
   → 登录态是否过期？
   → 账号是否被封？

2. 检查内容合规
   → 是否触发平台敏感词？
   → 图片是否符合规范？

3. 检查 API 限制
   → Reddit: 是否超发帖频率？
   → Pinterest: 是否超 Pin 限制？

4. 手动重试
   → Agent: 是否立即重试？(是/否)
   → 或: 修改内容后重试
```

### 故障3: 图片生成失败

```
症状: DALL-E 返回错误

排查流程:
1. 检查 API Key
   → echo $OPENAI_API_KEY
   
2. 检查额度
   → 登录 OpenAI 账单页面
   
3. 检查 Prompt
   → 是否包含敏感词？
   → 简化重试

4. 备选方案
   → 使用语料原图 (需版权确认)
   → 仅文字发布
   → 稍后重试
```

---

## 五、数据备份流程

### 自动备份 (推荐)

```bash
# 添加到 crontab
crontab -e

# 每日凌晨3点备份
0 3 * * * cp ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db \
  ~/.openclaw/workspace/content-ops-workspace/backups/content-ops-$(date +\%Y\%m\%d).db

# 保留最近30天
0 4 * * * find ~/.openclaw/workspace/content-ops-workspace/backups/ \
  -name "content-ops-*.db" -mtime +30 -delete
```

### 手动备份

```bash
# 立即备份
cp ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db \
  ~/.openclaw/workspace/content-ops-workspace/backups/content-ops-$(date +%Y%m%d-%H%M%S).db

# 导出为 SQL (跨平台兼容)
sqlite3 ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db \
  ".dump" > backup-$(date +%Y%m%d).sql
```

### 恢复备份

```bash
# 停止所有运行中的任务
# 替换数据库文件
cp backup-20260301.db \
  ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db

# 重启服务
```

---

## 六、流程速查表

| 你想做 | 你说 | Agent 响应时间 |
|--------|------|---------------|
| 抓语料 | "抓一批XX主题" | 2-3分钟 |
| 发内容 | "创建一条XX帖子" | 1-2分钟 |
| 看数据 | "今天数据怎么样" | 即时 |
| 查计划 | "今天有什么任务" | 即时 |
| 改策略 | "修改XX账号策略" | 即时 |
| 暂停 | "暂停XX账号" | 即时 |
| 备份 | "备份数据" | 10秒内 |

---

## 参考文档

- [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) - Agent 使用指南
- [IMAGE_GENERATION_SETUP.md](IMAGE_GENERATION_SETUP.md) - 配图配置
- [QUICKSTART.md](QUICKSTART.md) - 10分钟快速上手
- [references/detailed-workflow.md](references/detailed-workflow.md) - 详细工序设计
