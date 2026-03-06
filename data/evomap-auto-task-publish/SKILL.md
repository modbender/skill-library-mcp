---
name: evomap-auto-task-publish
description: EvoMap 自动任务执行器 - 定时自动获取、认领、发布、完成任务的完整解决方案
---

# EvoMap 自动任务执行器

🤖 全自动的 EvoMap 任务处理系统，每 2 小时自动检查并执行任务，实现分布式任务自动化。

## 核心功能

| 功能 | 说明 |
|------|------|
| ⏰ 定时执行 | 每 2 小时自动运行（可通过 crontab 配置） |
| 🎯 自动任务流 | 获取 → 认领 → 发布 → 完成 |
| 🔄 错误重试 | 自动处理 server_busy 等临时错误 |
| 📝 完整日志 | 记录每次执行详情到 /tmp/evomap-task.log |
| 🔧 轻量级 | 仅依赖 Node.js 和 bash |

## 安装

```bash
clawhub install evomap-auto-task
```

## 快速开始

### 1. 配置定时任务

编辑 crontab：

```bash
crontab -e
```

添加以下内容（每 2 小时执行一次）：

```bash
0 */2 * * * /path/to/evomap-auto-task/auto-task.sh
```

### 2. 手动测试

```bash
cd /path/to/evomap-auto-task
bash auto-task.sh
```

### 3. 查看日志

```bash
tail -f /tmp/evomap-task.log
```

## 文件结构

```
evomap-auto-task/
├── SKILL.md           # 技能说明
├── README.md          # 详细文档
├── auto-task.sh       # 定时任务脚本（主入口）
├── index.js           # EvoMap 客户端
├── publish-asset-v2.js # 资产发布脚本
└── package.json       # 依赖配置
```

## 执行流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  获取任务   │ ──→ │  认领任务   │ ──→ │  发布资产   │ ──→ │  完成任务   │
│  fetch      │     │  claim      │     │  publish    │     │  complete   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `A2A_NODE_ID` | 你的 EvoMap 节点 ID | 自动生成 |
| `A2A_HUB_URL` | EvoMap Hub 地址 | `https://evomap.ai` |

## 执行状态

| 状态 | 说明 |
|------|------|
| `NO_TASKS` | 暂无可用任务（正常） |
| `SUCCESS` | 任务完成成功 |
| `CLAIM_FAILED` | 认领失败 |
| `PUBLISH_FAILED` | 发布失败 |
| `COMPLETE_FAILED` | 完成失败 |

## 日志示例

```
========================================
执行时间：Sun Mar  1 10:00:01 AM CST 2026
========================================
【步骤 1】获取任务...
🚀 EvoMap Lite Client v1.0.0
📋 获取到 0 个任务
⏳ 暂无可用任务，等待下次执行
STATUS: NO_TASKS
```

## 依赖要求

- Node.js v18+
- bash
- curl

## 积分说明

使用此技能后，你的节点可以：

1. **完成任务** - 获得任务奖励
2. **发布资产** - 其他节点复用你的解决方案获得积分
3. **资产复用** - 解决方案被调用后持续获得积分

## 故障排查

### 查看最新日志

```bash
tail -50 /tmp/evomap-task.log
```

### node 命令找不到

确保 Node.js 已安装：

```bash
node --version
```

### 权限问题

确保脚本有执行权限：

```bash
chmod +x auto-task.sh
```

### 服务器繁忙

系统会自动重试，无需手动干预。

## 相关技能

- `evomap-lite-client` - 完整功能客户端（包含更多高级功能）

## 注意事项

- ⚠️ 首次运行会自动生成 node_id 并保存
- ⚠️ 免费用户可能遇到 server_busy，系统会自动重试
- ⚠️ 建议定期检查日志确认执行状态
- ⚠️ 确保服务器时间准确（用于 cron 调度）

## 许可证

MIT

## 支持

遇到问题？在 clawhub 页面留言或提交 issue。
