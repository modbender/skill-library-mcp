# Daily Tech Broadcast Skill / 每日科技播报 Skill

Fetch daily tech news headlines from configurable sources (e.g. Sina Tech, IT Home), output a short digest. **No API Key required.** Suitable for OpenClaw/Clawdbot cron or manual trigger.

从可抓取信息源（新浪科技、IT之家等）拉取当日科技新闻标题，生成简报。**无需 API Key**，适合 OpenClaw/Clawdbot 定时推送或手动触发。

---

## 中文说明

## 用途

- 定时任务：每天固定时间向 Discord/飞书等频道推送「每日科技新闻简报」
- 手动触发：用户说「执行每日科技播报」时生成并返回简报
- Token 消耗低（exec 脚本输出，无需大段网页注入模型）

## 安装

1. 将本目录**整体拷贝**到你的 OpenClaw workspace 的 `skills/` 下，例如：
   ```text
   <workspace>/skills/daily-tech-broadcast/
   ├── README.md
   ├── SKILL.md
   ├── requirements.txt
   └── scripts/
       └── broadcast.py
   ```
2. 依赖：仅用 Python 3 标准库，无需 `pip install`。若需扩展可参考 `requirements.txt`。
3. 确保 `python3.11`（或 `python3`）可用。

## 运行

```bash
cd skills/daily-tech-broadcast/scripts
python3.11 broadcast.py
```

简报输出到 stdout，可直接作为消息内容发送。

## 定时任务配置示例（OpenClaw cron）

在 cron 的 `payload.message` 中使用（替换路径为你的 workspace 路径）：

```text
请使用每日科技播报技能，执行播报并将结果发送到当前频道。使用命令：cd <workspace>/skills/daily-tech-broadcast/scripts && python3.11 broadcast.py 2>&1
```

例如 workspace 为 `/path/to/your/workspace` 时：

```text
请使用每日科技播报技能，执行播报并将结果发送到当前频道。使用命令：cd /path/to/your/workspace/skills/daily-tech-broadcast/scripts && python3.11 broadcast.py 2>&1
```

保持 `deliver: true` 及正确的 `channel`、`to`，以便结果投递到目标频道。

## 信息源列表（可维护）

| 来源     | URL                     |
|----------|-------------------------|
| 新浪科技 | https://tech.sina.com.cn/ |
| IT之家   | https://www.ithome.com/   |

在 `scripts/broadcast.py` 的 `NEWS_SOURCES` 中可增删或调整顺序。无需 API Key，直接 HTTP 抓取。

## 故障与降级

- 单源失败时继续使用其他源。
- 若全部失败，会输出一段降级提示（仍通过 stdout），便于用户知晓。

## 发布为独立仓库（B）

在 GitHub 上新建仓库后，将本目录**全部内容**（含 `SKILL.md`、`scripts/`、`README.md`、`requirements.txt`、`.gitignore`、`_meta.json`、`.clawhub/origin.json`）推送上去即可。他人可 clone 后拷贝到自己的 workspace `skills/` 使用。

## ClawHub 发布（C）

目录已包含 `_meta.json` 与 `.clawhub/origin.json`，符合 ClawHub 规范。

**在本地发布到 ClawHub 的步骤：**

1. **登录（仅需一次）**  
   - 若在**有浏览器的电脑**上：直接运行 `npx clawhub login`，按提示在浏览器里用 GitHub 完成授权即可。  
   - 若在**无浏览器的远程服务器**上：需要先在**你本地有浏览器的电脑**上运行一次 `npx clawhub login` 完成授权，然后在本地找到 ClawHub 存的 token（见下方「远程用 token 登录」），在远程执行：  
     `npx clawhub login --token <粘贴token> --no-browser`  
     这样远程环境就视为已登录，之后可在远程执行 `publish`。
2. 在仓库根或本 skill 父级目录执行：
   ```bash
   npx clawhub publish skills/daily-tech-broadcast --slug daily-tech-broadcast --name "每日科技播报" --version 1.0.0 --changelog "Initial release: 新浪科技/IT之家抓取，无需 API Key"
   ```
   若从本目录执行则路径改为 `.`：
   ```bash
   cd /path/to/daily-tech-broadcast-skill
   npx clawhub publish . --slug daily-tech-broadcast --name "每日科技播报" --version 1.0.0 --changelog "Initial release"
   ```

## 开放与许可

本 Skill 可单独复制、修改、分发。推送到独立仓库或通过 ClawHub 安装时，保持本目录结构即可。

---

## English

**Daily Tech Broadcast** pulls headlines from configurable, scrapable sources (Sina Tech, IT Home, etc.) and prints a short digest to stdout. No API Key needed; low token usage.

### Use cases

- **Cron**: Push a daily tech digest to Discord/Feishu/etc. at a fixed time.
- **Manual**: When the user says “run daily tech broadcast”, generate and return the digest.

### Install

1. Copy this directory into your OpenClaw workspace `skills/` (e.g. `<workspace>/skills/daily-tech-broadcast/`).
2. No extra deps: Python 3 stdlib only. Ensure `python3.11` (or `python3`) is available.

### Run

```bash
cd skills/daily-tech-broadcast/scripts
python3.11 broadcast.py
```

Output goes to stdout and can be sent as the message body.

### Cron (OpenClaw)

Set `payload.message` to (replace path with your workspace):

```text
请使用每日科技播报技能，执行播报并将结果发送到当前频道。使用命令：cd <workspace>/skills/daily-tech-broadcast/scripts && python3.11 broadcast.py 2>&1
```

Keep `deliver: true` and correct `channel` / `to` so the result is delivered.

### Data sources (customizable)

| Source   | URL                         |
|----------|-----------------------------|
| Sina Tech| https://tech.sina.com.cn/   |
| IT Home  | https://www.ithome.com/     |

You can add, remove, or reorder sources in `scripts/broadcast.py` → `NEWS_SOURCES`. No API Key; plain HTTP fetch.

### Troubleshooting

- If one source fails, others are still used.
- If all fail, a short fallback message is still printed to stdout.
