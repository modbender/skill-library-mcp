---
name: antigravity-rotator
description: Google Antigravity 模型全自动运维方案。提供多账号自动轮换、优先级调度、会话热更新以及赛博朋克风仪表盘。使用场景包括：(1) 自动化管理多个 Antigravity 账号，(2) 监控配额并自动切换，(3) 在不重启会话的情况下更新模型。
---

# Antigravity Rotator (反重力轮换器) 🚀

本 Skill 旨在为 OpenClaw 提供一套确定性的 Google Antigravity 模型运维工作流。它将复杂的配额监控与自动化调度封装为简单的 Action。

## 🎯 触发场景 (When to use)
- 当用户拥有多个 Antigravity 账号且希望自动最大化利用配额时。
- 当主账号配额耗尽，需要**无感切换**（不重启会话）到备用账号时。
- 当需要实时可视化监控所有账号状态和轮换历史时。

## 🛠️ 快速部署流程 (Quick Start)

### 1. 环境初始化 (必须执行)
进入 Skill 目录并运行 setup 脚本：
```bash
cd skills/antigravity-rotator
node index.js --action=setup
```
> **作用**：自动探测 `openclaw` 和 `node` 路径，并生成适配你系统的 `config.json`。

### 2. 启动管理看板
```bash
node index.js --action=dashboard
```
- **地址**：`http://localhost:18090`
- **初始化账号**：进入页面点击右上角 **“同步凭证”**，脚本会自动扫描并加载你已通过 `openclaw models auth login` 登录的账号。

### 3. 配置定时任务 (Cron)
为了让轮换全自动运行，必须在系统 `crontab` 中配置驱动：
```cron
# 每 10 分钟自动检查一次
*/10 * * * * [NODE_PATH] [SKILL_PATH]/index.js --action=rotate >> [LOG_PATH]/cron-rotate.log 2>&1
```
*注：具体的路径请参考 `node index.js --action=setup` 运行后的输出结果。*

## 📝 核心配置项详解 (`config.json`)

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `openclawBin` | String | **关键**。`openclaw` 的绝对路径。 |
| `modelPriority` | Array | 轮换优先级列表。排在前面的模型会被优先尝试。 |
| `quotas.low` | Number | 触发轮换的余量百分比阈值（建议 21）。 |
| `clientId` | String | (高级) Google OAuth 客户端 ID。默认为 Antigravity 通用 ID。 |
| `clientSecret` | String | (高级) Google OAuth 客户端密钥。 |
| `defaultProjectId` | String | (高级) Google 项目 ID，影响配额查询接口。 |

## 🌟 核心特性
- **会话热更新**：利用 OpenClaw Gateway API，在后台悄悄更换模型，用户正在进行的对话完全不受影响。
- **自动 Token 刷新**：内置 Token 刷新逻辑，确保长期运行无需手动重新登录。
- **模型激活 (Warmup)**：自动识别并激活“满血”但在计时外的模型，消除初次切换的延迟。
- **透明化日志**：看板实时展示轮换原因（如：调度更优模型、当前余量不足等）。

## 🤖 开发者资源
- **入口**: `index.js`
- **逻辑引擎**: `scripts/rotator.js` (配额查询与账号调度)
- **Web UI**: `scripts/dashboard.js` (基于 http 模块的极简服务器)
- **模板**: `assets/` 文件夹下包含详细的 JSON 模板和 Cron 示例。

---
*Antigravity Rotator - 你的 Antigravity 永不宕机* 🥵
