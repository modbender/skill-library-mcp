# Cron 组合方式

Skill 负责“怎么抓”，Cron 负责“什么时候跑”。

## 推荐组合

1. 将 Skill 安装到 OpenClaw workspace。
2. 用隔离会话创建每 10 分钟任务。
3. 抓取窗口设为最近 20 分钟，做时间重叠补抓。

## 示例

```bash
openclaw cron add \
  --name "weibo-fresh-posts" \
  --every 10m \
  --session isolated \
  --message "使用 weibo-fresh-posts 技能：先点最新微博，再按发帖时间抓取并去重写入日报。" \
  --timeout-seconds 240 \
  --no-deliver
```
