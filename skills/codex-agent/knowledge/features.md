# Codex CLI 功能全览

> 本机版本: **0.104.0** (stable) | 最新 alpha: 0.105.0-alpha.17
> 最后更新: 2026-02-25

## Feature Flags

通过 `codex features list` 获取，`~/.codex/config.toml` 的 `[features]` 中开关。

### ✅ Stable（稳定，可放心使用）

| Flag | 默认 | 当前 | 说明 |
|------|------|------|------|
| `undo` | true | true | 撤销上一轮操作 |
| `shell_tool` | true | true | Shell 命令执行工具 |
| `unified_exec` | true | true | PTY 支持的统一终端执行，比旧 shell 更稳定 |
| `shell_snapshot` | true | true | 快照 shell 环境，加速重复命令 |
| `enable_request_compression` | true | true | zstd 压缩 HTTP 请求体，减少传输量 |
| `skill_mcp_dependency_install` | true | true | Skill 的 MCP 依赖自动安装 |
| `steer` | true | true | 允许模型在对话中引导用户（如建议更好的方案） |
| `collaboration_modes` | true | true | 协作模式（Plan/Code/Review 等） |
| `personality` | true | true | 模型个性设置（none/friendly/pragmatic） |

### 🧪 Experimental / Under Development（实验性，谨慎使用）

| Flag | 成熟度 | 默认 | 当前 | 说明 |
|------|--------|------|------|------|
| `js_repl` | under dev | false | **true** | 持久化 Node.js REPL，支持 top-level await，跨工具调用 |
| `js_repl_tools_only` | under dev | false | false | 强制所有直接工具调用走 js_repl |
| `multi_agent` | experimental | false | **true** | 多智能体：主 agent 可 spawn 子 agent 线程 |
| `child_agents_md` | under dev | false | **true** | 层级化 AGENTS.md：子目录的 AGENTS.md 具有局部作用域 |
| `apply_patch_freeform` | under dev | false | **true** | 自由格式 patch 应用（不限于标准 diff） |
| `codex_git_commit` | under dev | false | false | 让 Codex 自动生成 git commit |
| `runtime_metrics` | under dev | false | false | 运行时性能指标收集 |
| `sqlite` | under dev | false | false | SQLite 工具（读写本地 .db 文件） |
| `memory_tool` | under dev | false | false | 记忆工具（跨会话持久化记忆） |
| `prevent_idle_sleep` | experimental | false | false | 防止系统休眠（长任务时有用） |
| `skill_env_var_dependency_prompt` | under dev | false | false | Skill 环境变量依赖的交互提示 |
| `powershell_utf8` | under dev | false | false | Windows PowerShell UTF-8 编码 |
| `responses_websockets` | under dev | false | false | WebSocket 传输（v1） |
| `responses_websockets_v2` | under dev | false | false | WebSocket 传输（v2） |
| `apps` | experimental | false | false | App/Connector 系统（ChatGPT 连接器） |
| `apps_mcp_gateway` | under dev | false | false | App 通过 MCP Gateway 连接 |

### ❌ Deprecated / Removed

| Flag | 状态 | 说明 |
|------|------|------|
| `web_search_request` | deprecated | 已被 `web_search = "live"` 配置替代 |
| `web_search_cached` | deprecated | 已被 `web_search = "cached"` 配置替代 |
| `search_tool` | removed | 已移除 |
| `request_rule` | removed | 已移除（当前 config 仍开启，应清理） |
| `remote_models` | removed | 已移除 |
| `experimental_windows_sandbox` | removed | 已移除 |
| `elevated_windows_sandbox` | removed | 已移除 |

### ⚠️ 当前配置问题

- `request_rule = true` 已被标记为 **removed**，应从 config.toml 的 `[features]` 中删除

### Schema 中新发现的 Feature（从官方文档补充）

| Flag | 说明 |
|------|------|
| `memories` | Codex 自带的跨会话记忆系统（区别于 OpenClaw 的记忆）|
| `voice_transcription` | 语音转录 |
| `shell_zsh_fork` | zsh fork 模式 |
| `skill_approval` | Skill 审批控制 |
| `collab` | 可能是 `collaboration_modes` 的旧名/别名 |

### Schema 中存在但 `features list` 未列出的 Flag

以下 flag 出现在 JSON Schema 但不在 CLI features list 中，可能是隐藏/内部/新增：
- `collab` — 可能是 `collaboration_modes` 的旧名
- `connectors` — 可能是 `apps` 的旧名
- `memories` — 记忆系统总开关（区别于 `memory_tool`）
- `voice_transcription` — 语音转录
- `web_search` — feature flag 层的 web search 开关
- `shell_zsh_fork` — zsh fork 模式
- `skill_approval` — Skill 审批控制

## 斜杠命令（TUI 交互模式）

从源码 `slash_command.rs` 提取，按使用频率排序：

| 命令 | 说明 | 任务中可用 |
|------|------|-----------|
| `/model` | 切换模型和推理强度 | ❌ |
| `/approvals` | 配置审批策略 | ❌ |
| `/permissions` | 配置权限 | ❌ |
| `/experimental` | 切换实验性功能 | ❌ |
| `/skills` | 管理 Skills | ✅ |
| `/review` | 代码审查（支持内联参数） | ❌ |
| `/rename` | 重命名当前线程（支持内联参数） | ✅ |
| `/new` | 开始新对话 | ❌ |
| `/resume` | 恢复之前的对话 | ❌ |
| `/fork` | 分叉当前对话 | ❌ |
| `/init` | 创建 AGENTS.md | ❌ |
| `/compact` | 压缩上下文（防止 context 爆满） | ❌ |
| `/plan` | 切换到 Plan 模式（支持内联参数） | ❌ |
| `/collab` | 切换协作模式 | ✅ |
| `/agent` | 切换活跃的 agent 线程 | ✅ |
| `/diff` | 显示 git diff（含 untracked） | ✅ |
| `/mention` | 提及文件 | ✅ |
| `/status` | 显示配置和 token 用量 | ✅ |
| `/mcp` | 列出已配置的 MCP 工具 | ✅ |
| `/apps` | 管理 App/Connector | ✅ |
| `/ps` | 列出后台终端 | ✅ |
| `/clean` | 停止所有后台终端 | ✅ |
| `/statusline` | 配置状态栏显示项 | ❌ |
| `/theme` | 选择语法高亮主题 | ❌ |
| `/personality` | 选择交流风格 | ❌ |
| `/feedback` | 发送日志给维护者 | ✅ |
| `/logout` | 登出 | ❌ |
| `/quit` `/exit` | 退出 | ✅ |

## CLI 子命令

| 命令 | 说明 |
|------|------|
| `codex` | 交互模式（完全体 TUI） |
| `codex exec` / `codex e` | 非交互式单次执行 |
| `codex review` | 非交互式代码审查 |
| `codex apply` / `codex a` | 应用最近一次 diff 到本地 |
| `codex resume` | 恢复之前的会话（`--last` 恢复最近） |
| `codex fork` | 分叉之前的会话 |
| `codex cloud` | [EXPERIMENTAL] 浏览 Codex Cloud 任务 |
| `codex mcp` | 管理 MCP servers |
| `codex mcp-server` | 作为 MCP server 运行（stdio） |
| `codex app-server` | [EXPERIMENTAL] 运行 app server |
| `codex app` | 启动桌面应用 |
| `codex sandbox` | 在沙盒内运行命令 |
| `codex features` | 查看 feature flags |
| `codex login` / `codex logout` | 认证管理 |
| `codex completion` | 生成 shell 补全 |
| `codex debug` | 调试工具 |

## CLI 关键参数

| 参数 | 说明 |
|------|------|
| `-m <MODEL>` | 指定模型 |
| `-c <key=value>` | 运行时覆盖 config.toml 值（支持 dotted path） |
| `--enable <FEATURE>` | 启用 feature（等同 `-c features.<name>=true`） |
| `--disable <FEATURE>` | 禁用 feature |
| `-i <FILE>...` | 附带图片 |
| `-p <PROFILE>` | 使用配置 profile |
| `-s <SANDBOX_MODE>` | 沙盒策略：read-only / workspace-write / danger-full-access |
| `-a <APPROVAL>` | 审批策略：untrusted / on-request / never |
| `--full-auto` | = `-a on-request --sandbox workspace-write` |
| `--dangerously-bypass-approvals-and-sandbox` | 无沙盒无审批（⚠️ 极危险） |
| `-C <DIR>` | 指定工作目录 |
| `--search` | 启用实时网页搜索 |
| `--add-dir <DIR>` | 额外可写目录 |
| `--no-alt-screen` | 禁用 alternate screen（tmux 友好） |
| `--oss` | 使用本地开源模型 |
| `--local-provider <P>` | 指定本地 provider（lmstudio/ollama） |
