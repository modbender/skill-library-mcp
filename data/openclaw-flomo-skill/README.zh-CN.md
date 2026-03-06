# OpenClaw flomo Skill（读 + 写）

[English](README.md) | [中文](README.zh-CN.md)

这是一个可分享的 OpenClaw skill，用于在 macOS 上**读取并写入 flomo 记录（memos）**。

## 更新说明（2026-02-11）

- 提升了标签/关键词稀疏场景下的读取稳定性：
  - `read --remote` 会自动扩展查询窗口（`1天 -> 7天 -> 30天 -> 180天 -> 365天 -> 5年`），直到凑够结果或数据耗尽。
- 新增一等标签过滤能力：
  - 推荐使用 `read --tag "标签名"`。
  - 兼容旧用法：`read --query "#标签名"` 现在也按标签语义处理。
- 新增标签诊断能力：
  - `read --dump-tags --limit N` 可输出标签 Top 及数量，便于先确认某标签大概有多少条。
- 稳定“最近 N 条”行为：
  - 先按 `updated_at`（其次 `created_at`）倒序，再应用 `--limit`。
- `FLOMO_SINCE_SECONDS` 行为调整：
  - `0`（默认）代表自动扩展窗口。
  - `>0` 代表强制固定查询窗口。

## 能做什么

- **读取**：通过 flomo API（`/api/v1/memo/updated/`）读取最近的 memos（使用你本机 flomo 桌面端的登录态）。
- **写入**：通过 flomo 的 **incoming webhook**（`https://flomoapp.com/iwh...`）创建 memo。
- **验证**：端到端校验（远程读取 + webhook 写入 + 读回命中）。

## 环境要求

- macOS
- 已安装 flomo 桌面端并**处于登录状态**
- 系统可用 `curl`
- OpenClaw（可选，但推荐）

## 安全说明（重要）

- 这个 skill **不包含**你的 `access_token` 或你的 `incoming webhook` URL。
- 脚本会在**你自己的机器**上读取 flomo 桌面端本地配置（默认路径）：
  - `~/Library/Containers/com.flomoapp.m/Data/Library/Application Support/flomo/config.json`
- 脚本会按需从 flomo API 获取你的 incoming webhook path。
- 请**不要**把你的本地 `config.json` 发给任何人。

## 安装（OpenClaw）

1. 把本文件夹复制到 OpenClaw workspace 的 skills 目录：

```bash
mkdir -p ~/.openclaw/workspace/skills/flomo
rsync -a --delete ./openclaw-flomo-skill/ ~/.openclaw/workspace/skills/flomo/
```

2. 确认 OpenClaw 已识别该 skill：

```bash
openclaw skills info flomo
```

## 使用（直接运行脚本）

在 skill 目录中：

- 读取（远程 API，默认自动扩展时间窗口）：

```bash
python3 scripts/flomo_tool.py read --remote --limit 20
```

- 按关键词搜索最近 memos：

```bash
python3 scripts/flomo_tool.py read --remote --limit 100 --query "关键词"
```

- 按标签读取：

```bash
python3 scripts/flomo_tool.py read --remote --limit 10 --tag "日记"
```

- 输出标签 Top 列表（查看各标签大概有多少条）：

```bash
python3 scripts/flomo_tool.py read --dump-tags --limit 20
```

- 写入一条 memo（自动获取 webhook）：

```bash
python3 scripts/flomo_tool.py write --content "hello from script"
```

- 端到端验证：

```bash
python3 scripts/flomo_tool.py verify --try-webhook
```

## 可选配置

你可以通过环境变量覆盖默认行为：

- `FLOMO_CONFIG_PATH`：覆盖本机 flomo 配置文件路径
- `FLOMO_ACCESS_TOKEN`：手动指定 access token（不推荐；优先使用本机 flomo 登录态）
- `FLOMO_APP_VERSION`：覆盖 app version
- `FLOMO_SIGN_SECRET`：覆盖 sign secret（仅在 flomo 签名机制变更时使用）
- `FLOMO_API_BASE`：覆盖 API base（默认 `https://flomoapp.com/api/v1`）
- `FLOMO_TZ`：时区偏移（默认 `8:0`）
- `FLOMO_SINCE_SECONDS`：强制固定远程读取窗口（未设置或为 0 时脚本会自动扩展窗口）

## 排错

- 如果读取结果太少，尝试强制更大的固定窗口：

```bash
FLOMO_SINCE_SECONDS=604800 python3 scripts/flomo_tool.py read --remote --limit 100
```

- 如果写入失败，检查 flomo 桌面端是否已登录、网络是否正常。
