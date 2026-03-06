---
name: heartbeat-manager
description: Agent 心跳管理系统：自动检查任务状态、智能超时分析、日报/周报、健康度评分。与 OpenClaw 心跳同步运行。
---

# Heartbeat Manager

> 自动化任务监控 · 智能超时分析 · 日报/周报 · 健康度评分

---

## ⚠️ 安装前须知

### Git / subprocess 声明
本 Skill 在 `tools/git_ops.py` 中使用 `subprocess.run` 调用系统 `git` 命令（`git add`、`git commit`、`git push`）。

**默认行为：Git 功能完全关闭（`git.enabled: false`）**，不会执行任何 git 操作，除非你在 `config/settings.yaml` 中显式开启。

安全措施：
- 所有 `subprocess.run` 使用参数列表，**禁止 `shell=True`**（杜绝 shell 注入）
- commit message 经过净化，移除控制字符
- `auto_push` 单独开关，默认同样关闭

### 凭证声明
本 Skill **不内置、不存储任何邮件凭证**。邮件功能（告警、日报、周报）需要你在安装后自行配置：
- 提供一个 Gmail 账号及其 App Password
- 填入 `config/.env`（该文件永远不会被上传或共享）

> 若不配置邮件，Skill 仍可正常运行心跳检查（任务监控、健康度评分），仅邮件通知功能不可用。

### 副作用声明
本 Skill 会在运行时产生以下副作用：

| 操作 | 说明 | 可关闭 |
|------|------|--------|
| 写入本地文件 | 更新 `workspace/` 下的 MASTER.md、state.json 等 | ❌ 核心功能 |
| 写入日志 | 追加 `logs/heartbeat.log` | ✅ `settings.yaml` |
| IMAP 读取邮件 | 检查指定邮箱未读邮件 | ✅ `email.enabled: false` |
| SMTP 发送邮件 | 发送告警、日报、周报 | ✅ `email.enabled: false` |
| Git commit + push | 自动提交工作区变更至远程 | ✅ `git.enabled: false`（默认关闭） |

---

## Quick Start

### 1. 安装依赖

```bash
pip install pyyaml jinja2 python-dotenv
# 或使用 uv（推荐）
uv venv .venv && uv pip install --python .venv/bin/python pyyaml jinja2 python-dotenv
```

### 2. 配置邮件（可选，但强烈推荐）

```bash
cp config/.env.example config/.env
```

编辑 `config/.env`：

```env
# Gmail 发件账号
EMAIL_SENDER=your-agent@gmail.com
# Gmail 应用专用密码（非登录密码）
# 获取方式：Google 账号 → 安全性 → 两步验证 → 应用专用密码
EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
# 收件人列表（逗号分隔）
EMAIL_RECIPIENTS=you@example.com
```

> 如何获取 Gmail App Password：
> 1. 开启 Google 账号两步验证
> 2. 访问 myaccount.google.com/apppasswords
> 3. 生成一个应用专用密码并粘贴到上方

### 3. 调整配置（可选）

编辑 `config/settings.yaml`：

```yaml
email:
  enabled: true          # 改为 false 可完全禁用邮件功能

git:
  enabled: false         # 改为 true 可开启 Git 同步（默认关闭）
  auto_push: false       # 改为 true 可开启自动推送
```

### 4. 配置 Git 同步（可选，默认关闭）

> ⚠️ Git 功能会调用系统 `git` 命令向远程仓库推送内容，请确认你了解并信任此操作后再开启。

如需开启，编辑 `config/settings.yaml`：

```yaml
git:
  enabled: true       # 第一步：开启 git 功能
  auto_commit: true   # 每次心跳自动 commit
  auto_push: false    # 推送到远程（确认 remote 已配置后再开启）
```

开启前请确认：
1. 当前目录已初始化 git 仓库（`git status`）
2. 已配置远程 remote（`git remote -v`）
3. 你信任此 Skill 向该 remote 推送内容

### 5. 验证配置

```bash
python tools/heartbeat_run.py status
```

### 6. 首次心跳

```bash
python tools/heartbeat_run.py beat
```

---

## 功能概览

### `beat` — 心跳检查（每30分钟）

0. 检查 `.last_heartbeat` 标记文件，距上次 < 30 分钟则静默退出（v1.2.0 watchdog）
1. 检查 `daily.md` 例行任务完成情况
2. 检查 `todo.md` 待办 + `@due:HH:MM` 超期检测
3. 检查 `ongoing.json` 任务状态机
4. 智能超时分析（正常推进 vs 完全卡死）
4.5. 检查 `upcoming.md` 未来7天事件 — 🔴🟡🔵分级预警（v1.1.0）
4.7. 检测 Chrome relay → 在线则同步 Canvas+FSP → `📡 同步`任务自动打勾（v1.1.0）
5. 检查邮件（需配置凭证）
6. 清理已完成 todo
7. Git 同步（可选）
8. 计算健康度评分（0-100）
9. 更新 `MASTER.md` 主控表（含 `## UPCOMING 7D` 段）

### `reset` — 每日重置（00:00）

- 发送昨日完成任务日报邮件（需配置凭证）
- 重置 `daily.md` 为新一天
- 清理已完成的 ongoing 任务

### `weekly` — 周报（每周日 23:59）

- 汇总本周健康度趋势与任务统计（需配置凭证）

### `status` — 查看状态

- 无需凭证，打印当前 MASTER 快照

---

## OpenClaw 集成

在 `HEARTBEAT.md` 中添加：

```bash
cd /path/to/heartbeat-manager && python tools/heartbeat_run.py beat
```

OpenClaw 内置心跳触发时将自动执行本 Skill。

---

## 任务文件格式

**`daily.md`** — 每日例行任务
```markdown
# DAILY | 2026-02-25
- [ ] 晨间邮件检查
- [ ] 更新记忆库
- [x] 系统状态确认 @done:14:30
```

**`todo.md`** — 动态待办
```markdown
- [ ] 修复登录 bug @due:18:00
- [ ] 写周报
```

**`ongoing.json`** — 任务状态机
```json
{
  "tasks": [{
    "id": "01", "title": "毕业论文",
    "status": "WIP", "priority": "P0",
    "eta": "2026-03-01", "progress": 65,
    "context": "第三章进行中"
  }]
}
```

状态流转：`IDLE → WIP → DONE`，`WIP → WAIT → WIP`，`WIP → BLOCK`（智能检测卡死）

---

## 健康度评分

| 维度 | 权重 | 说明 |
|------|------|------|
| Daily 完成率 | 25% | 例行任务完成比例 |
| Todo 完成率 | 20% | 超期扣分 |
| Ongoing 状态 | 25% | BLOCK/超期扣分 |
| 邮件处理 | 15% | 未读过多扣分 |
| Git 同步 | 15% | push 成功满分；Git 禁用时不扣分 |

连续 3 次低于 60 分 → 邮件告警

---

## 未来事件监控 (v1.1.0)

每次心跳自动检测 Chrome 扩展 relay，在线时同步 Canvas + FSP 数据到 `workspace/upcoming.md`；离线时保留现有数据不做任何删除。

### upcoming.md 四分区格式

```markdown
# Upcoming Events

## 🔮 FUTURE （待完成事件）
- 2026-03-01 | Canvas: CS601 Quiz 3 | [作业] @due:23:59 @src:canvas @id:canvas-xxx
- 2026-03-02 | 飞行训练 KGAI N12345 | [飞行] @time:14:00-17:00 @src:fsp @id:fsp-yyy

## 📌 MANUAL （手动添加，不受自动清理影响）
- 2026-05-15 | 期末考试周 | [考试]

## ✅ DONE （已完成，事件日期+7天后自动删除）
- [x] 2026-02-25 | Internet Systems Project #1 | [作业] @done:2026-02-25

## ⏰ OVERDUE （已过期未完成）
（暂无）
```

**标签说明：**
- `@src:canvas` / `@src:fsp` — 自动同步来源，未标记 src 的为手动事件
- `@id:xxx` — 来源系统唯一ID，用于去重更新
- `@due:HH:MM` — 截止时间；`@time:HH:MM-HH:MM` — 事件时段
- `@done:YYYY-MM-DD` — 完成日期，超过7天后自动清理

**7天预警颜色（MASTER.md 中显示）：**
- 🔴 ≤1天（紧急）→ ALERTS 区也会出现
- 🟡 ≤3天（注意）
- 🔵 ≤7天（提醒）

### Canvas LMS 配置

```bash
# 获取方式：Canvas → Account → Settings → Approved Integrations → New Access Token
# 注意：部分机构学生账户可能无权生成 token（可手动维护 upcoming.md）
```

在 `config/.env` 中填入：
```env
CANVAS_API_TOKEN=your_token_here
```

在 `config/settings.yaml` 中配置：
```yaml
monitoring:
  canvas:
    enabled: true
    base_url: "https://your-canvas-url.instructure.com"
    lookahead_days: 30
```

### Flight Schedule Pro (FSP) 配置

FSP API 为机构级权限，普通学员账户通常无法获取。如有权限：

```env
FSP_API_TOKEN=your_token_here
FSP_OPERATOR_ID=your_operator_id
```

### Chrome 浏览器自动同步

每次 `beat` 自动检测本地 Chrome 扩展 relay（`127.0.0.1:18792`）是否在线：

- **在线** → 调用 `tools/site_monitor.py` 同步 Canvas + FSP → 自动在 daily.md 的 `📡 同步` 任务打勾
- **离线** → 静默跳过，保留现有 upcoming.md 数据不变

**配置 Chrome 扩展 relay：**
```bash
openclaw browser extension install
openclaw browser extension path
# → 在 Chrome 中加载该路径的扩展，填入 Gateway token，attach 目标标签页
```

> 💡 若无 API token，可每天打开 Canvas/FSP 网页并 attach Chrome 扩展，让 Eva 通过浏览器直接抓取数据，无需 API 凭证。

**安全保证：** `site_monitor.py` 使用 `active_sources` 机制，仅删除已激活来源中不再存在的事件；未配置 token 的来源完全跳过，现有数据100%保留。

---

## 看门狗机制 (v1.2.0)

配合 `*/15 * * * *` cron 运行，实现可靠的30分钟心跳间隔：

- **原理**：beat 完成后 `touch workspace/.last_heartbeat`；cron 每 15 分钟触发，先检查 mtime，距上次不到 30 分钟则静默退出
- **最大延迟**：15 分钟（cron 最差情况下一个间隔）
- **无外部依赖**：只依赖文件系统，不调用 openclaw CLI
- **自愈**：cron 是幂等的，leaky 或 missed 触发自动修正

```yaml
# openclaw cron 建议配置：
schedule: "*/15 * * * *"
```

---

## 许可

MIT License
