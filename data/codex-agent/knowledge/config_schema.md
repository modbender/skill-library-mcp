# Codex config.toml 完整配置参考

> 基于 JSON Schema (codex-rs/core/config.schema.json) + 本机实际配置
> 最后更新: 2026-02-24

## 模型与推理

| 字段 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型名称，如 `"gpt-5.2"` |
| `model_provider` | string | `model_providers` map 中的 key |
| `model_reasoning_effort` | enum | `none` / `minimal` / `low` / `medium` / `high` / `xhigh` |
| `model_reasoning_summary` | enum | `auto` / `concise` / `detailed` / `none` |
| `model_verbosity` | enum | GPT-5 专用：`low` / `medium` / `high` |
| `model_context_window` | int | 上下文窗口大小（tokens） |
| `model_auto_compact_token_limit` | int | 触发自动压缩的 token 阈值 |
| `model_supports_reasoning_summaries` | bool | 强制启用推理摘要 |
| `plan_mode_reasoning_effort` | enum | Plan 模式专用推理强度（默认 `medium`） |
| `review_model` | string | `/review` 使用的模型 |
| `model_catalog_json` | path | 模型目录 JSON 路径 |

## Provider 配置

```toml
[model_providers.<name>]
name = "显示名"              # 必填
base_url = "http://..."     # API 地址
wire_api = "responses"      # responses（默认）或 chat
requires_openai_auth = false
env_key = "API_KEY_ENV_VAR"
env_key_instructions = "获取方式说明"
experimental_bearer_token = "..."  # 不推荐，用 env_key 更安全

# HTTP 配置
http_headers = { "X-Custom" = "value" }
env_http_headers = { "Auth" = "ENV_VAR_NAME" }
query_params = { "key" = "value" }
request_max_retries = 3
stream_idle_timeout_ms = 30000
stream_max_retries = 3
supports_websockets = false
```

## 沙盒与审批

| 字段 | 类型 | 说明 |
|------|------|------|
| `sandbox_mode` | enum | `read-only` / `workspace-write` / `danger-full-access` |
| `approval_policy` | enum/object | `untrusted` / `on-request` / `never` / `{ reject = {...} }` |

```toml
# 细粒度审批拒绝
[approval_policy]
[approval_policy.reject]
# 可配置自动拒绝特定类别的审批请求
```

## 沙盒工作区写入配置

```toml
[sandbox_workspace_write]
# SandboxWorkspaceWrite 的详细配置
```

## 指令与提示

| 字段 | 类型 | 说明 |
|------|------|------|
| `instructions` | string | 系统指令 |
| `developer_instructions` | string | developer role 消息 |
| `model_instructions_file` | path | 模型指令文件路径（覆盖内置提示） |
| `compact_prompt` | string | 历史压缩时使用的提示 |
| `personality` | enum | `none` / `friendly` / `pragmatic` |
| `project_doc_fallback_filenames` | [string] | AGENTS.md 不存在时的回退文件名 |
| `project_doc_max_bytes` | int | AGENTS.md 最大读取字节数 |
| `project_root_markers` | [string] | 项目根检测标记 |

## 网页搜索

| 字段 | 类型 | 说明 |
|------|------|------|
| `web_search` | enum | `"disabled"` / `"cached"` / `"live"` |

## Notify（🔑 关键：异步通知）

```toml
# notify 是一个字符串数组，agent 完成 turn 时执行
notify = ["python3", "/path/to/notify.py"]
```

**类型**: `array of string`（可选，默认 null）
**触发时机**: Codex 发出 supported events 时 spawn 这个命令（当前仅 `agent-turn-complete`）
**传入数据**: Codex 通过 **命令行参数** 传入 JSON payload（`sys.argv[1]`）

### JSON Payload 结构

```json
{
  "type": "agent-turn-complete",
  "thread-id": "xxx",
  "last-assistant-message": "完成摘要文本",
  "input-messages": ["用户输入消息列表"]
}
```

### 关键字段

- `type` — 事件类型，目前只有 `agent-turn-complete`
- `last-assistant-message` — Codex 最后一条回复的摘要
- `thread-id` — 会话线程 ID
- `input-messages` — 触发本轮的用户输入

### 示例 notify 脚本

```python
#!/usr/bin/env python3
import json, subprocess, sys

notification = json.loads(sys.argv[1])
if notification.get("type") != "agent-turn-complete":
    sys.exit(0)

title = f"Codex: {notification.get('last-assistant-message', 'Turn Complete!')}"
# 在这里调用 openclaw 通知、发送 Telegram 消息、或触发 webhook
```

### 用途

这是我们实现 **hooks 唤醒** 的关键机制：
1. Codex 完成 turn → 触发 notify 脚本
2. 脚本通知 OpenClaw agent（通过 Telegram/sessions_send/webhook）
3. Agent 被唤醒，去检查 Codex 的输出
4. 不满意则继续发指令，Codex 再次完成 turn 又触发 notify
5. 循环直到满意，向涛哥汇报

## TUI 通知

```toml
[tui]
notifications = true          # 或 ["命令", "参数"]
notification_method = "auto"  # auto / osc9 / bel
alternate_screen = "auto"     # auto / always / never
animations = true
show_tooltips = true
theme = "..."                 # 语法高亮主题
status_line = ["model-with-reasoning", "context-remaining", "current-dir"]
```

## MCP Servers

```toml
[mcp_servers.<name>]
type = "stdio"           # stdio 模式
command = "npx"
args = ["-y", "package@latest"]

[mcp_servers.<name>.env]
API_KEY = "..."
```

## Apps/Connectors

```toml
[apps._default]
enabled = true
destructive_enabled = false
open_world_enabled = false

[apps.<app-name>]
enabled = true
default_tools_enabled = true
default_tools_approval_mode = "auto"  # auto / prompt / approve
destructive_enabled = false
open_world_enabled = false

[apps.<app-name>.tools.<tool-name>]
enabled = true
approval_mode = "auto"
```

## 多智能体 (Agents)

```toml
[agents]
max_depth = 3       # 最大嵌套深度
max_threads = 5     # 最大并发线程

[agents.<role-name>]
description = "角色描述"
config_file = "path/to/role-config.toml"  # 角色专属配置
```

## 记忆系统 (Memories)

```toml
[memories]
phase_1_model = "..."              # 线程摘要模型
phase_2_model = "..."              # 记忆整合模型
max_raw_memories_for_global = 100  # 全局整合的最大原始记忆数
max_rollout_age_days = 30          # 用于记忆的线程最大天数
max_rollouts_per_startup = 5       # 每次启动处理的候选数
min_rollout_idle_hours = 12        # 最小空闲时间（推荐 >12h）
```

## Skills

```toml
[skills]
config = [
  { enabled = true, path = "/absolute/path/to/SKILL.md" }
]
```

## Shell 环境

```toml
[shell_environment_policy]
inherit = "all"  # 或具体策略
```

## 网络权限（沙盒内网络控制）

```toml
[permissions.network]
enabled = true
mode = "limited"              # limited / full
allowed_domains = ["api.example.com"]
denied_domains = ["evil.com"]
allow_local_binding = false
allow_upstream_proxy = false
enable_socks5 = false
```

## 环境变量

```toml
[env]
API_KEY = "value"
```

## 项目信任

```toml
[projects."/path/to/project"]
trust_level = "trusted"
```

## History

```toml
[history]
persistence = "save-all"  # save-all / none
max_bytes = 10485760      # 最大文件大小
```

## Ghost Snapshot（用于 undo）

```toml
[ghost_snapshot]
disable_warnings = false
ignore_large_untracked_dirs = 1000
ignore_large_untracked_files = 1048576
```

## 其他

| 字段 | 类型 | 说明 |
|------|------|------|
| `disable_response_storage` | bool | 禁用会话云存储 |
| `commit_attribution` | string | commit co-author 署名 |
| `file_opener` | URI | 文件引用的 URI opener |
| `hide_agent_reasoning` | bool | 隐藏推理过程 |
| `show_raw_agent_reasoning` | bool | 显示原始推理内容 |
| `check_for_update_on_startup` | bool | 启动时检查更新 |
| `tool_output_token_limit` | int | 工具输出 token 预算 |
| `background_terminal_max_timeout` | int(ms) | 后台终端最大超时 |
| `allow_login_shell` | bool | 允许登录 shell |
| `disable_paste_burst` | bool | 禁用粘贴检测 |
| `log_dir` | path | 日志目录 |
| `suppress_unstable_features_warning` | bool | 抑制不稳定功能警告 |
| `cli_auth_credentials_store` | enum | `file` / `keyring` / `auto` / `ephemeral` |
| `profile` | string | 使用的 profile 名 |
| `js_repl_node_path` | path | js_repl 的 Node 路径 |
| `js_repl_node_module_dirs` | [path] | js_repl 模块搜索目录 |
| `zsh_path` | path | 自定义 zsh 路径 |

## Profiles

```toml
[profiles.<name>]
model = "..."
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
# ... 支持 ConfigProfile 的所有字段
```
