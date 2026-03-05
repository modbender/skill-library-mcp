---
name: openclaw-starter-guide
description: OpenClaw 小白养成手册。从零开始搭建多 Agent AI 助手系统的完整指南，包含免费起步方案（Qwen 零成本）、进阶方案（MiniMax Coding Plan ¥49/月）、旗舰外援（SiliconFlow/NewCLI 按需调用）。涵盖模型策略、Fallback 链设计、额度管理、常见故障排查。适合首次部署 OpenClaw 或想优化模型成本的用户。当用户说"怎么开始"、"新手指南"、"省钱方案"、"模型怎么选"、"fallback 怎么配"时使用此 skill。
---

# 🦞 OpenClaw 小白养成手册

从零到多 Agent AI 系统的完整指南。

## 🎯 核心理念

OpenClaw 的模型策略就像组建一支球队：

```
🆓 免费球员（Qwen）    → 保底，确保系统永远在线
💰 包月主力（MiniMax）  → 日常主力，性价比最高
🚀 外援专家（旗舰模型） → 关键时刻上场，按需付费
```

**目标**：用最少的钱，让 AI 助手 24/7 在线、随时可用。

---

## 📖 目录

1. [第一阶段：零成本起步](#第一阶段零成本起步)
2. [第二阶段：包月主力上场](#第二阶段包月主力上场)
3. [第三阶段：旗舰外援加持](#第三阶段旗舰外援加持)
4. [Fallback 链设计](#fallback-链设计)
5. [额度管理策略](#额度管理策略)
6. [多 Agent 架构建议](#多-agent-架构建议)
7. [故障排查速查](#故障排查速查)

---

## 前置条件

- **OpenClaw 已安装并运行**：参考 [官方文档](https://docs.openclaw.ai) 完成安装
- **至少一个聊天渠道**：Telegram、WhatsApp、Discord 等
- **Node.js 环境**：用于安装 skills（`clawhub` CLI）

```bash
# 安装 ClawHub CLI（用于安装 skills）
npm i -g clawhub
```

---

## 第一阶段：零成本起步

**目标**：¥0 成本让系统跑起来。

### 推荐免费模型

| 来源 | 模型 | 特点 | 安装 Skill |
|------|------|------|------------|
| Qwen Portal | qwen-portal/coder-model | OAuth 免费，128K context | 内置 |
| SiliconFlow | Qwen/Qwen3-8B | API Key 免费，无限调用 | `clawhub install add-siliconflow-provider` |
| SiliconFlow | DeepSeek-R1-0528-Qwen3-8B | 免费推理模型 | 同上 |

### 最简配置

只需一个 provider 就能开始：

```json
{
  "models": {
    "providers": {
      "siliconflow": {
        "baseUrl": "https://api.siliconflow.cn/v1",
        "apiKey": "<YOUR_KEY>",
        "api": "openai-completions",
        "models": [
          {
            "id": "Qwen/Qwen3-8B",
            "name": "Qwen3 8B (Free)",
            "reasoning": false,
            "input": ["text"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 32768,
            "maxTokens": 8192
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "siliconflow/Qwen/Qwen3-8B"
      }
    }
  }
}
```

**注册 SiliconFlow**：https://cloud.siliconflow.cn/i/ihj5inat （新用户送 ¥14）

### 免费阶段能做什么

- ✅ 单 Agent 对话
- ✅ 基本工具调用（文件、搜索、命令）
- ✅ 简单自动化任务
- ⚠️ 复杂推理能力有限（8B 模型）
- ⚠️ 长对话可能质量下降（32K context）

---

## 第二阶段：包月主力上场

**目标**：¥49/月获得企业级体验。

当免费模型不够用时，上 **MiniMax Coding Plan**：

| 项目 | 值 |
|------|------|
| 价格 | ¥49/月 |
| 额度 | **1500 次/5小时窗口**（约 7200 次/天） |
| 模型 | MiniMax M2.1（200K context） |
| 质量 | 对标 Claude Sonnet / GPT-4o |

### 为什么选 MiniMax？

- 💰 **性价比无敌**：¥49/月 ≈ ¥0.007/次，比按量付费便宜 100 倍
- 📦 **额度充足**：7200 次/天，6 个 Agent 平均每个 1200 次
- 🧠 **200K Context**：长对话不丢失上下文
- 🔌 **OpenAI 兼容**：`openai-completions` 协议即插即用

### 安装

```bash
clawhub install add-minimax-provider
```

详细配置见：[add-minimax-provider](https://clawhub.com/skills/add-minimax-provider)

### 配置策略

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax/MiniMax-M2.1",
        "fallbacks": [
          "siliconflow/Qwen/Qwen3-8B"
        ]
      }
    }
  }
}
```

**关键**：免费模型放在 fallback 里！MiniMax 挂了或额度用完时，自动切到免费模型，系统不会停。

---

## 第三阶段：旗舰外援加持

**目标**：关键任务用最强模型，按需付费。

| 场景 | 推荐模型 | 来源 | 价格 |
|------|----------|------|------|
| 复杂推理 | DeepSeek R1 | SiliconFlow | ¥4/¥16 per M |
| 代码重构 | Qwen3 Coder 480B | SiliconFlow | ¥8/¥16 per M |
| 顶级对话 | Kimi K2.5 | SiliconFlow | ¥4/¥21 per M |
| 长文档 | Claude Opus | NewCLI | 按额度 |
| 多模态 | Gemini 3 Pro | NewCLI | 按额度 |

### 安装

```bash
clawhub install add-siliconflow-provider  # DeepSeek/Qwen/Kimi
clawhub install add-newcli-provider       # Claude/GPT/Gemini
```

### 使用方式

不需要改默认配置。需要时用 `/model` 命令临时切换：

```
/model sf-kimi        # 切到 Kimi K2.5
/model sf-coder-480b  # 切到 Qwen3 Coder 480B
/model claude-opus    # 切到 Claude Opus
/model Minimax        # 切回 MiniMax（默认）
```

---

## Fallback 链设计

Fallback 链是 OpenClaw 的生命线——主模型挂了，自动尝试下一个。

### 推荐 Fallback 策略

```
第1优先：minimax/MiniMax-M2.1 (API Key 包月主力)
    ↓ 如果额度用完或 API 故障
第2优先：minimax-portal/MiniMax-M2.1 (OAuth 免费额度)
    ↓ 如果 OAuth 也不可用
第3优先：siliconflow/Qwen/Qwen3-8B (免费兜底)
    ↓ 如果 SiliconFlow 也挂了
第4优先：qwen-portal/coder-model (OAuth 免费)
    ↓ 如果都挂了
第5优先：deepseek/deepseek-chat (便宜)
    ↓ 最后的最后
第6优先：newcli/claude-haiku (贵但稳)
```

### 配置示例

```json
"fallbacks": [
  "minimax-portal/MiniMax-M2.1",
  "siliconflow/Qwen/Qwen3-8B",
  "qwen-portal/coder-model",
  "deepseek/deepseek-chat",
  "newcli/claude-haiku-4-5-20251001"
]
```

### 设计原则

1. **免费模型优先放前面**：先用免费的，省钱
2. **至少 2 个不同来源**：避免单一供应商全挂
3. **最贵的放最后**：Claude/GPT 只在其他全挂时才用
4. **不放推理模型**：R1/Reasoner 慢且贵，不适合 fallback

---

## 额度管理策略

### MiniMax Coding Plan 额度

```
1500 次/5小时滑动窗口
每次调用时倒算前 5 小时消耗
每天理论上限约 7200 次
```

**⚠️ 注意**：MiniMax 额度查询 API (`/coding_plan/remains`) 的数据可能不准确（窗口切换后不及时刷新）。判断额度是否可用，最可靠的方法是**发一个真实测试请求**。

### 均匀消耗技巧

**问题**：白天集中使用，凌晨浪费额度。

**解决**：用 cron 安排夜间自动任务：

```
01:00  代码质量扫描
02:00  文档评审
03:00  TODO 整理
04:00  系统健康巡检
06:00  学习材料准备
07:00  早间简报
```

### 额度监控

**🔴 重要：额度查询 API 数据不可信！**

MiniMax 的额度查询 API 存在惰性更新问题——窗口切换后如果没有新调用，计数器不会刷新，返回的数字可能是上一窗口的残留数据。

**推荐做法**：不看数字，只看真实请求能不能通。

```bash
# 判断额度是否可用的唯一可靠方法
curl -s https://api.minimaxi.com/v1/chat/completions \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M2.1","messages":[{"role":"user","content":"test"}],"max_tokens":3}'
# 返回 choices → 可用 | 返回 429 → 额度耗尽
```

配合 OpenClaw cron 定期验证即可，无需频繁轮询 API 数字。

---

## 多 Agent 架构建议

### 起步（1 个 Agent）

```
main (默认 Agent) → 处理所有事务
```

### 进阶（3-4 个 Agent）

```
main          → 日常对话、任务协调
coder         → 代码开发（用编码专用模型）
assistant     → 日程、邮件、提醒
config-bot    → 系统运维（用高级模型）
```

### 模型分配原则

| Agent 类型 | 推荐模型 | 理由 |
|-----------|----------|------|
| 日常对话 | MiniMax M2.1 | 包月，不心疼 |
| 代码开发 | MiniMax M2.1 / sf-coder-30b | 编码质量好 |
| 系统运维 | Claude Opus | 需要最高可靠性 |
| 轻量任务 | Qwen3-8B (免费) | 简单任务不浪费 |

---

## 故障排查速查

### 模型不响应

```bash
# 1. 检查系统状态
openclaw doctor

# 2. 查看错误日志
tail -20 ~/.openclaw/logs/gateway.err.log

# 3. 测试模型可用性
curl -s '<BASE_URL>/chat/completions' \
  -H 'Authorization: Bearer <KEY>' \
  -H 'Content-Type: application/json' \
  -d '{"model":"<MODEL>","messages":[{"role":"user","content":"test"}],"max_tokens":5}'
```

### Agent 不说话

1. 检查 context 是否满了：`sessions_list` 看 `totalTokens/contextTokens`
2. 超过 90% → 重置 session（删除 sessions.json 中对应条目）
3. 检查 fallback 链是否配置正确

### 配置改错崩溃

```bash
# 恢复备份
cp ~/.openclaw/openclaw.json.backup.<TIMESTAMP> ~/.openclaw/openclaw.json
openclaw gateway restart
```

**⚠️ 牢记**：`agents.defaults.models.<id>` 只允许 `alias` 字段！一个非法字段 = 全面崩溃。

### 额度用完

- MiniMax Coding Plan：等 5 小时窗口重置
- SiliconFlow：充值或切到免费模型
- 临时方案：`/model sf-qwen3-8b`（免费）

详细故障排查见：[openclaw-troubleshooting](references/troubleshooting.md)（开发中）

---

## 💰 成本速算

| 方案 | 月费 | 每日可用次数 | 适合 |
|------|------|------------|------|
| 纯免费 | ¥0 | 无限（质量有限） | 个人试玩 |
| MiniMax 包月 | ¥49 | ~7200 | 日常使用 |
| MiniMax + SF 余额 | ¥49 + ¥50 | 7200 + 按需旗舰 | 进阶用户 |
| 全家桶 | ¥49 + ¥50 + NewCLI | 全模型覆盖 | 重度用户 |

---

## 🔗 相关资源

- **OpenClaw 文档**：https://docs.openclaw.ai
- **OpenClaw GitHub**：https://github.com/openclaw/openclaw
- **ClawHub 技能市场**：https://clawhub.com
- **社区 Discord**：https://discord.com/invite/clawd

### Provider 配置技能

| 技能 | 安装命令 | 说明 |
|------|----------|------|
| SiliconFlow | `clawhub install add-siliconflow-provider` | 98+ 模型，含免费 |
| MiniMax | `clawhub install add-minimax-provider` | ¥49/月包月方案 |
| NewCLI | `clawhub install add-newcli-provider` | Claude/GPT/Gemini |

### 注册链接

- **SiliconFlow**：https://cloud.siliconflow.cn/i/ihj5inat
- **NewCLI (FoxCode)**：https://foxcode.rjj.cc/auth/register?aff=7WTAV8R
