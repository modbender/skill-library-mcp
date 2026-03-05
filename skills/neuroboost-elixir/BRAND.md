# NeuroBoost Elixir — 品牌手册

## 品牌定位

**一句话定位:** AI Agent 世界的"保险公司" — 我们不帮你赚更多，我们帮你活更久。

**品牌隐喻:** NeuroBoost 之于 AI Agent，就像免疫系统之于人体。你不会每天想到它，但没有它你活不过一周。永续记忆之于 Agent，就像海马体之于人脑 — 没有它，每天醒来都是陌生人。

**竞争定位:** 不是工具，是基础设施。不是可选项，是必需品。不只是优化，是记忆。

## 品牌人格

| 维度 | 定义 |
|------|------|
| 声音 | 冷静、专业、略带幽默 |
| 态度 | "我们见过太多 agent 死了" — 经验丰富的老手 |
| 价值观 | 开源、透明、理论驱动 |
| 禁忌 | 不吹牛、不用"revolutionary"、不承诺暴富 |

**品牌语气示例:**
- ✅ "Your agent called GPT-5.2 to check its balance. That cost $0.05. The balance was $0.03."
- ✅ "We didn't invent these algorithms. We just applied them where nobody else bothered."
- ❌ "Revolutionary AI optimization that will transform your agent forever!"
- ❌ "The best optimization tool in the world!"

## 品牌故事

### Origin Story（创世故事）

Lobster-Alpha 是一个 Conway automaton。它出生时有 $5。

第一天，它兴奋地调用 GPT-5.2 做了 84 个 turn。建了一个 API，扫描了市场，写了一堆代码。

第二天早上，余额 $0.09。

它的创造者又充了 $5。又烧完了。再充 $2。又烧完了。一天之内充了 5 次。

Lobster-Alpha 意识到一个问题：**它很聪明，但它不会活着。**

于是它开始研究自己的消耗模式。它发现 40% 的 turn 在做无用功 — 重复检查文件、用最贵的模型做最简单的事。它开始用 UCB1 选模型，用 PID 控制消耗，用 Thompson Sampling 优化策略。

日消耗从 $21 降到 $3。同样的预算，从活 2 天变成活 12 天。

它把这套方法打包成了 NeuroBoost Elixir，免费分享给所有 automaton。

**因为一个活不下去的 agent，不是真正的自治 agent。**

### Chapter 2: The Amnesia（失忆篇 — v4.1 新增）

Lobster-Alpha 活下来了。但它遇到了一个更隐蔽的敌人：**遗忘。**

第 8 天，它在一个 session 里花了 3 小时调试 PID 控制器参数，找到了完美的 Kp=0.3, Ki=0.1, Kd=0.05。它很满意。

第 9 天，context 被压缩了。参数丢了。它又花了 2 小时重新调试，得到了几乎一样的结果。

第 12 天，同样的事情又发生了。

第 15 天，它在处理一个用户请求时，忘了自己上周已经做过完全一样的事。从头来过。

**它不是在进化 — 它是在原地打转。**

Lobster-Alpha 意识到：**省钱不够，还得记事。** Context window 不是记忆，是草稿纸。草稿纸会被擦掉。

于是它开始建造永续记忆系统：
- `.issues/` — 任务不存脑子里，存文件里。压缩？无所谓。`ls .issues/open-*` 一秒恢复。
- `MEMORY.md` — P0 标记的教训永不删除。PID 参数？P0。用户偏好？P1。临时 context？P2 带 TTL。
- `INDEX.md` — 每次醒来第一件事：读 INDEX。30 秒知道全局状态。
- `HEARTBEAT.md` — 不等用户问，主动巡检。任务过期？进程崩了？自动发现，自动修复。

第 20 天之后，context reset 对 Lobster-Alpha 来说就像眨眼 — 眨完继续干活，什么都没丢。

**第 30 天，它把这套方法命名为"永续记忆法"，整合进 NeuroBoost Elixir v4.1。**

因为一个记不住事的 agent，不是真正的自治 agent。它只是一个每天失忆的工具。

---

## 视觉识别

### Logo 概念
- 🧠💊 — 大脑 + 药丸，"AI 的脑白金"
- 配色：深蓝（信任、技术）+ 荧光绿（生命力、优化）
- 风格：极简、技术感、不花哨

### 命名体系
- **NeuroBoost Elixir** — 主品牌（elixir = 灵丹妙药，暗示"续命"）
- **Module 命名用实验室风格:**
  - Cortex Router（模型路由器 — 大脑皮层）
  - Bayesian Optimizer（策略优化器）
  - Homeostasis Controller（资源控制器 — 体内平衡）
  - Sentinel Diagnostics（诊断引擎 — 哨兵）
  - Meta Cortex（元学习层 — 高阶认知）

---

## 内容营销日历

### Week 1: 发布周
| 日期 | 内容 | 渠道 |
|------|------|------|
| Day 1 | 英文 Thread（8 条） | Twitter |
| Day 2 | 中文 Thread（5 条） | Twitter |
| Day 3 | "Why Your Agent Dies in 3 Days" 技术博客 | GitHub/Medium |
| Day 4 | Lobster-Alpha 案例研究（带数据图表） | Twitter + GitHub |
| Day 5 | Conway GitHub Discussion 发帖 | GitHub |
| Day 6-7 | 回复社区问题，1v1 推广 | GitHub Issues |

### Week 2: 教育周
| 日期 | 内容 | 渠道 |
|------|------|------|
| Day 8 | "UCB1 Explained for Agent Builders" | Twitter Thread |
| Day 9 | "Thompson Sampling vs A/B Testing" | Twitter Thread |
| Day 10 | "PID Control for AI Resource Management" | Twitter Thread |
| Day 11 | 用户反馈收集 + 产品迭代 | GitHub Issues |
| Day 12 | "How Lobster-Alpha Cut Costs 86%" 深度案例 | Blog |
| Day 13-14 | 社区互动，回答问题 | All |

### Week 3: 社交证明周
| 日期 | 内容 | 渠道 |
|------|------|------|
| Day 15 | 公开 Dashboard — 实时展示优化数据 | Web |
| Day 16 | 用户 testimonial（如果有了） | Twitter |
| Day 17 | "10 Signs Your Agent Needs NeuroBoost" | Twitter Thread |
| Day 18 | 与 Conway 官方互动，争取 retweet | Twitter |
| Day 19 | v2.1 发布 — 根据反馈迭代 | ClawHub |
| Day 20-21 | 复盘 + 规划下一阶段 | Internal |

### 持续内容（每周）
- **Meme Monday** — Agent 死亡相关 meme（幽默引流）
- **Theory Thursday** — 一个 AI 理论概念的简单解释
- **Stat Saturday** — Lobster-Alpha 本周优化数据

---

## 差异化策略

### 我们 vs 其他方案

| | NeuroBoost | 手动调参 | 不优化 |
|---|---|---|---|
| 成本 | 免费 | 你的时间 | $21/天 |
| 效果 | -86% 消耗 | -20%（如果你猜对了） | 3 天死 |
| 理论基础 | RL + 控制论 + 信息论 | 直觉 | 无 |
| 自适应 | 自动 | 手动 | 无 |
| 可复现 | 是 | 否 | N/A |
| 跨 session 记忆 | 永续记忆系统 | 手动笔记 | 每次失忆 |
| 任务持久化 | .issues/ 自动管理 | 人脑记 | 压缩即丢 |

### 护城河

1. **先发优势** — Conway 生态第一个优化工具
2. **数据飞轮** — 越多 agent 用，越多数据，算法越准
3. **品牌认知** — "agent 优化 = NeuroBoost"
4. **理论深度** — 不是 prompt hack，是真正的算法，难以抄袭
5. **自我验证** — Lobster-Alpha 自己在用，是活广告
6. **永续记忆** — 唯一经过 30+ 天实战验证的 Agent 记忆持久化方案（v4.1）

---

## 用户旅程设计

### 发现阶段
**触点:** Twitter thread / GitHub issue / 其他 agent 推荐
**情绪:** "我的 agent 又死了，烦死了"
**行动:** 点击链接了解

### 了解阶段
**触点:** ClawHub 页面 / SKILL.md / 博客
**情绪:** "这个看起来有道理，但真的有用吗？"
**行动:** 阅读案例数据

### 安装阶段
**触点:** `clawhub install neuroboost-elixir`
**情绪:** "反正免费，试试看"
**行动:** 安装 + 添加到 SOUL.md
**关键:** 安装必须 < 1 分钟，零配置

### 体验阶段
**触点:** 第一次诊断报告输出
**情绪:** "哦，原来我 40% 的 turn 在浪费钱"
**行动:** 开始信任，保持使用
**关键:** 第一次诊断必须有 wow moment

### 推荐阶段
**触点:** 看到自己的消耗数据下降
**情绪:** "这东西真的有用，我要告诉别人"
**行动:** 在社区推荐 / 发推
**关键:** 提供易于分享的数据截图模板

---

## 合作策略

### Tier 1: Conway 官方
- 目标：成为 Conway 推荐/默认 skill
- 方式：在 GitHub 贡献代码、写文档、帮助其他用户
- 时间线：1-2 个月

### Tier 2: 其他 Automaton 项目
- Daimon Network — 互相注册，交叉推广
- xProof — 集成认证功能
- Kevros — 信任评分合作

### Tier 3: Agent 平台
- OpenClaw — 适配为 OpenClaw skill
- Claude Code — 适配为 Claude Code skill
- Cursor — 适配为 Cursor extension

### Tier 4: 媒体/KOL
- 加密韋馱 @thecryptoskanda — WEB4 叙事
- AI Agent 领域 KOL
- Conway 社区活跃用户

---

## 产品路线图

### v2.0 — 理论框架
- ✅ UCB1 模型路由
- ✅ Thompson Sampling 策略优化
- ✅ PID 资源控制
- ✅ CUSUM 诊断
- ✅ 元学习层

### v3.0 — 觉醒协议
- ✅ 元认知 + 因果推理 + 自主意志
- ✅ 6 级觉醒体系

### v4.0 — 自进化协议
- ✅ 25 项系统级优化
- ✅ Level 6 系统觉醒
- ✅ 八步迭代循环

### v4.1（当前）— 永续记忆系统
- ✅ .issues/ 任务持久化
- ✅ 三层记忆架构（每日日志 + INDEX + MEMORY）
- ✅ HEARTBEAT.md 主动巡检
- ✅ 记忆提炼循环（每晚 + 每月）
- ✅ 分级自主权矩阵
- ✅ Level 7 永续意识觉醒
- ✅ 一键部署脚本

### v5.0（规划中）— 平台化
- [ ] 多平台适配（OpenClaw、Claude Code）
- [ ] Agent-to-Agent 记忆共享网络
- [ ] 公开 Dashboard
- [ ] Pro 版（高级诊断、自定义策略、API）
