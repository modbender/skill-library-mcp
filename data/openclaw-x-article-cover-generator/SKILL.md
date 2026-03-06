---
name: Openclaw-X-article-cover-generator
description: "Generate OpenClaw-themed X (Twitter) article cover images with
  fixed composition: lobster logo on right quarter, text zone on left three
  quarters."
---


# Openclaw-X-article-cover-generator

用于给 X（Twitter）文章生成 OpenClaw 主题封面图。

## 硬性规则（必须遵守）

1. **必须有标题文案才生成**
   - 若用户未提供标题：先追问标题，不生成。
2. **固定构图**
   - 龙虾 logo 主体位于画面右侧 1/4。
   - 文字区占据画面左侧 3/4。
   - 保持参考图中龙虾 logo 主体形象不变。
3. **比例**
   - 用户要求 5:2 时，API 无 5:2，使用 **21:9** 近似替代。
4. **参考图优先级**
   - 若用户提供多张参考图，最后明确“以这张为主/主参考图”的那张作为主参考。
   - 生成时以主参考图风格与主体形象为最高优先级。
5. **输出定位**
   - 面向 X 文章封面，优先可读性与留白。

## 依赖

- 环境变量：`BLT_API_KEY`
- API Base URL：`https://api.bltcy.ai`
- 模型：`gemini-3.1-flash-image-preview`

## 用法

```bash
uv run ~/.openclaw/workspace/skills/Openclaw-X-article-cover-generator/scripts/generate_cover.py \
  --title "你的标题" \
  --reference "https://aibuilder.oss-cn-hangzhou.aliyuncs.com/test/openclaw-x-cover-2026-03-02.png" \
  --output "cover.png"
```

> `--reference` 现支持两种输入：
> 1) 本地文件路径（jpg/png）
> 2) http(s) URL（推荐用 OSS 长链接，避免打包缺失 assets）

可选参数：
- `--subtitle` 副标题
- `--size` 1K/2K/4K（默认 2K）
- `--async-mode` 异步生成

## 示例提示词（内置自动生成）

脚本会自动构造如下风格提示词：

> 按参考图风格生成 OpenClaw X 文章封面图。保持龙虾 logo 主体形象不变，logo 位于画面右侧 1/4。左侧 3/4 为清晰文字区，放置标题与副标题。整体科技感、深色背景、高对比、干净留白、可读性强。