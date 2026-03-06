# Codeflow

[English](README.md) | 简体中文

Codeflow 用来运行你的 coding-agent CLI，并把会话过程结构化转发（relay）到 Discord 或 Telegram。

它在本地解析结构化输出（Claude Code 的 `stream-json`、Codex CLI 的 `--json`），把工具调用、文件写入、Shell 命令与结果发布到频道；不需要额外的 LLM 调用。

## 特性

- Discord：Webhook 投递，可选 thread（`--thread`）
- Telegram：Bot API 投递（chat + 可选 topic/thread）
- 输入支持：Claude Code（`--output-format stream-json`）、Codex CLI（`--json`），以及其他 CLI 的 raw 模式
- 投递侧做硬化：Discord 代码块拆分、Telegram 429 回退、结束汇总
- 每次运行落盘：`stream.jsonl`（事件）+ `delivery-summary.json`（投递统计）
- 非目标：远程控制；可选的 Discord bridge 设计上是只读的

## 依赖

- Python >= 3.10（`python3`）
- Claude Code 结构化输出：需要 `expect` 提供的 `unbuffer`（见 `references/setup.md`）
- 核心转发不依赖第三方 Python 包（bridge 模式除外）

## 安装/配置

按 `references/setup.md` 完成一次性配置：
- 给 `scripts/codeflow` 加执行权限
- 配 Discord（Webhook；`--thread` 可选 bot token）或 Telegram 凭据
- 跑一遍 smoke test

## 快速开始

在本目录下执行：

```basheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
# Codex CLI（结构化 JSON）
bash scripts/codeflow run -w ~/projects/myapp -- codex exec --json --full-auto 'fix tests'

# Claude Code（结构化 JSON stream）
bash scripts/codeflow run -w ~/projects/myapp -- claude -p --output-format stream-json --verbose 'your task'
```

如果是以 skill 形式安装，把 `bash scripts/codeflow` 换成 `bash {baseDir}/scripts/codeflow`。

## CLI

唯一公开入口：

```bash
bash scripts/codeflow <command> [...]
```

核心命令：
- `run`：启动一次 relay 会话
- `resume`：从 relay 目录回放（读取 `stream.jsonl`）
- `guard`：`activate|deactivate|status`（没有显式激活时阻止启动会话）
- `review`：PR review 模式
- `parallel`：按任务文件并发跑多会话
- `bridge`：可选 Discord gateway bridge（只读）
- `smoke`：前置依赖/配置校验
- `check`：本地自检（语法 + 单元测试）

以 `bash scripts/codeflow --help` 为准。

## 安全性

默认情况下，Codeflow 会转发：
- 文件写入预览
- 命令输出正文

这对排障有用，但对 secrets 一点也不友好。共享频道建议：

```bash
export CODEFLOW_SAFE_MODE=true
```

安全模式会抑制文件预览与命令输出正文（只发元数据），并启用更严格脱敏。它只能降低风险，不会把不安全流程变成安全流程。

## 常用配置

- `CODEFLOW_SAFE_MODE=true|false`：抑制文件预览 + 命令输出正文
- `CODEFLOW_OUTPUT_MODE=minimal|balanced|verbose`：频道侧输出密度（默认 `balanced`）
- `CODEFLOW_STREAM_LOG=full|redacted|off`：`stream.jsonl` 的落盘策略
- `CODEFLOW_DISCORD_ALLOW_MENTIONS=true|false`：是否允许 mentions/pings（默认 deny）
- `CODEFLOW_COMPACT=auto|true|false`：Telegram 的 compact 更新（默认 `auto`，Telegram → `true`）

运行参数与高级模式见：`references/advanced-modes.md` 与 `references/discord-output.md`。

## 文档

- `references/setup.md`：安装配置 + smoke test
- `references/discord-output.md`：频道侧输出形态、落盘产物、环境变量、架构
- `references/advanced-modes.md`：resume、PR review、parallel、Discord bridge

## 反馈渠道

Bug 反馈与功能需求： https://github.com/subjadeites/Skills/issues

## License

MIT（见 `LICENSE`）。

## 致谢

- 上游灵感：`https://clawhub.ai/allanjeng/codecast`
- 本仓库为 OpenClaw 场景做了重写/重构（多代理解析与安全/可靠性硬化）。
