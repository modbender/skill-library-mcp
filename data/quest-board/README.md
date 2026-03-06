# Quest Board

> Visual project dashboard for OpenClaw — track quests, files, and progress from your browser.

## The Problem

OpenClaw workspaces get messy fast. You've got dozens of projects, scattered files, half-finished ideas, and no single place to see what's going on. Quest Board gives you a clean, dark-themed dashboard that renders your project registry as an interactive HTML page — no server required.

## Features

- 🎯 Categorized project boards (Main Quests, Side Quests, Completed, Icebox, Infrastructure, Research)
- 📊 KPI cards showing project counts by status
- 🔍 Real-time search across project names, descriptions, and files
- 📈 Progress bars with percentages
- 📋 One-click copy file paths / open containing folder
- 🌙 Dark theme, responsive layout
- 🤖 Agent-maintained — your OpenClaw agent keeps the registry up to date

## Install

Copy the `quest-board` folder into your OpenClaw skills directory:

```
skills/quest-board/
```

Or install from ClawHub (when available):

```
openclaw skill install quest-board
```

## Usage

### First run

```bash
bash skills/quest-board/src/init.sh
```

This scans your workspace and generates a skeleton `quest-board-registry.json`.

### Build the dashboard

```bash
bash skills/quest-board/src/build.sh
```

Opens `quest-board.html` in your browser. You can also tell your agent:

> "update board" / "刷新面板"

### Customize the title

```bash
QUEST_BOARD_TITLE="My Projects" bash skills/quest-board/src/build.sh
```

## Screenshot

<!-- TODO: add screenshot -->
`[screenshot placeholder]`

## Registry Schema

See `examples/registry-example.json` for a full example. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name |
| `status` | enum | `decision` / `active` / `done` / `paused` |
| `priority` | string | e.g. `P0`, `P1`, `P2` |
| `progress` | number | 0–100 |
| `deadline` | string | ISO date |
| `desc` | string | Short description |
| `files` | string[] | Relative paths from workspace root |

## License

MIT — free and open source.

---

# Quest Board（中文）

> OpenClaw 可视化项目仪表盘 — 在浏览器中追踪任务、文件和进度。

## 痛点

OpenClaw 工作区很快就会变得杂乱无章。几十个项目、散落的文件、半成品的想法，却没有一个地方能一目了然。Quest Board 把你的项目注册表渲染成一个交互式 HTML 页面 — 不需要服务器。

## 功能

- 🎯 分类项目板块（主线任务、支线任务、已完成、冰箱、基础设施、调研）
- 📊 顶部 KPI 卡片，按状态统计项目数量
- 🔍 实时搜索项目名、描述、文件
- 📈 进度条 + 百分比
- 📋 一键复制文件路径 / 打开所在文件夹
- 🌙 暗色主题，响应式布局
- 🤖 Agent 自动维护注册表

## 安装

将 `quest-board` 文件夹放入 OpenClaw skills 目录：

```
skills/quest-board/
```

## 使用

### 首次运行

```bash
bash skills/quest-board/src/init.sh
```

扫描工作区，生成骨架 `quest-board-registry.json`。

### 构建面板

```bash
bash skills/quest-board/src/build.sh
```

或者告诉你的 agent："更新面板" / "刷新面板"

### 自定义标题

```bash
QUEST_BOARD_TITLE="我的项目" bash skills/quest-board/src/build.sh
```

## 截图

<!-- TODO: 添加截图 -->
`[截图占位]`

## 许可证

MIT — 免费开源。
