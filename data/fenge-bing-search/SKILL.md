---
name: bing-search
description: "基于 Microsoft Bing 的高精度搜索工具，支持质量过滤和智能排序。无需 API Key，免费无限使用，支持中英文搜索。"
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["python3", "requests"] } } }
---

# Bing Search - 高精准网页搜索

基于 Microsoft Bing 的高精度搜索工具，支持质量过滤和智能排序。

## 功能

- 🔍 实时搜索互联网最新信息
- ⭐ 质量标签（官方/优质/普通/低质量）
- 📝 自动提取搜索结果摘要
- 🛡️ 广告过滤
- 🌐 支持中英文搜索

## 使用方式

```bash
python3 skill.py "搜索词" [数量]
```

## 示例

```bash
# 搜索 OpenClaw
python3 skill.py "OpenClaw"

# 搜索5条结果
python3 skill.py "AI教程" 5
```

## 输出格式

```
🔍 搜索: OpenClaw AI
📊 结果: 10 条

1. ⭐⭐⭐【官方】
   OpenClaw - 官方文档
   https://docs.openclaw.ai/
   📝 从零开始玩转OpenClaw...

2. ⭐⭐【优质】
   GitHub - OpenClaw
   https://github.com/openclaw/openclaw
   ...
```

## 质量标签

| 标签 | 含义 | 示例 |
|------|------|------|
| ⭐⭐⭐ | 官方/权威 | GitHub, 官方文档 |
| ⭐⭐ | 优质 | 知乎, 掘金, 技术博客 |
| ⭐ | 普通 | 百科, 普通网站 |
| ⚠️ | 低质量 | 百度经验, 360搜索 |

## 特点

- ✅ 无需 API Key
- ✅ 免费无限使用
- ✅ 中文搜索效果好
- ✅ 高质量优先排序

## 作者

- 作者: 锋哥 (@fenge8400)
- 版本: 1.0.0
