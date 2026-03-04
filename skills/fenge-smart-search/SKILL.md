---
name: smart-search
description: "自动选择最佳搜索引擎的智能搜索工具。中文→Bing，英文→DuckDuckGo。无需 API Key，免费无限使用。"
metadata: { "openclaw": { "emoji": "🧠", "requires": { "bins": ["python3", "requests"] } } }
---

# Smart Search - 智能搜索

自动选择最佳搜索引擎的智能搜索工具。

## 功能

- 🧠 自动检测语言选择引擎
  - 中文 → Bing（精准）
  - 英文 → DuckDuckGo（无反爬）
- 🔍 支持手动指定引擎
- ⭐ 质量标签排序
- 📝 自动提取摘要

## 使用方式

```bash
python3 skill.py "搜索词" [引擎] [数量]
```

## 参数

| 参数 | 说明 | 可选值 |
|------|------|--------|
| 搜索词 | 要搜索的内容 | 必填 |
| 引擎 | 搜索引擎 | `bing`, `ddg`, `auto`(默认) |
| 数量 | 返回结果数 | 默认10 |

## 示例

```bash
# 自动选择（默认）
python3 skill.py "OpenClaw AI"
# → 自动选择 DuckDuckGo（检测到英文）

python3 skill.py "抖音小说教程"
# → 自动选择 Bing（检测到中文）

# 手动指定
python3 skill.py "AI" bing
python3 skill.py "AI" ddg
python3 skill.py "AI" auto 5
```

## 输出示例

```
🔍 自动选择引擎: BING (检测语言: 中文)
🔍 Bing搜索: 抖音小说教程
📊 结果: 10 条

1. ⭐⭐【优质】
   自媒体小说推文视频的制作方法 - 知乎
   https://zhuanlan.zhihu.com/p/668066771
   📝 小说推文是...
...
```

## 引擎选择规则

| 语言 | 引擎 | 原因 |
|------|------|------|
| 中文 | Bing | 中文结果更精准 |
| 英文 | DuckDuckGo | 无反爬，更稳定 |

## 特点

- ✅ 无需 API Key
- ✅ 免费无限使用
- ✅ 智能自动切换
- ✅ 质量过滤排序

## 作者

- 作者: 锋哥 (@fenge8400)
- 版本: 1.0.0
