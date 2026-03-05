---
name: d4-world-boss
description: 暗黑4世界BOSS刷新时间查询。使用 @D4世界boss 或询问暗黑4世界boss时触发。自动获取踩蘑菇地图的世界BOSS刷新时间，并询问是否设置定时提醒。
---

暗黑4世界BOSS查询

## 使用方式

**触发方式**：
- `@D4世界boss`
- `暗黑4世界boss`
- `D4世界boss刷新时间`

**执行**：
```bash
cd ~/.openclaw/skills/d4-world-boss && python3 scripts/fetch_boss.py
```

## 输出格式

```
🔥 暗黑4 世界BOSS

【当前BOSS】"诅咒之金"贪魔
【状态】🔄 刷新倒计时
【刷新倒计时】30分19秒

📊 数据来源: https://map.caimogu.cc/d4.html
```

**注意**：网站仅显示可信的倒计时数据，预计刷新时间可能不准确，以倒计时为准。

## 定时提醒

查询后询问用户是否需要设置定时提醒。如果需要，使用 cron 工具在刷新前提醒：

- 提醒时间：预计刷新前 15 分钟
- 消息示例："🔥 暗黑4 世界BOSS 即将刷新！预计时间：2026-02-09 14:30"
