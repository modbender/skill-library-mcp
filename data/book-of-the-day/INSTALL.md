# 安装说明（给使用「今日之书」技能的人）

## 一条命令安装 + 每日定时推送（默认）

若发布者已开放默认 API，执行下面命令即可完成**安装**和**每日定时推送**（每天 8 点自动收到今日之书）：

```bash
clawhub install book-of-the-day && openclaw cron add \
  --name "今日之书" \
  --cron "0 8 * * *" \
  --tz "Asia/Shanghai" \
  --session main \
  --message "给我今日之书" \
  --announce \
  --channel telegram
```

- **按需修改**：`--cron "0 8 * * *"`（每天 8:00）、`--tz "Asia/Shanghai"`（时区）、`--channel telegram`（推送渠道；若用 Slack 改为 `--channel slack --to "channel:你的频道ID"`）。
- 需先在 OpenClaw 里配置好对应 channel（Telegram/Slack 等）。
- 安装后重启 OpenClaw。

若**不需要**定时推送，只要手动问「今日之书」即可，则只运行：`clawhub install book-of-the-day`

---

## 若需自行配置 API 地址

若发布者未开放默认 API，会提供「一键安装命令」或 API 地址。收到后：

- **一键命令**：直接复制执行即可，会自动完成安装并写入配置。
- **仅 API 地址**：先执行 `clawhub install book-of-the-day`，再在 `~/.openclaw/openclaw.json` 的 `skills.entries["book-of-the-day"].config` 中设置 `BOOK_OF_THE_DAY_API_URL` 为该地址，保存后重启 OpenClaw。
