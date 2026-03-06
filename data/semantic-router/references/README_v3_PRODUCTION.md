# Semantic Router v7.2 — Production Deployment Guide

**版本**：v7.2 (生产环境)  
**发布日期**：2026-03-01  
**状态**：✅ ROM 级固化，生产环境部署完成

---

## 🎯 重大更新摘要

### v7.2 核心突破（2026-03-01）

在之前的 v7.1 版本基础上，我们发现并解决了**会话隔离**的关键问题：

#### **问题诊断**
Discord 渠道的会话频繁被重置，表面症状：
- 每 5-20 分钟自动 reset 一次
- 用户无法延续长任务
- AGENTS.md 文件被截断注入（>20KB 限制）

#### **根因分析**
两个后台 Cron Job 错误地绑定了 Discord 直连会话：
1. `cloudflared-watchdog` — 每 2h 检查一次 cloudflared 进程
2. `Fallback 回切检查` — 每 2h 检查一次模型池状态

当这些 Job 执行时：
```
Cron Job 消息 "检查 cloudflared 进程"
  ↓
semantic-router 语义检查（找不到关键词）
  ↓
触发 C-auto 分支（低关联度 <0.08）
  ↓
强制会话重置 /new
  ↓
Discord 用户会话丢失上下文 ❌
```

#### **解决方案**
将 Cron Job 的 `sessionKey` 改为 `null`，启用 `sessionTarget: "isolated"`：

```bash
# 隔离 cloudflared-watchdog
cron update ba28e228-473a-4963-8413-c228762bf2d1 \
  --patch '{"sessionKey": null, "sessionTarget": "isolated"}'

# 隔离 Fallback 回切检查
cron update 56ceed8c-9f53-438b-a33d-6a39cb38847e \
  --patch '{"sessionKey": null, "sessionTarget": "isolated"}'
```

**结果**：✅ Cron Job 现在在独立隔离会话中执行，不再影响用户直连渠道会话

---

## 📐 架构概览

### 三层会话模型

```
┌─────────────────────────────────────────────────────────┐
│                    用户直连渠道                           │
│  (Telegram / Discord / WhatsApp / Signal)                 │
│  ✅ 保持稳定，不被后台任务打断                              │
└──────────────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐    ┌──────▼──────┐   ┌──────▼──────┐
   │主代理会话 │    │ Cron Job1   │   │ Cron Job2  │
   │(MAIN)    │    │(隔离会话)    │   │(隔离会话)   │
   └──────────┘    └─────────────┘   └────────────┘
```

### 四大核心功能

| 功能 | 触发方式 | 运行位置 | 输出 |
|------|--------|--------|------|
| **语义检查** | 每条用户消息 | 主代理会话 | 路由决策 (branch/model/action) |
| **Cron 隔离** | 后台定时任务 | 独立隔离会话 | 任务完成日志（不影响主会话） |
| **Fallback 回切** | 每 2 小时 | 隔离会话 | 模型状态检查 + 日志记录 |
| **配置守护** | 修改配置前 | 本地脚本 | 快照 + 验证 + 自动回滚 |

---

## 🚀 快速开始

### 1. 前置要求

```bash
# 确保安装了必要的依赖
python3 --version  # Python 3.9+
pip3 list | grep -E "sentence-transformers|numpy"
```

### 2. 配置三池模型

编辑 `~/.openclaw/workspace/.lib/pools.json`：

```json
{
  "pools": {
    "Highspeed": {
      "primary": "custom-llmapi-lovbrowser-com/anthropic/claude-haiku-4.5",
      "fallbacks": [
        "openai/gpt-4o-mini",
        "google-ai/gemini-1.5-flash",
        "zai/glm-5"
      ]
    },
    "Intelligence": {
      "primary": "custom-llmapi-lovbrowser-com/anthropic/claude-opus-4.6",
      "fallbacks": [
        "openai/gpt-4-turbo",
        "anthropic-claude/claude-3-5-sonnet",
        "google-ai/gemini-2.0-pro"
      ]
    },
    "Humanities": {
      "primary": "custom-llmapi-lovbrowser-com/anthropic/claude-sonnet-4.6",
      "fallbacks": [
        "openai/gpt-4o",
        "google-ai/gemini-1.5-pro",
        "anthropic-claude/claude-3-opus"
      ]
    }
  }
}
```

### 3. 定义任务关键词

编辑 `~/.openclaw/workspace/.lib/tasks.json`：

```json
{
  "tasks": {
    "development": {
      "keywords": ["开发", "写代码", "编程", "实现", "调试", "接口", "API", "数据库", "爬虫", ...],
      "pool": "Intelligence"
    },
    "query": {
      "keywords": ["查一下", "搜索", "多少钱", "天气", "最新", ...],
      "pool": "Highspeed"
    },
    "content": {
      "keywords": ["写文章", "总结", "翻译", "润色", "改写", ...],
      "pool": "Humanities"
    },
    ...
  }
}
```

### 4. 运行语义检查

```bash
# 直接调用
python3 ~/.openclaw/workspace/.lib/semantic_check.py \
  "帮我写个Python爬虫" \
  "Highspeed"

# 输出示例
{
  "branch": "C",
  "current_pool": "Highspeed",
  "target_pool": "Intelligence",
  "task": "development",
  "method": "keyword",
  "primary_model": "anthropic/claude-opus-4.6",
  "action_command": "switch",
  "declaration": "【语义检查】P1-任务切换 > 开发任务｜目标池:【智能池】｜实际模型:claude-opus-4.6"
}
```

---

## 🔧 配置指南（防冲突）

### ⚠️ 对于 ClawHub 用户：完整配置引导

由于用户环境差异（模型可用性、网络状态、资源限制）可能导致配置冲突，以下是**零冲突配置流程**：

#### **Step 1: 环境检测**

```bash
# 检查已有配置
cat ~/.openclaw/openclaw.json | grep -A 50 '"models"'

# 列出可用提供商
grep -o '"provider": "[^"]*"' ~/.openclaw/openclaw.json | sort -u

# 列出可用模型
grep -o '"model": "[^"]*"' ~/.openclaw/openclaw.json | sort -u
```

#### **Step 2: 冲突预检**

使用预检脚本确保配置不会覆盖现有设置：

```bash
# 备份当前配置
cp ~/.openclaw/openclaw.json ~/.openclaw/backup/openclaw.json.backup-$(date +%s)

# 运行预检
python3 ~/.openclaw/workspace/.lib/config-rollback-guard.py check

# 查看冲突报告
cat ~/.openclaw/logs/config-modification.log
```

#### **Step 3: 智能合并配置**

使用配置合并工具（不覆盖，只补充）：

```bash
# 与现有配置合并（推荐）
python3 <<'EOF'
import json
from pathlib import Path

# 读取现有配置
with open(Path.home() / '.openclaw' / 'openclaw.json') as f:
    existing = json.load(f)

# 读取语义路由模板
with open(Path.home() / '.openclaw' / 'workspace' / '.lib' / 'semantic-router-template.json') as f:
    template = json.load(f)

# 智能合并（不覆盖现有字段）
for key in ['models', 'env', 'agents']:
    if key in template:
        if key not in existing:
            existing[key] = template[key]
        elif key == 'models':
            # 仅添加缺失的模型
            for provider, models in template['models'].items():
                if provider not in existing['models']:
                    existing['models'][provider] = models

# 保存合并结果
with open(Path.home() / '.openclaw' / 'openclaw.json.new', 'w') as f:
    json.dump(existing, f, indent=2)

print("✅ 配置已合并，新文件: openclaw.json.new")
print("请手动审查后重命名为 openclaw.json，然后重启 Gateway")
EOF
```

#### **Step 4: 验证 & 回滚**

```bash
# 验证新配置的 JSON 语法
python3 -c "import json; json.load(open('~/.openclaw/openclaw.json'))" && echo "✅ JSON 有效"

# 启动 Gateway（如果配置有问题会立即报错）
openclaw gateway restart

# 如果启动失败，自动回滚
python3 ~/.openclaw/workspace/.lib/config-rollback-guard.py rollback
```

---

## 🎛️ Cron Job 隔离最佳实践

### 规则 1: 后台任务不得使用渠道会话

❌ **错误做法**：
```bash
cron add \
  --name "my-task" \
  --sessionKey "agent:main:telegram:direct:123456" \
  ...
```

✅ **正确做法**：
```bash
cron add \
  --name "my-task" \
  --sessionTarget "isolated" \
  --sessionKey null \
  ...
```

### 规则 2: Cron 消息必须包含任务关键词

❌ **会导致 C-auto 误触发**：
```
"message": "检查服务状态"  # 无法匹配任何关键词
```

✅ **正确做法**（两种方案）：

**方案 A: 添加显式关键词**
```
"message": "运维任务：检查服务状态。运行命令：systemctl status myservice。"
# 关键词 "运维"、"检查"、"命令" 会被识别
```

**方案 B: 使用隔离会话（推荐）**
```bash
"sessionTarget": "isolated",
"sessionKey": null
# 完全隔离，semantic-router 只在这个临时会话内触发
```

### 规则 3: 隔离会话的清理

隔离会话会自动过期（默认 24h），不需要手动清理。

查看隔离会话统计：
```bash
openclaw status | grep "isolated"
# 输出: 32 isolated sessions (auto-cleanup after 24h)
```

---

## 📊 监控 & 故障排除

### 检查 Cron Job 隔离状态

```bash
cron list | jq '.jobs[] | {id, name, sessionKey, sessionTarget}'

# 输出示例
[
  {
    "id": "ba28e228-473a-4963-8413-c228762bf2d1",
    "name": "cloudflared-watchdog",
    "sessionKey": null,          # ✅ 已隔离
    "sessionTarget": "isolated"
  },
  {
    "id": "56ceed8c-9f53-438b-a33d-6a39cb38847e",
    "name": "Fallback 回切检查",
    "sessionKey": null,          # ✅ 已隔离
    "sessionTarget": "isolated"
  }
]
```

### 检查语义路由日志

```bash
# 查看最近的语义检查
tail -50 ~/.openclaw/logs/gateway.log | grep "semantic-router"

# 查看路由决策
cat ~/.openclaw/workspace/.lib/semantic_check.log | tail -20

# 查看 Cron 执行日志
tail -100 ~/.openclaw/logs/semantic-webhook.log
```

### 常见问题排除

| 现象 | 根因 | 解决方案 |
|------|------|--------|
| Cron Job 频繁失败 | 消息文本无关键词 | 添加任务关键词或改用隔离会话 |
| 会话仍被重置 | sessionKey 未清空 | `cron update <id> --patch '{"sessionKey": null}'` |
| 模型池不切换 | primary_model 被全局覆盖 | 检查 `default_model`，改为 isolated 会话 |
| 配置修改后失效 | 缓存未更新 | 运行 `config-rollback-guard.py sync && gateway restart` |

---

## 🔐 安全与权限

### 配置修改授权流程

```bash
# Step 1: 前置授权检查
python3 ~/.openclaw/workspace/.lib/pre-action-auth-check.py \
  "修改 OpenClaw 模型配置"
# 输出: BLOCK / WARN / PASS

# Step 2: 快照备份
python3 ~/.openclaw/workspace/.lib/config-rollback-guard.py snapshot

# Step 3: 执行修改
# ... (编辑文件)

# Step 4: 验证 & 回滚
python3 ~/.openclaw/workspace/.lib/config-rollback-guard.py verify
```

### 审计日志

所有敏感操作记录在：`~/.openclaw/logs/authorization-audit.log`

```bash
# 查看最近的授权决策
cat ~/.openclaw/logs/authorization-audit.log | tail -20
```

---

## 📚 文档与参考

| 文档 | 内容 | 位置 |
|------|------|------|
| **SKILL.md** | 技能说明（本文件）| `/skills/semantic-router/` |
| **README_v3_PRODUCTION.md** | 生产部署指南 | `/skills/semantic-router/` |
| **完整架构指南** | 五分支、双通道评分、Fallback 回路 | `docs/INTELLIGENT_ROUTING_SYSTEM.md` |
| **部署清单** | 7 步完整部署流程 | `docs/ROUTING_DEPLOYMENT_CHECKLIST.md` |
| **故障排除** | 5 大常见问题与解决方案 | `docs/semantic-router/TROUBLESHOOTING.md` |

---

## 🎓 学习路径

### 初级用户（快速上手）
1. 阅读本文档的"快速开始"部分
2. 运行 `python3 scripts/setup_wizard.py` 自动配置
3. 验证语义检查是否工作：`python3 scripts/semantic_check.py "测试消息" "Highspeed"`

### 中级用户（深入理解）
1. 阅读完整架构指南（`INTELLIGENT_ROUTING_SYSTEM.md`）
2. 自定义 tasks.json 关键词库
3. 配置三池模型（对应自己的资源）
4. 测试各个分支的触发条件

### 高级用户（定制化）
1. 修改 semantic_check.py 的评分算法
2. 自定义 Fallback 降级策略
3. 集成到自己的工作流（Webhook / Cron）
4. 贡献回馈（在 ClawHub 发布定制化版本）

---

## 📦 版本历史

| 版本 | 日期 | 主要变更 | 状态 |
|------|------|--------|------|
| **v7.2** | 2026-03-01 | **🎯 会话隔离突破** - Cron Job 隔离规则 + 冲突预防 | ✅ 生产版 |
| **v7.1** | 2026-02-28 | 优先级修正、Embedding 落地、Jaccard 双通道评分 | ✅ 稳定版 |
| **v7.0** | 2026-02-26 | 五分支架构、本地 embedding、Fallback 链 | ✅ 可用版 |
| v2.0 | 2026-02-23 | 交互式 Setup Wizard | ✅ 可用版 |

---

## 💬 支持与反馈

- **ClawHub**: https://clawhub.ai/halfmoon82/semantic-router
- **Issues**: 提交问题或改进建议
- **联系作者**: halfmoon82 @ OpenClaw Community

---

## 📄 许可证

MIT License — 自由使用、修改、分发

---

**最后更新**：2026-03-01 15:21 GMT+8  
**维护者**：halfmoon82  
**稳定性**：⭐⭐⭐⭐⭐ (生产级)
