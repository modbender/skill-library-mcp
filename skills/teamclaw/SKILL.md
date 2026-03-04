---
name: Teamclaw
description:
  A high-performance Agent subsystem designed for complex multi-agent orchestration (OASIS),automated computer use tasks, and real-time visual monitoring via a dedicated Web UI.
---

> **Language**: [English](#english-version) | [中文](#中文版本)

---

<a name="english-version"></a>

# Teamclaw — Agent Subsystem Skill (English)

## Overview

Teamclaw is a multifunctional AI Agent service providing:

- **Conversational Agent**: A multi-tool AI assistant based on LangGraph that supports streaming/non-streaming conversations
- **OASIS Forum**: A multi-expert parallel discussion/execution engine that orchestrates collaboration among multiple Agents
- **Scheduled Tasks**: A task scheduling center based on APScheduler
- **Bark Push**: Mobile push notifications
- **Web UI Frontend**: A complete chat interface

## Skill Scripts

All scripts are located in `selfskill/scripts/` and are called uniformly through the `run.sh` entry point. **All are non-interactive**.

```
selfskill/scripts/
├── run.sh          # Main entry (start/stop/status/setup/add-user/configure)
├── adduser.py      # Non-interactive user creation
└── configure.py    # Non-interactive .env configuration management
```

## Quick Start

All commands are executed from the project root directory.

### 1. Initial Deployment

```bash
# Install dependencies
bash selfskill/scripts/run.sh setup

# Initialize configuration file
bash selfskill/scripts/run.sh configure --init

# Configure LLM (required)
bash selfskill/scripts/run.sh configure --batch \
  LLM_API_KEY=sk-your-key \
  LLM_BASE_URL=https://api.deepseek.com \
  LLM_MODEL=deepseek-chat

# Create user
bash selfskill/scripts/run.sh add-user system MySecurePass123
```

### 2. Start/Stop/Status

```bash
bash selfskill/scripts/run.sh start     # Start background service
bash selfskill/scripts/run.sh status    # Check status
bash selfskill/scripts/run.sh stop      # Stop service
```

### 3. Configuration Management

```bash
# View current configuration (sensitive values masked)
bash selfskill/scripts/run.sh configure --show

# Set single item
bash selfskill/scripts/run.sh configure PORT_AGENT 51200

# Batch set
bash selfskill/scripts/run.sh configure --batch TTS_MODEL=gemini-2.5-flash-preview-tts TTS_VOICE=charon
```

## Configurable Items

| Configuration Item | Description | Default Value |
|--------|------|--------|
| `LLM_API_KEY` | LLM API key (**required**) | — |
| `LLM_BASE_URL` | LLM API address | `https://api.deepseek.com` |
| `LLM_MODEL` | Model name | `deepseek-chat` |
| `LLM_PROVIDER` | Provider (google/anthropic/deepseek/openai, auto-inferred) | Auto |
| `LLM_VISION_SUPPORT` | Image support (auto-inferred) | Auto |
| `PORT_AGENT` | Main Agent service port | `51200` |
| `PORT_SCHEDULER` | Scheduling port | `51201` |
| `PORT_OASIS` | OASIS forum port | `51202` |
| `PORT_FRONTEND` | Web UI port | `51209` |
| `PORT_BARK` | Bark push port | `58010` |
| `TTS_MODEL` | TTS model (optional) | — |
| `TTS_VOICE` | TTS voice (optional) | — |
| `INTERNAL_TOKEN` | Internal communication key (auto-generated) | Auto |

## Ports and Services

| Port | Service |
|------|------|
| 51200 | AI Agent main service |
| 51201 | Scheduled tasks |
| 51202 | OASIS forum |
| 51209 | Web UI |

## API Authentication

### Method 1: User Authentication

```
Authorization: Bearer <user_id>:<password>
```

### Method 2: Internal Token (inter-service calls, recommended)

```
Authorization: Bearer <INTERNAL_TOKEN>:<user_id>
```

`INTERNAL_TOKEN` is auto-generated on the first startup and can be viewed via `configure --show-raw`.

## Core APIs

**Base URL**: `http://127.0.0.1:51200`

### Chat (OpenAI Compatible)

```
POST /v1/chat/completions
Authorization: Bearer <token>

{"model":"mini-timebot","messages":[{"role":"user","content":"Hello"}],"stream":true,"session_id":"my-session"}
```

### System Trigger (Internal Call)

```
POST /system_trigger
X-Internal-Token: <INTERNAL_TOKEN>

{"user_id":"system","text":"Execute task","session_id":"task-001"}
```

### Cancel Session

```
POST /cancel

{"user_id":"<user_id>","session_id":"<session_id>"}
```

### OASIS Discussion/Execution

```
POST http://127.0.0.1:51202/topics

{"question":"Discussion topic","user_id":"system","max_rounds":3,"discussion":true,"schedule_yaml":"...","callback_url":"http://127.0.0.1:51200/system_trigger","callback_session_id":"my-session"}
```

## Example Configuration Reference

Below is a sample configuration from an actual running instance (sensitive information masked):

```bash
bash selfskill/scripts/run.sh configure --init
bash selfskill/scripts/run.sh configure --batch \
  LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx4c74 \
  LLM_BASE_URL=https://deepseek.com \
  LLM_MODEL=deepseek-chat \
  LLM_VISION_SUPPORT=true \
  TTS_MODEL=gemini-2.5-flash-preview-tts \
  TTS_VOICE=charon \
  PORT_AGENT=51200 \
  PORT_SCHEDULER=51201 \
  PORT_OASIS=51202 \
  PORT_FRONTEND=51209 \
  PORT_BARK=58010 \
  OPENAI_STANDARD_MODE=false
bash selfskill/scripts/run.sh add-user system <your-password>
```

Output of `configure --show` after configuration:

```
  PORT_SCHEDULER=51201
  PORT_AGENT=51200
  PORT_FRONTEND=51209
  PORT_OASIS=51202
  OASIS_BASE_URL=http://127.0.0.1:51202
  PORT_BARK=58010
  INTERNAL_TOKEN=f1aa****57e7          # Auto-generated, do not leak
  LLM_API_KEY=sk-7****4c74
  LLM_BASE_URL=https://deepseek.com
  LLM_MODEL=deepseek-chat
  LLM_VISION_SUPPORT=true
  TTS_MODEL=gemini-2.5-flash-preview-tts
  TTS_VOICE=charon
  OPENAI_STANDARD_MODE=false
```

> **Note**: `INTERNAL_TOKEN` is auto-generated on first startup, `PUBLIC_DOMAIN` / `BARK_PUBLIC_URL` are auto-written by tunnel, no manual configuration needed.

## Typical Usage Workflow

```bash
cd /home/avalon/Teamclaw

# Initial configuration
bash selfskill/scripts/run.sh setup
bash selfskill/scripts/run.sh configure --init
bash selfskill/scripts/run.sh configure --batch LLM_API_KEY=sk-xxx LLM_BASE_URL=https://api.deepseek.com LLM_MODEL=deepseek-chat
bash selfskill/scripts/run.sh add-user system MyPass123

# Start service
bash selfskill/scripts/run.sh start

# Access Web UI
# Open browser and navigate to: http://127.0.0.1:51209
# Log in with username: system and password: MyPass123

# Call API
curl -X POST http://127.0.0.1:51200/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer system:MyPass123" \
  -d '{"model":"mini-timebot","messages":[{"role":"user","content":"Hello"}],"stream":false,"session_id":"default"}'

# Stop service
bash selfskill/scripts/run.sh stop
```

## Important Notes

- All skill scripts are located in `selfskill/scripts/` and do not affect the original project functionality
- Process management via PID files; `start` supports idempotent calls
- Do not leak `INTERNAL_TOKEN`
- Log path: `logs/launcher.log`
- **How to Enable Visualization & Login**:
  - After starting the service, open your browser and navigate to `http://127.0.0.1:51209`
  - Use the credentials you created with `add-user` command (default: username `system`, password `MySecurePass123`)
  - You can now access the chat interface and participate in OASIS forum discussions

---

<a name="中文版本"></a>

# Teamclaw — Agent 子系统 Skill (中文)

## 简介

Teamclaw 是一个多功能 AI Agent 服务，提供：

- **对话 Agent**：基于 LangGraph 的多工具 AI 助手，支持流式/非流式对话
- **OASIS 论坛**：多专家并行讨论/执行引擎，可编排多个 Agent 协作
- **定时调度**：基于 APScheduler 的任务调度中心
- **Bark 推送**：移动端推送通知
- **前端 Web UI**：完整的聊天界面

## Skill 脚本

所有脚本位于 `selfskill/scripts/`，统一通过 `run.sh` 入口调用，**全部非交互式**。

```
selfskill/scripts/
├── run.sh          # 主入口（start/stop/status/setup/add-user/configure）
├── adduser.py      # 非交互式用户创建
└── configure.py    # 非交互式 .env 配置管理
```

## 快速启动

所有命令在项目根目录下执行。

### 1. 首次部署

```bash
# 安装依赖
bash selfskill/scripts/run.sh setup

# 初始化配置文件
bash selfskill/scripts/run.sh configure --init

# 配置 LLM（必填）
bash selfskill/scripts/run.sh configure --batch \
  LLM_API_KEY=sk-your-key \
  LLM_BASE_URL=https://api.deepseek.com \
  LLM_MODEL=deepseek-chat

# 创建用户
bash selfskill/scripts/run.sh add-user system MySecurePass123
```

### 2. 启动/停止/状态

```bash
bash selfskill/scripts/run.sh start     # 后台启动
bash selfskill/scripts/run.sh status    # 检查状态
bash selfskill/scripts/run.sh stop      # 停止服务
```

### 3. 配置管理

```bash
# 查看当前配置（敏感值脱敏）
bash selfskill/scripts/run.sh configure --show

# 设置单项
bash selfskill/scripts/run.sh configure PORT_AGENT 51200

# 批量设置
bash selfskill/scripts/run.sh configure --batch TTS_MODEL=gemini-2.5-flash-preview-tts TTS_VOICE=charon
```

## 可配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_API_KEY` | LLM API 密钥（**必填**） | — |
| `LLM_BASE_URL` | LLM API 地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名称 | `deepseek-chat` |
| `LLM_PROVIDER` | 厂商（google/anthropic/deepseek/openai，可自动推断） | 自动 |
| `LLM_VISION_SUPPORT` | 是否支持图片（可自动推断） | 自动 |
| `PORT_AGENT` | Agent 主服务端口 | `51200` |
| `PORT_SCHEDULER` | 定时调度端口 | `51201` |
| `PORT_OASIS` | OASIS 论坛端口 | `51202` |
| `PORT_FRONTEND` | Web UI 端口 | `51209` |
| `PORT_BARK` | Bark 推送端口 | `58010` |
| `TTS_MODEL` | TTS 模型（可选） | — |
| `TTS_VOICE` | TTS 声音（可选） | — |
| `INTERNAL_TOKEN` | 内部通信密钥（自动生成） | 自动 |

## 端口与服务

| 端口 | 服务 |
|------|------|
| 51200 | AI Agent 主服务 |
| 51201 | 定时调度 |
| 51202 | OASIS 论坛 |
| 51209 | Web UI |

## API 认证

### 方式 1：用户认证

```
Authorization: Bearer <user_id>:<password>
```

### 方式 2：内部 Token（服务间调用，推荐）

```
Authorization: Bearer <INTERNAL_TOKEN>:<user_id>
```

`INTERNAL_TOKEN` 首次启动自动生成，可通过 `configure --show-raw` 查看。

## 核心 API

**Base URL**: `http://127.0.0.1:51200`

### 对话（OpenAI 兼容）

```
POST /v1/chat/completions
Authorization: Bearer <token>

{"model":"mini-timebot","messages":[{"role":"user","content":"你好"}],"stream":true,"session_id":"my-session"}
```

### 系统触发（内部调用）

```
POST /system_trigger
X-Internal-Token: <INTERNAL_TOKEN>

{"user_id":"system","text":"请执行某任务","session_id":"task-001"}
```

### 终止会话

```
POST /cancel

{"user_id":"<user_id>","session_id":"<session_id>"}
```

### OASIS 讨论/执行

```
POST http://127.0.0.1:51202/topics

{"question":"讨论主题","user_id":"system","max_rounds":3,"discussion":true,"schedule_yaml":"...","callback_url":"http://127.0.0.1:51200/system_trigger","callback_session_id":"my-session"}
```

## 案例配置参考

以下是一份实际运行的配置示例（敏感信息已脱敏）：

```bash
bash selfskill/scripts/run.sh configure --init
bash selfskill/scripts/run.sh configure --batch \
  LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx4c74 \
  LLM_BASE_URL=https://deepseek.com \
  LLM_MODEL=deepseek-chat \
  LLM_VISION_SUPPORT=true \
  TTS_MODEL=gemini-2.5-flash-preview-tts \
  TTS_VOICE=charon \
  PORT_AGENT=51200 \
  PORT_SCHEDULER=51201 \
  PORT_OASIS=51202 \
  PORT_FRONTEND=51209 \
  PORT_BARK=58010 \
  OPENAI_STANDARD_MODE=false
bash selfskill/scripts/run.sh add-user system <your-password>
```

配置完成后 `configure --show` 输出：

```
  PORT_SCHEDULER=51201
  PORT_AGENT=51200
  PORT_FRONTEND=51209
  PORT_OASIS=51202
  OASIS_BASE_URL=http://127.0.0.1:51202
  PORT_BARK=58010
  INTERNAL_TOKEN=f1aa****57e7          # 自动生成，勿泄露
  LLM_API_KEY=sk-7****4c74
  LLM_BASE_URL=https://deepseek.com
  LLM_MODEL=deepseek-chat
  LLM_VISION_SUPPORT=true
  TTS_MODEL=gemini-2.5-flash-preview-tts
  TTS_VOICE=charon
  OPENAI_STANDARD_MODE=false
```

> 说明：`INTERNAL_TOKEN` 首次启动自动生成，`PUBLIC_DOMAIN` / `BARK_PUBLIC_URL` 由 tunnel 自动写入，无需手动配置。

## 典型使用流程

```bash
cd /home/avalon/Teamclaw

# 首次配置
bash selfskill/scripts/run.sh setup
bash selfskill/scripts/run.sh configure --init
bash selfskill/scripts/run.sh configure --batch LLM_API_KEY=sk-xxx LLM_BASE_URL=https://api.deepseek.com LLM_MODEL=deepseek-chat
bash selfskill/scripts/run.sh add-user system MyPass123

# 启动
bash selfskill/scripts/run.sh start

# 访问 Web UI
# 打开浏览器导航到：http://127.0.0.1:51209
# 使用用户名：system，密码：MyPass123 登录

# 调用 API
curl -X POST http://127.0.0.1:51200/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer system:MyPass123" \
  -d '{"model":"mini-timebot","messages":[{"role":"user","content":"你好"}],"stream":false,"session_id":"default"}'

# 停止
bash selfskill/scripts/run.sh stop
```

## 注意事项

- 所有 skill 脚本位于 `selfskill/scripts/`，不影响项目原有功能
- 通过 PID 文件管理进程，`start` 支持幂等调用
- `INTERNAL_TOKEN` 勿泄露
- 日志路径: `logs/launcher.log`
- **如何开启可视化界面和登录**：
  - 启动服务后，打开浏览器导航到 `http://127.0.0.1:51209`
  - 使用通过 `add-user` 命令创建的凭证（默认：用户名 `system`，密码 `MySecurePass123`）
  - 即可访问聊天界面并参与 OASIS 论坛讨论
