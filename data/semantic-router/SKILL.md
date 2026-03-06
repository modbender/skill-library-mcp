---
name: semantic-router
description: 让 AI 代理根据对话内容自动选择最合适的模型。四层识别（系统过滤→关键词→指示词→语义相似度），三池架构（高速/智能/人文），五分支路由，全自动 Fallback 回路。
version: 7.6.3
author: halfmoon82
tags: [semantic, routing, model-pools, task-classification, fallback, system-passthrough, production]
requires_approval: true
---

# Semantic Router v7.6 — 生产级会话路由系统

**ClawHub**: https://clawhub.ai/halfmoon82/semantic-router  
**版本**: 7.6.0 (生产环境)  
**状态**: ✅ ROM 级固化，完全测试通过

## 🎯 这个技能解决什么问题？

### 核心问题（v7.2 新解决）

你是否遇到过：
- **Cron Job 导致会话频繁重置** — 后台定时任务打断用户交互
- **Discord/Telegram 渠道会话突然清空** — 长任务无法延续
- **AGENTS.md 被截断注入** — 大文件超过 20KB 限制
- **模型自动切换被全局配置覆盖** — 切换不生效

### 解决方案

**会话隔离架构**：
```
用户直连渠道（稳定）
    ├─ 主代理会话 → semantic-router（精准路由）
    └─ Cron Job 隔离会话（独立环境）
        ├─ cloudflared-watchdog
        ├─ Fallback 回切检查
        └─ 自定义后台任务
```

**完整配置引导**：
- 零冲突的智能合并配置
- 预检脚本防止覆盖现有设置
- 自动回滚失败的配置修改

---

## 🚀 快速安装

### 第一步：安装技能

```bash
# 从 ClawHub 安装
clawhub install https://clawhub.ai/halfmoon82/semantic-router

# 或手动复制到本地
cp -r ~/.openclaw/workspace/skills/semantic-router ~/my-projects/
```

### 第二步：运行配置引导

```bash
# 启动交互式配置向导
python3 ~/.openclaw/workspace/skills/semantic-router/scripts/setup_wizard.py

# 向导将：
# 1. 检测你的已有配置
# 2. 扫描可用模型
# 3. 推荐三池配置
# 4. 生成 pools.json 和 tasks.json
```

### 第三步：隔离现有 Cron Job（重要！）

```bash
# 列出你的所有 Cron Job
cron list | jq '.jobs[] | {id, name, sessionKey}'

# 对每个使用了渠道会话（telegram/discord/whatsapp）的 Job，执行隔离
cron update {job_id} \
  --patch '{"sessionKey": null, "sessionTarget": "isolated"}'

# 示例（cloudflared-watchdog）
cron update ba28e228-473a-4963-8413-c228762bf2d1 \
  --patch '{"sessionKey": null, "sessionTarget": "isolated"}'
```

### 第四步：验证安装

```bash
# 测试语义检查
python3 ~/.openclaw/workspace/skills/semantic-router/scripts/semantic_check.py \
  "帮我写个Python爬虫" "Highspeed"

# 预期输出
# {
#   "branch": "C",
#   "task": "development",
#   "target_pool": "Intelligence",
#   "primary_model": "claude-opus-4.6",
#   "declaration": "【语义检查 by DeepEye@halfmoon82】P1-任务切换..."
# }
```

---

## 🎓 核心概念

### 三池模型架构

| 池名 | 用途 | 模型示例 | 特点 |
|------|------|---------|------|
| **Highspeed** | 查询、检索、信息搜索 | claude-haiku-4.5 | 快速、成本低 |
| **Intelligence** | 开发、编程、复杂任务 | claude-opus-4.6 | 精准、能力强 |
| **Humanities** | 内容生成、翻译、写作 | claude-sonnet-4.6 | 平衡、流畅 |

### 两步判断法

**Step 1: 关键词 + 指示词检测**
```
"帮我写个爬虫" → 关键词 "写" + "爬虫" → 开发任务 → Intelligence
"继续刚才的" → 指示词 "继续" → 延续当前池 → B 分支
"查一下天气" → 关键词 "查" + "天气" → 查询任务 → Highspeed
```

**Step 2: 上下文关联度评分**（当 Step 1 无结果时）
```
相似度 ≥ 0.15 → 延续当前会话（B 分支）
相似度 0.08~0.15 → 延续但警告（B+ 分支）
相似度 < 0.08 → 新话题，重置会话（C-auto 分支）
```

### 五分支路由决策

| 分支 | 触发条件 | 动作 | 会话行为 |
|------|--------|------|--------|
| **A** | 关键词完全匹配 | 直接切到目标池 | 切换模型，不重置 |
| **B** | 指示词（延续） | 保持当前 | 无动作 |
| **B+** | 中等关联度（0.08~0.15） | 保持 + 警告 | 输出漂移警告 |
| **C** | 新任务关键词 | 切到目标池 | 切换模型，不重置 |
| **C-auto** | 低关联度（<0.08） | 重置 + 切池 | `/new` + 切换模型 |

---

## ⚙️ 完整配置指南（无冲突）

### 问题：为什么配置容易冲突？

你的 OpenClaw 配置可能已经存在：
- 已配置的模型提供商（OpenAI、Claude、本地 LLM 等）
- 已配置的模型池（可能与语义路由的池名冲突）
- 已定义的任务类型（可能与 tasks.json 冲突）

直接覆盖会导致：❌ 原有配置丢失  
❌ 某些模型无法使用  
❌ Cron Job 执行失败

### 解决方案：智能合并流程

#### **Step 1: 环境检测**

```bash
# 检查现有配置
cat ~/.openclaw/openclaw.json | jq '.models | keys'
# 输出: ["anthropic", "openai", "google-ai", "minimax-cn"]

cat ~/.openclaw/openclaw.json | jq '.agents[0].model'
# 输出: "custom-llmapi-lovbrowser-com/anthropic/claude-haiku-4.5"
```

#### **Step 2: 冲突预检**

```bash
# 备份当前配置
cp ~/.openclaw/openclaw.json \
   ~/.openclaw/backup/openclaw.json.backup-$(date +%s)

# 运行预检脚本
python3 ~/.openclaw/workspace/.lib/config-rollback-guard.py check

# 查看冲突报告
cat ~/.openclaw/logs/config-modification.log
```

#### **Step 3: 智能合并（推荐）**

```bash
# 选项 A: 使用自动合并脚本
python3 ~/.openclaw/workspace/.lib/merge-config.py \
  --existing ~/.openclaw/openclaw.json \
  --new ~/.openclaw/workspace/skills/semantic-router/config/pools.json \
  --output ~/.openclaw/openclaw.json.merged \
  --mode append  # 仅追加，不覆盖

# 选项 B: 手动合并（更安全）
# 编辑 ~/.openclaw/openclaw.json，按以下步骤：
# 1. 检查 .models 字段，仅追加缺失的提供商
# 2. 检查 .agents[].model，如果已有则不修改
# 3. 检查 .env，仅追加缺失的环境变量（如 LOVBROWSER_API_KEY）
```

#### **Step 4: 验证 & 激活**

```bash
# 验证 JSON 语法
python3 -c "import json; json.load(open('~/.openclaw/openclaw.json'))" && echo "✅ JSON 有效"

# 备份原配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 应用新配置
cp ~/.openclaw/openclaw.json.merged ~/.openclaw/openclaw.json

# 重启 Gateway（失败时自动回滚）
openclaw gateway restart

# 如果启动失败，自动回滚
python3 ~/.openclaw/workspace/.lib/config-rollback-guard.py rollback
```

---

## 🔧 Cron Job 隔离最佳实践

### ❌ 错误做法（会导致会话重置）

```bash
cron add \
  --name "my-background-task" \
  --sessionKey "agent:main:telegram:direct:123456" \
  --sessionTarget "main" \
  --payload '{"kind": "agentTurn", "message": "执行任务..."}'
```

**为什么错？**
- sessionKey 使用了 Telegram 渠道的直连会话
- 任务消息可能无法匹配 tasks.json 中的关键词
- semantic-router 触发 C-auto 分支 → 会话被强制重置
- 用户的长任务被打断 ❌

### ✅ 正确做法 A：隔离会话（推荐）

```bash
cron add \
  --name "my-background-task" \
  --sessionTarget "isolated" \
  --payload '{
    "kind": "agentTurn",
    "message": "运维任务：执行后台清理。检查磁盘空间...",
    "timeoutSeconds": 60
  }'

# 关键字段：
# - sessionKey: null （让 Gateway 自动分配隔离会话）
# - sessionTarget: "isolated" （完全隔离，语义路由只在这个会话内生效）
```

**优点：**
- ✅ 后台任务不影响用户会话
- ✅ 完全隔离，无须担心关键词匹配
- ✅ 自动过期清理（24h）

### ✅ 正确做法 B：包含显式关键词（如果需要直连会话）

```bash
cron add \
  --name "my-background-task" \
  --sessionKey "agent:main:cron:manual" \
  --payload '{
    "kind": "agentTurn",
    "message": "【运维检查】执行磁盘空间检查。关键词: 检查、运维、系统。"
  }'

# 消息中必须包含 tasks.json 中的关键词
# （检查、运维、系统）→ 可以匹配到 "query" 或 "operations" 任务类型
```

---

## 📊 监控与故障排除

### 检查隔离状态

```bash
# 验证 Cron Job 已隔离
cron list | jq '.jobs[] | select(.name == "cloudflared-watchdog") | {id, name, sessionKey, sessionTarget}'

# 期望输出
# {
#   "id": "ba28e228-473a-4963-8413-c228762bf2d1",
#   "name": "cloudflared-watchdog",
#   "sessionKey": null,              ✅ 已隔离
#   "sessionTarget": "isolated"      ✅ 隔离会话
# }
```

### 查看语义路由日志

```bash
# 实时监控路由决策
tail -f ~/.openclaw/logs/gateway.log | grep "semantic-router"

# 查看特定消息的路由结果
cat ~/.openclaw/workspace/.lib/semantic_check.log | jq '.[] | select(.input | contains("爬虫"))'
```

### 故障排除表

| 症状 | 根因 | 解决方案 |
|------|------|--------|
| "Cron Job 执行失败，超时 30s" | 消息文本不在 tasks.json 中，semantic-router 无法识别 | 方案 A: 改用隔离会话 / 方案 B: 添加关键词 |
| "Discord 会话仍在被重置" | sessionKey 未清空，仍使用渠道会话 | `cron update {id} --patch '{"sessionKey": null}'` |
| "模型没有切换到目标池" | 全局 default_model 覆盖了切换结果 | 改用隔离会话避免全局影响 |
| "配置修改后 Gateway 启动失败" | JSON 语法错误 或 模型不可用 | 运行 `config-rollback-guard.py rollback` 回滚 |

---

## 📋 语义检查声明格式

semantic-router 自动生成的声明格式规范：

### 声明示例
```
【语义检查 by DeepEye@halfmoon82】P2-延续｜模型池:【智能池】｜实际模型:claude-opus-4.6
【语义检查 by DeepEye@halfmoon82】P1-执行开发任务｜新会话→智能池｜实际模型:claude-opus-4.6
```

### 字段说明
| 字段 | 说明 |
|------|------|
| `PX` | P1=开发/自动化, P2=信息检索, P3=内容生成 |
| `模型池:【XXX池】` | 当前所属模型池中文名 |
| `实际模型:` | 当前调用的模型 ID |
| `新会话→` | C分支专用，表示触发 session reset |

完整规范见：[references/declaration-format.md](references/declaration-format.md)

## 📚 完整文档

| 文档 | 内容 | 位置 |
|------|------|------|
| **SKILL.md** | 技能说明（本文件） | `/skills/semantic-router/` |
| **README_v3_PRODUCTION.md** | 完整部署指南（英文） | `/skills/semantic-router/` |
| **README_v7.2_生产部署指南_中文.docx** | 完整部署指南（中文 DOCX） | `/skills/semantic-router/` |
| **declaration-format.md** | 声明格式规范（已内置） | `/skills/semantic-router/references/` |
| **完整架构指南** | 五分支、评分算法、Fallback 回路 | `docs/INTELLIGENT_ROUTING_SYSTEM.md` |
| **部署清单** | 7 步完整部署流程 | `docs/ROUTING_DEPLOYMENT_CHECKLIST.md` |

---

## 💡 常见问题

**Q: 我应该选择哪种隔离方案？**
A: 99% 的情况下，选择方案 A（隔离会话）。只有在特殊需求下（需要在用户可见的会话中执行）才选方案 B。

**Q: 隔离会话会占用额外资源吗？**
A: 不会。隔离会话是临时的，自动过期（24h），不会额外占用内存。

**Q: 如何自定义三池模型？**
A: 编辑 `~/.openclaw/workspace/.lib/pools.json`，或运行 `setup_wizard.py` 交互式配置。

**Q: 我的原有配置会被覆盖吗？**
A: 不会。使用智能合并流程（Step 3），仅追加缺失配置，保留原有设置。

---

## 🎓 学习路径

1. **快速体验（5 分钟）**
   - 运行 `setup_wizard.py`
   - 隔离现有 Cron Job
   - 测试语义检查

2. **深入理解（30 分钟）**
   - 阅读本文档
   - 自定义 tasks.json 关键词
   - 配置三池模型

3. **生产部署（1 小时）**
   - 完整配置指南
   - 智能合并配置
   - 故障排除与监控

---

## 📊 版本对比

| 特性 | v7.0 | v7.1 | v7.2 |
|------|------|------|------|
| 关键词匹配 | ✅ | ✅ | ✅ |
| 上下文评分 | ✅ | ✅ | ✅ |
| 三池架构 | ✅ | ✅ | ✅ |
| **会话隔离规则** | ❌ | ❌ | **✅ 新增** |
| **无冲突配置** | ❌ | ❌ | **✅ 新增** |
| **完整故障排除** | ❌ | ❌ | **✅ 新增** |

---

## 📝 许可与支持

- **许可证**: MIT
- **ClawHub**: https://clawhub.ai/halfmoon82/semantic-router
- **反馈**: 在 ClawHub 提交 issue 或改进建议

---

**最后更新**: 2026-03-01 15:21 GMT+8  
**维护者**: halfmoon82  
**稳定性**: ⭐⭐⭐⭐⭐ (生产级)
