---
name: wechat-image-generator
description: Generate beautiful images for WeChat articles (covers, comparisons, charts) with zero token cost. Use when user needs images for social media posts, article covers, data visualization. Triggers include "生成封面图", "对比图", "配图", "公众号图片".
homepage: https://github.com/jingyu525/wechat-image-generator
metadata: { "openclaw": { "emoji": "🎨", "requires": { "bins": ["python3"] } } }
---

# WeChat Image Generator

Generate beautiful images for WeChat articles with zero token cost and auto-screenshot.

## Quick Start

### 1. Cover Image (封面图)
```bash
python3 scripts/generate.py cover \
  --title "我的第一个开源项目" \
  --subtitle "Token 成本降低 90%" \
  --output output/cover.png
```

### 2. Comparison Image (对比图)
```bash
python3 scripts/generate.py compare \
  --left "# Markdown\n**Bold** text" \
  --right "HTML 渲染结果" \
  --label "1 秒转换" \
  --output output/compare.png
```

### 3. Chart Image (数据图)
```bash
python3 scripts/generate.py chart \
  --data "Token消耗:8000,650|生成耗时:20,1" \
  --labels "AI生成,预制模板" \
  --output output/chart.png
```

## Workflow

1. Run generator script with parameters
2. Script creates HTML with embedded data
3. Opens in browser via OpenClaw browser tool
4. Auto-screenshot and save to output folder

## Design Philosophy

**Zero token cost**: All templates are pre-built HTML/CSS
**Auto-screenshot**: Integrated with OpenClaw browser tool
**Customizable**: Easy to modify templates for different styles

## Token Cost Analysis

Per image generation:
- Read SKILL.md: ~500 tokens (first time only)
- Execute script: ~100 tokens
- Browser screenshot: ~50 tokens

**Total: ~650 tokens** vs DALL-E/Midjourney ~1000-5000 tokens per image.

## Requirements

- Python 3
- OpenClaw browser tool (for auto-screenshot)
