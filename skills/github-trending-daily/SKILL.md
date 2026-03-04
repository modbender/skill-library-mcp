# github-trending-daily - 每日 GitHub Trending 推送

每天定时获取 GitHub Trending 热门项目并推送到钉钉群。

## 使用方法

### 基础用法
```bash
github-trending-daily              # 获取今日热门并推送
github-trending-daily --weekly     # 获取本周热门
github-trending-daily --monthly    # 获取本月热门
github-trending-daily --dry-run    # 测试模式（预览消息）
```

### 示例
```bash
# 推送今日热门
github-trending-daily

# 推送本周热门
github-trending-daily --weekly

# 测试模式（不实际发送）
github-trending-daily --dry-run

# 只获取不推送
github-trending-daily --no-push
```

## 定时任务配置

### 工作日每天早上 9 点推送
```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 9 * * 1-5 /usr/bin/python3 ~/.openclaw/workspace/skills/github-trending-daily/github-trending-daily.py
```

### 每天早上 9 点推送（包括周末）
```bash
0 9 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/github-trending-daily/github-trending-daily.py
```

## 配置信息

- **钉钉 Webhook**: 已配置
- **安全关键词**: `AI 推送`
- **推送时间**: 默认每天早上 9 点（可自定义）
- **消息格式**: Markdown

## 消息格式

```markdown
# AI 推送

## 🔥 GitHub Trending 今日 (2026-02-25)

🥇 **huggingface/skills** (Python) +1,206⭐
   _Hugging Face 官方技能库_
   ⭐ 5,612 | [GitHub](https://github.com/huggingface/skills)

...

---
_📊 数据来源：GitHub Trending_
_🤖 自动推送 by 小牛马_
```

## 故障排除

1. **推送失败**: 检查钉钉机器人 Webhook 是否有效
2. **无数据**: 检查网络连接或 GitHub 访问状态
3. **定时任务未执行**: 检查 cron 服务状态 `sudo systemctl status cron`

## 相关技能

- `dingtalk-push`: 钉钉推送基础技能
- `github-trending`: GitHub Trending 查询技能
