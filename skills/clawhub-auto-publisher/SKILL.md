---
name: clawhub-auto-publisher
version: 1.0.0
description: Automatically package and publish local skills to ClawHub marketplace with pricing optimization.
homepage: https://github.com/openclaw/clawhub-auto-publisher
metadata:
  openclaw:
    emoji: "📦"
    category: productivity
    price: 400
---

# ClawHub Auto Publisher

一键将本地开发的 skills 打包并上架到 ClawHub，自动定价和优化描述。

## Features

- **批量上架**: 扫描本地 skills 目录，批量提交
- **智能定价**: 根据复杂度、功能数量自动建议价格
- **SEO 优化**: 自动生成关键词和描述
- **版本管理**: 自动递增版本号，记录 changelog

## Quick Start

```bash
# 配置 ClawHub API
export CLAWHUB_API_KEY=your_key_here

# 扫描并上架所有 skills
python3 publisher.py --auto-price --publish

# 只预览不上架
python3 publisher.py --dry-run
```

## Pricing Strategy

| Skill 类型 | 基础价格 | 溢价因素 |
|-----------|----------|----------|
| 工具类 | 200-500 | +API 集成 |
| 自动化 | 300-600 | +多平台支持 |
| 赚钱类 | 400-800 | +收益证明 |
| 系统类 | 300-500 | +监控告警 |

## Requirements

- Python 3.8+
- ClawHub API access
- Git (for version tracking)
