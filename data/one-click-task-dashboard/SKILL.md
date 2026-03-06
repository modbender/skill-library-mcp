---
name: one-click-task-dashboard
description: 一键生成并常驻刷新任务数据大屏（index.html + data.json + 本地服务）。适合 OpenClaw + launchctl 自动化任务可视化与巡检。
---

# One-Click Task Dashboard

## 何时使用

- 你需要一个本地可访问的数据大屏，看清楚哪些任务已跑/待跑/未跑。
- 你希望把 OpenClaw cron 任务和 macOS launchctl 任务放在一个页面里。
- 你想快速搭建常驻刷新，不再手动运行脚本。

## 一键命令

在你的工作目录执行：

```bash
bash skills/one-click-task-dashboard/scripts/setup_dashboard.sh
```

执行后会自动完成：

1. 生成大屏文件：`~/.openclaw/dashboard/index.html` 和 `~/.openclaw/dashboard/data.json`
2. 安装并启动两个 LaunchAgent：
   - `ai.x.task-dashboard-refresh`（每 5 分钟刷新）
   - `ai.x.task-dashboard-http`（本地 HTTP 服务）
3. 输出访问地址：`http://127.0.0.1:8787/index.html`

## 上架售卖（定价 100）

```bash
bash skills/one-click-task-dashboard/scripts/publish_to_clawhub.sh
```

说明：
- 脚本会先检测登录状态，再自动发布。
- ClawHub CLI 当前不支持命令行直接设置售价；脚本会提示你去创作者后台把价格改为 `100`。

如果发布被限流，可以启用自动重试（每 30 分钟一次）：

```bash
bash skills/one-click-task-dashboard/scripts/setup_publisher_retry.sh
```
