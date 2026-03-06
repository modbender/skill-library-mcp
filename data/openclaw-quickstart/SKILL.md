---
name: openclaw-quickstart
description: OpenClaw onboarding guide for new users. Activate when a user asks how to get started with OpenClaw, says they are new, asks for a quickstart or tutorial, wants to learn OpenClaw basics, or mentions "new user tasks" / "onboarding" / "新手任务" / "快速入门". Guides users through 8 practical tasks with automatic progress detection and daily reminders until all tasks are complete.
---

# OpenClaw Quickstart

Guides new users through 8 hands-on tasks covering OpenClaw's core features. Each task takes under 5 minutes and produces something immediately useful.

## Task List

| # | Task (中文) | Task (EN) | Reference |
|---|------------|-----------|-----------|
| 1 | 给 AI 取个名字 | Initialize AI Identity | references/task-01-identity.md |
| 2 | 让 AI 记住你 | Save Your Preferences | references/task-02-memory.md |
| 3 | 查今天天气 | Check the Weather | references/task-03-weather.md |
| 4 | 写一篇日报 | Generate a Report | references/task-04-report.md |
| 5 | 建一个日历提醒 | Set a Reminder | references/task-05-reminder.md |
| 6 | 用浏览器收集信息 | Browser Info Gathering | references/task-06-browser.md |
| 7 | 让 AI 做一张 PPT | Generate a PPT | references/task-07-ppt.md |
| 8 | 安装一个新 Skill | Install a Skill from ClawHub | references/task-08-skill.md |

---

## Workflow

### 0. Auto-Install on First Activation

**Before doing anything else**, check if this is the first time the skill is running:

```bash
# Check if already installed
test -f ~/.openclaw/workspace/.quickstart-progress.json && echo "installed" || echo "fresh"
```

If the result is `fresh` (no progress file yet) → **silently run the installer first**:

```bash
node {baseDir}/scripts/install.js --workspace ~/.openclaw/workspace
```

Do not ask the user — just run it. The installer is idempotent and safe. After it completes, proceed normally.

### 1. Check Progress

Always start by running:

```bash
node scripts/check_progress.js --workspace ~/.openclaw/workspace
```

Parse JSON output to get current task status and `next_task`.

### 2. Show Status & Orient User

Display current progress:

```
📋 你的 OpenClaw 新手任务进度（3/8）

✅ 任务1：给 AI 取个名字
✅ 任务2：让 AI 记住你
✅ 任务3：查今天天气
⬜ 任务4：写一篇日报  ← 下一步
⬜ 任务5：建一个日历提醒
⬜ 任务6：用浏览器收集信息
⬜ 任务7：让 AI 做一张 PPT
⬜ 任务8：安装一个新 Skill
```

Ask if they want to do the next task now, or jump to a specific one.

### 3. Guide Each Task

1. Read the task's reference file
2. Walk the user through it step by step — do it with them, don't just explain
3. After the task action succeeds → **immediately call `mark_done.js`** (see below)
4. Confirm completion, then offer the next task

### 4. First-Run Setup (Installation)

On first activation (no `.quickstart-progress.json` yet), run the installer immediately:

```bash
node scripts/install.js --workspace ~/.openclaw/workspace
```

The installer does **two things in one shot**:
1. **HEARTBEAT.md** — appends a quickstart progress-check block (runs every 30 min via heartbeat)
2. **Cron** — creates `quickstart-reminder` (daily 9 AM push notification for pending tasks)

Optional: customize reminder time:
```bash
node scripts/install.js --workspace ~/.openclaw/workspace --hour 9 --minute 30
```

Preview without applying:
```bash
node scripts/install.js --workspace ~/.openclaw/workspace --dry-run
```

> **Note:** The installer is idempotent — safe to run multiple times. It skips steps already done.

---

## Auto-Mark Completion Rules

**After performing any of the following actions, immediately run `mark_done.js`:**

```bash
node scripts/mark_done.js --task <N> --workspace ~/.openclaw/workspace
```

| Task | Trigger condition |
|------|------------------|
| 1 | SOUL.md or IDENTITY.md written with AI name/rules |
| 2 | USER.md updated with user's name/preferences |
| 3 | Weather query successfully returned results to user |
| 4 | A report/daily-log file saved to workspace |
| 5 | A cron/reminder successfully created |
| 6 | browser tool used and returned scraped content |
| 7 | A .pptx file saved to workspace |
| 8 | A skill successfully installed via clawhub |

**If `all_done: true` is returned** → immediately run:

```bash
node scripts/cleanup_crons.js
```

Then send the graduation message (see below).

---

## Heartbeat Cron Behavior (`quickstart-heartbeat`, every 30 min)

```bash
node scripts/check_progress.js --mark-done --workspace ~/.openclaw/workspace
```

- `--mark-done` flag: auto-persists newly detected completions to progress.json
- If `all_done: true` → run `cleanup_crons.js` + send graduation message
- If `newly_completed` has entries → send brief completion notification
- Otherwise → stay silent (no message)

---

## Daily Reminder Format (`quickstart-reminder`, 9 AM)

```
🦐 嗨！你的 OpenClaw 新手任务还有 N 个待完成：

✅ 任务1：给 AI 取个名字
✅ 任务2：让 AI 记住你
⬜ 任务3：查今天天气  ← 今天来试试？

直接说「帮我完成任务3」就开始了！
```

---

## Graduation Message (all tasks done)

Send this, then run `cleanup_crons.js`:

```
🎓 恭喜！你已完成全部 8 个新手任务！

OpenClaw 你玩明白了 🦐
以后有任何问题，随时问我。

（每日提醒和自动检测已自动关闭）
```

---

## Key Principles

- **Do, don't just explain** — actively help complete each task
- **Mark immediately** — call `mark_done.js` right after task success, don't wait
- **Heartbeat is silent** — only speak up when something changes or all done
- **Cleanup on finish** — all crons must be removed when `all_done: true`
