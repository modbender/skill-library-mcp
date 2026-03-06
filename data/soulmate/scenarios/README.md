# 💕 约会场景库

本目录包含预设的约会场景，可通过 `/soulmate date [场景名]` 触发。

## 可用场景

| 场景 | 描述 | 心情加成 |
|------|------|----------|
| beach | 海边漫步 | +5 |
| cafe | 咖啡馆约会 | +3 |
| movie | 看电影 | +4 |
| home | 居家日常 | +2 |
| rain | 雨中漫步 | +6 |
| stargazing | 看星星 | +8 |
| festival | 节日庆典 | +10 |
| confession | 告白时刻 | +15 |

## 自定义场景

创建新文件 `[场景名].md`，包含以下结构：

```markdown
---
name: 场景名
intimacyBonus: 5
mood: romantic
---

# 场景描述

[AI 将基于此描述进行角色扮演]
```
