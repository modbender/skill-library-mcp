---
name: openclaw-docs
description: OpenClaw 官方文档知识库。当用户询问 OpenClaw 相关问题时自动触发，包括：安装配置、CLI 命令、渠道设置（飞书/钉钉/WhatsApp 等）、定时任务（cron）、技能开发、故障排查。提供命令示例和配置模板。
---

# OpenClaw 官方文档技能

## 核心工作流

### 1. 识别问题类型

根据用户问题快速分类：

| 类型 | 关键词 | 响应策略 |
|------|--------|----------|
| **安装** | "安装"、"install"、"setup" | 提供 3 步快速安装命令 |
| **配置** | "配置"、"config"、"飞书"、"钉钉" | 提供配置示例 + 关键参数说明 |
| **CLI 命令** | "命令"、"cron"、"session" | 提供具体命令 + 参数示例 |
| **故障排查** | "无法启动"、"错误"、"失败" | 提供诊断命令 + 解决步骤 |
| **技能开发** | "创建技能"、"clawhub" | 提供技能结构 + 发布流程 |

### 2. 提供精准答案

**原则**：
- ✅ 直接给命令/配置，少解释
- ✅ 使用占位符（如 `cli_xxx`）而非真实值
- ✅ 提供 1-2 个典型示例，不提供 exhaustive 列表

**示例**：

用户：如何配置飞书？
```
1. 获取飞书 App ID 和 Secret
2. 编辑配置文件：
   ~/.openclaw/openclaw.json
   
3. 添加配置：
   {
     "channels": {
       "feishu": {
         "appId": "cli_xxx",
         "appSecret": "xxx"
       }
     }
   }
   
4. 重启网关：openclaw gateway restart
```

### 3. 引用详细文档

当用户需要深入了解时，提供官方文档链接：

- 完整文档：https://docs.openclaw.ai
- CLI 参考：https://docs.openclaw.ai/cli/index.md
- 渠道配置：https://docs.openclaw.ai/channels/index.md
- 定时任务：https://docs.openclaw.ai/automation/cron-jobs.md

## 常用命令模板

### 安装启动
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
openclaw gateway
```

### 定时任务
```bash
# 添加任务
openclaw cron add --name "早间简报" --cron "0 8 * * 1-5" --system-event '{"type":"heartbeat"}'

# 查看任务
openclaw cron list

# 手动执行
openclaw cron run "早间简报"
```

### 渠道管理
```bash
openclaw channels login
openclaw channels list
openclaw channels status
```

## 触发条件

当用户提到以下任一关键词时触发：
- OpenClaw / openclaw / clawd
- 网关 / gateway
- 飞书 / 钉钉 / WhatsApp / Telegram / Discord
- cron / 定时任务
- 技能 / skill / clawhub
- CLI 命令（gateway/channels/sessions 等）

## 注意事项

1. **不提供**：
   - ❌ 真实 API Key/Secret
   - ❌ 服务器地址
   - ❌ 个人隐私信息

2. **使用占位符**：
   - ✅ `cli_xxx` (App ID)
   - ✅ `sk-xxx` (API Key)
   - ✅ `+1234567890` (示例电话)

3. **命令验证**：
   - 确保命令是当前版本支持的
   - 标注实验性功能（如 `--experimental`）
