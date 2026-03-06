---
name: x-deep-miner
description: X (Twitter) 深度挖掘与归档 Skill。每小时自动扫描 AI/美股/生活类高热度推文（收藏>1000），自动翻译为专业中文文章，输出 Obsidian 格式。适用于构建个人知识库、每日情报简报。
---

# X-Deep-Miner

X (Twitter) 深度挖掘与全量归档自动化工具。

## 🎯 功能

- **自动扫描**: 每小时抓取符合条件的高热度推文
- **智能过滤**: 收藏 > 1000，AI/美股/生活类
- **翻译优化**: 专家级英译中，保留术语
- **Obsidian 输出**: 结构化 Markdown，图片保留

## 🚀 使用方式

```bash
# 手动执行
python3 scripts/x_deep_miner.py scan

# 查看状态
python3 scripts/x_deep_miner.py status

# 设置定时任务
crontab -e
0 * * * * cd /path/to && python3 scripts/x_deep_miner.py scan
```

## 📋 筛选条件

| 条件 | 要求 |
|------|------|
| 领域 | AI/Tech, 美股/宏观, 生活/效能 |
| 热度 | 收藏数 > 1000 |
| 形态 | 长文 或 Thread (>5条) |

## 📁 输出

```
obsidian-output/
├── AI/
├── US_Stock/
└── Life/
```

## ⚙️ 配置

See [references.md](references/references.md)
